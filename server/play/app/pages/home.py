from nicegui import ui


@ui.page("/")
def home():
    ui.button("Play", on_click=lambda: ui.navigate.to("/play"))
