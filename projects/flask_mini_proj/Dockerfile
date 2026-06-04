# Stage 1: Build React frontend
FROM node:20-alpine AS frontend-build
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Python Flask app
FROM python:3.11-slim
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
COPY --from=frontend-build /static/dist ./static/dist

EXPOSE 5000
ENV FLASK_APP=app.py
ENV FLASK_DEBUG=false
ENV PORT=5000

CMD ["python", "app.py"]
