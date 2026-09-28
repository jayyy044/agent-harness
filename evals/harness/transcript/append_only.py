"""Transcript refuses every change except append, so memory can't drift from disk."""
import tempfile
from pathlib import Path

from transcript import Transcript
from ._fixtures import SYS, USR, TEXT

MUTATIONS = {
    "del":     lambda t: t.__delitem__(slice(1, None)),
    "setitem": lambda t: t.__setitem__(0, USR),
    "iadd":    lambda t: t.__iadd__([USR]),
    "insert":  lambda t: t.insert(0, USR),
    "extend":  lambda t: t.extend([USR]),
    "pop":     lambda t: t.pop(),
    "remove":  lambda t: t.remove(SYS),
    "clear":   lambda t: t.clear(),
}


def refuses_mutation():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "s.jsonl"
        t = Transcript(p)
        for m in (SYS, USR, TEXT):
            t.append(m)
        for name, mutate in MUTATIONS.items():
            try:
                mutate(t)
            except TypeError:
                pass
            else:
                raise AssertionError(f"{name} was allowed")
        assert list(t) == [SYS, USR, TEXT], "a refused mutation still changed memory"
        t2 = Transcript(p)
        t2.load()
        assert list(t2) == list(t), "disk differs from memory"


CASES = [{"name": "transcript_append_only", "check": refuses_mutation}]
