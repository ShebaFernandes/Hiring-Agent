# Hiring Agent

A small hiring portal: candidates apply to job postings through a public form (with resume upload), and an admin reviews applications and moves them through a hiring pipeline from a dashboard.

## Features

- Public apply page — pick a job, fill in details, upload a resume (PDF/Word)
- Admin login (single hardcoded admin account, JWT-based)
- Admin dashboard:
  - **Jobs** tab — create, edit, delete job postings
  - **Candidates** tab — view applicants, filter by job/stage, download resumes, move candidates through the pipeline (`Applied → R1 → R2 → R3 → Approved`, with a reject option at each round)

## Tech stack

- **Backend**: Flask, SQLite (via Python's built-in `sqlite3`), Flask-JWT-Extended, Flask-CORS
- **Frontend**: React 19, Vite, React Router, Axios

## Project structure

```
backend/
  app/
    routes/         # auth, jobs, candidates endpoints
    utils/          # response serializers
    config.py       # env-driven settings
    extensions.py   # SQLite connection + schema
  run.py            # entrypoint
  seed.py           # populates sample jobs
  uploads/          # uploaded resumes (gitignored)

frontend/
  src/
    pages/          # ApplyPage, AdminLogin, AdminDashboard
    components/      # JobsManager, CandidatesPanel, etc.
    api/client.js    # axios instance with auth header + 401 handling
```

## Setup

### Backend

```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python seed.py       # creates sample jobs (run once)
python run.py
```

The API runs at `http://localhost:5000`. It stores data in a local SQLite file at `backend/hiring_agent.db` (created automatically on first run) — no external database needed.

### Frontend

```powershell
cd frontend
npm install
copy .env.example .env
npm run dev
```

The site runs at `http://localhost:5173` and talks to the API via `VITE_API_URL` (defaults to `http://localhost:5000/api`).

## Default admin login

```
Email:    admin@enter.in
Password: admin123
```

Change these via `ADMIN_EMAIL` / `ADMIN_PASSWORD` in `backend/.env`.

## Environment variables (`backend/.env`)

| Variable | Default | Purpose |
|---|---|---|
| `DATABASE_PATH` | `backend/hiring_agent.db` | SQLite file location |
| `JWT_SECRET_KEY` | `dev-secret-change-me` | Signs admin JWTs — change for anything beyond local dev |
| `ADMIN_EMAIL` / `ADMIN_PASSWORD` | `admin@enter.in` / `admin123` | The one hardcoded admin login |

## API overview

| Method | Path | Auth | Purpose |
|---|---|---|---|
| POST | `/api/auth/login` | — | Admin login, returns a JWT |
| GET | `/api/auth/me` | ✓ | Validate a stored token |
| GET | `/api/jobs` | — | List jobs (for the apply page dropdown) |
| GET | `/api/admin/jobs` | ✓ | List jobs (admin) |
| POST | `/api/admin/jobs` | ✓ | Create a job |
| PUT | `/api/admin/jobs/<id>` | ✓ | Edit a job |
| DELETE | `/api/admin/jobs/<id>` | ✓ | Delete a job |
| POST | `/api/apply` | — | Submit an application (multipart, includes resume) |
| GET | `/api/admin/candidates` | ✓ | List candidates, optional `?job_id=` / `?stage=` filters |
| PATCH | `/api/admin/candidates/<id>/stage` | ✓ | Move a candidate to a new stage |
| GET | `/api/admin/candidates/<id>/resume` | ✓ | Download a candidate's resume |
| GET | `/api/stages` | — | Canonical list of pipeline stages |

## Notes

- Deleting a job does **not** delete its candidates — past applications stay visible for record-keeping.
- Resumes are stored on disk under `backend/uploads/`, prefixed with a UUID so identically-named files never collide.
- Reseeding: `python seed.py --force` wipes and repopulates jobs + candidates.
