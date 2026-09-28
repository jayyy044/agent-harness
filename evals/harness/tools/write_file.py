"""write_file writes exactly what it is given, or returns an error and writes nothing."""
import tempfile
from pathlib import Path

from tool import write_file

# what bash quoting mangles: both quote kinds, a variable, backslashes, non-ASCII
AWKWARD = 'echo "$HOME" \'$USER\' \\n C:\\path ünï — alpine\u2011quartz\n'


def nested_creates_dirs():
    with tempfile.TemporaryDirectory() as d:
        out = write_file("a/b/c.txt", "hi", cwd=d)
        assert (Path(d) / "a/b/c.txt").read_text() == "hi", out


def overwrite_replaces_all():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "f.txt"
        p.write_text("old line\n" * 100)
        out = write_file("f.txt", "new", cwd=d)
        assert p.read_text() == "new", f"old content survived: {out}"


def awkward_content_exact():
    with tempfile.TemporaryDirectory() as d:
        out = write_file("x.sh", AWKWARD, cwd=d)
        got = (Path(d) / "x.sh").read_bytes()
        assert got == AWKWARD.encode(), f"{out}\ngot {got!r}"


def directory_path_errors():
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "sub").mkdir()
        out = write_file("sub", "x", cwd=d)
        assert out.startswith("error:"), out
        assert (Path(d) / "sub").is_dir(), "directory was replaced"


def parent_is_file_errors():
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "f").write_text("keep")
        out = write_file("f/x.txt", "x", cwd=d)
        assert out.startswith("error:"), out
        assert (Path(d) / "f").read_text() == "keep", "file in the way was touched"


def result_counts():
    with tempfile.TemporaryDirectory() as d:
        out = write_file("x.sh", AWKWARD, cwd=d)
        n_lines = len(AWKWARD.splitlines())
        n_bytes = len(AWKWARD.encode())
        assert f"{n_lines} lines" in out and f"{n_bytes} bytes" in out, out


CASES = [
    {"name": "write_file_nested_dirs", "check": nested_creates_dirs},
    {"name": "write_file_overwrite", "check": overwrite_replaces_all},
    {"name": "write_file_awkward_content", "check": awkward_content_exact},
    {"name": "write_file_directory_errors", "check": directory_path_errors},
    {"name": "write_file_parent_is_file", "check": parent_is_file_errors},
    {"name": "write_file_result_counts", "check": result_counts},
]
