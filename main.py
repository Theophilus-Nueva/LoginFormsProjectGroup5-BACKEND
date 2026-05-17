from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import login
from routers import signup
from routers import dashboard

app = FastAPI()

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

@app.get("/")
def read_root():
    return {"message": "Listening to https://loginformsprojectgroup5-production.up.railway.app"}