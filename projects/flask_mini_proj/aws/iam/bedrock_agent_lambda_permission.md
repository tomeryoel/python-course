# Bedrock Agent Lambda Permission

After creating each Lambda, allow Bedrock Agent to invoke it:

```bash
aws lambda add-permission \
  --function-name ptsd-weekly-wellness-snapshot \
  --statement-id bedrock-agent-invoke-weekly \
  --action lambda:InvokeFunction \
  --principal bedrock.amazonaws.com \
  --source-arn "arn:aws:bedrock:REGION:ACCOUNT_ID:agent/AGENT_ID"

aws lambda add-permission \
  --function-name ptsd-emergency-contact-voice-call \
  --statement-id bedrock-agent-invoke-emergency \
  --action lambda:InvokeFunction \
  --principal bedrock.amazonaws.com \
  --source-arn "arn:aws:bedrock:REGION:ACCOUNT_ID:agent/AGENT_ID"
```

Replace REGION, ACCOUNT_ID, and AGENT_ID with your values.

In the Bedrock Agent console:
1. Open your Agent → **Action groups** → **Add**.
2. Choose **Define with API schemas** or **Quick create with Lambda**.
3. Upload the OpenAPI schema from `action_group_*.json` or select the Lambda.
4. Save and **Prepare** the Agent, then create/update an **Alias**.
