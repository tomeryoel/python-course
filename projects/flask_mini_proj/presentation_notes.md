# PTSD Companion — Presentation Notes (5–7 minutes)

## Slide 1 — About Me
- Name, background, why this project matters personally/professionally
- One sentence: helping reduce cognitive load for PTSD recovery

## Slide 2 — Project Overview
- PTSD Companion = external brain for therapist instructions, tasks, grounding
- Hebrew-first, calm tone, safety disclaimers
- Based only on uploaded clinical documents (S3)

## Slide 3 — Technologies Used
- **AWS:** S3, Bedrock Knowledge Base, Bedrock Agent, Lambda, Amazon Connect (demo)
- **Backend:** Flask, boto3, SQLite chat memory
- **Frontend:** React, Vite, TailwindCSS
- **DevOps:** Docker, EC2, GitHub

## Slide 4 — System Architecture
```text
User → React → Flask → invoke_agent → Bedrock Agent
                              ↓              ↓
                         SQLite memory   Knowledge Base ← S3
                                              ↓
                                    Lambda tools (weekly snapshot, emergency call)
```

Key points:
- Agent orchestrates RAG — Flask does not call KB or Lambda directly in the main chat path
- MCP-style tools = Bedrock Agent Action Groups backed by Lambda

## Slide 5 — Live Demo (script)
1. Open EC2 public URL (or localhost)
2. Ask Hebrew question → grounded answer from KB documents (RAG)
3. Ask follow-up referring to previous question → memory demo
4. Open previous conversation in sidebar
5. Home → **Generate Weekly Snapshot** → show JSON summary
6. **Contact Emergency Support** → show confirmation modal (do NOT call unless intended)
7. Documents page → show Agent + KB + S3 status

## Slide 6 — Challenges and Next Steps
**Challenges:**
- Aligning architecture with instructor requirements (Agent vs direct KB/FAISS)
- Bedrock Agent Action Group setup (manual AWS Console)
- Amazon Connect configuration for outbound demo calls
- Chat memory + Agent sessionId coordination

**Next steps:**
- Production hardening (auth, rate limits)
- Richer Agent traces in UI
- Optional multilingual documents

## Slide 7 — Q&A
- Emphasize: not medical advice, emergency feature is demo-only
- OpenSearch behind KB is AWS-managed — we don't query it from Flask
