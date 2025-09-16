from nicegui import ui
from nicegui.events import KeyEventArguments

from app.components import ConfirmationDialog
from app.services.questions import generate_question_pool, get_max_valid_questions


class FlashCard:
    def __init__(self, session_state):
        self.session_state = session_state
        self.quit_dialog = None

    @ui.refreshable
    def card_content(self):
        if self.session_state.show_key_hints:
            self.show_key_hints()
            return

        if self.session_state.game_phase == "setup":
            with ui.column().classes("items-center gap-6"):
                ui.label("Are you ready?").classes(
                    "text-6xl font-bold text-center mb-8"
                ).style("line-height: 1.2;")

                ui.button(
                    "Start Game",
                    on_click=lambda: (
                        self.start_game(),
                        self.card_content.refresh(),
                    ),
                ).classes("text-xl px-8 py-4")

        elif self.session_state.game_phase == "playing":
            with ui.column().classes("items-center gap-8"):

                # Show question or answer based on show_answer state
                if self.session_state.show_answer:
                    ui.label("Answer:").classes(
                        "text-4xl font-bold text-center text-green-600"
                    )
                    ui.label(str(self.session_state.current_answer)).classes(
                        "text-8xl font-bold text-center text-green-600"
                    ).style("line-height: 1.2;")
                    ui.label("Release ARROW DOWN to go back to the question").classes(
                        "text-lg text-gray-600"
                    )
                else:
                    ui.label().bind_text_from(
                        self.session_state, "current_question"
                    ).classes("text-8xl font-bold text-center").style(
                        "line-height: 1.2;"
                    )
            with ui.linear_progress(show_value=False, size="20px").classes(
                "w-64"
            ).bind_value_from(
                self.session_state,
                "current_card",
                backward=lambda x: x / self.session_state.cards_per_round,
            ):
                ui.label().classes(
                    "text-sm text-gray-600 absolute-center"
                ).bind_text_from(
                    self.session_state,
                    "current_card",
                    backward=lambda x: f"{x} of {self.session_state.cards_per_round}",
                )
        else:
            with ui.column().classes("items-center gap-6"):
                ui.label("Game Complete!").classes(
                    "text-6xl font-bold text-center"
                ).style("line-height: 1.2;")

                ui.button(
                    "New Game",
                    on_click=lambda: (
                        self.reset_game(),
                        self.card_content.refresh(),
                    ),
                ).classes("text-xl px-8 py-4")

    def show_key_hints(self):
        """Display key hints UI"""
        ui.label("Key Hints:").classes("text-4xl font-bold text-center text-blue-600")
        ui.label("Press SPACE for next question").classes("text-lg text-gray-600")
        ui.label("Hold DOWN ARROW to see answer").classes("text-lg text-gray-600")
        ui.label("Press UP ARROW to see these hints").classes("text-lg text-gray-600")
        ui.label("Or press ESCAPE to quit").classes("text-lg text-gray-600")

    def reset_game(self):
        self.session_state.game_phase = "setup"
        self.session_state.current_card = 0
        self.session_state.current_question = None

    def start_game(self):
        # Validate and adjust card count if necessary
        self.validate_card_count()

        # Generate question pool using settings panel method
        self.session_state.question_pool = generate_question_pool(
            self.session_state.operations, self.session_state.selected_numbers
        )

        self.session_state.game_phase = "playing"
        self.session_state.current_card = 0
        self.advance_card()

    def validate_card_count(self):
        """Ensure cards_per_round doesn't exceed possible unique questions"""
        max_possible = get_max_valid_questions(
            self.session_state.operations, self.session_state.selected_numbers
        )
        if self.session_state.cards_per_round > max_possible:
            self.session_state.cards_per_round = max_possible

    def advance_card(self):
        self.session_state.current_card += 1
        if self.session_state.current_card > self.session_state.cards_per_round:
            self.end_game()
            return

        # Get next question and answer from the pre-generated pool
        question, answer = self.session_state.question_pool[
            self.session_state.current_card - 1
        ]
        self.session_state.current_question = question
        self.session_state.current_answer = answer
        self.session_state.show_answer = False

    def end_game(self):
        self.session_state.game_phase = "finished"
        self.session_state.is_active = False

    def show_quit_dialog(self):
        """Show a dialog asking if the user wants to quit"""
        self.quit_dialog = ConfirmationDialog(
            title="Quit Game?",
            message="Are you sure you want to quit?",
            confirm_text="Yes",
            cancel_text="No",
        )

        self.quit_dialog.show(
            on_confirm=lambda: (self.reset_game(), self.card_content.refresh()),
            on_cancel=None,
        )

        return self.quit_dialog

    def handle_key(self, e: KeyEventArguments):
        if e.key.space and e.action.keydown:
            if self.session_state.game_phase == "playing":
                self.advance_card()
                self.card_content.refresh()
        elif e.key.arrow_down:
            if self.session_state.game_phase == "playing":
                if e.action.keydown:
                    # Show answer when down arrow is pressed
                    self.session_state.show_answer = True
                else:
                    # Hide answer when down arrow is released
                    self.session_state.show_answer = False
                self.card_content.refresh()
        elif e.key.arrow_up:
            if e.action.keydown:
                self.session_state.show_key_hints = True
            else:
                self.session_state.show_key_hints = False
            self.card_content.refresh()
        elif e.key.escape and e.action.keydown:
            # If quit dialog is open, close it. Otherwise show it.
            if self.quit_dialog is not None and self.quit_dialog.is_open:
                self.quit_dialog.close()
            else:
                self.show_quit_dialog()
