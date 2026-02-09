# Nudj Backend

FastAPI backend for the Nudj HR Maturity Assessment Platform.

## Setup

```bash
cd src/backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

## Run

```bash
uvicorn main:app --reload
```

## Database Migrations

```bash
alembic upgrade head
```
