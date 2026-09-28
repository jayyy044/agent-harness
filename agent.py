import asyncio
import sys
import uuid
from pathlib import Path

import requests

from loop import modelTurns, SYSTEM
from tool import REGISTRY
from transcript import Transcript


async def main():
    SESSIONS = Path(__file__).parent / "sessions"
    SESSIONS.mkdir(parents=True, exist_ok=True)

    resume_id = None
    if "--resume" in sys.argv:
        i = sys.argv.index("--resume")
        if i + 1 < len(sys.argv):
            resume_id = sys.argv[i + 1]
        else:
            sys.exit("--resume needs a session id")

    if resume_id:
        path = SESSIONS / f"{resume_id}.jsonl"
        if not path.exists():
            sys.exit(f"no such session: {resume_id}")
        session_id = resume_id
        history = Transcript(path)
        history.load()
        print(f"[resumed {session_id}, {len(history)} messages]")
    else:
        session_id = uuid.uuid4()
        history = Transcript(SESSIONS / f"{session_id}.jsonl")
        history.append({"role": "system", "content": SYSTEM})
        print(f"[session {session_id}]")


    while True:
        try:
            line = input("> ")
        except EOFError:
            break
        if line.strip().lower() in ("quit", "exit"):
            print(f"resume this session by python3 agent.py --resume {session_id}")
            break

        history.append({"role": "user", "content": line})
        try:
            reply = await modelTurns(history, tools=REGISTRY)
        except requests.HTTPError as e:
            print(f"\n[groq error: {e}]")
            # keep the failed turn: it is already on disk, and deleting it from
            # memory only would make --resume load a different history. Tell the
            # model instead, so it knows any tool calls above did run.
            history.append({"role": "user", "content":
                f"[harness] the request above failed and got no answer: {str(e)[:300]}"})
            continue

        print(reply)


if __name__ == "__main__":
    asyncio.run(main())
