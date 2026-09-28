from .basic_func.basicFunction import CASES as BASIC
from .basic_func.noPersistentCwd import CASES as NO_CWD
from .basic_func.truncation import CASES as TRUNC
from .basic_func.budgetExhaustion import CASES as BUDGET
from .basic_func.resume import CASES as RESUME

from .tools.read_specific_line import CASES as READLINE
from .tools.write_file import CASES as WRITE_FILE

# Stage 1
STAGE_1 = [*BASIC, *NO_CWD, *TRUNC, *BUDGET, *RESUME]

# Stage 2 - Tools
STAGE_2 = [*READLINE, *WRITE_FILE]

ALL_CASES = [*STAGE_1, *STAGE_2]

