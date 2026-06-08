# PTSD Companion

Personal digital assistant for PTSD-related memory difficulties, cognitive overload, and stress.
Acts as an **external brain** grounded in clinical documents stored in **Amazon S3**, indexed by a
**Bedrock Knowledge Base** (with **S3 Vectors**), orchestrated by a **Bedrock Agent**, and accessed
through **Flask + boto3 `invoke_agent`**.

> **Medical disclaimer:** This system does not replace medical care, therapy, psychiatry, or
> emergency services. The stress classifier routes responses safely — it does not diagnose.

---

## Final runtime architecture

```text
S3 document bucket (data/)
  → Bedrock Knowledge Base (S3 Vectors vector store)
  → Bedrock Agent (RAG + Lambda Action Groups)
  → Flask backend (boto3 bedrock-agent-runtime.invoke_agent)
  → React UI
  → Docker → EC2 public demo → cleanup
```

**Flask never:**
- queries OpenSearch
- queries S3 for RAG retrieval
- uses local FAISS as the main chat path (`ENABLE_LEGACY_FAISS=false` by default)

**RAG source of truth:** S3 documents → Bedrock Knowledge Base → Bedrock Agent

### MCP-style tools (Lambda Action Groups)

| Tool | Lambda | Purpose |
|------|--------|---------|
| `weekly_wellness_snapshot` | `ptsd-weekly-wellness-snapshot` | Weekly summary from tasks/topics |
| `stress_check_in_classifier` | `ptsd-stress-check-in-classifier` | Classify overload/stress and route Agent response |
| `emergency_contact_voice_call` | `ptsd-emergency-contact-voice-call` | **Optional/future** — Amazon Connect (not required) |

Optional direct demo endpoints: `POST /api/tools/weekly-snapshot`, `POST /api/tools/stress-check-in`.

---

## Environment variables

Copy `.env.example` → `.env` (never commit `.env`):

| Variable | Purpose |
|----------|---------|
| `BEDROCK_AGENT_ID` | Bedrock Agent ID (**required for chat**) |
| `BEDROCK_AGENT_ALIAS_ID` | Agent alias ID (**required for chat**) |
| `BEDROCK_KNOWLEDGE_BASE_ID` | S3 Vectors-backed Knowledge Base ID |
| `S3_BUCKET_NAME` | S3 bucket with clinical documents |
| `S3_PREFIX` | Prefix, e.g. `data/` |
| `WEEKLY_SNAPSHOT_LAMBDA_NAME` | Weekly snapshot Lambda |
| `STRESS_CHECK_IN_LAMBDA_NAME` | Stress classifier Lambda |
| `ENABLE_LEGACY_FAISS` | Must stay `false` for target architecture |

---

## Run locally

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
copy .env.example .env          # fill Agent ID, Alias, S3, AWS creds

cd frontend && npm install && npm run build && cd ..
python app.py                   # http://127.0.0.1:5000
```

---

## Docker

```bash
docker build -t ptsd-companion .
docker run -d -p 5000:5000 --env-file .env --name ptsd-companion ptsd-companion
```

---

## EC2 deployment

```bash
git clone <repo> && cd flask_mini_proj
cp .env.example .env && nano .env
docker build -t ptsd-companion .
docker run -d -p 5000:5000 --env-file .env --name ptsd-companion ptsd-companion
```

Attach IAM role with `bedrock:InvokeAgent`. Open port **5000**. See `aws/bedrock_agent/setup_notes.md`.

---

## API highlights

| Endpoint | Description |
|----------|-------------|
| `POST /api/chat` | Chat via **Bedrock Agent** |
| `GET/POST /api/conversations` | SQLite chat memory |
| `GET /api/knowledge-base/status` | KB + Agent + S3 status |
| `POST /api/tools/stress-check-in` | Demo: stress classifier Lambda |
| `POST /api/tools/weekly-snapshot` | Demo: weekly snapshot Lambda |

---

## Cost control — OpenSearch Serverless (legacy cleanup)

**OpenSearch Serverless is NOT part of the intended architecture.**

If an earlier Knowledge Base setup created an OpenSearch Serverless collection, it may incur
high daily costs. For urgent cost control:

1. **Do NOT delete** the normal S3 bucket with your clinical documents.
2. **Do NOT delete** a new S3 Vectors-backed Knowledge Base if already working.
3. Delete the **old** OpenSearch-backed Knowledge Base if no longer needed.
4. Delete the OpenSearch Serverless collection (irreversible — removes indexes/data).
5. Check **AWS Billing / Cost Explorer**.

### AWS Console cleanup

**Amazon Bedrock → Knowledge Bases**
- Identify any old KB that used OpenSearch Serverless
- Delete/detach if no longer needed

**Amazon OpenSearch Service → Serverless → Collections**
- Select the expensive old collection → **Delete** → Confirm

### AWS CLI (placeholders)

```bash
aws opensearchserverless list-collections --region us-east-1

aws opensearchserverless delete-collection \
  --id <COLLECTION_ID> \
  --region us-east-1
```

**Do NOT delete the S3 source document bucket.**

---

## Manual AWS setup required

1. S3 bucket + documents under `data/`
2. Bedrock Knowledge Base with **S3 Vectors** (not OpenSearch Serverless)
3. Sync/index documents
4. Bedrock Agent connected to KB
5. Deploy Lambdas + Action Groups (weekly snapshot + stress classifier)
6. Agent alias + `.env` values

Full steps: [`aws/bedrock_agent/setup_notes.md`](aws/bedrock_agent/setup_notes.md)

---

## Submission screenshot checklist

### AWS (required)
1. S3 bucket with `data/` clinical documents
2. Bedrock Knowledge Base synced/indexed
3. KB using **S3 Vectors** (not OpenSearch), if visible in Console
4. Bedrock Agent details
5. Agent connected to Knowledge Base
6. Action Group: `stress_check_in_classifier`
7. Lambda list showing `ptsd-stress-check-in-classifier`
8. Lambda test outputs: low / medium / high / crisis
9. EC2 instance + Docker container running
10. AWS Billing / Cost Explorer after OpenSearch cleanup (if applicable)

### Application (required)
11. Chat page + previous conversations sidebar
12. Successful RAG answer from uploaded documents
13. Stress/high overload scenario in chat or classifier demo
14. Documents/status page (KB + Agent)
15. Weekly Snapshot card (if configured)

### Optional / future
- Amazon Connect screenshots (only if service becomes available)

---

## Cleanup (after grading)

- Terminate EC2
- Delete Bedrock Agent
- Delete Knowledge Base (only project-specific KBs)
- Delete Lambda functions
- Delete **legacy** OpenSearch Serverless collection (if still exists)
- **Keep or empty** S3 document bucket as you prefer
- Check AWS Billing

---

## Project structure

```text
agent_engine.py        # invoke_agent (primary chat)
chat_store.py          # SQLite memory
kb_status.py           # KB/S3 status (no OpenSearch queries)
tools.py               # Optional Lambda demo endpoints
aws/lambda/stress_check_in_classifier/
aws/bedrock_agent/     # Schemas + setup notes
rag_engine.py          # LEGACY FAISS (optional, disabled by default)
```

---

## Hebrew summary (עברית)

**זרימה:** S3 → Bedrock KB (S3 Vectors) → Bedrock Agent → Flask (`invoke_agent`) → React.

**כלים:** סיכום שבועי + מסווג עומס/סטרס. Connect — אופציונלי בלבד.

**OpenSearch:** לא חלק מהארכיטקטורה — למחיקה לשליטת עלויות אם נוצר בעבר.

---

## Tests

```bash
pytest -q
```

See [`presentation_notes.md`](presentation_notes.md) for presentation outline.
