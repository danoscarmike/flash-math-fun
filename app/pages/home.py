from nicegui import ui


@ui.page("/home")
def home():
    ui.button("Play", on_click=lambda: ui.navigate.to("/play"))
