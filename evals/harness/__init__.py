from .transcript.repair import CASES as REPAIR
from .transcript.roundtrip import CASES as ROUNDTRIP
from .tools.registry import CASES as REGISTRY

ALL_CASES = [*ROUNDTRIP, *REPAIR, *REGISTRY]
