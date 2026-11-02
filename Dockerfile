# ---- Backend ----
FROM python:3.13-slim AS backend-base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN mkdir /data

FROM backend-base AS backend-dev
COPY backend/requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt
EXPOSE 5000
CMD ["sh", "-c", "alembic upgrade head && exec flask --app app run --debug --host 0.0.0.0 --port 5000"]

# ---- Frontend ----
FROM node:24-slim AS frontend-base
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

FROM frontend-base AS frontend-dev
EXPOSE 5173
# npm install keeps the node_modules volume in step with package.json.
CMD ["sh", "-c", "npm install && exec npm run dev -- --host 0.0.0.0"]

FROM frontend-base AS frontend-build
COPY frontend/ ./
RUN npm run build

# ---- Production: Flask serves the built UI from one origin ----
FROM backend-base AS prod
COPY backend/ ./
COPY --from=frontend-build /app/dist ./frontend_dist
ENV FRONTEND_DIST=/app/frontend_dist
RUN useradd --create-home app && chown app:app /data
USER app
EXPOSE 5000
VOLUME /data
CMD ["sh", "-c", "alembic upgrade head && exec gunicorn --bind 0.0.0.0:5000 'app:create_app()'"]
