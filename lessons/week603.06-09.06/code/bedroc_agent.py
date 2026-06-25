import boto3
client = boto3.client("bedrock-agent-runtime", region_name="us-east-1")
agent_id = "XLYXR4MDG0"
agent_alias_id = "LWDOFPO11O"
session_id = "example-session-001"
response = client.invoke_agent(
    agentId=agent_id,
    agentAliasId=agent_alias_id,
    sessionId=session_id,
    inputText="What is the capital of France?"
)

for event in response.get("completion", []):
    if "chunk" in event:
        print(event["chunk"]["bytes"].decode("utf-8"))
    elif "trace" in event:
        print("Trace:", event["trace"])