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

# Global reference to cards container for refreshing
cards_container = None

# Global reference to dialogs
quit_dialog = None

# Global reference to number checkboxes
number_checkbox_vars = {}


def select_all_numbers():
    """Select all numbers 1-12"""
    session_state.selected_numbers = list(range(1, 13))
    # Update all checkboxes
    for num in range(1, 13):
        if num in number_checkbox_vars:
            number_checkbox_vars[num].value = True
    update_cards_select()
    regenerate_question_pool_if_needed()


def clear_all_numbers():
    """Clear all numbers and set to just 1"""
    session_state.selected_numbers = [1]
    # Update all checkboxes
    for num in range(1, 13):
        if num in number_checkbox_vars:
            number_checkbox_vars[num].value = num == 1
    update_cards_select()
    regenerate_question_pool_if_needed()


@ui.refreshable
def number_checkboxes():
    """Create refreshable number checkboxes"""
    global number_checkbox_vars
    number_checkbox_vars.clear()

    with ui.row().classes("flex-wrap gap-2 w-full"):
        for num in range(1, 13):  # 1 to 12
            checkbox = ui.checkbox(str(num)).classes("text-sm")
            number_checkbox_vars[num] = checkbox
            # Set the initial value
            checkbox.value = num in session_state.selected_numbers
            # Add the event handler
            checkbox.on(
                "update:model-value", lambda e, n=num: toggle_number(n, e.value)
            )


def regenerate_question_pool_if_needed():
    """Regenerate question pool if game is in setup phase"""
    if session_state.game_phase == "setup":
        session_state.question_pool = generate_question_pool()


def toggle_number(number, is_checked):
    """Toggle a number in the selected_numbers list"""
    if is_checked:
        if number not in session_state.selected_numbers:
            session_state.selected_numbers.append(number)
    else:
        if number in session_state.selected_numbers:
            session_state.selected_numbers.remove(number)

    # Ensure at least one number is selected
    if not session_state.selected_numbers:
        session_state.selected_numbers = [1]

    # Update all checkbox values to reflect the new state
    for num in range(1, 13):
        if num in number_checkbox_vars:
            number_checkbox_vars[num].value = num in session_state.selected_numbers

    # Refresh the cards select to update available options
    update_cards_select()

    # Regenerate question pool if game is in setup phase
    regenerate_question_pool_if_needed()


def update_cards_select():
    """Update the cards per round select options based on current selected numbers and operations"""
    if cards_container is None:
        return

    cards_container.clear()

    max_possible = get_max_possible_cards()
    predefined_options = [5, 10, 15, 20, 25]

    # Only include predefined options that don't exceed the maximum possible
    options = {}
    for i in predefined_options:
        if i <= max_possible:
            options[i] = f"{i} cards"

    # Find the highest valid option from the predefined list
    valid_options = [i for i in predefined_options if i <= max_possible]
    max_valid_option = max(valid_options) if valid_options else 5

    # If current selection exceeds the highest valid option, reset to it
    if session_state.cards_per_round > max_valid_option:
        session_state.cards_per_round = max_valid_option

    with cards_container:
        ui.select(options=options, value=session_state.cards_per_round).bind_value(
            session_state, "cards_per_round"
        ).classes("w-full")


def get_max_possible_cards():
    """Calculate maximum possible unique questions for selected numbers and operations"""
    # If no operations selected, default to multiplication
    if not session_state.operations:
        return len(session_state.selected_numbers) * 12

    total_questions = 0
    for first in session_state.selected_numbers:
        for second in range(1, 13):  # 1 to 12
            for operation in session_state.operations:
                if operation == "Addition":
                    total_questions += 1
                elif operation == "Subtraction":
                    total_questions += 1  # We always generate one subtraction per pair
                elif operation == "Multiplication":
                    total_questions += 1
                elif operation == "Division":
                    # Only count if it results in a whole number
                    if (second != 0 and first % second == 0) or (
                        first != 0 and second % first == 0
                    ):
                        total_questions += 1

    return total_questions


def generate_question_pool():
    """Generate all possible unique questions and shuffle them"""
    questions = []

    # If no operations selected, default to multiplication
    if not session_state.operations:
        session_state.operations = ["Multiplication"]

    # If no numbers selected, default to 1-8
    if not session_state.selected_numbers:
        session_state.selected_numbers = [1, 2, 3, 4, 5, 6, 7, 8]

    for first in session_state.selected_numbers:
        for second in range(1, 13):  # 1 to 12
            for operation in session_state.operations:
                if operation == "Addition":
                    question = f"{first} + {second}"
                    answer = first + second
                elif operation == "Subtraction":
                    # Ensure positive results for subtraction
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
                    # Ensure whole number results for division
                    if second != 0 and first % second == 0:
                        question = f"{first} ÷ {second}"
                        answer = first // second
                    elif first != 0 and second % first == 0:
                        question = f"{second} ÷ {first}"
                        answer = second // first
                    else:
                        continue  # Skip this combination if it doesn't result in a whole number

                questions.append((question, answer))

    random.shuffle(questions)
    return questions


def validate_card_count():
    """Ensure cards_per_round doesn't exceed possible unique questions"""
    max_possible = get_max_possible_cards()
    if session_state.cards_per_round > max_possible:
        session_state.cards_per_round = max_possible
        return False  # Indicates we had to adjust
    return True


def start_game():
    # Validate and adjust card count if necessary
    validate_card_count()

    # Generate question pool
    session_state.question_pool = generate_question_pool()

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

with ui.right_drawer(fixed=False).style("background-color: #ebf1fa").props(
    "bordered"
) as right_drawer:
    ui.label("Settings").classes("text-2xl font-bold mb-6")

    with ui.column().classes("gap-6"):
        # Number selection - checkboxes for individual numbers
        ui.label("Numbers").classes("text-lg font-semibold")
        ui.label("Select which number facts to include:").classes(
            "text-sm text-gray-600"
        )

        # Select All / Clear All buttons
        with ui.row().classes("gap-2 mb-2"):
            ui.button("Select All", on_click=lambda: select_all_numbers()).classes(
                "text-xs px-2 py-1"
            )
            ui.button("Clear All", on_click=lambda: clear_all_numbers()).classes(
                "text-xs px-2 py-1"
            )

        number_checkboxes()

        ui.label("Operations").classes("text-medium font-semibold")
        ui.select(
            session_state.supported_operations,
            multiple=True,
            value=session_state.operations,
        ).bind_value(session_state, "operations").on(
            "update:model-value",
            lambda: (update_cards_select(), regenerate_question_pool_if_needed()),
        )

        with ui.column().classes("w-full gap-2"):
            # Cards per round - dynamic options based on max_facts
            ui.label("Cards per round").classes("text-lg font-semibold")

        # Create a container for the select that we can refresh
        with ui.column() as cards_container:
            pass

        # Initialize the select
        update_cards_select()

        ui.space()
        ui.space()
        ui.space()
        ui.separator()
        ui.label("Hold ARROW UP to see key hints")


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
