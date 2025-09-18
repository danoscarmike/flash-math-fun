from typing import Callable, Optional

from nicegui import ui

from app.components import ui_section


class CardsPerRoundSelector:
    """Reusable cards per round selection component with context manager support"""

    def __init__(
        self,
        session_state,
        max_possible_cards_func: Callable,
        on_change_callback: Optional[Callable] = None,
    ):
        self.session_state = session_state
        self.max_possible_cards_func = max_possible_cards_func
        self.on_change_callback = on_change_callback
        self.container = None
        self.predefined_options = [5, 10, 15, 20, 25]

    def __enter__(self):
        """Context manager entry"""
        return self.create_ui()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup"""
        pass

    def create_ui(self):
        """Create the cards per round selection UI with context manager"""
        with ui_section("Cards per round", "gap-4"):
            # Create a container for the select that we can refresh
            with ui.column() as self.container:
                pass

            # Initialize the select
            self.update_options()

    def update_options(self):
        """Update the available options based on max possible cards"""
        if self.container is None:
            return

        self.container.clear()

        max_possible = self.max_possible_cards_func(
            self.session_state.operations, self.session_state.selected_numbers
        )
        print(
            f"CardsPerRoundSelector: update_options called, max_possible: {max_possible}"
        )

        # If no numbers are selected, show a message instead of options
        if max_possible == 0:
            print("CardsPerRoundSelector: No numbers selected, showing error message")
            with self.container:
                ui.label(
                    "Please select at least one number to generate questions"
                ).classes("text-red-500 text-sm")
            return

        # Only include predefined options that don't exceed the maximum possible
        options = {}
        for i in self.predefined_options:
            if i <= max_possible:
                options[i] = f"{i} cards"

        # Find the highest valid option from the predefined list
        valid_options = [i for i in self.predefined_options if i <= max_possible]
        max_valid_option = max(valid_options) if valid_options else 5

        # If current selection exceeds the highest valid option, reset to it
        if self.session_state.cards_per_round > max_valid_option:
            self.session_state.cards_per_round = max_valid_option

        print(f"CardsPerRoundSelector: Creating dropdown with options: {options}")
        with self.container:
            ui.select(
                options=options, value=self.session_state.cards_per_round
            ).bind_value(self.session_state, "cards_per_round").on(
                "update:model-value",
                lambda: (
                    self.on_change_callback() if self.on_change_callback else None
                ),
            ).classes(
                "w-full"
            )
