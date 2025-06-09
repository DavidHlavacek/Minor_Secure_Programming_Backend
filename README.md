# Gamer Stats API

Simple FastAPI backend for gaming statistics tracking.

## What it does

- Add games with username → fetches stats from external APIs
- View your games list 
- Click game → see detailed stats
- Profile page → aggregated stats by category (MOBA/FPS/RPG)

## Quick Start

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up environment:**
```bash
cp example.env .env
# Edit .env with your Supabase credentials
```

3. **Run:**
```bash
python main.py
```

API available at `http://localhost:8000`
- Docs: `http://localhost:8000/docs`

## API Endpoints

### Games
- `POST /api/v1/games` - Add game
- `GET /api/v1/games` - List games
- `DELETE /api/v1/games/{id}` - Remove game

### Stats  
- `GET /api/v1/stats/games/{id}` - Get game stats
- `POST /api/v1/stats/games/{id}/refresh` - Refresh from external API
- `GET /api/v1/stats/profile` - User profile with category totals

### Auth
- `POST /api/v1/auth/register` - Register
- `POST /api/v1/auth/login` - Login

## Project Structure

```
app/
├── models/          # Data models (games, stats, auth)
├── routers/         # API endpoints
├── services/        # Business logic
└── core/           # Database, security, config
```

## Environment Variables

Required in `.env`:
```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
SECRET_KEY=your_jwt_secret
``` 