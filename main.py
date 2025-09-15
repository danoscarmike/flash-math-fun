import os
from nicegui import ui

from app.pages import home, health

home()

# Get port from environment variable (required for Cloud Run)
port = int(os.environ.get("PORT", 8080))

# Run the application
ui.run(host="0.0.0.0", port=port)
