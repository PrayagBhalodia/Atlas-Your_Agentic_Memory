"""ATLAS — Bedrock connectivity check .

Confirms two things before we build anything on top of Bedrock:
  1. Claude answers via the Converse API   (the agent's brain)
  2. Titan returns an embedding vector      (the memory index's search key)

Run:  python hello.py
It also lists the Anthropic/Titan model IDs available in your account, so if a
call fails you can copy the correct ID into your .env.
"""
import os
import json

from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError

load_dotenv()

REGION = os.getenv("AWS_REGION", "us-east-1")
CHAT_MODEL = os.getenv("BEDROCK_CHAT_MODEL_ID", "us.anthropic.claude-sonnet-4-5-20250929-v1:0")
EMBED_MODEL = os.getenv("BEDROCK_EMBED_MODEL_ID", "amazon.titan-embed-text-v2:0")

runtime = boto3.client("bedrock-runtime", region_name=REGION)
control = boto3.client("bedrock", region_name=REGION)


def show_error(e):
    err = e.response.get("Error", {})
    meta = e.response.get("ResponseMetadata", {})
    print(f"  FAIL  [Code={err.get('Code')}]  {err.get('Message')}")
    print(f"        HTTPStatus={meta.get('HTTPStatusCode')}  RequestId={meta.get('RequestId')}")


def who_am_i():
    print("\n=== Identity your code is using ===")
    try:
        ident = boto3.client("sts", region_name=REGION).get_caller_identity()
        print("  Account:", ident["Account"])
        print("  ARN:    ", ident["Arn"])   # should be .../user/atlas-dev, NOT :root
    except ClientError as e:
        show_error(e)


def list_models():
    print(f"\n=== Available models in {REGION} (Anthropic / Titan embeddings) ===")
    try:
        resp = control.list_foundation_models()
        for m in resp["modelSummaries"]:
            mid = m["modelId"]
            if mid.startswith("anthropic.") or "titan-embed" in mid:
                print(f"  {mid}")
    except ClientError as e:
        print("  (couldn't list models):", e.response["Error"]["Message"])


def test_chat():
    print(f"\n=== Test 1: Claude via Converse  ({CHAT_MODEL}) ===")
    try:
        resp = runtime.converse(
            modelId=CHAT_MODEL,
            messages=[{"role": "user", "content": [{"text": "Say hello in one short sentence."}]}],
            inferenceConfig={"maxTokens": 50},
        )
        print("  Claude says:", resp["output"]["message"]["content"][0]["text"].strip())
        print("  PASS")
    except ClientError as e:
        show_error(e)


def test_embedding():
    print(f"\n=== Test 2: Titan embedding  ({EMBED_MODEL}) ===")
    try:
        resp = runtime.invoke_model(
            modelId=EMBED_MODEL,
            body=json.dumps({"inputText": "mobile offline sync"}),
        )
        vec = json.loads(resp["body"].read())["embedding"]
        print(f"  Got a vector of length {len(vec)} (expected 1024 for Titan v2).")
        print("  PASS")
    except ClientError as e:
        show_error(e)


if __name__ == "__main__":
    print(f"Region: {REGION}")
    who_am_i()
    list_models()
    test_chat()
    test_embedding()
    print("\nDone. Two PASS lines = your Bedrock setup is complete.")
