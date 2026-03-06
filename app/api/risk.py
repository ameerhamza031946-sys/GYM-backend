from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import os
import json
from google import genai

from app.core.database import get_db
from app.models import schema, api_schemas

router = APIRouter()

api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

@router.get("/metrics/{user_id}", response_model=api_schemas.PerformanceStats)
async def get_performance_metrics(user_id: int, db: Session = Depends(get_db)):
    user = db.query(schema.User).filter(schema.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    return {
        "strength": int(user.strength_score),
        "stamina": int(user.stamina_score),
        "recovery": int(user.recovery_score),
        "weekly_progress": [
            {"title": "FITAI HEAVY SQUATS", "time": "Yesterday", "metric": "+1.2k Vol", "trend": "+12%"},
            {"title": "FITAI ENDURANCE RUN", "time": "2 days ago", "metric": "5.4 km", "trend": "+5%"}
        ]
    }

@router.get("/alerts/{user_id}", response_model=api_schemas.RecoveryAlertResponse)
async def get_recovery_alerts(user_id: int, db: Session = Depends(get_db)):
    user = db.query(schema.User).filter(schema.User.id == user_id).first()
    if not user:
        return {"has_warning": False, "message": None}
        
    recovery = db.query(schema.RecoveryData).filter(schema.RecoveryData.user_id == user_id).order_by(schema.RecoveryData.date.desc()).first()
    
    if user.recovery_score < 40.0:
        # 1. Multi-factor Risk Context
        # We look at strength vs recovery, sleep, and soreness to identify "Overtraining Syndrome" risk
        context = {
            "recovery_score": user.recovery_score,
            "strength_score": user.strength_score,
            "sleep_hours": recovery.sleep_hours if recovery else "unknown",
            "soreness": recovery.soreness_level if recovery else "unknown",
            "trend": "decreasing" if user.recovery_score < 50 else "stable"
        }
        
        msg = f"Your recovery is low today ({user.recovery_score:.1f}%). Biometrics suggest reduced CNS readiness. Reduce intensity by 20% to avoid overtraining."
        
        if client:
             try:
                 prompt = f"""
                 Analyze the following biometric data for an athlete:
                 {json.dumps(context)}
                 
                 Identify specific risks (e.g. Overtraining, CNS Fatigue, Sleep Deprivation).
                 Provide a 2-sentence warning that is professional, empathetic, and scientifically grounded.
                 Advise on specific training adjustments (e.g. deload, active recovery, or complete rest).
                 """
                 response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
                 msg = response.text.strip()
             except Exception as e:
                 print(f"Risk AI Error: {e}")
                 pass
        return {"has_warning": True, "message": msg}
        
    return {"has_warning": False, "message": None}
