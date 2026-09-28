import asyncio
import os

import requests
from dotenv import load_dotenv

load_dotenv()

MODEL = "openai/gpt-oss-120b"

RETRYABLE = {429, 500, 502, 503, 529}


async def modelRequest(messages: list[dict], tools: list[dict] | None = None, retries: int = 4) -> dict:
    """POST one chat completion to Groq and return the parsed JSON body."""
    body = {
        "model": MODEL,
        "messages": messages,
        "reasoning_effort": "high",
        "temperature": 0,
        "top_p": 1,
        "max_completion_tokens": 4096,
    }
    if tools:
        body["tools"] = tools
        body["tool_choice"] = "auto"

    for attempt in range(retries):
        # ponytail: requests is sync, run in a thread; swap for httpx if streaming needed
        resp = await asyncio.to_thread(
            requests.post,
            url="https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.environ['groqKey']}",
                "Content-Type": "application/json",
            },
            json=body,
            timeout=300
        )

        if resp.status_code in RETRYABLE and attempt < retries - 1:
            wait = float(resp.headers.get("retry-after", 2 ** attempt))
            print(f"[{resp.status_code}, retrying in {wait}s]")
            await asyncio.sleep(wait)
            continue

        if resp.status_code >= 400:
            raise requests.HTTPError(f"{resp.status_code}: {resp.text}", response=resp)

        return resp.json()


def cleanMsg(msg: dict) -> dict:
    """Strip provider-specific extras; keep only what the API accepts back."""
    out = {"role": "assistant", "content": msg.get("content")}
    if msg.get("tool_calls"):
        out["tool_calls"] = msg["tool_calls"]
    return out
