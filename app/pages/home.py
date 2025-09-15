from nicegui import ui


def home():
    ui.button("Play", on_click=lambda: ui.navigate.to("/play"))
