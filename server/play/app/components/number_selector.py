from typing import Any, Callable, Dict, List, Optional

from nicegui import ui

from app.components import ui_section


class NumberSelector:
    """Reusable number selection component with checkboxes and context manager support"""

    def __init__(
        self,
        selected_numbers: List[int],
        on_change_callback: Optional[Callable] = None,
    ):
        self.selected_numbers = selected_numbers
        self.on_change_callback = on_change_callback
        self.checkbox_vars: Dict[int, Any] = {}

    def __enter__(self):
        """Context manager entry"""
        return self.create_ui()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup"""
        pass

    def create_ui(self):
        """Create the number selection UI with context manager"""
        with ui_section("Numbers", "gap-4"):
            ui.label("Select which number facts to include:").classes(
                "text-sm text-gray-600"
            )

            # Select All / Clear All buttons
            with ui.row().classes("gap-2 mb-2"):
                ui.button("Select All", on_click=self.select_all).classes(
                    "text-xs px-2 py-1"
                )
                ui.button("Clear All", on_click=self.clear_all).classes(
                    "text-xs px-2 py-1"
                )

            # Number checkboxes
            with ui.row().classes("flex-wrap gap-2 w-full"):
                for num in range(1, 13):  # 1 to 12
                    checkbox = ui.checkbox(str(num)).classes("text-sm")
                    self.checkbox_vars[num] = checkbox
                    checkbox.value = num in self.selected_numbers

                    # Create a closure to capture the current value of num
                    def make_handler(n):
                        def handler():
                            # Get the current value of the checkbox
                            is_checked = self.checkbox_vars[n].value
                            self.toggle_number(n, is_checked)

                        return handler

                    checkbox.on("update:model-value", make_handler(num))

    def toggle_number(self, number: int, is_checked: bool):
        """Toggle a number in the selected list"""
        print(
            f"NumberSelector: toggle_number called for number {number}, is_checked: {is_checked}"
        )
        try:
            if is_checked:
                if number not in self.selected_numbers:
                    self.selected_numbers.append(number)
                    print(f"NumberSelector: Added {number} to selected_numbers")
            else:
                if number in self.selected_numbers:
                    self.selected_numbers.remove(number)
                    print(f"NumberSelector: Removed {number} from selected_numbers")
        except Exception as e:
            ui.label(f"Error toggling number {number}: {str(e)}").classes(
                "text-red-500"
            )
            return

        print(f"NumberSelector: Current selected_numbers: {self.selected_numbers}")
        self._update_ui_after_change()

    def _update_ui_after_change(self):
        """Update UI after state change"""
        self.update_checkbox_states()
        if self.on_change_callback:
            print(
                f"NumberSelector: Calling on_change_callback, selected_numbers: {self.selected_numbers}"
            )
            self.on_change_callback()

    def select_all(self):
        """Select all numbers 1-12"""
        try:
            self.selected_numbers.clear()
            self.selected_numbers.extend(range(1, 13))
        except Exception as e:
            ui.label(f"Error selecting all numbers: {str(e)}").classes("text-red-500")
            return

        self._update_ui_after_change()

    def clear_all(self):
        """Clear all numbers"""
        try:
            self.selected_numbers.clear()
        except Exception as e:
            ui.label(f"Error clearing numbers: {str(e)}").classes("text-red-500")
            return

        self._update_ui_after_change()

    def update_checkbox_states(self):
        """Update all checkbox values to reflect current selection"""
        for num in range(1, 13):
            if num in self.checkbox_vars:
                self.checkbox_vars[num].value = num in self.selected_numbers
