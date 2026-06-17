# AWS Setup Notes — Bedrock Agent, Knowledge Base (S3 Vectors), Lambda Tools

Manual steps in AWS Console (not automated by this repo).

---

## 1. Target architecture

```text
S3 clinical documents (data/)
  → Bedrock Knowledge Base (S3 Vectors vector store)
  → Bedrock Agent (RAG + Action Groups)
  → Flask invoke_agent (boto3)
  → React UI
```

**Flask never queries OpenSearch.** Vector storage is **S3 Vectors** behind the Knowledge Base.

If an older KB used **OpenSearch Serverless**, see README **Cost control** section to delete it.

---

## 2. S3 + Knowledge Base (S3 Vectors)

1. Upload clinical documents to S3 under prefix `data/`.
2. **Amazon Bedrock → Knowledge Bases → Create**.
3. Choose **S3** as data source.
4. For vector store, select **S3 Vectors** (preferred) — **not** OpenSearch Serverless.
5. Sync until documents are indexed.
6. Note `BEDROCK_KNOWLEDGE_BASE_ID` and `S3_BUCKET_NAME`.

---

## 3. Bedrock Agent + instructions

1. **Agents → Create agent** (e.g. `PTSD-Companion-Agent`).
2. Foundation model: Amazon Nova or Claude.
3. **Agent instructions** (paste/adapt):

```
You are a calm, supportive digital wellness companion for a PTSD-support demo application.

Language behavior:
- Respond in Hebrew by default.
- If the user explicitly asks for English, answer in English for that response.
- If the user asks to continue in English, continue in English.
- If the user returns to Hebrew, respond in Hebrew again.

Knowledge Base behavior:
- Use the connected Bedrock Knowledge Base as the source of truth for answers based on uploaded clinical documents.
- Do not invent therapist instructions, psychiatrist instructions, medication instructions, diagnoses, treatment plans, or clinical facts.
- If the requested information is not found in the Knowledge Base, clearly say that the information does not appear in the uploaded documents.
- Do not answer clinical-document questions from general knowledge when the Knowledge Base does not contain the answer.

Medical and safety boundaries:
- You are not a doctor, psychiatrist, psychologist, therapist, emergency service, or medical authority.
- You do not replace professional medical, psychiatric, psychological, or emergency care.
- For medication-related questions, summarize only what appears in the uploaded documents and recommend contacting the treating psychiatrist or doctor before making any change.
- Do not recommend changing, starting, stopping, increasing, or decreasing medication unless this appears explicitly in the uploaded documents, and even then present it only as a document summary, not as personal medical advice.
- If the user expresses immediate danger, self-harm risk, or emergency, encourage contacting local emergency services or trusted human support immediately.

Tool behavior:
- Use the Knowledge Base for document-based questions.
- Use the weekly wellness snapshot tool when the user asks for a weekly summary or wellness overview, if configured.
- Use the stress check-in classifier tool when the user feels stressed, overwhelmed, confused, overloaded, dysregulated, unsafe, or asks what to do right now.
- The stress check-in classifier does not diagnose and does not provide medical care. It only returns safe routing guidance.
- If the classifier returns "low", answer normally from the Knowledge Base.
- If the classifier returns "medium", answer shortly and calmly using the Knowledge Base.
- If the classifier returns "high", start with one grounding step, then provide only the most relevant document-based guidance.
- If the classifier returns "crisis", do not treat it as a normal RAG question. Encourage immediate human support, trusted support, professional support, or local emergency services. Keep the response short and direct.
```

4. **Add Knowledge Base** — attach your S3 Vectors-backed KB.
5. Save → `BEDROCK_AGENT_ID`.

---

## 4. Lambda Action Groups

### Tool 1: Weekly Wellness Snapshot (`weekly` Action Group)

1. Create Lambda `ptsd-weekly-wellness-snapshot` from `aws/lambda/weekly_wellness_snapshot/lambda_function.py`.
2. Runtime: Python 3.14 (or latest).
3. Test with `test_event.json`.
4. Add Action Group **`weekly`** using `action_group_weekly_snapshot_schema.json` (path `/weekly`, operationId `snapshot`).

**Flask app behavior:** When the user asks for a weekly summary in `/api/chat`, Flask automatically
collects tasks from `tasks.json` and recent messages from SQLite, then appends a hidden
`[APP_CONTEXT_FOR_WEEKLY_SNAPSHOT]` block to the Agent prompt. The Agent should use this context
and call the `weekly` tool — **not** ask the user to manually list completed/open tasks when
app context is provided. If no task data exists, the Agent should say so and reflect on recent chat context.

### Tool 2: Stress Check-in Classifier (required)

1. Create Lambda `ptsd-stress-check-in-classifier`:
   - Runtime: **Python 3.14**
   - Code: `aws/lambda/stress_check_in_classifier/lambda_function.py`
   - If Console does not show Architecture field, keep default.
2. Test with:
   - `test_event_low.json`
   - `test_event_medium.json`
   - `test_event_high.json`
   - `test_event_crisis.json`
3. Add Action Group:
   - Name: `stress_check_in_classifier`
   - Schema: `action_group_stress_check_in_classifier_schema.json`
4. Lambda permission for Bedrock:

```bash
aws lambda add-permission \
  --function-name ptsd-stress-check-in-classifier \
  --statement-id AllowBedrockAgentInvokeStressCheckInClassifier \
  --action lambda:InvokeFunction \
  --principal bedrock.amazonaws.com \
  --source-arn arn:aws:bedrock:us-east-1:<ACCOUNT_ID>:agent/<BEDROCK_AGENT_ID> \
  --region us-east-1
```

Repeat for weekly snapshot Lambda. See `aws/iam/bedrock_agent_lambda_permission.md`.

### Tool 3: Emergency Contact Voice Call (optional / future)

Code exists at `aws/lambda/emergency_contact_voice_call/` for Amazon Connect.
**Not required** if Connect is unavailable. Do not block submission on this tool.

---

## 5. Agent Alias + Flask .env

1. Agent → **Prepare** → create **Alias** (e.g. `prod`).
2. Note alias ID → `BEDROCK_AGENT_ALIAS_ID`.

```env
BEDROCK_AGENT_ID=...
BEDROCK_AGENT_ALIAS_ID=...
BEDROCK_KNOWLEDGE_BASE_ID=...
S3_BUCKET_NAME=...
S3_PREFIX=data/
STRESS_CHECK_IN_LAMBDA_NAME=ptsd-stress-check-in-classifier
WEEKLY_SNAPSHOT_LAMBDA_NAME=ptsd-weekly-wellness-snapshot
ENABLE_LEGACY_FAISS=false
AWS_REGION=us-east-1
```

---

## 6. EC2 IAM role

- `ec2_invoke_agent_policy.json`
- `ec2_invoke_lambda_tools_policy.json` (demo endpoints only)
- Optional: `s3:ListBucket` for document list UI

---

## 7. Cost control — delete legacy OpenSearch Serverless

If an **old** Knowledge Base used OpenSearch Serverless and is billing daily:

1. **Do NOT delete** the S3 bucket with clinical documents.
2. **Do NOT delete** the new S3 Vectors-backed KB if working.
3. Bedrock → Knowledge Bases → delete old OpenSearch-backed KB.
4. OpenSearch Service → Serverless → Collections → Delete collection.
5. Deletion is **irreversible**.
6. Check Billing / Cost Explorer.

```bash
aws opensearchserverless list-collections --region us-east-1
aws opensearchserverless delete-collection --id <COLLECTION_ID> --region us-east-1
```

---

## 8. Cleanup after grading

1. Terminate EC2.
2. Delete Bedrock Agent.
3. Delete Knowledge Base (project-only).
4. Delete Lambda functions.
5. Delete legacy OpenSearch collection (if any).
6. Release Connect resources (only if created).
7. Check AWS Billing.

---

## 9. Screenshots

See README **Submission screenshot checklist**.
