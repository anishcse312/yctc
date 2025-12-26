FROM node:20-slim AS frontend

WORKDIR /app/frontend
COPY app/frontend/package.json app/frontend/package-lock.json* ./
RUN npm install
COPY app/frontend .
RUN npm run build

FROM python:3.11-slim

WORKDIR /app
COPY app/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ .
COPY migrate_schema.py migrate_schema.py
COPY migrate_data.py migrate_data.py
COPY make_db.py make_db.py
COPY schemas ./schemas
COPY N24 ./N24
COPY M32 ./M32
COPY --from=frontend /app/public/vite /app/public/vite
RUN chmod +x /app/entrypoint.sh

EXPOSE 8080

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "--worker-class", "eventlet", "-w", "1", "--bind", "0.0.0.0:8080", "server:app"]
