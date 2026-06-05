# PTSD Companion

A personal digital assistant for people coping with PTSD-related memory difficulties,
cognitive overload, and stress. It acts as an **external brain**: it remembers therapist
and psychiatrist instructions, surfaces practical next steps, tracks daily therapeutic
tasks, and answers questions in calm, grounding Hebrew — **based only on the uploaded
clinical documents**.

> **Medical disclaimer:** This system does not replace medical, psychiatric, or
> psychological advice. It only presents information based on the uploaded documents.

---

## 1. Project overview

- **Backend:** Flask + boto3
- **Frontend:** React (Vite) + TailwindCSS, full RTL Hebrew
- **Retrieval (runtime):** **local FAISS** vector search
- **Embeddings (runtime):** **TF-IDF by default** (lightweight, no torch); optional
  sentence-transformers backend
- **Generation (runtime):** **Amazon Bedrock Runtime** (`converse`)
- **Bedrock Knowledge Base:** kept in AWS **for assignment/demo/screenshots only** —
  no longer used by the live application

## 2. Architecture

```text
User question
  → Flask backend (/api/chat)
  → local embedding of the question (TF-IDF default, sentence-transformers optional)
  → local FAISS cosine similarity search
  → top-k relevant chunks
  → prompt construction (context + open tasks + safety rules)
  → Amazon Bedrock Runtime `converse` (boto3)
  → AI answer → React frontend
```

### Embedding backends

Selected via `EMBEDDING_BACKEND`:

| Value | Deps | Notes |
|-------|------|-------|
| `tfidf` (default) | `scikit-learn` (in `requirements.txt`) | Lightweight, offline, Windows/CI/Docker friendly. Lexical retrieval. |
| `sentence_transformers` | `requirements-ml.txt` (PyTorch) | Higher-quality multilingual semantic retrieval. Heavy download. |

To use the transformer backend: `pip install -r requirements-ml.txt` then set
`EMBEDDING_BACKEND=sentence_transformers` and run `python rag_engine.py --rebuild`.

## 3. Bedrock Runtime (generation)

Final answers are generated with `bedrock-runtime.converse` via boto3. The engine tries
an ordered list of on-demand models (Amazon **Nova** first, then Claude 3 fallbacks) so the
app keeps working without an AWS Marketplace subscription. Configure with `BEDROCK_MODEL_ID`
and optional `BEDROCK_MODEL_FALLBACKS`.

## 4. Bedrock Knowledge Base still exists (demo only)

The instructor requirements include creating a Bedrock Knowledge Base and showing
screenshots. The KB resource may remain in AWS for that purpose. To demonstrate it:

```bash
python bedrock_kb_demo.py "מה ההמלצות לגבי שינה?"
```

`bedrock_kb_demo.py` is **standalone and never imported by the app runtime**.

## 5. Runtime retrieval uses local FAISS

At runtime the app embeds the question locally and searches a local FAISS index built from
the documents in `data/`. No Knowledge Base call and no OpenSearch query happen during
normal operation.

## 6. Why OpenSearch costs were removed

The previous flow used `bedrock-agent-runtime.retrieve()`, backed by a Bedrock Knowledge
Base on **OpenSearch Serverless**. OpenSearch Serverless bills continuously (per OCU/hour)
**even when idle** — wasteful for a student demo. Local FAISS retrieval is free and
in-memory, so the only pay-per-use AWS cost left is Bedrock Runtime generation.

## 7. How FAISS retrieval works

1. `load_documents()` reads TXT/PDF/DOCX from `data/` (including `data/uploads/`).
2. `chunk_documents()` splits text into overlapping, paragraph-aware chunks.
3. The embedding model encodes chunks into normalized vectors.
4. `build_faiss_index()` creates an `IndexFlatIP` index (cosine similarity).
5. Artifacts are persisted (`faiss_index.bin`, `chunks.npy`, `embeddings.npy`,
   `faiss_meta.json`). They are auto-loaded next time and **rebuilt only when the data
   or embedding model changes** (validated via a data fingerprint stored in the meta file).
6. `retrieve_chunks()` embeds the query and returns the top-k chunks.

## 8. Run locally

```bash
# 1) Backend
python -m venv .venv
.venv\Scripts\activate          # Windows  (source .venv/bin/activate on macOS/Linux)
pip install -r requirements.txt

cp .env.example .env            # then fill AWS_* and BEDROCK_MODEL_ID

# 2) Frontend (build once into static/dist)
cd frontend
npm install
npm run build
cd ..

# 3) Start
python app.py                   # http://127.0.0.1:5000
```

Frontend dev mode with hot reload (proxies API to Flask on :5000):

```bash
cd frontend && npm run dev      # http://127.0.0.1:5173
```

## 9. Rebuild the FAISS index

```bash
python rag_engine.py --rebuild     # rebuild from data/
python rag_engine.py --status      # print index status as JSON
```

Run rebuild after adding documents. The app also rebuilds automatically when it detects that
`data/` changed, and the **Documents page** has a "בנה אינדקס מחדש" (rebuild) button that calls
`POST /api/index/rebuild`.

### Index / document API

| Endpoint | Purpose |
|----------|---------|
| `GET /api/index/status` | index_exists, chunk_count, document_count, embedding_backend, last_built_at, rebuild_needed, errors |
| `POST /api/index/rebuild` | rebuild FAISS from current `data/` |
| `GET /api/documents` | real files in `data/` + per-file indexed/chunk_count + index status |
| `POST /api/documents/upload` | upload PDF/DOCX/TXT into `data/uploads/`, then rebuild |

## 10. Add new documents

- Drop TXT/PDF/DOCX files into `data/` (or upload via the Documents page → `data/uploads/`).
- Run `python rag_engine.py --rebuild` (or restart the app).
- New content becomes part of the patient's evolving local knowledge base.

## 11. Docker

```bash
docker build -t ptsd-companion .
docker run -p 5000:5000 --env-file .env ptsd-companion
```

The image builds the React frontend, installs the lightweight Python deps (no torch with the
default TF-IDF backend), and builds the FAISS index from `data/` at image-build time.

## 12. EC2 deployment

```bash
# On the EC2 instance (Amazon Linux/Ubuntu) with Docker installed:
git clone <your-repo> && cd flask_mini_proj
cp .env.example .env && nano .env          # fill AWS_* + BEDROCK_MODEL_ID (never commit)

docker build -t ptsd-companion .
docker run -d -p 5000:5000 --env-file .env --name ptsd-companion ptsd-companion
docker ps                                  # confirm the container is running
```

1. Open port **5000** in the EC2 security group (inbound, your IP or 0.0.0.0/0 for demo).
2. Browse to `http://<EC2_PUBLIC_IP>:5000` and take screenshots.
3. Local FAISS loads into the instance's memory; Bedrock Runtime is called from EC2.
   **No OpenSearch and no KB retrieval are required at runtime.**

### Submission Screenshot Checklist

Capture these for the report:

1. **Bedrock Knowledge Base** screen (the KB you created in AWS Console).
2. **Bedrock data source / sync status** screen (data source + last sync).
3. **Flask app running locally** in the browser (`http://127.0.0.1:5000`).
4. **EC2 instance details** screen (instance ID, public IPv4/DNS, state running).
5. **Public app page via EC2** (`http://<EC2_PUBLIC_IP>:5000` in the browser).
6. **Docker container running on EC2** (`docker ps` output in the SSH terminal).
7. **Successful Q&A example** — a Hebrew question with a grounded answer + sources.
8. **Cleanup proof** — note/screenshot listing deleted AWS resources (KB, OpenSearch
   collection, EC2 instance, S3 buckets).

### Quick command recap

```bash
# FAISS index
python rag_engine.py --rebuild
python rag_engine.py --status

# Local run
pip install -r requirements.txt
cd frontend && npm install && npm run build && cd ..
python app.py

# Docker / EC2
docker build -t ptsd-companion .
docker run -d -p 5000:5000 --env-file .env --name ptsd-companion ptsd-companion
docker ps
```

## 13. AWS requirements

- IAM credentials with **Bedrock Runtime** access (`bedrock:InvokeModel` / `converse`).
- A Bedrock **model access** grant (Amazon Nova recommended).
- (Optional, demo only) a Bedrock Knowledge Base for screenshots.

## 14. Cost optimization

| Service | Before | After |
|---------|--------|-------|
| OpenSearch Serverless | Always-on hourly billing | **Removed from runtime** |
| Bedrock KB retrieval | Per request | **Removed from runtime** |
| Bedrock Runtime | Per request | Per request (kept) |
| FAISS retrieval | — | Local, free |

## 15. Cleanup (after grading)

To avoid charges, delete:
- The EC2 instance (and any Elastic IP).
- The Bedrock Knowledge Base **and its OpenSearch Serverless collection**.
- Any temporary S3 buckets used for KB ingestion.

## 16. Security notes

- Secrets come only from environment variables / `.env` (which is git-ignored).
- `.env.example` documents required variables with empty values.
- Flask debug is off by default (`FLASK_DEBUG=false`).
- No AWS keys in code or in the Docker image.

## 17. Do not commit secrets

Never commit `.env`, real AWS keys, `chat_memory.db`, `node_modules/`, build artifacts, or
generated FAISS files. See `.gitignore`.

---

## Project structure

```text
app.py               # Flask API + serves React build
rag_engine.py        # Local FAISS retrieval + Bedrock Runtime generation
response_utils.py    # Locale detection + multilingual disclaimers + response formatting
documents.py         # Upload handling + document registry (future KB ingestion)
tasks.py / tasks.json# Therapeutic task management
memory.py            # SQLite conversation memory
bedrock_kb_demo.py   # Standalone KB demo (screenshots only, not used at runtime)
data/                # Source clinical documents (+ data/uploads/)
frontend/            # React + Vite + Tailwind
static/dist/         # Built frontend (served by Flask)
tests/               # pytest (mocked AWS, real FAISS pipeline test)
Dockerfile
```

---
---

# PTSD Companion (עברית)

עוזר דיגיטלי אישי למתמודדים עם PTSD — קשיי זיכרון, עומס קוגניטיבי וסטרס. המערכת משמשת
**מוח חיצוני**: זוכרת הנחיות מהמטפלים, מציגה צעדים מעשיים, עוקבת אחר משימות יומיות, ועונה
בעברית רגועה — **על בסיס המסמכים שהועלו בלבד**.

> **הצהרה רפואית:** המערכת אינה מחליפה ייעוץ רפואי, פסיכיאטרי או פסיכולוגי. היא מציגה מידע
> על בסיס המסמכים שהועלו בלבד.

## 1. סקירה
- **שרת:** Flask + boto3
- **צד לקוח:** React (Vite) + TailwindCSS, תמיכת RTL מלאה
- **אחזור (זמן ריצה):** **FAISS מקומי**
- **Embeddings (זמן ריצה):** **TF-IDF כברירת מחדל** (קל, ללא torch); אופציונלי sentence-transformers
- **יצירת תשובה (זמן ריצה):** **Amazon Bedrock Runtime**
- **Bedrock Knowledge Base:** נשמר ב-AWS **לצורכי המטלה/הדגמה/צילומי מסך בלבד** — לא בשימוש בזמן ריצה

## 2. ארכיטקטורה
```text
שאלת משתמש
  → שרת Flask (/api/chat)
  → embedding מקומי של השאלה (sentence-transformers)
  → חיפוש דמיון FAISS מקומי
  → קטעים רלוונטיים (top-k)
  → בניית פרומפט (הקשר + משימות פתוחות + כללי בטיחות)
  → Amazon Bedrock Runtime converse (boto3)
  → תשובה → ממשק React
```

## 3. Bedrock Runtime
התשובות נוצרות עם `bedrock-runtime.converse`. המנוע מנסה רשימת מודלים לפי סדר (Amazon **Nova**
תחילה, ואז Claude 3 כגיבוי) כדי לעבוד ללא מנוי AWS Marketplace.

## 4. ה-Knowledge Base עדיין קיים (הדגמה בלבד)
דרישות הקורס כוללות יצירת Knowledge Base וצילומי מסך. ה-KB יכול להישאר ב-AWS לצורך זה.
להדגמה: `python bedrock_kb_demo.py "מה ההמלצות לגבי שינה?"`. הקובץ עצמאי ואינו חלק מזמן הריצה.

## 5. אחזור בזמן ריצה — FAISS מקומי
בזמן ריצה המערכת מבצעת embedding לשאלה מקומית ומחפשת באינדקס FAISS שנבנה מהמסמכים שב-`data/`.
אין קריאה ל-Knowledge Base ואין שאילתת OpenSearch בפעולה רגילה.

## 6. למה הוסרו עלויות OpenSearch
הזרימה הקודמת השתמשה ב-`retrieve()` שמבוסס על Knowledge Base מעל **OpenSearch Serverless**,
שמחייב בתשלום שעתי **גם במנוחה**. FAISS מקומי הוא חינמי ובזיכרון, כך שהעלות היחידה שנותרה היא
קריאות Bedrock Runtime לפי שימוש.

## 7. איך FAISS עובד
טעינת מסמכים (TXT/PDF/DOCX) → חלוקה לקטעים חופפים → embedding מקומי → אינדקס `IndexFlatIP`
(קוסינוס) → שמירה לקבצים (`faiss_index.bin`, `chunks.npy`, `embeddings.npy`, `faiss_meta.json`)
→ טעינה אוטומטית, ובנייה מחדש רק כשהנתונים או מודל ה-embedding משתנים.

## 8. הרצה מקומית
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # מלא AWS_* ו-BEDROCK_MODEL_ID

cd frontend && npm install && npm run build && cd ..
python app.py                   # http://127.0.0.1:5000
```

## 9. בנייה מחדש של אינדקס FAISS
```bash
python rag_engine.py --rebuild
```

## 10. הוספת מסמכים
הוסף קבצי TXT/PDF/DOCX ל-`data/` (או דרך עמוד "מסמכים" → `data/uploads/`), והרץ
`python rag_engine.py --rebuild`. התוכן החדש מצטרף לבסיס הידע המקומי המתעדכן.

## 11. Docker
```bash
docker build -t ptsd-companion .
docker run -p 5000:5000 --env-file .env ptsd-companion
```

## 12. פריסה ל-EC2
הפעל EC2, התקן Docker, העתק פרויקט, צור `.env`, בנה והרץ קונטיינר, פתח פורט 5000, בדוק
ב-IP הציבורי, צלם מסכים. FAISS נטען לזיכרון; Bedrock Runtime נקרא מה-EC2; אין צורך ב-OpenSearch.

## 13. דרישות AWS
הרשאות IAM ל-Bedrock Runtime (`bedrock:InvokeModel`/`converse`), הרשאת גישה למודל (Nova מומלץ),
ואופציונלית Knowledge Base להדגמה.

## 14. אופטימיזציית עלות
OpenSearch Serverless ו-KB retrieval הוסרו מזמן הריצה. נותרה רק עלות Bedrock Runtime לפי שימוש.

## 15. ניקוי (אחרי הגשה)
מחק את ה-EC2, את ה-Knowledge Base **ואת אוסף ה-OpenSearch Serverless**, וכל bucket זמני ב-S3.

## 16. אבטחה
סודות מגיעים רק ממשתני סביבה / `.env` (ב-gitignore). אין מפתחות בקוד או ב-Docker image.
`FLASK_DEBUG=false` כברירת מחדל.

## 17. אין להעלות סודות ל-git
לעולם אל תעלה `.env`, מפתחות AWS, `chat_memory.db`, `node_modules/` או קבצי FAISS שנוצרים.
```
