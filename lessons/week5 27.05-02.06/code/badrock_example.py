import boto3
from botocore.exceptions import ClientError

REGION = "us-east-1"
MODEL_ID = "amazon.nova-lite-v1:0"

def nova_complete(prompt: str) -> str:
    client = boto3.client("bedrock-runtime", region_name=REGION)

    try:
        response = client.converse(
            modelId=MODEL_ID,
            messages=[
                {
                    "role": "user",
                    "content": [{"text": prompt}],
                }
            ],
            inferenceConfig={
                "maxTokens": 400,
                "temperature": 0.2,
                "topP": 0.9,
            },
        )

        return response["output"]["message"]["content"][0]["text"]

    except ClientError as e:
        raise RuntimeError(
            f"Bedrock failed: {e.response.get('Error', {}).get('Message')}"
        ) from e

if __name__ == "__main__":
    out = nova_complete("Give me two bullet points about SQL injection.")
    print(out)