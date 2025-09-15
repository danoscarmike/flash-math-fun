from nicegui import ui
from nicegui.events import KeyEventArguments
from app.services import SessionState, generate_question_pool, get_max_valid_questions
from app.components import ConfirmationDialog, SettingsPanel


@ui.page("/play")
def play():
    # Global references
    session_state = SessionState()
    settings_panel = SettingsPanel(session_state)
    quit_dialog = None

    def validate_card_count():
        """Ensure cards_per_round doesn't exceed possible unique questions"""
        max_possible = get_max_valid_questions(
            session_state.operations, session_state.selected_numbers
        )
        if session_state.cards_per_round > max_possible:
            session_state.cards_per_round = max_possible

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

                ui.page_title("Flash Math Fun!")

    with ui.header(elevated=True).style("background-color: #3874c8").classes(
        "items-center justify-between"
    ):
        ui.label("Flash Math Fun!").classes("text-2xl font-bold")
        ui.space()
        ui.button(on_click=lambda: ui.navigate.to("/"), icon="home").props(
            "flat color=white"
        )
        ui.button(on_click=lambda: right_drawer.toggle(), icon="menu").props(
            "flat color=white"
        )

    with ui.right_drawer(fixed=False).style("background-color: #ebf1fa").props(
        "bordered"
    ) as right_drawer:
        ui.label("Settings").classes("text-2xl font-bold mb-6")
        settings_panel.create_ui()

    with ui.footer().style("background-color: #3874c8"):
        ui.label("Copyright")
        ui.link("Session State Software", "http://www.sessionstate.net").style(
            "color: #ebf1fa"
        )
        ui.label("(c) 2025")

    @ui.refreshable
    def card_content():
        if session_state.show_key_hints:
            show_key_hints()
            return

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
        else:
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

    with ui.card().classes("w-full flex flex-col justify-center items-center").style(
        "height: calc(100vh - 200px)"
    ):
        card_content()

    ui.keyboard(on_key=handle_key)
