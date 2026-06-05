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

# Build deps occasionally needed by faiss / sentence-transformers wheels.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the embedding model at build time so the container starts fast
# and works without internet access at runtime (e.g. on a locked-down EC2).
ARG EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
ENV EMBEDDING_MODEL=${EMBEDDING_MODEL}
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('${EMBEDDING_MODEL}')"

COPY . .
COPY --from=frontend-build /static/dist ./static/dist

# Build the FAISS index from data/ at image build time (optional but convenient).
# Safe to fail if data/ is empty; the app rebuilds on first request otherwise.
RUN python rag_engine.py --rebuild || echo "FAISS index will be built on first request"

EXPOSE 5000
ENV FLASK_APP=app.py
ENV FLASK_DEBUG=false
ENV PORT=5000

CMD ["python", "app.py"]
