from contextlib import contextmanager
from typing import Optional, Callable, Any, Dict, List, Tuple
from nicegui import ui
from nicegui.events import KeyEventArguments

from app.components import ConfirmationDialog, ui_section
from app.services import generate_question_pool, get_max_valid_questions


# Context Managers for better code organization and error handling


def startup():

    class NumberSelector:
        """Reusable number selection component with checkboxes and context manager support"""

        def __init__(
            self,
            selected_numbers: List[int],
            on_change_callback: Optional[Callable] = None,
        ):
            self.selected_numbers = selected_numbers
            self.on_change_callback = on_change_callback
            self.checkbox_vars: Dict[int, Any] = {}

        def __enter__(self):
            """Context manager entry"""
            return self.create_ui()

        def __exit__(self, exc_type, exc_val, exc_tb):
            """Context manager exit with cleanup"""
            pass

        def create_ui(self):
            """Create the number selection UI with context manager"""
            with ui_section("Numbers", "gap-4"):
                ui.label("Select which number facts to include:").classes(
                    "text-sm text-gray-600"
                )

                # Select All / Clear All buttons
                with ui.row().classes("gap-2 mb-2"):
                    ui.button("Select All", on_click=self.select_all).classes(
                        "text-xs px-2 py-1"
                    )
                    ui.button("Clear All", on_click=self.clear_all).classes(
                        "text-xs px-2 py-1"
                    )

                # Number checkboxes
                with ui.row().classes("flex-wrap gap-2 w-full"):
                    for num in range(1, 13):  # 1 to 12
                        checkbox = ui.checkbox(str(num)).classes("text-sm")
                        self.checkbox_vars[num] = checkbox
                        checkbox.value = num in self.selected_numbers

                        # Create a closure to capture the current value of num
                        def make_handler(n):
                            def handler():
                                # Get the current value of the checkbox
                                is_checked = self.checkbox_vars[n].value
                                self.toggle_number(n, is_checked)

                            return handler

                        checkbox.on("update:model-value", make_handler(num))

        def toggle_number(self, number: int, is_checked: bool):
            """Toggle a number in the selected list"""
            print(
                f"NumberSelector: toggle_number called for number {number}, is_checked: {is_checked}"
            )
            try:
                if is_checked:
                    if number not in self.selected_numbers:
                        self.selected_numbers.append(number)
                        print(f"NumberSelector: Added {number} to selected_numbers")
                else:
                    if number in self.selected_numbers:
                        self.selected_numbers.remove(number)
                        print(f"NumberSelector: Removed {number} from selected_numbers")
            except Exception as e:
                ui.label(f"Error toggling number {number}: {str(e)}").classes(
                    "text-red-500"
                )
                return

            print(f"NumberSelector: Current selected_numbers: {self.selected_numbers}")
            self._update_ui_after_change()

        def _update_ui_after_change(self):
            """Update UI after state change"""
            self.update_checkbox_states()
            if self.on_change_callback:
                print(
                    f"NumberSelector: Calling on_change_callback, selected_numbers: {self.selected_numbers}"
                )
                self.on_change_callback()

        def select_all(self):
            """Select all numbers 1-12"""
            try:
                self.selected_numbers.clear()
                self.selected_numbers.extend(range(1, 13))
            except Exception as e:
                ui.label(f"Error selecting all numbers: {str(e)}").classes(
                    "text-red-500"
                )
                return

            self._update_ui_after_change()

        def clear_all(self):
            """Clear all numbers"""
            try:
                self.selected_numbers.clear()
            except Exception as e:
                ui.label(f"Error clearing numbers: {str(e)}").classes("text-red-500")
                return

            self._update_ui_after_change()

        def update_checkbox_states(self):
            """Update all checkbox values to reflect current selection"""
            for num in range(1, 13):
                if num in self.checkbox_vars:
                    self.checkbox_vars[num].value = num in self.selected_numbers

    class OperationsSelector:
        """Reusable operations selection component with context manager support"""

        def __init__(
            self, session_state, on_change_callback: Optional[Callable] = None
        ):
            self.session_state = session_state
            self.on_change_callback = on_change_callback

        def __enter__(self):
            """Context manager entry"""
            return self.create_ui()

        def __exit__(self, exc_type, exc_val, exc_tb):
            """Context manager exit with cleanup"""
            pass

        def create_ui(self):
            """Create the operations selection UI with context manager"""
            with ui_section("Operations", "gap-4"):
                ui.select(
                    self.session_state.supported_operations,
                    multiple=True,
                    value=self.session_state.operations,
                ).bind_value(self.session_state, "operations").on(
                    "update:model-value",
                    lambda: (
                        self.on_change_callback() if self.on_change_callback else None
                    ),
                )

    class CardsPerRoundSelector:
        """Reusable cards per round selection component with context manager support"""

        def __init__(
            self,
            session_state,
            max_possible_cards_func: Callable,
            on_change_callback: Optional[Callable] = None,
        ):
            self.session_state = session_state
            self.max_possible_cards_func = max_possible_cards_func
            self.on_change_callback = on_change_callback
            self.container = None
            self.predefined_options = [5, 10, 15, 20, 25]

        def __enter__(self):
            """Context manager entry"""
            return self.create_ui()

        def __exit__(self, exc_type, exc_val, exc_tb):
            """Context manager exit with cleanup"""
            pass

        def create_ui(self):
            """Create the cards per round selection UI with context manager"""
            with ui_section("Cards per round", "gap-4"):
                # Create a container for the select that we can refresh
                with ui.column() as self.container:
                    pass

                # Initialize the select
                self.update_options()

        def update_options(self):
            """Update the available options based on max possible cards"""
            if self.container is None:
                return

            self.container.clear()

            max_possible = self.max_possible_cards_func(
                self.session_state.operations, self.session_state.selected_numbers
            )
            print(
                f"CardsPerRoundSelector: update_options called, max_possible: {max_possible}"
            )

            # If no numbers are selected, show a message instead of options
            if max_possible == 0:
                print(
                    "CardsPerRoundSelector: No numbers selected, showing error message"
                )
                with self.container:
                    ui.label(
                        "Please select at least one number to generate questions"
                    ).classes("text-red-500 text-sm")
                return

            # Only include predefined options that don't exceed the maximum possible
            options = {}
            for i in self.predefined_options:
                if i <= max_possible:
                    options[i] = f"{i} cards"

            # Find the highest valid option from the predefined list
            valid_options = [i for i in self.predefined_options if i <= max_possible]
            max_valid_option = max(valid_options) if valid_options else 5

            # If current selection exceeds the highest valid option, reset to it
            if self.session_state.cards_per_round > max_valid_option:
                self.session_state.cards_per_round = max_valid_option

            print(f"CardsPerRoundSelector: Creating dropdown with options: {options}")
            with self.container:
                ui.select(
                    options=options, value=self.session_state.cards_per_round
                ).bind_value(self.session_state, "cards_per_round").on(
                    "update:model-value",
                    lambda: (
                        self.on_change_callback() if self.on_change_callback else None
                    ),
                ).classes(
                    "w-full"
                )

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

    session_state = SessionState()

    # Global reference to dialogs
    quit_dialog = None

    def validate_card_count():
        """Ensure cards_per_round doesn't exceed possible unique questions"""
        max_possible = get_max_valid_questions(
            session_state.operations, session_state.selected_numbers
        )
        if session_state.cards_per_round > max_possible:
            session_state.cards_per_round = max_possible
            return False  # Indicates we had to adjust
        return True

    def start_game():
        # Validate and adjust card count if necessary
        validate_card_count()

        # Generate question pool using settings panel method
        session_state.question_pool = generate_question_pool(
            session_state.operations, session_state.selected_numbers
        )

        session_state.game_phase = "playing"
        session_state.current_card = 0
        advance_card()

    def advance_card():
        session_state.current_card += 1
        if session_state.current_card > session_state.cards_per_round:
            end_game()
            return

        # Get next question and answer from the pre-generated pool
        question, answer = session_state.question_pool[session_state.current_card - 1]
        session_state.current_question = question
        session_state.current_answer = answer
        session_state.show_answer = False

    def end_game():
        session_state.game_phase = "finished"
        session_state.is_active = False

    def reset_game():
        session_state.game_phase = "setup"
        session_state.current_card = 0
        session_state.current_question = None

    def show_key_hints():
        """Display key hints UI"""
        ui.label("Key Hints:").classes("text-4xl font-bold text-center text-blue-600")
        ui.label("Press SPACE for next question").classes("text-lg text-gray-600")
        ui.label("Hold DOWN ARROW to see answer").classes("text-lg text-gray-600")
        ui.label("Press UP ARROW to see these hints").classes("text-lg text-gray-600")
        ui.label("Or press ESCAPE to quit").classes("text-lg text-gray-600")

    def show_quit_dialog():
        """Show a dialog asking if the user wants to quit"""
        global quit_dialog
        quit_dialog = ConfirmationDialog(
            title="Quit Game?",
            message="Are you sure you want to quit?",
            confirm_text="Yes",
            cancel_text="No",
        )

        quit_dialog.show(
            on_confirm=lambda: (reset_game(), card_content.refresh()), on_cancel=None
        )

        return quit_dialog

    def handle_key(e: KeyEventArguments):
        if e.key.space and e.action.keydown:
            if session_state.game_phase == "playing":
                advance_card()
                card_content.refresh()
            elif session_state.game_phase == "finished":
                reset_game()
                card_content.refresh()
        elif e.key.arrow_down:
            if session_state.game_phase == "playing":
                if e.action.keydown:
                    # Show answer when down arrow is pressed
                    session_state.show_answer = True
                else:
                    # Hide answer when down arrow is released
                    session_state.show_answer = False
                card_content.refresh()
        elif e.key.arrow_up:
            if e.action.keydown:
                session_state.show_key_hints = True
            else:
                session_state.show_key_hints = False
            card_content.refresh()
        elif e.key.escape and e.action.keydown:
            # If quit dialog is open, close it. Otherwise show it.
            if quit_dialog is not None and quit_dialog.is_open:
                quit_dialog.close()
            else:
                show_quit_dialog()

    ui.page_title("Flash Card Magic")

    with ui.header(elevated=True).style("background-color: #3874c8").classes(
        "items-center justify-between"
    ):
        ui.label("Flash Card Magic").classes("text-2xl font-bold")
        ui.button(on_click=lambda: right_drawer.toggle(), icon="menu").props(
            "flat color=white"
        )

    # Create settings panel
    settings_panel = SettingsPanel(session_state)

    with ui.right_drawer(fixed=False).style("background-color: #ebf1fa").props(
        "bordered"
    ) as right_drawer:
        ui.label("Settings").classes("text-2xl font-bold mb-6")
        settings_panel.create_ui()

    with ui.footer().style("background-color: #3874c8"):
        ui.label("Copyright District/2 Software (c) 2025")

    @ui.refreshable
    def card_content():
        if session_state.game_phase == "setup":
            with ui.column().classes("items-center gap-6"):
                ui.label("Are you ready?").classes(
                    "text-6xl font-bold text-center mb-8"
                ).style("line-height: 1.2;")

                ui.button(
                    "Start Game",
                    on_click=lambda: (
                        start_game(),
                        card_content.refresh(),
                    ),
                ).classes("text-xl px-8 py-4")

                if session_state.show_key_hints:
                    show_key_hints()

        elif session_state.game_phase == "playing":
            with ui.column().classes("items-center gap-8"):

                # Show question or answer based on show_answer state
                if session_state.show_answer:
                    ui.label("Answer:").classes(
                        "text-4xl font-bold text-center text-green-600"
                    )
                    ui.label(str(session_state.current_answer)).classes(
                        "text-8xl font-bold text-center text-green-600"
                    ).style("line-height: 1.2;")
                    ui.label("Release ARROW DOWN to go back to the question").classes(
                        "text-lg text-gray-600"
                    )
                elif session_state.show_key_hints:
                    show_key_hints()
                else:
                    ui.label().bind_text_from(
                        session_state, "current_question"
                    ).classes("text-8xl font-bold text-center").style(
                        "line-height: 1.2;"
                    )
            with ui.linear_progress(show_value=False, size="20px").classes(
                "w-64"
            ).bind_value_from(
                session_state,
                "current_card",
                backward=lambda x: x / session_state.cards_per_round,
            ):
                ui.label().classes(
                    "text-sm text-gray-600 absolute-center"
                ).bind_text_from(
                    session_state,
                    "current_card",
                    backward=lambda x: f"{x} of {session_state.cards_per_round}",
                )

        elif session_state.game_phase == "finished":
            with ui.column().classes("items-center gap-6"):
                ui.label("Game Complete!").classes(
                    "text-6xl font-bold text-center"
                ).style("line-height: 1.2;")

                ui.button(
                    "New Game",
                    on_click=lambda: (
                        reset_game(),
                        card_content.refresh(),
                    ),
                ).classes("text-xl px-8 py-4")

                if session_state.show_key_hints:
                    show_key_hints()

    with ui.card().classes("w-full flex flex-col justify-center items-center").style(
        "height: calc(100vh - 200px)"
    ):
        card_content()

    ui.keyboard(on_key=handle_key)
