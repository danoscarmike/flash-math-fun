"""Test configuration and fixtures for the flash card app."""

from unittest.mock import patch

import pytest

from app.services import SessionState, generate_question_pool, get_max_valid_questions


@pytest.fixture
def sample_operations():
    """Sample operations for testing."""
    return ["Addition", "Multiplication"]


@pytest.fixture
def sample_numbers():
    """Sample numbers for testing."""
    return [1, 2, 3, 4, 5]


@pytest.fixture
def all_operations():
    """All supported operations."""
    return ["Addition", "Subtraction", "Multiplication", "Division"]


@pytest.fixture
def all_numbers():
    """All numbers 1-12."""
    return list(range(1, 13))


@pytest.fixture
def session_state():
    """Create a fresh session state for testing."""
    return SessionState()


@pytest.fixture
def mock_ui():
    """Mock NiceGUI UI components for testing."""
    with patch("nicegui.ui") as mock_ui:
        yield mock_ui


@pytest.fixture
def sample_question_pool():
    """Sample question pool for testing."""
    operations = ["Multiplication"]
    numbers = [2, 3]
    return generate_question_pool(operations, numbers)


@pytest.fixture
def expected_multiplication_questions():
    """Expected multiplication questions for numbers 1-5."""
    questions = []
    for first in range(1, 6):  # 1-5
        for second in range(1, 13):  # 1-12
            questions.append((f"{first} x {second}", first * second))
    return questions


@pytest.fixture
def expected_addition_questions():
    """Expected addition questions for numbers 1-5."""
    questions = []
    for first in range(1, 6):  # 1-5
        for second in range(1, 13):  # 1-12
            questions.append((f"{first} + {second}", first + second))
    return questions


@pytest.fixture
def expected_division_questions():
    """Expected division questions for numbers 1-5."""
    questions = []
    for first in range(1, 6):  # 1-5
        for second in range(1, 13):  # 1-12
            # Only add if division results in integer
            if second != 0 and first % second == 0:
                questions.append((f"{first} ÷ {second}", first // second))
            elif first != 0 and second % first == 0:
                questions.append((f"{second} ÷ {first}", second // first))
    return questions


@pytest.fixture
def expected_subtraction_questions():
    """Expected subtraction questions for numbers 1-5."""
    questions = []
    for first in range(1, 6):  # 1-5
        for second in range(1, 13):  # 1-12
            # Subtraction: larger number - smaller number
            if first >= second:
                questions.append((f"{first} - {second}", first - second))
            else:
                questions.append((f"{second} - {first}", second - first))
    return questions
