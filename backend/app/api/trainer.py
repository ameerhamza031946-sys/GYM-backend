from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models import schema, api_schemas
from app.services.ai_trainer import generate_workout_plan

router = APIRouter()

@router.get("/workout/{workout_id}", response_model=api_schemas.WorkoutPlanResponse)
def get_workout_by_id(workout_id: int, db: Session = Depends(get_db)):
    workout = db.query(schema.Workout).filter(schema.Workout.id == workout_id).first()
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    return workout

@router.get("/today/{user_id}", response_model=api_schemas.WorkoutPlanResponse)
def get_todays_workout(user_id: int, db: Session = Depends(get_db)):
    user = db.query(schema.User).filter(schema.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    recovery = db.query(schema.RecoveryData).filter(schema.RecoveryData.user_id == user_id).order_by(schema.RecoveryData.date.desc()).first()
    print(f"DEBUG: Recovery data: {recovery}")
    
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    workout = db.query(schema.Workout).filter(
        schema.Workout.user_id == user_id, 
        schema.Workout.date >= today_start
    ).first()
    
    if workout:
        return workout
        
    user_profile = {
        "id": user.id,
        "name": user.name,
        "goal": user.fitness_goal,
        "level": user.fitness_level,
        "equipment_preference": user.equipment_preference,
        "targeted_muscle_groups": user.targeted_muscle_groups or [],
        "mobility_test_results": user.mobility_test_results or {},
        "training_frequency": user.training_frequency,
        "strength": user.strength_score,
        "stamina": user.stamina_score
    }
    recovery_metrics = {"sleep_hours": recovery.sleep_hours, "cns_readiness": recovery.cns_readiness} if recovery else {}
    
    ai_plan = generate_workout_plan(user_profile, recovery_metrics)
    
    new_workout = schema.Workout(
        user_id=user.id,
        title="Daily Session",
        focus=ai_plan["focus"],
        duration_mins=ai_plan.get("duration_mins", 45),
        calories=ai_plan.get("calories", 350),
        exercises=ai_plan.get("exercises", []),
        completed=False
    )
    
    db.add(new_workout)
    db.commit()
    db.refresh(new_workout)
    
    return new_workout

@router.post("/complete", response_model=api_schemas.WorkoutPlanResponse)
async def complete_workout(request: api_schemas.CompleteWorkoutRequest, db: Session = Depends(get_db)):
    workout = db.query(schema.Workout).filter(schema.Workout.id == request.workout_id).first()
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
        
    workout.completed = True
    
    # Update user metrics
    user = db.query(schema.User).filter(schema.User.id == workout.user_id).first()
    if user:
        user.strength_score = min(100.0, user.strength_score + 0.5)
        user.stamina_score = min(100.0, user.stamina_score + 1.2)
        user.recovery_score = max(0.0, user.recovery_score - 15.0) # Workout reduces recovery score until rest
        
    db.commit()
    db.refresh(workout)
    return workout
