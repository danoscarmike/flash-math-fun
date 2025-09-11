from typing import Callable, Optional

from nicegui import ui

from .dialog_context import dialog_context


class ConfirmationDialog:
    """Reusable confirmation dialog component with context manager support"""

    def __init__(
        self,
        title: str,
        message: str,
        confirm_text: str = "Yes",
        cancel_text: str = "No",
        confirm_color: str = "red",
        cancel_color: str = "gray",
    ):
        self.title = title
        self.message = message
        self.confirm_text = confirm_text
        self.cancel_text = cancel_text
        self.confirm_color = confirm_color
        self.cancel_color = cancel_color
        self.dialog = None
        self.is_open = False
        self.on_confirm = None
        self.on_cancel = None

    def __enter__(self):
        """Context manager entry"""
        return self.show()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with automatic cleanup"""
        self.close()

    def show(
        self,
        on_confirm: Optional[Callable] = None,
        on_cancel: Optional[Callable] = None,
    ):
        """Show the dialog with optional callbacks"""
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel

        with dialog_context(
            self.title, self.message, self.confirm_text, self.cancel_text
        ) as self.dialog:

            def handle_confirm():
                self.close()
                if self.on_confirm:
                    self.on_confirm()

            def handle_cancel():
                self.close()
                if self.on_cancel:
                    self.on_cancel()

            with ui.row():
                ui.button(self.confirm_text, on_click=handle_confirm).classes(
                    f"bg-{self.confirm_color}-500 text-white px-6 py-2"
                )
                ui.button(self.cancel_text, on_click=handle_cancel).classes(
                    f"bg-{self.cancel_color}-500 text-white px-6 py-2"
                )

        self.dialog.open()
        self.is_open = True
        return self.dialog

    def close(self):
        """Close the dialog"""
        if self.dialog:
            self.dialog.close()
        self.is_open = False
