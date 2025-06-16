"""
Stats Transformer Service

Converts external game API responses into standardized category schemas.
Each game's API response is transformed to match the category it belongs to.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from app.models.games import MOBAStats, FPSStats, RPGStats


class StatsTransformer:
    """
    Transforms external API responses to standardized category schemas.
    """
    
    @staticmethod
    def transform_riot_lol_to_moba(riot_data: Dict[str, Any]) -> MOBAStats:
        """
        Transform Riot API League of Legends response to MOBAStats schema.
        
        Args:
            riot_data: Combined data from multiple Riot API endpoints including:
                - Summoner data (from get_summoner_by_name)
                - Ranked stats (from get_ranked_stats)
                - Champion mastery (from get_champion_mastery)
                - Match history summary (from processing match details)
                
        Returns:
            Standardized MOBAStats object
        """
        # Extract base summoner data
        summoner_data = riot_data.get("summoner", {})
        ranked_data = riot_data.get("ranked", {})
        mastery_data = riot_data.get("mastery", [])
        match_data = riot_data.get("matches", [])
        
        # Process champion mastery to get favorite champions
        favorite_champions = []
        for champ in mastery_data[:3]:  # Take top 3 champions
            # In a real app, we'd convert champion IDs to names using static data
            champ_id = champ.get("championId", 0)
            champion_name = f"Champion {champ_id}"  # Placeholder, would use actual names
            favorite_champions.append(champion_name)
        
        # Calculate win rate
        wins = ranked_data.get("wins", 0)
        losses = ranked_data.get("losses", 0)
        total_games = wins + losses
        win_rate = (wins / total_games * 100) if total_games > 0 else 0
        
        # Calculate average KDA from match history
        total_kills = 0
        total_deaths = 0
        total_assists = 0
        main_roles_count = {}
        
        for match in match_data:
            # In a real implementation, find the participant that matches our summoner
            # Here we'll just assume we have participant data directly
            participant = match.get("participant", {})
            
            # Add KDA stats
            total_kills += participant.get("kills", 0)
            total_deaths += participant.get("deaths", 0)
            total_assists += participant.get("assists", 0)
            
            # Track role frequencies
            role = participant.get("role", "UNKNOWN")
            main_roles_count[role] = main_roles_count.get(role, 0) + 1
        
        # Calculate average KDA
        match_count = len(match_data)
        average_kda = None
        if match_count > 0:
            avg_kills = total_kills / match_count
            avg_deaths = max(1, total_deaths / match_count)  # Avoid division by zero
            avg_assists = total_assists / match_count
            average_kda = (avg_kills + avg_assists) / avg_deaths
        
        # Determine main role
        main_role = None
        if main_roles_count:
            main_role = max(main_roles_count, key=main_roles_count.get)
        
        # Combine into MOBAStats
        return MOBAStats(
            player_level=summoner_data.get("summonerLevel"),
            current_rank=f"{ranked_data.get('tier', '')} {ranked_data.get('rank', '')}".strip(),
            rank_tier=ranked_data.get("tier"),
            rank_division=ranked_data.get("rank"),
            wins=wins,
            losses=losses,
            win_rate=win_rate,
            total_games=total_games,
            main_role=main_role,
            favorite_champions=favorite_champions if favorite_champions else None,
            average_kda=round(average_kda, 2) if average_kda is not None else None
        )
    
    @staticmethod 
    def transform_ubisoft_r6_to_fps(ubisoft_data: Dict[str, Any]) -> FPSStats:
        """
        Transform Ubisoft R6 Siege API response to FPSStats schema.
        
        Example Ubisoft API response structure:
        {
            "level": 156,
            "mmr": 3420,
            "rank": "Gold 1",
            "kills": 12450,
            "deaths": 8930,
            "assists": 3420,
            "headshots": 4680,
            "wins": 234,
            "losses": 189
        }
        """
        # TODO: Implement actual transformation logic
        total_shots = ubisoft_data.get("kills", 0) + ubisoft_data.get("deaths", 0)  # Simplified
        headshots = ubisoft_data.get("headshots", 0)
        
        return FPSStats(
            player_level=ubisoft_data.get("level"),
            current_rank=ubisoft_data.get("rank"),
            rank_mmr=ubisoft_data.get("mmr"),
            kills=ubisoft_data.get("kills"),
            deaths=ubisoft_data.get("deaths"),
            assists=ubisoft_data.get("assists"),
            kd_ratio=ubisoft_data.get("kills") / max(ubisoft_data.get("deaths", 1), 1),
            headshot_percentage=headshots / max(total_shots, 1) * 100 if total_shots > 0 else None,
            wins=ubisoft_data.get("wins"),
            losses=ubisoft_data.get("losses"),
            total_matches=ubisoft_data.get("wins", 0) + ubisoft_data.get("losses", 0),
            favorite_operators=ubisoft_data.get("most_played_operators", [])
        )
    
    @staticmethod
    def transform_blizzard_wow_to_rpg(blizzard_data: Dict[str, Any]) -> RPGStats:
        """
        Transform Blizzard WoW API response to RPGStats schema.
        """
        # TODO: Implement WoW transformation
        return RPGStats(
            character_level=blizzard_data.get("level"),
            character_class=blizzard_data.get("character_class"),
            guild_name=blizzard_data.get("guild", {}).get("name"),
            achievements_count=blizzard_data.get("achievements_count"),
            total_playtime_hours=blizzard_data.get("playtime_seconds", 0) / 3600,
            equipment_score=blizzard_data.get("item_level")
        )
    
    @classmethod
    def transform_by_game_and_category(
        cls, 
        game_name: str, 
        category: str, 
        raw_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Route transformation based on game name and category.
        
        Args:
            game_name: Name of the game (e.g., "League of Legends")
            category: Game category (e.g., "MOBA", "FPS", "RPG")
            raw_data: Raw response from external API
            
        Returns:
            Transformed data as dictionary matching category schema
        """
        transformers = {
            ("League of Legends", "MOBA"): cls.transform_riot_lol_to_moba,
            ("Rainbow Six Siege", "FPS"): cls.transform_ubisoft_r6_to_fps,
            ("World of Warcraft", "RPG"): cls.transform_blizzard_wow_to_rpg,
            # TODO: Add more game/category combinations
        }
        
        transformer = transformers.get((game_name, category))
        if not transformer:
            raise ValueError(f"No transformer found for {game_name} ({category})")
            
        transformed_stats = transformer(raw_data)
        return transformed_stats.dict()
    
    @staticmethod
    def get_supported_transformations() -> Dict[str, list]:
        """
        Return list of supported game/category transformations.
        """
        return {
            "MOBA": ["League of Legends", "Dota 2"],
            "FPS": ["Rainbow Six Siege", "Valorant", "CS:GO"],
            "RPG": ["World of Warcraft", "Final Fantasy XIV"]
        } 