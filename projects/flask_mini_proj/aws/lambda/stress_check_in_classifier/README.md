# ptsd-stress-check-in-classifier

Bedrock Agent Action Group Lambda that classifies user distress / cognitive overload
and returns **safe routing guidance** for the Agent.

## Not medical care

- Not a diagnosis, therapy, psychiatric advice, or emergency service
- Does not recommend medication changes
- Does not replace emergency services or professional care
- Rule-based only — no LLM inside the Lambda

## Deploy

1. AWS Console → Lambda → Create function
2. Name: `ptsd-stress-check-in-classifier`
3. Runtime: **Python 3.14** (or latest available)
4. Paste `lambda_function.py`
5. Test with `test_event_low.json`, `test_event_medium.json`, `test_event_high.json`, `test_event_crisis.json`

## Bedrock Agent Action Group

- Schema: `aws/bedrock_agent/action_group_stress_check_in_classifier_schema.json`
- Operation: `stress_check_in_classifier`

## Classifications

| Level | Route | Behavior |
|-------|-------|----------|
| `low` | `kb_answer` | Normal KB answer |
| `medium` | `kb_answer_short` | Short calm KB answer |
| `high` | `grounding_then_kb` | Grounding first, then brief KB |
| `crisis` | `crisis_support` | Human / emergency support — not normal RAG |
