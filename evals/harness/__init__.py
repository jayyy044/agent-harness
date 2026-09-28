from .transcript.repair import CASES as REPAIR
from .transcript.roundtrip import CASES as ROUNDTRIP
from .transcript.append_only import CASES as APPEND_ONLY
from .tools.registry import CASES as REGISTRY
from .tools.write_file import CASES as WRITE_FILE

ALL_CASES = [*ROUNDTRIP, *APPEND_ONLY, *REPAIR, *REGISTRY, *WRITE_FILE]
