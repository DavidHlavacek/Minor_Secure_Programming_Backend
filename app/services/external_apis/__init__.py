"""
External Game APIs Integration Services

This module handles integration with various game APIs and transforms
their responses into standardized category schemas.

Supported APIs:
- Riot Games API (League of Legends, Valorant)
- Ubisoft API (Rainbow Six Siege)
- Steam API (CS:GO, Dota 2)
- Blizzard API (Overwatch, WoW)
"""

from .riot_api import RiotAPIService
from .ubisoft_api import UbisoftAPIService
from .transformer import StatsTransformer

__all__ = [
    "RiotAPIService",
    "UbisoftAPIService", 
    "StatsTransformer"
] 