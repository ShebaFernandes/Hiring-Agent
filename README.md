# Hiring Agent

A small hiring portal: candidates apply to job postings through a public form (with resume upload), and an admin reviews applications and moves them through a hiring pipeline from a dashboard.

## Features

- Public apply page — pick a job, fill in details (name, phone, email, note), upload a resume (PDF/Word)
- Admin login (single hardcoded admin account, JWT-based — no signup)
- Admin dashboard:
  - **Jobs** tab — create, edit, delete job postings
  - **Candidates** tab — view applicants, filter by job/stage, download resumes, move candidates through the pipeline (`Applied → R1 → R2 → R3 → Approved`, with a reject option at each round)
- **10 sample jobs auto-seeded** on first startup, so the dropdown and dashboard are never empty
- Deploys as a **single service** — in production Flask serves the built React app *and* the API from one origin

## Tech stack

- **Backend**: Flask, SQLite (via Python's built-in `sqlite3`), Flask-JWT-Extended, Flask-CORS, Gunicorn
- **Frontend**: React 19, Vite, React Router, Axios
- **Deployment**: Docker (multi-stage build) — runs anywhere that takes a Dockerfile (Render, Railway, Fly.io, …)

## Project structure

```
Dockerfile          # multi-stage: builds React, then runs Flask serving it
backend/
  app/
    routes/         # auth, jobs, candidates endpoints
    utils/          # response serializers
    config.py       # env-driven settings
    extensions.py   # SQLite connection + schema
    seed_data.py    # the 10 sample jobs + auto-seed helper
    __init__.py     # app factory; also serves the built frontend
  run.py            # entrypoint
  seed.py           # manual seed/reset script (optional — startup auto-seeds)
  uploads/          # uploaded resumes (gitignored)

frontend/
  src/
    pages/          # ApplyPage, AdminLogin, AdminDashboard
    components/     # JobsManager, CandidatesPanel, etc.
    api/client.js   # axios instance (same-origin /api) with auth + 401 handling
```

## Run locally (development)

Two terminals: Flask API on `:5000`, Vite dev server on `:5173` (Vite proxies `/api` to Flask).

### Backend

```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python run.py            # jobs auto-seed on first run
```

API runs at `http://localhost:5000`, storing data in `backend/hiring_agent.db` (created automatically).

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

## Run the production build locally (Docker)

This runs the exact same container a host will run — the whole app on one port:

```bash
docker build -t hiring-agent .
docker run -p 8000:8000 hiring-agent
```

Open `http://localhost:8000` — both the apply page (`/`) and admin dashboard (`/admin/login`) are served from that single port.

## Deploy (single service)

The Dockerfile builds the frontend and runs the backend that serves it, so you deploy **one service, one URL**.

### Render (free)

1. Push this repo to GitHub.
2. On [render.com](https://render.com): **New → Web Service** → connect the repo (Render auto-detects the `Dockerfile`).
3. Instance type: **Free**.
4. Add environment variables:
   - `JWT_SECRET_KEY` — a long random string
   - `ADMIN_EMAIL` — `admin@enter.in`
   - `ADMIN_PASSWORD` — your choice
5. Create the service. You get a URL like `https://your-app.onrender.com` — apply page at `/`, admin at `/admin/login`.

> **Free-tier note:** Render's free disk is ephemeral and the service sleeps when idle, so on restart the DB resets. The 10 jobs auto-reseed, but candidate applications submitted during testing are cleared. For durable data, use a paid **Persistent Disk** mounted at `/data`.

### Railway (data persists)

Same Dockerfile. Create a service from the repo, add a **Volume mounted at `/data`**, set the same environment variables. `DATABASE_PATH` and `UPLOAD_FOLDER` already point at `/data` (see the Dockerfile), so the SQLite DB and resumes survive restarts.

## Default admin login

```
Email:    admin@enter.in
Password: Enter@Hiring2026
```

Change these via `ADMIN_EMAIL` / `ADMIN_PASSWORD` (env vars in production, `backend/.env` locally).

## Environment variables

| Variable | Default | Purpose |
|---|---|---|
| `DATABASE_PATH` | `backend/hiring_agent.db` (`/data/hiring_agent.db` in Docker) | SQLite file location |
| `UPLOAD_FOLDER` | `backend/uploads` (`/data/uploads` in Docker) | Where resumes are stored |
| `FRONTEND_DIST` | `frontend/dist` | Built React app Flask serves in production |
| `JWT_SECRET_KEY` | `dev-secret-change-me` | Signs admin JWTs — change for anything beyond local dev |
| `ADMIN_EMAIL` / `ADMIN_PASSWORD` | `admin@enter.in` / `admin123` | The one hardcoded admin login |
| `VITE_API_URL` | `/api` | Frontend API base (leave default; same-origin in production) |

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
| GET | `/api/health` | — | Health check (`{"status":"ok"}`) |

## How to test

Open the app (`http://localhost:5173` in dev, or your deployed URL) and walk through:

1. **Apply page** — the Job dropdown lists 10 jobs; submit an application with a PDF/Word resume.
2. **Admin login** (`/admin/login`) — sign in with the credentials above.
3. **Jobs tab** — create, edit, and delete a job.
4. **Candidates tab** — your application appears with all details; filter by **Job** and by **Stage**; change a candidate's stage; download their resume.

Quick backend health checks:

```bash
curl http://localhost:5000/api/health   # -> {"status":"ok"}
curl http://localhost:5000/api/jobs      # -> the 10 jobs as JSON
```

## Notes

- Jobs **auto-seed** on startup only when the DB is empty; `python seed.py --force` wipes and repopulates jobs + candidates manually.
- Deleting a job does **not** delete its candidates — past applications stay visible for record-keeping.
- Resumes are stored on disk, prefixed with a UUID so identically-named files never collide.
