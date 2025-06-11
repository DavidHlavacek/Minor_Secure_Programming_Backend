from fastapi import APIRouter
from app.routers import auth, games, stats, users


api_router = APIRouter()

# Include all routers with their respective prefixes
api_router.include_router(auth.router)
api_router.include_router(games.router)
api_router.include_router(stats.router)
api_router.include_router(users.router)

# TODO: Add more routers as needed
# api_router.include_router(admin.router)  # For admin endpoints
# api_router.include_router(analytics.router)  # For advanced analytics
# api_router.include_router(social.router)  # For friend system 