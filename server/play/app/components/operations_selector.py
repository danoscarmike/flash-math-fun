from typing import Callable, Optional

from nicegui import ui

from app.components import ui_section


class OperationsSelector:
    """Reusable operations selection component with context manager support"""

    def __init__(self, session_state, on_change_callback: Optional[Callable] = None):
        self.session_state = session_state
        self.on_change_callback = on_change_callback

    def __enter__(self):
        """Context manager entry"""
        return self.create_ui()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup"""
        pass

    def create_ui(self):
        """Create the operations selection UI with context manager"""
        with ui_section("Operations", "gap-4"):
            ui.select(
                self.session_state.supported_operations,
                multiple=True,
                value=self.session_state.operations,
            ).bind_value(self.session_state, "operations").on(
                "update:model-value",
                lambda: (
                    self.on_change_callback() if self.on_change_callback else None
                ),
            )
