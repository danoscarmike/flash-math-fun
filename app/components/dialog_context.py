from contextlib import contextmanager
from nicegui import ui


@contextmanager
def dialog_context(
    title: str, message: str, confirm_text: str = "Yes", cancel_text: str = "No"
):
    """Context manager for creating dialogs with automatic cleanup"""
    dialog = None
    try:
        with ui.dialog() as dialog, ui.card():
            ui.label(title).classes("text-2xl font-bold mb-4")
            ui.label(message).classes("text-lg mb-6")
            yield dialog
    except Exception as e:
        if dialog:
            dialog.close()
        raise
