# 🐾 KittenConnect

A full-stack cat adoption platform. Users can create an account, post cats for
adoption with photos, browse listings, and manage (edit/delete) their own posts.

**Live demo:** _add your Vercel URL here after deploying_

## Tech stack

| Layer | Tech |
|-------|------|
| Frontend | React (Vite) |
| Backend | FastAPI (Python) |
| Database | SQLAlchemy ORM + SQLite |
| Auth | JWT (OAuth2 bearer tokens), bcrypt password hashing |
| Testing | pytest (30 tests, 97% coverage) |

## Features

- **Accounts** — signup / login with hashed passwords and JWT sessions
- **Listings** — post a cat with name, age, location, notes, and an uploaded photo
- **Photo upload** — image files uploaded from the device and served by the API
- **Ownership** — users can only edit or delete their own listings (403 otherwise)
- **8 REST endpoints** covering the full adoption flow

## Running locally

Two terminals:

```bash
# Terminal 1 — backend (http://127.0.0.1:8000, docs at /docs)
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload

# Terminal 2 — frontend (http://localhost:5173)
cd frontend
npm install
npm run dev
```

## Running the tests

```bash
pip install -r requirements-dev.txt
coverage run --source=. --omit="venv/*,test_main.py,conftest.py" -m pytest
coverage report -m
```

## Deployment

See [DEPLOY.md](DEPLOY.md) for step-by-step deployment to Render (backend) and
Vercel (frontend).
