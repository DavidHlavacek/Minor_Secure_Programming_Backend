Mobile App requests stats for a game
Backend identifies game's category (MOBA/FPS/RPG)
Service Layer calls appropriate external API (Riot/Ubisoft/Steam)
Transformer converts raw API response → standardized category schema
Database caches transformed data
Mobile App receives consistent format regardless of source game