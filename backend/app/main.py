import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from .api import models as models_router # Rename to avoid conflict
from .api import chat as chat_router     # Rename to avoid conflict


load_dotenv() # Load .env file if present

app = FastAPI(title="LLM-Forge Backend")

# Configure CORS (Cross-Origin Resource Sharing)
# Allows the frontend (running on a different port/domain) to talk to the backend
origins = [
    "http://localhost",        # Allow frontend dev server
    "http://localhost:80",     # Allow frontend served by Nginx in Docker
    "http://localhost:5173",   # Default Vite dev server port
    # Add your production frontend URL here if deploying
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods (GET, POST, etc.)
    allow_headers=["*"], # Allows all headers
)

@app.get("/")
async def read_root():
    """ Basic endpoint to check if backend is running """
    return {"message": "Welcome to LLM-Forge Backend"}

@app.get("/api/status")
async def get_status():
    """ Simple status endpoint for frontend to check connectivity """
    return {"status": "Backend is running!"}

# Include the new API routers
app.include_router(models_router.router, prefix="/api/models", tags=["Models"])
app.include_router(chat_router.router, prefix="/api/chat", tags=["Chat"])


print("Backend started successfully with Chat and Models endpoints.")
