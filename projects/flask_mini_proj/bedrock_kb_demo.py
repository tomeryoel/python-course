"""
Standalone Bedrock Knowledge Base demo — FOR ASSIGNMENT SCREENSHOTS ONLY.

This script is intentionally **NOT imported by the application runtime**.
The live app uses local FAISS retrieval (see rag_engine.py). The Bedrock
Knowledge Base + OpenSearch resource is kept only to satisfy the instructor
requirement of "create a Knowledge Base and show screenshots".

Run it manually when you want to demonstrate that the KB still answers:

    python bedrock_kb_demo.py "מה ההמלצות לגבי שינה?"

Requires KNOWLEDGE_BASE_ID in .env and AWS credentials. Because OpenSearch
Serverless bills while it exists, delete the KB/collection after taking
screenshots (see README cleanup section).
"""

from __future__ import annotations

import os
import sys

import boto3
from dotenv import load_dotenv

load_dotenv()


def kb_retrieve(question: str) -> None:
    kb_id = os.getenv("KNOWLEDGE_BASE_ID", "").strip()
    region = os.getenv("AWS_REGION", "us-east-1")
    if not kb_id:
        print("KNOWLEDGE_BASE_ID is not set in .env — nothing to demo.")
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
