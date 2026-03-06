from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import time
from dotenv import load_dotenv
load_dotenv()  # Load .env file so GEMINI_API_KEY is available

from app.core.init_db import init_db
from app.core.database import SessionLocal
from app.models.schema import ActivityLog

# Rate Limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

app = FastAPI(title="FitAI API", version="1.0.0")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

@app.on_event("startup")
def on_startup():
    try:
        print("Starting FitAI API...")
        init_db()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"CRITICAL: Database initialization failed: {e}")
        # We don't raise here to let the app start even if DB fails 
        # (useful for reaching health checks or diagnostic endpoints)

@app.get("/api/debug-info")
def debug_info(request: Request):
    import sys
    import os
    return {
        "python_version": sys.version,
        "cwd": os.getcwd(),
        "path": sys.path,
        "env": {k: v for k, v in os.environ.items() if "KEY" not in k.upper() and "SECRET" not in k.upper()},
        "vercel_env": os.environ.get("VERCEL")
    }
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://fitai.com",
    "*" # Keep * during active dev for ease, but in production replace with explicit domains
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Activity Tracking Middleware
@app.middleware("http")
async def log_requests_middleware(request: Request, call_next):
    start_time = time.time()
    
    # Process the request
    response = await call_next(request)
    
    # Avoid logging spammy requests like /health or pure OPTIONS
    if request.url.path not in ["/health", "/docs", "/openapi.json"] and request.method != "OPTIONS":
        db = SessionLocal()
        try:
            # We don't have the user_id context easily here without parsing the token, 
            # so we log IP and Agent. The actual user_id could be added if we inspect the Authorization header.
            ip_addr = request.client.host if request.client else "unknown"
            user_agent = request.headers.get("user-agent", "unknown")
            
            activity = ActivityLog(
                endpoint=request.url.path,
                method=request.method,
                ip_address=ip_addr,
                user_agent=user_agent
            )
            db.add(activity)
            db.commit()
        except Exception as e:
            print(f"Error logging activity: {e}")
        finally:
            db.close()
            
    # Add custom processing time header
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    return response

@app.get("/")
@limiter.limit("10/minute")
def read_root(request: Request):
    return {"status": "ok", "message": "FitAI Secure API is running", "timestamp": time.time()}

@app.get("/health")
def health_check(request: Request):
    return {"status": "healthy"}

from app.api import trainer, nutrition, risk, users, auth

app.include_router(trainer.router, prefix="/api/trainer", tags=["Trainer"])
app.include_router(nutrition.router, prefix="/api/nutrition", tags=["Nutrition"])
app.include_router(risk.router, prefix="/api/risk", tags=["Risk Analysis"])
app.include_router(users.router, prefix="/api/users", tags=["User Profile"])
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
