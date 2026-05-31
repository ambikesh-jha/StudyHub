# StudyHub — Personal Learning CMS

A full-stack personal knowledge base. Organize your study material by course and topic — write notes, upload code files, images, and HTML files — all stored in PostgreSQL.

---

## Stack

- **Frontend**: React + Vite
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL

---

## Setup (Windows)

### 1. Create the database

Open **pgAdmin** or **psql** and run:

```sql
CREATE DATABASE studyhub;
```

---

### 2. Backend setup

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure your database
# Edit .env and set your PostgreSQL password:
# DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/studyhub

# Start the server
uvicorn main:app --reload --port 8000
```

Backend will run at: http://localhost:8000  
API docs at: http://localhost:8000/docs

---

### 3. Frontend setup

Open a **new terminal**:

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

Frontend will run at: http://localhost:5173

---

## Features

- **Home page** — Course cards (LangChain, LangGraph, etc.) with topic/material counts
- **Dashboard** — Per-course topic sidebar + materials grid
- **Note editor** — Write and edit text notes inline
- **File upload** — Upload images (preview), HTML files (iframe preview), code files (.py, .js, etc.)
- **Full CRUD** — Create, read, update, delete on courses, topics, and materials
- **Search** — Filter materials by title or content within a topic
- **Topic status** — Mark topics as To do / In progress / Done

---

## Project Structure

```
study-hub/
├── backend/
│   ├── main.py           # FastAPI app + CORS + routes
│   ├── models.py         # SQLAlchemy models
│   ├── schemas.py        # Pydantic schemas
│   ├── database.py       # DB connection
│   ├── .env              # DB config (edit this)
│   ├── requirements.txt
│   ├── uploads/          # Uploaded files (auto-created)
│   └── routes/
│       ├── courses.py
│       ├── topics.py
│       └── materials.py
└── frontend/
    ├── index.html
    ├── vite.config.js
    ├── package.json
    └── src/
        ├── App.jsx
        ├── index.css
        ├── api/
        │   └── client.js
        └── pages/
            ├── Home.jsx
            └── Dashboard.jsx
```

---

## API Reference

| Method | Path | Description |
|--------|------|-------------|
| GET | /courses/ | List all courses |
| POST | /courses/ | Create course |
| PUT | /courses/{id} | Update course |
| DELETE | /courses/{id} | Delete course |
| GET | /courses/{id}/topics/ | List topics |
| POST | /courses/{id}/topics/ | Create topic |
| PUT | /courses/{id}/topics/{tid} | Update topic |
| DELETE | /courses/{id}/topics/{tid} | Delete topic |
| GET | /topics/{id}/materials/ | List materials |
| POST | /topics/{id}/materials/ | Create note |
| POST | /topics/{id}/materials/upload | Upload file |
| PUT | /topics/{id}/materials/{mid} | Update material |
| DELETE | /topics/{id}/materials/{mid} | Delete material |
| GET | /topics/{id}/materials/file/{mid} | Serve file |
