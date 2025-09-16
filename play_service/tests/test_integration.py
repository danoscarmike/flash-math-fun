"""Integration tests for the flash card app."""

from unittest.mock import Mock, patch

import pytest

from app.components import FlashCard, SettingsPanel
from app.services import SessionState, generate_question_pool, get_max_valid_questions


class TestGameFlow:
    """Test complete game flow integration."""

    @pytest.mark.integration
    def test_complete_game_flow(self):
        """Test a complete game flow from setup to finish."""
        # Initialize session state
        session_state = SessionState()
        session_state.selected_numbers = [2, 3]
        session_state.operations = ["Multiplication"]
        session_state.cards_per_round = 5

        # Generate question pool
        question_pool = generate_question_pool(
            session_state.operations, session_state.selected_numbers
        )
        session_state.question_pool = question_pool

        # Verify question pool
        assert len(question_pool) > 0
        assert all(isinstance(q, tuple) and len(q) == 2 for q in question_pool)

        # Test max valid questions calculation
        max_questions = get_max_valid_questions(
            session_state.operations, session_state.selected_numbers
        )
        assert max_questions > 0
        assert session_state.cards_per_round <= max_questions

        # Test game progression
        session_state.game_phase = "playing"
        session_state.current_card = 0

        # Simulate playing through cards
        for i in range(session_state.cards_per_round):
            session_state.current_card = i + 1
            question, answer = question_pool[i]
            session_state.current_question = question
            session_state.current_answer = answer

            assert session_state.current_question is not None
            assert session_state.current_answer is not None

        # End game
        session_state.game_phase = "finished"
        assert session_state.game_phase == "finished"

    @pytest.mark.integration
    def test_settings_panel_integration(self, session_state):
        """Test settings panel integration with session state."""
        with patch("nicegui.ui") as mock_ui:
            panel = SettingsPanel(session_state)

            # Test number selection
            panel.number_selector = Mock()
            panel.operations_selector = Mock()
            panel.cards_selector = Mock()

            # Simulate changing numbers
            session_state.selected_numbers = [1, 2, 3]
            panel.on_settings_change()

            # Verify callbacks were called
            panel.cards_selector.update_options.assert_called_once()

    @pytest.mark.integration
    def test_flash_card_integration(self, session_state, sample_question_pool):
        """Test flash card integration with session state."""
        session_state.question_pool = sample_question_pool
        session_state.current_card = 0

        card = FlashCard(session_state)

        # Test advancing through cards
        for i in range(min(3, len(sample_question_pool))):
            card.advance_card()
            assert session_state.current_card == i + 1
            assert session_state.current_question is not None
            assert session_state.current_answer is not None

    @pytest.mark.integration
    def test_question_generation_consistency(self):
        """Test that question generation is consistent across calls."""
        operations = ["Multiplication"]
        numbers = [2, 3]

        # Generate questions multiple times
        pool1 = generate_question_pool(operations, numbers)
        pool2 = generate_question_pool(operations, numbers)

        # Should have same questions (but possibly different order due to shuffling)
        assert len(pool1) == len(pool2)
        assert set(pool1) == set(pool2)

    @pytest.mark.integration
    def test_max_questions_accuracy(self):
        """Test that max questions calculation is accurate."""
        operations = ["Multiplication"]
        numbers = [2, 3]

        # Calculate max questions
        max_questions = get_max_valid_questions(operations, numbers)

        # Generate actual questions
        actual_questions = generate_question_pool(operations, numbers)

        # Max should be at least as many as actual questions
        assert max_questions >= len(actual_questions)

        # For multiplication, should be exactly numbers × 12
        expected_max = len(numbers) * 12
        assert max_questions == expected_max

    @pytest.mark.integration
    def test_multiple_operations_integration(self):
        """Test integration with multiple operations."""
        operations = ["Addition", "Multiplication"]
        numbers = [2, 3]

        # Generate questions
        questions = generate_question_pool(operations, numbers)

        # Should have both addition and multiplication questions
        addition_questions = [q for q in questions if "+" in q[0]]
        multiplication_questions = [q for q in questions if "x" in q[0]]

        assert len(addition_questions) > 0
        assert len(multiplication_questions) > 0
        assert len(questions) == len(addition_questions) + len(multiplication_questions)

        # Test max questions calculation
        max_questions = get_max_valid_questions(operations, numbers)
        addition_max = get_max_valid_questions(["Addition"], numbers)
        multiplication_max = get_max_valid_questions(["Multiplication"], numbers)

        assert max_questions == addition_max + multiplication_max

    @pytest.mark.integration
    def test_division_questions_integration(self):
        """Test integration with division questions."""
        operations = ["Division"]
        numbers = [2, 4, 6]  # Numbers that divide evenly

        # Generate questions
        questions = generate_question_pool(operations, numbers)

        # Should have division questions
        assert len(questions) > 0
        assert all("÷" in q[0] for q in questions)

        # Verify answers are correct
        for question, answer in questions:
            parts = question.split(" ÷ ")
            if len(parts) == 2:
                dividend = int(parts[0])
                divisor = int(parts[1])
                assert dividend // divisor == answer

    @pytest.mark.integration
    def test_subtraction_questions_integration(self):
        """Test integration with subtraction questions."""
        operations = ["Subtraction"]
        numbers = [2, 3]

        # Generate questions
        questions = generate_question_pool(operations, numbers)

        # Should have subtraction questions
        assert len(questions) > 0
        assert all("-" in q[0] for q in questions)

        # Verify answers are correct and positive
        for question, answer in questions:
            parts = question.split(" - ")
            if len(parts) == 2:
                minuend = int(parts[0])
                subtrahend = int(parts[1])
                assert minuend - subtrahend == answer
                assert answer >= 0  # Should always be positive

    @pytest.mark.integration
    def test_edge_cases_integration(self):
        """Test edge cases in integration."""
        # Test with single number
        operations = ["Multiplication"]
        numbers = [1]
        questions = generate_question_pool(operations, numbers)
        assert len(questions) == 12  # 1 × 1 through 1 × 12

        # Test with single operation
        operations = ["Addition"]
        numbers = [1, 2, 3, 4, 5]
        questions = generate_question_pool(operations, numbers)
        assert len(questions) == 60  # 5 × 12

        # Test with no valid division questions
        operations = ["Division"]
        numbers = [3, 5, 7]  # Prime numbers
        questions = generate_question_pool(operations, numbers)
        # Should have some questions where the numbers divide evenly
        assert len(questions) > 0

    @pytest.mark.integration
    def test_session_state_persistence(self):
        """Test that session state persists correctly across operations."""
        session_state = SessionState()

        # Set initial state
        session_state.selected_numbers = [1, 2, 3]
        session_state.operations = ["Addition", "Multiplication"]
        session_state.cards_per_round = 15

        # Generate questions
        questions = generate_question_pool(
            session_state.operations, session_state.selected_numbers
        )
        session_state.question_pool = questions

        # Verify state is preserved
        assert session_state.selected_numbers == [1, 2, 3]
        assert session_state.operations == ["Addition", "Multiplication"]
        assert session_state.cards_per_round == 15
        assert len(session_state.question_pool) > 0

        # Test max questions calculation with current state
        max_questions = get_max_valid_questions(
            session_state.operations, session_state.selected_numbers
        )
        assert max_questions > 0
        assert session_state.cards_per_round <= max_questions
