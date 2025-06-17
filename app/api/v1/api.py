from fastapi import APIRouter
from app.routers import auth, games, stats, users
from app.routers.specific_games import lol, dota, overwatch, valorant

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(games.router)
api_router.include_router(stats.router)
api_router.include_router(users.router)
api_router.include_router(lol.router)
api_router.include_router(dota.router)
api_router.include_router(overwatch.router)
api_router.include_router(valorant.router)
