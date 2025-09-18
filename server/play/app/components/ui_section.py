from contextlib import contextmanager
from nicegui import ui


@contextmanager
def ui_section(title: str, classes: str = "gap-4"):
    """Context manager for creating consistent UI sections with error handling"""
    try:
        with ui.column().classes(classes):
            if title:
                ui.label(title).classes("text-lg font-semibold")
            yield
    except Exception as e:
        ui.label(f"Error in {title}: {str(e)}").classes("text-red-500")
        raise
