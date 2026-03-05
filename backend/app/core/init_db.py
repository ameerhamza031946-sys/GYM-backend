from app.core.database import engine, SessionLocal, Base
from app.models.schema import User, Workout, RecoveryData, MealPlan, LoggedMeal

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    user = db.query(User).first()
    if not user:
        user = User(
            name="Elite Athlete",
            email="test@vibe.com",
            password="password123",
            strength_score=85.0,
            stamina_score=62.0,
            recovery_score=34.0,
            equipment_preference="gym",
            targeted_muscle_groups=[],
            mobility_test_results={}
        )
        db.add(user)
        db.commit()
        
        # Add a default recovery entry representing low recovery
        recovery = RecoveryData(
            user_id=user.id,
            sleep_hours=4.5,
            soreness_level="High",
            cns_readiness=34.0
        )
        db.add(recovery)
        db.commit()
    db.close()
