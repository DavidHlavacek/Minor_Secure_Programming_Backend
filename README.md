# Gamer CV API

A secure FastAPI backend for the Gamer CV mobile application, focusing on secure gaming statistics aggregation and user management.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- pip or poetry
- Supabase account and project

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Minor_Secure_Programming_Backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp example.env .env
# Edit .env with your actual values
```

5. Run the application:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### API Documentation
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🏗️ Project Structure

```
Minor_Secure_Programming_Backend/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── example.env            # Environment variables template
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## 🔧 Development

### Branch Strategy
- `main`: Production-ready FastAPI skeleton
- `dev`: Development branch with full API structure
- Feature branches: Checkout from `dev`, PR back to `dev`

### Environment Variables
Copy `example.env` to `.env` and configure:

- **Supabase**: Database connection and authentication
- **Security**: JWT secrets and algorithm settings
- **External APIs**: Game API keys (Riot, Steam, etc.)

## 📚 Features (Planned)

- User authentication and registration
- Secure password handling with bcrypt
- Game statistics aggregation
- Gaming wellness tracking
- Friend comparison system
- Secure API with JWT tokens

## 🔒 Security Features

- JWT-based authentication
- Password hashing with bcrypt
- Input validation with Pydantic
- CORS configuration
- Environment-based secrets
- Supabase integration for secure data storage

## 🧪 Testing

```bash
pytest
```

## 📝 License

[Add your license here]

## 👥 Team

- Ian Donker - Team Leader
- Timothy Adewale - Scrum Master
- David Hlaváček - Code Reviewer
- Stefan Tasca - Secretary
- Batuhan Gezgin - Developer 