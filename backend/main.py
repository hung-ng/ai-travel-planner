from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.api import chat, trips

# Create tables
# Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Travel Planner API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(trips.router, prefix="/api/trips", tags=["trips"])
# app.include_router(users.router, prefix="/api/users", tags=["users"])

@app.get("/")
async def root():
    return {"message": "AI Travel Planner API", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}