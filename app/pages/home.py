from nicegui import ui


@ui.page("/")
def home():
    ui.label("Home")
