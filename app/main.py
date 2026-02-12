import os
import secrets
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import analyze, pages, token


app = FastAPI(title="FastAPI OCR System")


# Security Token
API_TOKEN = os.getenv("APP_API_TOKEN", secrets.token_urlsafe(32))
print(f"Server starting. Access Token required in Header 'X-Token': {API_TOKEN}")

# Save into app state for router access
app.state.API_TOKEN = API_TOKEN


# Middleware Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# Path Setup + Static
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")


# Routers
app.include_router(analyze.router)  # API routes
app.include_router(pages.router) # pages routes
app.include_router(token.router, prefix="/api")
