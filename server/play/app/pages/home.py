from nicegui import ui


@ui.page("/", title="Flash Math Fun!")
def home():
    ui.button("Play", on_click=lambda: ui.navigate.to("/play"))
