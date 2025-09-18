import random
from contextlib import contextmanager
from typing import List, Optional, Tuple

from nicegui import ui


@contextmanager
def _question_generator(operations: List[str], selected_numbers: List[int]):
    """Context manager for question generation with validation"""
    if not operations:
        operations = ["Multiplication"]
    if not selected_numbers:
        selected_numbers = [1, 2, 3, 4, 5, 6, 7, 8]

    questions = []
    try:
        yield questions, operations, selected_numbers
    except Exception as e:
        ui.label(f"Error generating questions: {str(e)}").classes("text-red-500")
        raise


def _generate_single_question(
    first: int, second: int, operation: str
) -> Tuple[Optional[str], Optional[int]]:
    """Generate a single question with proper error handling"""
    try:
        if operation == "Addition":
            return f"{first} + {second}", first + second
        elif operation == "Subtraction":
            if first >= second:
                return f"{first} - {second}", first - second
            else:
                return f"{second} - {first}", second - first
        elif operation == "Multiplication":
            return f"{first} x {second}", first * second
        elif operation == "Division":
            if second != 0 and first % second == 0:
                return f"{first} ÷ {second}", first // second
            elif first != 0 and second % first == 0:
                return f"{second} ÷ {first}", second // first
            else:
                return None, None
        else:
            return None, None
    except Exception as e:
        ui.label(
            f"Error generating question {first} {operation} {second}: {str(e)}"
        ).classes("text-red-500")
        return None, None


def generate_question_pool(operations: List[str], selected_numbers: List[int]):
    """Generate all possible unique questions and shuffle them with context manager"""
    with _question_generator(operations, selected_numbers) as (
        questions,
        operations,
        selected_numbers,
    ):

        for first in selected_numbers:
            for second in range(1, 13):  # 1 to 12
                for operation in operations:
                    question, answer = _generate_single_question(
                        first, second, operation
                    )
                    if question and answer is not None:
                        questions.append((question, answer))

        random.shuffle(questions)
        return questions


def get_max_valid_questions(operations: List[str], selected_numbers: List[int]):
    """Calculate maximum possible unique questions for selected numbers and operations"""
    if not selected_numbers:
        return 0

    if not operations:
        return len(selected_numbers) * 12

    max_valid_questions = 0
    for first in selected_numbers:
        for second in range(1, 13):  # 1 to 12
            for operation in operations:
                if operation == "Addition":
                    max_valid_questions += 1
                elif operation == "Subtraction":
                    max_valid_questions += 1
                elif operation == "Multiplication":
                    max_valid_questions += 1
                elif operation == "Division":
                    # Only allow division if the result is an integer
                    if (second != 0 and first % second == 0) or (
                        first != 0 and second % first == 0
                    ):
                        max_valid_questions += 1

    return max_valid_questions
