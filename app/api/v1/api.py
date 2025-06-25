from fastapi import APIRouter
from app.routers import auth, games, stats, users
from app.routers.specific_games import lol, dota, overwatch, valorant
import os

# Check if we're in debug mode
DEBUG_MODE = os.getenv("DEBUG", "False").lower() == "true"

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(games.router, prefix="/games", tags=["games"])
api_router.include_router(dota.router, prefix="/dota", tags=["dota"])
api_router.include_router(overwatch.router, prefix="/overwatch", tags=["overwatch"])
api_router.include_router(valorant.router, prefix="/valorant", tags=["valorant"])
