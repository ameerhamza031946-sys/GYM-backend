import sys
import os

# Add the backend directory to the sys.path
path = os.path.join(os.path.dirname(__file__), '../backend')
sys.path.append(path)

try:
    from main import app
except Exception as e:
    print(f"FAILED TO IMPORT APP: {e}")
    # Create a dummy app to report the error if the main one fails
    from fastapi import FastAPI
    app = FastAPI()
    @app.get("/")
    @app.get("/{path:path}")
    def fallback(path: str = None):
        return {"error": "Startup Failed", "detail": str(e), "path": path}
