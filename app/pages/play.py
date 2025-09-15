from nicegui import ui
from app.services import SessionState
from app.components import FlashCard, SettingsPanel


@ui.page("/play")
def play():
    # Global references
    session_state = SessionState()
    settings_panel = SettingsPanel(session_state)
    flash_card = FlashCard(session_state)

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

    ui.keyboard(on_key=flash_card.handle_key)

    with ui.card().classes("w-full flex flex-col justify-center items-center").style(
        "height: calc(100vh - 200px)"
    ):
        flash_card.card_content()
