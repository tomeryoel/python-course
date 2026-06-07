# AWS Setup Notes — Bedrock Agent, Knowledge Base, Lambda Tools, Amazon Connect

Manual steps required in AWS Console (not automated by this repo).

---

## 1. Architecture overview

```text
S3 (clinical documents)
  → Bedrock Knowledge Base (sync/index)
  → Bedrock Agent (orchestration + RAG + tools)
  → Flask invoke_agent (boto3)
  → React UI
```

OpenSearch Serverless (if created behind the KB) is **AWS-managed vector storage** — do not query it from Flask.

---

## 2. S3 + Knowledge Base (already done in your project)

1. Upload 6 clinical documents to S3 bucket under prefix `data/`.
2. Create Bedrock Knowledge Base with S3 data source.
3. Sync until **6 documents indexed**.
4. Note `BEDROCK_KNOWLEDGE_BASE_ID` and `S3_BUCKET_NAME`.

Screenshot: KB screen + data source sync status.

---

## 3. Create Bedrock Agent

1. AWS Console → **Amazon Bedrock** → **Agents** → **Create agent**.
2. Name: e.g. `PTSD-Companion-Agent`.
3. Select foundation model (Amazon Nova or Claude 3).
4. Instructions (Hebrew-friendly system prompt): calm wellness companion, use KB for RAG only, medication disclaimers, refuse unsafe medical advice.
5. **Add Knowledge Base** — attach your existing KB.
6. Save agent ID → `BEDROCK_AGENT_ID`.

---

## 4. Lambda Action Groups (MCP-style tools)

### Tool 1: Weekly Wellness Snapshot

1. Create Lambda `ptsd-weekly-wellness-snapshot` from `aws/lambda/weekly_wellness_snapshot/lambda_function.py`.
2. Test with `test_event.json`.
3. Add Action Group to Agent using `action_group_weekly_snapshot_schema.json`.
4. Grant Bedrock permission to invoke Lambda (see `aws/iam/bedrock_agent_lambda_permission.md`).

### Tool 2: Emergency Contact Voice Call

1. Create Lambda `ptsd-emergency-contact-voice-call` from `aws/lambda/emergency_contact_voice_call/lambda_function.py`.
2. Set Connect env vars (section 5).
3. Attach IAM policy `lambda_connect_policy.json`.
4. Add Action Group using `action_group_emergency_call_schema.json`.

**Important:** Configure Agent instructions so the emergency tool is **never** called without user confirmation.

---

## 5. Amazon Connect setup

### 5.1 Create instance

1. AWS Console → **Amazon Connect** → **Create instance**.
2. Choose **Store users in Amazon Connect** (simplest for demo).
3. Note **Instance ID** → `CONNECT_INSTANCE_ID`.

### 5.2 Claim phone number

1. In Connect → **Phone numbers** → **Claim**.
2. Choose a number capable of **outbound** calls in your region.
3. Note E.164 format → `CONNECT_SOURCE_PHONE_NUMBER` (e.g. `+972...`).

**Cost warning:** Connect charges per minute for outbound calls + monthly number fee.

### 5.3 Create Contact Flow

1. **Routing** → **Contact flows** → **Create contact flow** → **Outbound whisper flow**.
2. Add **Play prompt** block with text (Hebrew):

   > שלום, זו הודעת תמיכה אוטומטית ממערכת ה-wellness companion. המשתמש שהגדיר אותך כאיש קשר חירום ביקש ליצור איתך קשר. מומלץ ליצור איתו קשר בהקדם ולוודא שהוא בסדר. הודעה זו אינה שירות חירום רפואי.

3. Use attributes from Lambda (`$.Attributes.user_display_name`, etc.) if needed.
4. Publish flow and note **Contact flow ID** → `CONNECT_CONTACT_FLOW_ID`.

### 5.4 Lambda environment

On `ptsd-emergency-contact-voice-call`:

```
CONNECT_INSTANCE_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
CONNECT_CONTACT_FLOW_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
CONNECT_SOURCE_PHONE_NUMBER=+972XXXXXXXXX
EMERGENCY_CONTACT_PHONE=+972XXXXXXXXX
```

### 5.5 Test safely

- Use **your own phone number** as emergency contact.
- Require UI confirmation before triggering.
- This is **not** 101/100 — educational demo only.

---

## 6. Agent Alias + Flask .env

1. In Agent → **Prepare** → create **Alias** (e.g. `prod`).
2. Note alias ID → `BEDROCK_AGENT_ALIAS_ID`.

Flask `.env`:

```env
BEDROCK_AGENT_ID=...
BEDROCK_AGENT_ALIAS_ID=...
BEDROCK_KNOWLEDGE_BASE_ID=...
S3_BUCKET_NAME=...
S3_PREFIX=data/
AWS_REGION=us-east-1
```

---

## 7. EC2 IAM role

Attach to EC2 instance role:

- `ec2_invoke_agent_policy.json`
- `ec2_invoke_lambda_tools_policy.json` (if using direct tool demo endpoints)
- Optional: `s3:ListBucket`, `s3:GetObject` on your bucket

---

## 8. Cleanup

After grading, delete in order:

1. Stop/terminate EC2.
2. Delete Bedrock Agent.
3. Delete Knowledge Base + OpenSearch collection (if created).
4. Delete Lambda functions.
5. Release Connect phone number + delete Connect instance (if demo-only).
6. Empty/delete S3 bucket if project-only.
7. Check **AWS Billing / Cost Explorer**.

---

## 9. Screenshots checklist

See README **Submission Screenshot Checklist** section.
