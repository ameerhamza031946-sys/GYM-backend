import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'app'))
sys.path.append(os.getcwd())

from app.core.database import SessionLocal, engine, Base
from app.models.schema import User

def list_users():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        print(f"Total Users: {len(users)}")
        for u in users:
            print(f"ID: {u.id}, Email: {u.email}, Password: {u.password}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    list_users()
