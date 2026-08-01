FROM python:3.12-slim

WORKDIR /app

COPY backend/requirements.txt ./backend/requirements.txt

RUN pip install --no-cache-dir -r backend/requirements.txt

COPY backend ./backend
COPY frontend/dist ./frontend/dist

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "backend.app:app"]