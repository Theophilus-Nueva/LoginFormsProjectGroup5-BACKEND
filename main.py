from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from services.rate_limiter import InMemoryLimiter
from routers import login, signup, dashboard, OTP

global_app_firewall = InMemoryLimiter(max_requests=60, window_seconds=60)

app = FastAPI(dependencies=[Depends(global_app_firewall.check_limit)])

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://loginformsprojectgroup5-production.up.railway.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(login.router)
app.include_router(signup.router) 
app.include_router(dashboard.router)
app.include_router(OTP.router)

@app.get("/")
def read_root():
    return {"message": "Listening to https://loginformsprojectgroup5-production.up.railway.app"}