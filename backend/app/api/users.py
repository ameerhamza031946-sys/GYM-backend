from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import schema, api_schemas
from app.api import deps
from app.core import security

router = APIRouter()

@router.get("/me", response_model=api_schemas.UserProfileUpdate)
async def read_user_me(current_user: schema.User = Depends(deps.get_current_user)):
    return current_user

@router.get("/{user_id}", response_model=api_schemas.UserProfileUpdate)
async def get_user_profile(user_id: int, db: Session = Depends(get_db), current_user: schema.User = Depends(deps.get_current_user)):
    if current_user.id != user_id and current_user.email != "admin@fitai.com": # basic role check
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    user = db.query(schema.User).filter(schema.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=api_schemas.UserProfileUpdate)
async def update_user_profile(user_id: int, profile: api_schemas.UserProfileUpdate, db: Session = Depends(get_db), current_user: schema.User = Depends(deps.get_current_user)):
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this user")
    
    user = db.query(schema.User).filter(schema.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = profile.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)
        
    db.commit()
    db.refresh(user)
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: Session = Depends(get_db), current_user: schema.User = Depends(deps.get_current_user)):
    if current_user.id != user_id and current_user.email != "admin@fitai.com":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this user")
        
    user = db.query(schema.User).filter(schema.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    db.delete(user)
    db.commit()
    return None

@router.get("/", response_model=list[api_schemas.UserResponse])
async def get_all_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: schema.User = Depends(deps.get_current_user)):
    # Restrict fetching all users to an admin or return subset in production
    if current_user.email != "admin@fitai.com":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to list all users")
    users = db.query(schema.User).offset(skip).limit(limit).all()
    return users
