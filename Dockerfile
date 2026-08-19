# ---- Stage 1: build the React frontend ----
FROM node:20-slim AS frontend
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# ---- Stage 2: Python backend that also serves the built frontend ----
FROM python:3.12-slim
WORKDIR /app

COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY backend/ ./backend/
# Bring the compiled frontend in from stage 1.
COPY --from=frontend /app/frontend/dist ./frontend/dist

ENV FRONTEND_DIST=/app/frontend/dist \
    DATABASE_PATH=/data/hiring_agent.db \
    UPLOAD_FOLDER=/data/uploads \
    PYTHONUNBUFFERED=1

WORKDIR /app/backend
EXPOSE 8000

# $PORT is provided by the host (Render/Railway); default to 8000 locally.
# --preload loads the app once in the master (running the startup auto-seed a
# single time) before forking workers, so jobs can't be seeded twice.
CMD gunicorn run:app --bind 0.0.0.0:${PORT:-8000} --workers 2 --preload --timeout 120
