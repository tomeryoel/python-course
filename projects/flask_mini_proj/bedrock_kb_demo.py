"""
Standalone Bedrock Knowledge Base retrieve demo — FOR MANUAL TESTING / SCREENSHOTS ONLY.

NOT imported by the application runtime. Live chat uses:
    Flask → invoke_agent → Bedrock Agent → Knowledge Base

Run manually to verify KB retrieval against S3-indexed documents:

    python bedrock_kb_demo.py "מה ההמלצות לגבי שינה?"

Requires BEDROCK_KNOWLEDGE_BASE_ID (or KNOWLEDGE_BASE_ID) in .env and AWS credentials.
"""

from __future__ import annotations

import os
import sys

import boto3
from dotenv import load_dotenv

load_dotenv()


def kb_retrieve(question: str) -> None:
    kb_id = (
        os.getenv("BEDROCK_KNOWLEDGE_BASE_ID", "")
        or os.getenv("KNOWLEDGE_BASE_ID", "")
    ).strip()
    region = os.getenv("AWS_REGION", "us-east-1")
    if not kb_id:
        print("BEDROCK_KNOWLEDGE_BASE_ID is not set in .env — nothing to demo.")
        sys.exit(1)

    client = boto3.client("bedrock-agent-runtime", region_name=region)
    response = client.retrieve(
        knowledgeBaseId=kb_id,
        retrievalQuery={"text": question},
        retrievalConfiguration={"vectorSearchConfiguration": {"numberOfResults": 5}},
    )

    print(f"Knowledge Base: {kb_id} (region {region})")
    print(f"Question: {question}\n--- Retrieved chunks ---")
    for i, result in enumerate(response.get("retrievalResults", []), start=1):
        text = result.get("content", {}).get("text", "").strip()
        score = result.get("score")
        print(f"\n[{i}] score={score}\n{text[:400]}")


if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "מה ההמלצות לגבי שינה?"
    kb_retrieve(query)
