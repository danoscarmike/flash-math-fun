from nicegui import ui


@ui.page("/")
def home():
    ui.button("Play", on_click=lambda: ui.navigate.to("/play"))


@ui.page("/health")
def health():
    """Health check endpoint for Cloud Run"""
    return {"status": "healthy", "service": "flash-math-fun"}
