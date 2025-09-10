import random
from nicegui import ui
from nicegui.events import KeyEventArguments


class ConfirmationDialog:
    """Reusable confirmation dialog component"""

    def __init__(
        self,
        title,
        message,
        confirm_text="Yes",
        cancel_text="No",
        confirm_color="red",
        cancel_color="gray",
    ):
        self.title = title
        self.message = message
        self.confirm_text = confirm_text
        self.cancel_text = cancel_text
        self.confirm_color = confirm_color
        self.cancel_color = cancel_color
        self.dialog = None
        self.is_open = False
        self.on_confirm = None
        self.on_cancel = None

    def show(self, on_confirm=None, on_cancel=None):
        """Show the dialog with optional callbacks"""
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel

        with ui.dialog() as self.dialog, ui.card():
            ui.label(self.title).classes("text-2xl font-bold mb-4")
            ui.label(self.message).classes("text-lg mb-6")

            def handle_confirm():
                self.close()
                if self.on_confirm:
                    self.on_confirm()

            def handle_cancel():
                self.close()
                if self.on_cancel:
                    self.on_cancel()

            with ui.row():
                ui.button(self.confirm_text, on_click=handle_confirm).classes(
                    f"bg-{self.confirm_color}-500 text-white px-6 py-2"
                )
                ui.button(self.cancel_text, on_click=handle_cancel).classes(
                    f"bg-{self.cancel_color}-500 text-white px-6 py-2"
                )

        self.dialog.open()
        self.is_open = True
        return self.dialog

    def close(self):
        """Close the dialog"""
        if self.dialog:
            self.dialog.close()
        self.is_open = False


class NumberSelector:
    """Reusable number selection component with checkboxes"""

    def __init__(self, selected_numbers, on_change_callback=None):
        self.selected_numbers = selected_numbers
        self.on_change_callback = on_change_callback
        self.checkbox_vars = {}

    def create_ui(self):
        """Create the number selection UI"""
        with ui.column().classes("gap-4"):
            ui.label("Numbers").classes("text-lg font-semibold")
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
                    checkbox.on(
                        "update:model-value",
                        lambda e, n=num: self.toggle_number(n, e.args),
                    )

    def toggle_number(self, number, is_checked):
        """Toggle a number in the selected list"""
        if is_checked:
            if number not in self.selected_numbers:
                self.selected_numbers.append(number)
        else:
            if number in self.selected_numbers:
                self.selected_numbers.remove(number)

        # Ensure at least one number is selected
        if not self.selected_numbers:
            self.selected_numbers.append(1)

        # Update all checkbox values to reflect the new state
        self.update_checkbox_states()

        # Call the change callback if provided
        if self.on_change_callback:
            self.on_change_callback()

    def select_all(self):
        """Select all numbers 1-12"""
        self.selected_numbers.clear()
        self.selected_numbers.extend(range(1, 13))
        self.update_checkbox_states()
        if self.on_change_callback:
            self.on_change_callback()

    def clear_all(self):
        """Clear all numbers and set to just 1"""
        self.selected_numbers.clear()
        self.selected_numbers.append(1)
        self.update_checkbox_states()
        if self.on_change_callback:
            self.on_change_callback()

    def update_checkbox_states(self):
        """Update all checkbox values to reflect current selection"""
        for num in range(1, 13):
            if num in self.checkbox_vars:
                self.checkbox_vars[num].value = num in self.selected_numbers


class OperationsSelector:
    """Reusable operations selection component"""

    def __init__(self, operations, supported_operations, on_change_callback=None):
        self.operations = operations
        self.supported_operations = supported_operations
        self.on_change_callback = on_change_callback

    def create_ui(self):
        """Create the operations selection UI"""
        with ui.column().classes("gap-4"):
            ui.label("Operations").classes("text-lg font-semibold")
            ui.select(
                self.supported_operations,
                multiple=True,
                value=self.operations,
            ).bind_value(self, "operations").on(
                "update:model-value",
                lambda: self.on_change_callback() if self.on_change_callback else None,
            )


class CardsPerRoundSelector:
    """Reusable cards per round selection component"""

    def __init__(
        self, cards_per_round, max_possible_cards_func, on_change_callback=None
    ):
        self.cards_per_round = cards_per_round
        self.max_possible_cards_func = max_possible_cards_func
        self.on_change_callback = on_change_callback
        self.container = None
        self.predefined_options = [5, 10, 15, 20, 25]

    def create_ui(self):
        """Create the cards per round selection UI"""
        with ui.column().classes("gap-4"):
            ui.label("Cards per round").classes("text-lg font-semibold")

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

        max_possible = self.max_possible_cards_func()

        # Only include predefined options that don't exceed the maximum possible
        options = {}
        for i in self.predefined_options:
            if i <= max_possible:
                options[i] = f"{i} cards"

        # Find the highest valid option from the predefined list
        valid_options = [i for i in self.predefined_options if i <= max_possible]
        max_valid_option = max(valid_options) if valid_options else 5

        # If current selection exceeds the highest valid option, reset to it
        if self.cards_per_round > max_valid_option:
            self.cards_per_round = max_valid_option

        with self.container:
            ui.select(options=options, value=self.cards_per_round).bind_value(
                self, "cards_per_round"
            ).on(
                "update:model-value",
                lambda: self.on_change_callback() if self.on_change_callback else None,
            ).classes(
                "w-full"
            )


class SettingsPanel:
    """Main settings panel that combines all configuration components"""

    def __init__(self, session_state):
        self.session_state = session_state
        self.number_selector = None
        self.operations_selector = None
        self.cards_selector = None

    def create_ui(self):
        """Create the complete settings panel UI"""
        with ui.column().classes("gap-6"):
            # Number selection
            self.number_selector = NumberSelector(
                self.session_state.selected_numbers,
                on_change_callback=self.on_settings_change,
            )
            self.number_selector.create_ui()

            # Operations selection
            self.operations_selector = OperationsSelector(
                self.session_state.operations,
                self.session_state.supported_operations,
                on_change_callback=self.on_settings_change,
            )
            self.operations_selector.create_ui()

            # Cards per round selection
            self.cards_selector = CardsPerRoundSelector(
                self.session_state.cards_per_round,
                self.get_max_possible_cards,
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
        # Update cards selector when numbers or operations change
        if self.cards_selector:
            self.cards_selector.update_options()

        # Regenerate question pool if in setup phase
        if self.session_state.game_phase == "setup":
            self.session_state.question_pool = self.generate_question_pool()

    def get_max_possible_cards(self):
        """Calculate maximum possible unique questions for selected numbers and operations"""
        if not self.session_state.operations:
            return len(self.session_state.selected_numbers) * 12

        total_questions = 0
        for first in self.session_state.selected_numbers:
            for second in range(1, 13):  # 1 to 12
                for operation in self.session_state.operations:
                    if operation == "Addition":
                        total_questions += 1
                    elif operation == "Subtraction":
                        total_questions += 1
                    elif operation == "Multiplication":
                        total_questions += 1
                    elif operation == "Division":
                        if (second != 0 and first % second == 0) or (
                            first != 0 and second % first == 0
                        ):
                            total_questions += 1

        return total_questions

    def generate_question_pool(self):
        """Generate all possible unique questions and shuffle them"""
        questions = []

        if not self.session_state.operations:
            self.session_state.operations = ["Multiplication"]

        if not self.session_state.selected_numbers:
            self.session_state.selected_numbers = [1, 2, 3, 4, 5, 6, 7, 8]

        for first in self.session_state.selected_numbers:
            for second in range(1, 13):  # 1 to 12
                for operation in self.session_state.operations:
                    if operation == "Addition":
                        question = f"{first} + {second}"
                        answer = first + second
                    elif operation == "Subtraction":
                        if first >= second:
                            question = f"{first} - {second}"
                            answer = first - second
                        else:
                            question = f"{second} - {first}"
                            answer = second - first
                    elif operation == "Multiplication":
                        question = f"{first} x {second}"
                        answer = first * second
                    elif operation == "Division":
                        if second != 0 and first % second == 0:
                            question = f"{first} ÷ {second}"
                            answer = first // second
                        elif first != 0 and second % first == 0:
                            question = f"{second} ÷ {first}"
                            answer = second // first
                        else:
                            continue

                    questions.append((question, answer))

        random.shuffle(questions)
        return questions


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


# Old functions removed - now handled by NumberSelector component


# Old functions removed - now handled by components


# Old functions removed - now handled by SettingsPanel component


def validate_card_count():
    """Ensure cards_per_round doesn't exceed possible unique questions"""
    max_possible = settings_panel.get_max_possible_cards()
    if session_state.cards_per_round > max_possible:
        session_state.cards_per_round = max_possible
        return False  # Indicates we had to adjust
    return True


def start_game():
    # Validate and adjust card count if necessary
    validate_card_count()

    # Generate question pool using settings panel method
    session_state.question_pool = settings_panel.generate_question_pool()

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
            ui.label(
                f"Question {session_state.current_card} of {session_state.cards_per_round}"
            ).classes("text-2xl font-bold")

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
                ui.label().bind_text_from(session_state, "current_question").classes(
                    "text-8xl font-bold text-center"
                ).style("line-height: 1.2;")

    elif session_state.game_phase == "finished":
        with ui.column().classes("items-center gap-6"):
            ui.label("Game Complete!").classes("text-6xl font-bold text-center").style(
                "line-height: 1.2;"
            )

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

ui.run()
