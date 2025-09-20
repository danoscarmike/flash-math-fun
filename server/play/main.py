import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from nicegui import app, ui

from app.pages import health, home


# --- Google Analytics ---
GA_MEASUREMENT_ID = os.environ.get("GA_MEASUREMENT_ID", "G-EVJXJQ0KYX")

ga_script = f"""
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id={GA_MEASUREMENT_ID}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());

  gtag('config', '{GA_MEASUREMENT_ID}');
</script>
"""

# Add the Google Analytics script to the head of your NiceGUI app
ui.add_head_html(ga_script, shared=True)

# --- CORS Configuration ---
allowed_origins = [
    "http://localhost:8080",  # Your local development URL
    "http://localhost:3000",  # Common frontend dev port
    "https://flashmath.fun",  # Custom domain
]

# Add CORSMiddleware to the underlying FastAPI app
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# --- Configure Socket.IO transports ---
app.config.socket_io_js_transports = ["polling", "websocket"]

# --- Start the application ---
home()

# Get port from environment variable (required for Cloud Run)
port = int(os.environ.get("PORT", 8080))

# Run the application
ui.run(host="0.0.0.0", port=port, favicon="💥")
