from nicegui import ui
from app.components.cards_per_round_selector import CardsPerRoundSelector
from app.components.number_selector import NumberSelector
from app.components.operations_selector import OperationsSelector
from app.services import generate_question_pool, get_max_valid_questions


class SettingsPanel:
    """Main settings panel that combines all configuration components with context manager support"""

    def __init__(self, session_state):
        self.session_state = session_state
        self.number_selector = None
        self.operations_selector = None
        self.cards_selector = None

    def __enter__(self):
        """Context manager entry"""
        return self.create_ui()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup"""
        pass

    def create_ui(self):
        """Create the complete settings panel UI with context manager"""
        with ui.column().classes("gap-6"):
            # Number selection
            self.number_selector = NumberSelector(
                self.session_state.selected_numbers,
                on_change_callback=self.on_settings_change,
            )
            self.number_selector.create_ui()

            # Operations selection
            self.operations_selector = OperationsSelector(
                self.session_state,
                on_change_callback=self.on_settings_change,
            )
            self.operations_selector.create_ui()

            # Cards per round selection
            self.cards_selector = CardsPerRoundSelector(
                self.session_state,
                get_max_valid_questions,
                on_change_callback=self.on_settings_change,
            )
            self.cards_selector.create_ui()

            # Spacing and hints
            ui.space()
            ui.space()
            ui.space()
            ui.separator()
            ui.label("Hold ARROW UP to see key hints")

    def on_settings_change(self):
        """Handle changes to any setting"""
        print(
            f"SettingsPanel: on_settings_change called, selected_numbers: {self.session_state.selected_numbers}"
        )
        # Update cards selector when numbers or operations change
        if self.cards_selector:
            print("SettingsPanel: Updating cards selector options")
            self.cards_selector.update_options()

        # Regenerate question pool if in setup phase
        if self.session_state.game_phase == "setup":
            self.session_state.question_pool = generate_question_pool(
                self.session_state.operations, self.session_state.selected_numbers
            )
