from nicegui import ui


@ui.page("/health")
def health():
    """Health check endpoint for Cloud Run"""
    return {"status": "healthy", "service": "flash-math-fun"}
