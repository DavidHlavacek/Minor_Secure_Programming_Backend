# app/api/endpoints/valorant_api.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Any, Dict

from app.core.config import get_settings
from app.services.external_apis.valorant_service import ValorantService

# ──────────────────────────────
# Router – *no* prefix here; we add it when including the router
# ──────────────────────────────
router = APIRouter(tags=["valorant"])


# ──────────────────────────────
# Dependency – grabs the cached settings each request
# ──────────────────────────────
async def get_val_service() -> ValorantService:
    s = get_settings()
    return ValorantService(api_key=s.riot_api_key, region=s.riot_region)


# ───────────────────────────────────────────────
# VAL-CONTENT-V1
# ───────────────────────────────────────────────
@router.get("/content", response_model=Dict[str, Any])
async def content(locale: str | None = None,
                  svc: ValorantService = Depends(get_val_service)):
    try:
        return {"success": True, "data": await svc.get_content(locale)}
    except Exception as exc:
        raise HTTPException(500, f"Failed to fetch content: {exc}")


# ───────────────────────────────────────────────
# VAL-MATCH-V1
# ───────────────────────────────────────────────
@router.get("/matches/{match_id}", response_model=Dict[str, Any])
async def match(match_id: str,
                svc: ValorantService = Depends(get_val_service)):
    try:
        return {"success": True, "data": await svc.get_match(match_id)}
    except ValueError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc))
    except Exception as exc:
        raise HTTPException(500, f"Failed to fetch match: {exc}")


@router.get("/players/{puuid}/matchlist", response_model=Dict[str, Any])
async def matchlist(puuid: str, start: int = 0, count: int = 20,
                    svc: ValorantService = Depends(get_val_service)):
    try:
        data = await svc.get_matchlist_by_puuid(puuid, start, count)
        return {"success": True, "data": data}
    except Exception as exc:
        raise HTTPException(500, f"Failed to fetch matchlist: {exc}")


@router.get("/queues/{queue}/recent", response_model=Dict[str, Any])
async def recent_matches(queue: str, max_games: int = 15,
                         svc: ValorantService = Depends(get_val_service)):
    """queue examples: unrated, competitive, swiftplay, spike_rush …"""
    try:
        data = await svc.get_recent_matches(queue, max_games)
        return {"success": True, "data": data}
    except Exception as exc:
        raise HTTPException(500, f"Failed to fetch recent matches: {exc}")


# ───────────────────────────────────────────────
# VAL-RANKED-V1
# ───────────────────────────────────────────────
@router.get("/leaderboards/{act_id}", response_model=Dict[str, Any])
async def leaderboard(act_id: str, size: int = 100, start: int = 0,
                      svc: ValorantService = Depends(get_val_service)):
    try:
        data = await svc.get_leaderboard(act_id, size, start)
        return {"success": True, "data": data}
    except Exception as exc:
        raise HTTPException(500, f"Failed to fetch leaderboard: {exc}")


# ───────────────────────────────────────────────
# VAL-STATUS-V1
# ───────────────────────────────────────────────
@router.get("/status", response_model=Dict[str, Any])
async def status_endpoint(svc: ValorantService = Depends(get_val_service)):
    try:
        return {"success": True, "data": await svc.get_status()}
    except Exception as exc:
        raise HTTPException(500, f"Failed to fetch platform status: {exc}")


# ───────────────────────────────────────────────
#  NEW 1/2  —  Riot-ID ➜ account object
# ───────────────────────────────────────────────
@router.get("/players/by-riot-id/{game_name}/{tag_line}", response_model=Dict[str, Any])
async def account_by_riot_id(game_name: str, tag_line: str,
                             svc: ValorantService = Depends(get_val_service)):
    """
    Resolve a public Riot ID (game name + tag) to its account object.
    """
    try:
        data = await svc.get_account_by_riot_id(game_name, tag_line)
        return {"success": True, "data": data}
    except Exception as exc:
        if "404" in str(exc):
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Riot ID not found")
        raise HTTPException(500, f"Lookup failed: {exc}")


# ───────────────────────────────────────────────
#  NEW 2/2  —  Riot-ID ➜ combined profile
# ───────────────────────────────────────────────
@router.get("/profile/by-riot-id/{game_name}/{tag_line}", response_model=Dict[str, Any])
async def combined_profile_by_riot_id(game_name: str, tag_line: str,
                                      svc: ValorantService = Depends(get_val_service)):
    """
    Convenience endpoint: Riot ID → PUUID → same combined profile you
    already serve at /profile/{puuid}.
    """
    try:
        account = await svc.get_account_by_riot_id(game_name, tag_line)
        puuid = account["puuid"]

        matchlist = await svc.get_matchlist_by_puuid(puuid, 0, 5)

        rank_info = None
        for game in matchlist.get("history", []):
            if game.get("queueId") == "competitive":
                match = await svc.get_match(game["matchId"])
                rank_info = match.get("competitiveTier")
                break

        return {
            "success": True,
            "data": {
                "puuid": puuid,
                "game_name": game_name,
                "tag_line": tag_line,
                "recent_matches": matchlist,
                "last_known_rank": rank_info
            }
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(500, f"Failed to build profile: {exc}")


# ───────────────────────────────────────────────
# Existing convenience profile by PUUID
# ───────────────────────────────────────────────
@router.get("/profile/{puuid}", response_model=Dict[str, Any])
async def combined_profile(puuid: str,
                           svc: ValorantService = Depends(get_val_service)):
    """
    Mini-profile pulling matchlist + last known competitive tier.
    """
    try:
        matchlist = await svc.get_matchlist_by_puuid(puuid, 0, 5)

        rank_info = None
        for game in matchlist.get("history", []):
            if game.get("queueId") == "competitive":
                match = await svc.get_match(game["matchId"])
                rank_info = match.get("competitiveTier")
                break

        return {
            "success": True,
            "data": {
                "puuid": puuid,
                "recent_matches": matchlist,
                "last_known_rank": rank_info
            }
        }
    except Exception as exc:
        raise HTTPException(500, f"Failed to build profile: {exc}")
