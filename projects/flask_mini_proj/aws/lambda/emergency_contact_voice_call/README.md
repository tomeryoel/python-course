# Emergency Contact Voice Call Lambda

**Function name:** `ptsd-emergency-contact-voice-call`

## Purpose

Triggers an automated **support call** (not emergency services) to a predefined contact via
**Amazon Connect**, after explicit user confirmation (`confirmed: true`).

## Lambda environment variables

| Variable | Description |
|----------|-------------|
| `CONNECT_INSTANCE_ID` | Amazon Connect instance ID |
| `CONNECT_CONTACT_FLOW_ID` | Outbound contact flow ID |
| `CONNECT_SOURCE_PHONE_NUMBER` | Claimed Connect outbound number (E.164) |
| `EMERGENCY_CONTACT_PHONE` | Default contact if not passed in event |

## IAM

Attach policy with `connect:StartOutboundVoiceContact` — see `aws/iam/lambda_connect_policy.json`.

## Safety

- Requires `confirmed: true` in every invocation.
- The UI must show a confirmation modal before calling this tool.
- This is **not** a replacement for emergency services (101/100).

## Test

Use `test_event.json` in Lambda console. Connect must be configured or you'll get a config error (expected in dev).
