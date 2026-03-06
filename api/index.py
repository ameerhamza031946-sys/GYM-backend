import sys
import os

# Add the backend directory to the sys.path
# This allows 'from app...' and other imports to work
path = os.path.join(os.path.dirname(__file__), '../backend')
sys.path.append(path)

from main import app
