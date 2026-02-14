# Lerno Backend - FastAPI Server

Backend API for the Lerno Student Learning Assistant.

## Setup

1. Create virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure `.env` file with your settings

4. Run server:
```bash
uvicorn main:app --reload --port 8000
```

## API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation.

## Environment Variables

- `MONGO_URI`: MongoDB connection string
- `DATABASE_NAME`: Database name
- `SECRET_KEY`: JWT secret key
- `ALGORITHM`: JWT algorithm (HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time
- `OPENAI_API_KEY`: (Optional) OpenAI API key
- `ANTHROPIC_API_KEY`: (Optional) Anthropic API key
