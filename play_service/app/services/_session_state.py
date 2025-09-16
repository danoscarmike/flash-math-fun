# Global state for the flash card session
class SessionState:
    def __init__(self):
        self.cards_per_round = 10
        self.current_card = 0
        self.current_question = None
        self.current_answer = None
        self.game_phase = "setup"  # "setup", "playing", "finished"
        self.is_active = False
        self.selected_numbers = [1, 2, 3, 4, 5, 6, 7, 8]  # Default numbers
        self.operations = ["Multiplication"]  # Default to multiplication
        self.question_pool = []  # All generated questions
        self.show_answer = False
        self.show_key_hints = False
        self.supported_operations = [
            "Addition",
            "Subtraction",
            "Multiplication",
            "Division",
        ]
