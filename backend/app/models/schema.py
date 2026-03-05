from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, default="Athlete")
    email = Column(String, unique=True, index=True)
    password = Column(String)
    strength_score = Column(Float, default=85.0)
    stamina_score = Column(Float, default=62.0)
    recovery_score = Column(Float, default=34.0)
    equipment_preference = Column(String, default="gym") # 'gym' or 'home'
    fitness_goal = Column(String)
    gender = Column(String)
    age_range = Column(String)
    fitness_level = Column(String)
    training_frequency = Column(String)
    nutrition_goal = Column(String)
    onboarding_completed = Column(Boolean, default=False)
    targeted_muscle_groups = Column(JSON, default=list) # List of strings
    mobility_test_results = Column(JSON, default=dict) # Dict of test results
    available_equipment = Column(JSON, default=list) # List of strings

    logged_meals = relationship("LoggedMeal", back_populates="user")

class Workout(Base):
    __tablename__ = "workouts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(DateTime, default=datetime.utcnow)
    title = Column(String)
    focus = Column(String)
    duration_mins = Column(Integer)
    calories = Column(Integer)
    completed = Column(Boolean, default=False)
    exercises = Column(JSON) # Store list of exercises

class RecoveryData(Base):
    __tablename__ = "recovery_data"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(DateTime, default=datetime.utcnow)
    sleep_hours = Column(Float)
    soreness_level = Column(String)
    cns_readiness = Column(Float)

class MealPlan(Base):
    __tablename__ = "meal_plans"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(DateTime, default=datetime.utcnow)
    daily_calories_target = Column(Integer)
    macros = Column(JSON)
    meals = Column(JSON)

class LoggedMeal(Base):
    __tablename__ = "logged_meals"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    calories = Column(Integer)
    protein = Column(Integer)
    carbs = Column(Integer)
    fats = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="logged_meals")

class ActivityLog(Base):
    __tablename__ = "activity_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True) # allow null for unauthenticated interactions
    endpoint = Column(String)
    method = Column(String)
    ip_address = Column(String)
    user_agent = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
