1. Mobile App requests stats for a game
2. Backend identifies game's category (MOBA/FPS/RPG)
3. Service Layer calls appropriate external API (Riot/Ubisoft/Steam)
4. Transformer converts raw API response → standardized category schema
5. Database caches transformed data
6. Mobile App receives consistent format regardless of source game
