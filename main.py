from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import login

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(login.router)

@app.get("/")
def read_root():
    return {"message": "Group 5 Backend is modular, awake, and listening!"}