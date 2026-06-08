# PTSD Companion — Presentation Notes (5–7 minutes)

## Slide 1 — About Me
- Personal motivation: reducing cognitive load for PTSD recovery
- External brain for therapist/psychiatrist instructions

## Slide 2 — Project Overview
- Hebrew-first wellness companion
- Answers only from uploaded clinical documents
- Safety boundaries and disclaimers

## Slide 3 — Technologies
- AWS: S3, Bedrock KB (**S3 Vectors**), Bedrock Agent, Lambda
- Flask + boto3 `invoke_agent`, SQLite memory
- React, Docker, EC2

## Slide 4 — System Architecture

```text
User → React → Flask → invoke_agent → Bedrock Agent
                              ↓              ↓
                         SQLite memory   Knowledge Base (S3 Vectors) ← S3 data/
                                              ↓
                              Lambda tools (weekly snapshot, stress classifier)
```

- Flask does **not** query OpenSearch or S3 for RAG
- Agent orchestrates KB retrieval and tools

## Slide 5 — Live Demo
1. Open EC2 or localhost
2. Hebrew RAG question from uploaded documents
3. Follow-up question (memory)
4. Previous conversations sidebar
5. Stress/overload scenario → classifier routing
6. Weekly Snapshot demo
7. Documents page — KB + Agent status

## Slide 6 — Challenges & Next Steps
- Migrating from OpenSearch Serverless to S3 Vectors (cost control)
- Bedrock Agent Action Group manual setup
- Amazon Connect unavailable — replaced stress classifier as required tool
- Coordinating Agent sessionId + SQLite memory

## Slide 7 — Q&A
- Not medical advice; crisis classifier routes to human/emergency support
- OpenSearch cleanup for billing — not part of target architecture
