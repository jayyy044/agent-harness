import asyncio
import sys
import time 
import tempfile
import traceback
from functools import partial
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))   # learning/
sys.path.insert(0, str(Path(__file__).parent))          # evals/

from loop import modelTurns, SYSTEM
from tool import REGISTRY
from model import ALL_CASES


async def run_case(case) -> tuple[bool, str]:
    with tempfile.TemporaryDirectory() as d:
        case["setup"](d)

        tools = {name: (schema, partial(fn, cwd=d)) for name, (schema, fn) in REGISTRY.items()}
        history = case["history"](d) if "history" in case else [{"role": "system", "content": SYSTEM}]
        history.append({"role": "user", "content": case["prompt"]})

        try:
            out = await modelTurns(history, tools=tools, max_hops=case.get("max_hops", 5))

        except Exception:
            return False, traceback.format_exc(limit=1).strip()

        try:
            passed = case["check"](d, out or "", history)
        except Exception as e:
            return False, f"check raised: {e}"

        hops = sum(1 for m in history if m["role"] == "tool")
        return passed, f"{hops} tool calls | {(out or '')[:80]}"


async def main():
    results = []
    for case in ALL_CASES:
        passed, detail = await run_case(case)
        results.append(passed)
        print(f"{'PASS' if passed else 'FAIL'}  {case['name']:24} {detail}\n")
        print("[Pausing to prevent rate limiting, 5s]")
        time.sleep(5)

    print(f"\n{sum(results)}/{len(results)} passed")


if __name__ == "__main__":
    asyncio.run(main())