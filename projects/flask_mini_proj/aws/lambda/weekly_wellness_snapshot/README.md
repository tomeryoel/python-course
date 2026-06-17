# Weekly Wellness Snapshot Lambda

**Function name:** `ptsd-weekly-wellness-snapshot`

## Purpose

Generates a weekly wellness snapshot from completed tasks, open tasks, and recent topics.
Used as a **Bedrock Agent Action Group** (MCP-style tool).

## Deploy

1. Create Lambda in AWS Console (Python 3.11).
2. Paste `lambda_function.py` as the handler (`lambda_function.lambda_handler`).
3. Add CloudWatch Logs basic execution role.
4. Attach to Bedrock Agent Action Group using `action_group_weekly_snapshot_schema.json`.

## Test

Use `test_event.json` in the Lambda console Test tab.

## Bedrock Agent

When invoked by the Agent, the handler detects the Action Group event format and returns
the required `messageVersion: 1.0` wrapper.
