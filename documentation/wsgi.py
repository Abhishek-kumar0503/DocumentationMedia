"""
WSGI config for documentation project.
"""

import os
import threading

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'documentation.settings')

# Get the WSGI application
application = get_wsgi_application()

# Initialize heavy components in background thread after server starts
def initialize_heavy_components():
    # Import here to avoid loading during server startup
    try:
        from media.views import get_ml_model, get_torch_device
        print("Initializing ML components in background...")
        # Initialize models in background
        model = get_ml_model()
        device = get_torch_device()
        print("ML components initialized successfully!")
    except Exception as e:
        print(f"Background initialization error: {e}")

# Start initialization in a separate thread
threading.Thread(target=initialize_heavy_components, daemon=True).start()
