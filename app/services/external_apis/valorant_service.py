import os
from typing import Any, Dict, Optional

import httpx


class ValorantService:
    """
    Thin async wrapper around Riot’s official VAL-* endpoints.

    A production API key is required – store it in the environment
    variable `RIOT_API_KEY`.  Region clusters that currently serve
    VALORANT data are `americas`, `asia`, and `europe`.
    """

    def __init__(self,
                 api_key: Optional[str] = None,
                 region: str = "americas") -> None:
        self.api_key: str = api_key or os.getenv("RIOT_API_KEY", "")
        if not self.api_key:
            raise RuntimeError("RIOT_API_KEY is not set")

        self.base_url = f"https://{region}.api.riotgames.com"
        self.headers = {"X-Riot-Token": self.api_key}

    # ---------- low-level helper ---------- #
    async def _get(self, path: str,
                   params: Optional[Dict[str, Any]] = None) -> Any:
        url = f"{self.base_url}{path}"
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get(url, headers=self.headers, params=params)
            if r.status_code != 200:
                raise ValueError(
                    f"Riot API {r.status_code}: {r.text[:200]}")
            return r.json()

    # ---------- VAL-CONTENT-V1 ---------- #
    async def get_content(self, locale: str | None = None) -> Any:
        params = {"locale": locale} if locale else None
        return await self._get("/val/content/v1/contents", params)

    # ---------- VAL-MATCH-V1 ---------- #
    async def get_match(self, match_id: str) -> Any:
        return await self._get(f"/val/match/v1/matches/{match_id}")

    async def get_matchlist_by_puuid(
        self, puuid: str, start: int = 0, count: int = 20
    ) -> Any:
        params = {"startIndex": start, "endIndex": start + count}
        return await self._get(
            f"/val/match/v1/matchlists/by-puuid/{puuid}", params)

    async def get_recent_matches(self, queue: str, max_games: int = 15) -> Any:
        params = {"queue": queue}
        # Riot’s endpoint already caps results (default 10, hard-limit 15)
        data = await self._get(
            f"/val/match/v1/recent-matches/by-queue/{queue}", params)
        return data if max_games >= 15 else data[:max_games]

    # ---------- VAL-RANKED-V1 ---------- #
    async def get_leaderboard(self, act_id: str,
                              size: int = 100, start: int = 0) -> Any:
        params = {"size": size, "startIndex": start}
        return await self._get(
            f"/val/ranked/v1/leaderboards/by-act/{act_id}", params)

    # ---------- VAL-STATUS-V1 ---------- #
    async def get_status(self) -> Any:
        return await self._get("/val/status/v1/platform-data")

 # ─── RIOT-ACCOUNT-V1
    async def get_account_by_riot_id(
        self, game_name: str, tag_line: str
    ) -> Dict[str, Any]:
        """
        Convert a Riot ID (e.g. 'TenZ' + 'NA1') into an account object:
        { 'puuid': '...', 'gameName': 'TenZ', 'tagLine': 'NA1' }
        """
        path = f"/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
        return await self._get(path)