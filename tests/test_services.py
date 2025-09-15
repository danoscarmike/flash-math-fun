"""Tests for the services module."""

from unittest.mock import patch

import pytest

from app.services import (SessionState, generate_question_pool,
                          get_max_valid_questions)


class TestQuestionGeneration:
    """Test question generation functionality."""

    @pytest.mark.unit
    def test_generate_question_pool_multiplication(
        self, sample_numbers, expected_multiplication_questions
    ):
        """Test generating multiplication questions."""
        operations = ["Multiplication"]
        questions = generate_question_pool(operations, sample_numbers)

        # Convert to set for comparison (order doesn't matter due to shuffling)
        question_set = set(questions)
        expected_set = set(expected_multiplication_questions)

        assert len(questions) == len(expected_multiplication_questions)
        assert question_set == expected_set

    @pytest.mark.unit
    def test_generate_question_pool_addition(
        self, sample_numbers, expected_addition_questions
    ):
        """Test generating addition questions."""
        operations = ["Addition"]
        questions = generate_question_pool(operations, sample_numbers)

        question_set = set(questions)
        expected_set = set(expected_addition_questions)

        assert len(questions) == len(expected_addition_questions)
        assert question_set == expected_set

    @pytest.mark.unit
    def test_generate_question_pool_division(
        self, sample_numbers, expected_division_questions
    ):
        """Test generating division questions."""
        operations = ["Division"]
        questions = generate_question_pool(operations, sample_numbers)

        question_set = set(questions)
        expected_set = set(expected_division_questions)

        assert len(questions) == len(expected_division_questions)
        assert question_set == expected_set

    @pytest.mark.unit
    def test_generate_question_pool_subtraction(
        self, sample_numbers, expected_subtraction_questions
    ):
        """Test generating subtraction questions."""
        operations = ["Subtraction"]
        questions = generate_question_pool(operations, sample_numbers)

        question_set = set(questions)
        expected_set = set(expected_subtraction_questions)

        assert len(questions) == len(expected_subtraction_questions)
        assert question_set == expected_set

    @pytest.mark.unit
    def test_generate_question_pool_multiple_operations(self, sample_numbers):
        """Test generating questions with multiple operations."""
        operations = ["Addition", "Multiplication"]
        questions = generate_question_pool(operations, sample_numbers)

        # Should have both addition and multiplication questions
        addition_questions = [q for q in questions if "+" in q[0]]
        multiplication_questions = [q for q in questions if "x" in q[0]]

        assert len(addition_questions) > 0
        assert len(multiplication_questions) > 0
        assert len(questions) == len(addition_questions) + len(multiplication_questions)

    @pytest.mark.unit
    def test_generate_question_pool_empty_operations_defaults(self, sample_numbers):
        """Test that empty operations list defaults to multiplication."""
        operations = []
        questions = generate_question_pool(operations, sample_numbers)

        # Should generate multiplication questions
        assert len(questions) > 0
        assert all("x" in q[0] for q in questions)

    @pytest.mark.unit
    def test_generate_question_pool_empty_numbers_defaults(self, sample_operations):
        """Test that empty numbers list defaults to 1-8."""
        numbers = []
        questions = generate_question_pool(sample_operations, numbers)

        # Should generate questions for numbers 1-8
        assert len(questions) > 0
        # Check that questions contain numbers 1-8
        question_texts = [q[0] for q in questions]
        for num in range(1, 9):
            assert any(str(num) in text for text in question_texts)

    @pytest.mark.unit
    def test_generate_question_pool_shuffled(self, sample_operations, sample_numbers):
        """Test that questions are shuffled."""
        questions1 = generate_question_pool(sample_operations, sample_numbers)
        questions2 = generate_question_pool(sample_operations, sample_numbers)

        # Questions should be in different order (very unlikely to be identical)
        assert questions1 != questions2

    @pytest.mark.unit
    def test_generate_question_pool_no_duplicates(
        self, sample_operations, sample_numbers
    ):
        """Test that no duplicate questions are generated."""
        questions = generate_question_pool(sample_operations, sample_numbers)
        question_texts = [q[0] for q in questions]

        assert len(question_texts) == len(set(question_texts))


class TestMaxValidQuestions:
    """Test maximum valid questions calculation."""

    @pytest.mark.unit
    def test_get_max_valid_questions_multiplication(self, sample_numbers):
        """Test max questions for multiplication."""
        operations = ["Multiplication"]
        max_questions = get_max_valid_questions(operations, sample_numbers)

        # Each number (1-5) × each second number (1-12) = 5 × 12 = 60
        expected = len(sample_numbers) * 12
        assert max_questions == expected

    @pytest.mark.unit
    def test_get_max_valid_questions_addition(self, sample_numbers):
        """Test max questions for addition."""
        operations = ["Addition"]
        max_questions = get_max_valid_questions(operations, sample_numbers)

        # Each number (1-5) + each second number (1-12) = 5 × 12 = 60
        expected = len(sample_numbers) * 12
        assert max_questions == expected

    @pytest.mark.unit
    def test_get_max_valid_questions_subtraction(self, sample_numbers):
        """Test max questions for subtraction."""
        operations = ["Subtraction"]
        max_questions = get_max_valid_questions(operations, sample_numbers)

        # Each number (1-5) - each second number (1-12) = 5 × 12 = 60
        expected = len(sample_numbers) * 12
        assert max_questions == expected

    @pytest.mark.unit
    def test_get_max_valid_questions_division(self, sample_numbers):
        """Test max questions for division."""
        operations = ["Division"]
        max_questions = get_max_valid_questions(operations, sample_numbers)

        # Division questions are more complex - only valid when result is integer
        # This is harder to calculate exactly, so we'll check it's reasonable
        assert max_questions > 0
        assert max_questions <= len(sample_numbers) * 12

    @pytest.mark.unit
    def test_get_max_valid_questions_multiple_operations(self, sample_numbers):
        """Test max questions for multiple operations."""
        operations = ["Addition", "Multiplication"]
        max_questions = get_max_valid_questions(operations, sample_numbers)

        # Should be sum of both operations
        addition_max = get_max_valid_questions(["Addition"], sample_numbers)
        multiplication_max = get_max_valid_questions(["Multiplication"], sample_numbers)
        expected = addition_max + multiplication_max

        assert max_questions == expected

    @pytest.mark.unit
    def test_get_max_valid_questions_empty_numbers(self, sample_operations):
        """Test max questions with empty numbers list."""
        numbers = []
        max_questions = get_max_valid_questions(sample_operations, numbers)

        assert max_questions == 0

    @pytest.mark.unit
    def test_get_max_valid_questions_empty_operations(self, sample_numbers):
        """Test max questions with empty operations list."""
        operations = []
        max_questions = get_max_valid_questions(operations, sample_numbers)

        # Should default to multiplication
        expected = len(sample_numbers) * 12
        assert max_questions == expected


class TestSessionState:
    """Test SessionState class."""

    @pytest.mark.unit
    def test_session_state_initialization(self):
        """Test that SessionState initializes with correct defaults."""
        state = SessionState()

        assert state.cards_per_round == 10
        assert state.current_card == 0
        assert state.current_question is None
        assert state.current_answer is None
        assert state.game_phase == "setup"
        assert state.is_active is False
        assert state.selected_numbers == [1, 2, 3, 4, 5, 6, 7, 8]
        assert state.operations == ["Multiplication"]
        assert state.question_pool == []
        assert state.show_answer is False
        assert state.show_key_hints is False
        assert state.supported_operations == [
            "Addition",
            "Subtraction",
            "Multiplication",
            "Division",
        ]

    @pytest.mark.unit
    def test_session_state_custom_initialization(self):
        """Test SessionState with custom initialization."""
        state = SessionState()
        state.cards_per_round = 20
        state.selected_numbers = [1, 2, 3]
        state.operations = ["Addition", "Subtraction"]

        assert state.cards_per_round == 20
        assert state.selected_numbers == [1, 2, 3]
        assert state.operations == ["Addition", "Subtraction"]

    @pytest.mark.unit
    def test_session_state_question_pool_assignment(self, sample_question_pool):
        """Test assigning question pool to session state."""
        state = SessionState()
        state.question_pool = sample_question_pool

        assert len(state.question_pool) > 0
        assert all(isinstance(q, tuple) and len(q) == 2 for q in state.question_pool)
        assert all(
            isinstance(q[0], str) and isinstance(q[1], int) for q in state.question_pool
        )

    @pytest.mark.unit
    def test_session_state_game_phase_transitions(self):
        """Test game phase transitions."""
        state = SessionState()

        # Initial state
        assert state.game_phase == "setup"

        # Transition to playing
        state.game_phase = "playing"
        assert state.game_phase == "playing"

        # Transition to finished
        state.game_phase = "finished"
        assert state.game_phase == "finished"

        # Transition back to setup
        state.game_phase = "setup"
        assert state.game_phase == "setup"
