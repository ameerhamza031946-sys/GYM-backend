import sys
import os

# Add the app directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.services.knowledge_base import populate_knowledge_base

if __name__ == "__main__":
    print("Populating FitAI Knowledge Base...")
    try:
        populate_knowledge_base()
        print("Success! Knowledge base is ready for the hackathon.")
    except Exception as e:
        print(f"Error populating knowledge base: {e}")
