# syntax=docker/dockerfile:1

# ------------------------------------------------------------------ #
# Stage 1 — build the React/Vite frontend into static/dist
# ------------------------------------------------------------------ #
FROM node:20-alpine AS frontend-build
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# ------------------------------------------------------------------ #
# Stage 2 — Python Flask backend (local FAISS + Bedrock Runtime)
# ------------------------------------------------------------------ #
FROM python:3.11-slim
WORKDIR /app

# Lightweight default backend (TF-IDF) — no torch, fast image build.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Default embedding backend. Switch to "sentence_transformers" only if you also
# install requirements-ml.txt (heavy: pulls in PyTorch).
ENV EMBEDDING_BACKEND=tfidf

COPY . .
COPY --from=frontend-build /static/dist ./static/dist

# Build the FAISS index from data/ at image-build time (TF-IDF is fast).
# Safe to no-op if data/ is empty; the app rebuilds on demand otherwise.
RUN python rag_engine.py --rebuild || echo "FAISS index will be built on first request"

EXPOSE 5000
ENV FLASK_APP=app.py
ENV FLASK_DEBUG=false
ENV PORT=5000

CMD ["python", "app.py"]
