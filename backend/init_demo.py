import sys
import os

# Add the current directory to sys.path so we can import 'app'
sys.path.append(os.getcwd())

from app.core.database import SessionLocal, engine
from app.models.schema import User, Base
from app.core.init_db import init_db

def init_demo():
    print("Initializing Database...")
    init_db()
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == 'test@vibe.com').first()
        if user:
            user.password = 'password123'
            user.onboarding_completed = True
            print("Updated existing demo user.")
        else:
            user = User(
                name='Demo User',
                email='test@vibe.com',
                password='password123',
                onboarding_completed=True
            )
            db.add(user)
            print("Created new demo user.")
        db.commit()
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_demo()
