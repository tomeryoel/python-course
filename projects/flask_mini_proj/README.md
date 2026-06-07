# PTSD Companion

Personal digital assistant for PTSD-related memory difficulties, cognitive overload, and stress.
Acts as an **external brain** grounded in clinical documents stored in **Amazon S3**, indexed by a
**Bedrock Knowledge Base**, orchestrated by a **Bedrock Agent**, and accessed through **Flask +
boto3 `invoke_agent`**.

> **Medical disclaimer:** This system does not replace medical care. The demo emergency-contact
> feature is for educational purposes only and is not an emergency service (101/100).

---

## Final runtime architecture

```text
Documents in S3 (data/)
  → Bedrock Knowledge Base (sync/index)
  → Bedrock Agent (RAG + Lambda Action Groups)
  → Flask backend (boto3 bedrock-agent-runtime.invoke_agent)
  → React UI
  → Docker → EC2 public demo → cleanup
```

**RAG source of truth:** S3 → Bedrock Knowledge Base → Bedrock Agent  
**NOT used for /api/chat:** local FAISS (legacy optional only, `ENABLE_LEGACY_FAISS=true`)

### MCP-style tools (Lambda Action Groups)

| Tool | Lambda | Purpose |
|------|--------|---------|
| `weekly_wellness_snapshot` | `ptsd-weekly-wellness-snapshot` | Weekly summary from tasks/topics |
| `emergency_contact_voice_call` | `ptsd-emergency-contact-voice-call` | Amazon Connect outbound call (requires explicit confirmation) |

Implemented as **Bedrock Agent Action Groups** (MCP-like: structured input/output, external functions).
Optional direct demo endpoints: `POST /api/tools/weekly-snapshot`, `POST /api/tools/emergency-call`.

---

## Environment variables

Copy `.env.example` → `.env` (never commit `.env`):

| Variable | Purpose |
|----------|---------|
| `BEDROCK_AGENT_ID` | Bedrock Agent ID (**required for chat**) |
| `BEDROCK_AGENT_ALIAS_ID` | Agent alias ID (**required for chat**) |
| `BEDROCK_KNOWLEDGE_BASE_ID` | Knowledge Base ID (documentation/status) |
| `S3_BUCKET_NAME` | S3 bucket with clinical documents |
| `S3_PREFIX` | Prefix, e.g. `data/` |
| `WEEKLY_SNAPSHOT_LAMBDA_NAME` | Weekly snapshot Lambda |
| `EMERGENCY_CALL_LAMBDA_NAME` | Emergency call Lambda |
| `EMERGENCY_CONTACT_PHONE` | E.164 default contact |
| `AWS_REGION` | e.g. `us-east-1` |

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

Frontend dev: `cd frontend && npm run dev` (proxies API to :5000)

---

## Docker

```bash
docker build -t ptsd-companion .
docker run -d -p 5000:5000 --env-file .env --name ptsd-companion ptsd-companion
docker ps
```

No FAISS rebuild in Docker by default. Runtime depends on AWS credentials/IAM role + Bedrock Agent.

---

## EC2 deployment

```bash
git clone <repo> && cd flask_mini_proj
cp .env.example .env && nano .env
docker build -t ptsd-companion .
docker run -d -p 5000:5000 --env-file .env --name ptsd-companion ptsd-companion
docker ps
```

1. Attach IAM role with `bedrock:InvokeAgent` (+ optional `lambda:InvokeFunction`, `s3:ListBucket`).
2. Open port **5000** in security group.
3. Browse `http://<EC2_PUBLIC_IP>:5000`.

See `aws/bedrock_agent/setup_notes.md` for Agent, KB, Lambda, and Connect setup.

---

## API highlights

| Endpoint | Description |
|----------|-------------|
| `POST /api/chat` | Chat via **Bedrock Agent** (`message`, optional `conversation_id`) |
| `GET/POST /api/conversations` | List/create conversations (SQLite memory) |
| `GET /api/knowledge-base/status` | KB + Agent + S3 status |
| `GET /api/documents` | S3-backed document list + architecture status |
| `POST /api/tools/weekly-snapshot` | Demo: invoke weekly snapshot Lambda |
| `POST /api/tools/emergency-call` | Demo: emergency call (requires `confirmed: true`) |

---

## Manual AWS setup required

This repo provides code, schemas, IAM examples, and setup notes — **not** automatic AWS provisioning:

1. S3 bucket + documents (you already have 6 indexed)
2. Bedrock Knowledge Base connected to S3
3. Bedrock Agent connected to KB
4. Two Lambda functions + Action Groups
5. Amazon Connect (for emergency call demo)
6. Agent alias + `.env` values

Full steps: [`aws/bedrock_agent/setup_notes.md`](aws/bedrock_agent/setup_notes.md)

---

## Legacy local FAISS (optional)

Previous architecture used local FAISS + Bedrock Runtime. Kept for experiments only:

```bash
pip install -r requirements-legacy-faiss.txt
set ENABLE_LEGACY_FAISS=true
python rag_engine.py --rebuild
```

**Not used by `/api/chat` in the final architecture.**

---

## Submission screenshot checklist

### Core project flow
1. Bedrock Knowledge Base screen
2. S3 data source / sync status (6 documents indexed)
3. Bedrock Agent screen
4. Agent connected to Knowledge Base
5. Agent Action Groups / Lambda tools
6. Flask/React app in browser (local)
7. EC2 instance details
8. Docker container running (`docker ps`)
9. Public EC2 app page
10. Successful Q&A showing RAG
11. Cleanup notes

### Instructor requirements
12. Lambda list (both functions)
13. Weekly Snapshot Lambda test output
14. Emergency Call Lambda test / Connect setup
15. Amazon Connect Contact Flow (if created)
16. Chat memory / previous conversations UI
17. Weekly Snapshot UI card (Home)
18. Emergency Contact confirmation modal
19. Agent trace / CloudWatch showing tool invocation (if available)
20. README architecture section

---

## Safety — emergency contact demo

> This project includes a demo emergency-contact feature that can trigger an automated support call
> to a predefined contact after **explicit confirmation**. It is intended for educational
> demonstration only and is **not** a replacement for emergency services, medical care, or
> professional mental-health support.

---

## Cleanup (after grading)

- Terminate EC2
- Delete Bedrock Agent, Knowledge Base, OpenSearch collection (if created for KB)
- Delete Lambda functions
- Release Amazon Connect number / delete instance (if demo-only)
- Empty/delete S3 bucket if project-only
- Check AWS Billing / Cost Explorer

---

## Project structure

```text
app.py                 # Flask API (Agent-centric chat)
agent_engine.py        # boto3 invoke_agent (primary chat path)
chat_store.py          # SQLite conversations + messages
kb_status.py           # S3 + KB status
tools.py               # Optional direct Lambda demo endpoints
bedrock_llm.py         # Bedrock Runtime for task extraction only
rag_engine.py          # LEGACY local FAISS (optional)
aws/lambda/            # Lambda tool implementations
aws/bedrock_agent/     # Action Group schemas + setup notes
aws/iam/               # Example IAM policies
frontend/              # React/Vite UI
presentation_notes.md  # 5–7 min presentation outline
```

---

## Hebrew summary (עברית)

**זרימת ריצה:** מסמכים ב-S3 → Bedrock Knowledge Base → Bedrock Agent → Flask (`invoke_agent`) → React → Docker → EC2.

**צ'אט:** `/api/chat` משתמש ב-Bedrock Agent בלבד — לא FAISS מקומי.

**זיכרון:** SQLite — שיחות קודמות, שאלה אחרונה, המשך שיחה.

**כלים:** שני Lambda Action Groups — סיכום שבועי + שיחת חירום (Connect, עם אישור מפורש).

**הגדרה ידנית ב-AWS:** Agent, KB, Lambda, Connect — ראה `aws/bedrock_agent/setup_notes.md`.

---

## Tests

```bash
pytest -q
```

---

## Presentation

See [`presentation_notes.md`](presentation_notes.md) for a suggested 5–7 minute slide structure.
