# News Copilot Reader

A news platform with AI text completion features built

## What it does

This is a news website where you can:
- Read and write articles
- Get AI help to complete your writing
- Browse articles by category
- Comment and bookmark articles
- Basic user management

## What I built

- **Frontend**: SvelteKit app with a text editor that has AI completions
- **Backend**: Flask API with user auth, article management, and AI text generation
- **AI Model**: Custom transformer model for generating news-style text
- **Database**: PostgreSQL with user accounts, articles, comments, bookmarks

## Tech Stack

**Frontend**
- SvelteKit + TypeScript
- TailwindCSS for styling
- Monaco Editor for writing articles
- Vite build tool

**Backend**
- Flask (Python)
- SQLAlchemy + PostgreSQL
- JWT auth
- Redis for caching

**AI Stuff**
- Custom transformer model (PyTorch)
- Text generation API
- Training pipeline

## Features

- User registration/login
- Write and edit articles
- AI text completion while writing
- Categories and search
- Comments and bookmarks
- File uploads for images
- Basic admin panel

## How to run it

### Setup project

**Frontend:**
```bash
cd news-copilot-frontend
pnpm install
pnpm dev
```

**Backend:**
```bash
cd news-copilot-backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
flask run
```

**AI Model (optional):**
```bash
cd news-copilot-models
pip install -r requirements.txt
# The backend will work without this, just won't have AI completions
```

## Project structure

```
news-copilot-reader/
├── news-copilot-frontend/     # SvelteKit app
├── news-copilot-backend/      # Flask API
├── news-copilot-models/       # AI model code
└── docs/                      # Documentation
```

## What I learned

- Building a custom transformer model from scratch
- Integrating AI into a web application
- Full-stack development with modern tools
- Database design and API development
- Real-time features with WebSockets

This was a fun project to explore AI + web development. The code might not be perfect but it works!
