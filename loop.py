import json

import requests

from llm import modelRequest, cleanMsg

SYSTEM = (
    "You are a coding agent working inside a git repository. Your job is to "
    "complete the user's task, not to explore the repository.\n\n"
    "Rules:\n"
    "- If the task is genuinely ambiguous, ask one short question. Otherwise act."
)

def toolRun(calls, history, hops_left, dispatch):
    for call in calls:
        name = call["function"]["name"]
        fn = dispatch.get(name)
        try:
            args = json.loads(call["function"]["arguments"] or "{}")
            print(f"Tool Run: [{name}] {args}")
            result = fn(**args) if fn else f"unknown tool: {name}"
            print("Tool Run Output: ", result, "\n")
        except Exception as e:
            result = f"error: {e}"

        history.append({
            "role": "tool",
            "tool_call_id": call["id"],
            "content": f"{result}\n\n" + (
                "[tool budget exhausted — answer now with what you have so far]"
                if hops_left == 0 else
                f"[{hops_left} tool iterations left this turn]"
            ),
        })

async def askModel(history: list[dict], schemas: list[dict]) -> dict:
    """One model request, appended to history. If the provider rejects the
    model's own tool call (made-up tool name, bad JSON), tell the model what was
    wrong and ask once more instead of dying — the model never saw its mistake."""
    try:
        reply = await modelRequest(history, tools=schemas)
    except requests.HTTPError as e:
        err = {}
        try:
            err = e.response.json().get("error", {})
        except Exception:
            pass
        if err.get("code") != "tool_use_failed":
            raise
        names = ", ".join(t["function"]["name"] for t in schemas)
        history.append({"role": "user", "content":
            f"[harness] Your last tool call was rejected: {err.get('message')}. "
            f"Available tools: {names}. For grep, sed, find and similar, use bash."})
        reply = await modelRequest(history, tools=schemas)
    msg = reply["choices"][0]["message"]
    history.append(cleanMsg(msg))
    return msg

async def modelTurns(history: list[dict], tools: dict, max_hops: int = 5) -> str:
    """tools: name -> (schema, fn), see tool.REGISTRY."""
    schemas = [schema for schema, _ in tools.values()]
    dispatch = {name: fn for name, (_, fn) in tools.items()}
    msg = await askModel(history, schemas)

    for i in range(max_hops):
        calls = msg.get("tool_calls")
        if not calls:
            return msg["content"]

        toolRun(calls, history, hops_left=max_hops - i - 1, dispatch=dispatch)

        msg = await askModel(history, schemas)

    # budget spent; model may still ask for tools. Refuse to run them, ask once
    # more for text. Tools stay in the request so the API never rejects a call.
    if msg.get("tool_calls"):
        for call in msg["tool_calls"]:
            history.append({
                "role": "tool",
                "tool_call_id": call["id"],
                "content": "[tool budget exhausted — answer now with what you have so far]",
            })
        msg = await askModel(history, schemas)

    return msg["content"] or "[no answer: tool budget exhausted]"
