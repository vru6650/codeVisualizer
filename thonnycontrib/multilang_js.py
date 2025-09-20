"""JavaScript tooling integration for Thonny's Tools menu."""
from __future__ import annotations

import os
import queue
import shlex
import shutil
import subprocess
import sys
import threading
from pathlib import Path
from typing import Optional, Sequence, Tuple

from thonny import get_workbench
from thonny.common import is_remote_path

SUPPORTED_SUFFIXES: Tuple[str, ...] = (".js", ".mjs", ".cjs")
_PACKAGE_JSON_SEARCH_DEPTH = 10


def load_plugin() -> None:
    """Register commands for JavaScript workflows."""

    workbench = get_workbench()

    def register_command(command_id: str, label: str, handler, tester, *, default_sequence: Optional[str] = None) -> None:
        try:
            kwargs = {"default_sequence": default_sequence} if default_sequence else {}
            workbench.add_command(
                command_id,
                "tools",
                label,
                handler,
                tester=tester,
                group=110,
                **kwargs,
            )
        except TypeError:
            # Older Thonny builds might not accept default_sequence.
            workbench.add_command(
                command_id,
                "tools",
                label,
                handler,
                tester=tester,
                group=110,
            )

    register_command(
        "run_js_node",
        "Run JavaScript (Node)",
        _run_with_node,
        _js_menu_tester,
        default_sequence="<F7>",
    )

    deno_path = _find_executable(["deno"])
    if deno_path:
        register_command(
            "run_js_deno",
            "Run JavaScript (Deno)",
            lambda: _run_with_deno(deno_path),
            _js_menu_tester,
        )

    register_command(
        "lint_js_eslint",
        "Lint JavaScript (ESLint)",
        _lint_with_eslint,
        _js_menu_tester,
        default_sequence="<Shift-F7>",
    )


def _js_menu_tester() -> bool:
    filename = _current_editor_filename()
    return bool(filename and filename.lower().endswith(SUPPORTED_SUFFIXES) and not is_remote_path(filename))


def _run_with_node() -> None:
    filename = _require_active_js_file()
    if not filename:
        return

    node_path = _find_executable(["node", "node.exe"])
    if not node_path:
        _write_to_shell("Node.js not found on PATH. Install Node.js from https://nodejs.org/.\n", stream_name="stderr")
        return

    cwd = _detect_project_root(Path(filename))
    _stream_subprocess([node_path, filename], cwd)


def _run_with_deno(deno_path: str) -> None:
    filename = _require_active_js_file()
    if not filename:
        return

    cwd = Path(filename).parent
    _stream_subprocess([deno_path, "run", "-A", filename], cwd)


def _lint_with_eslint() -> None:
    filename = _require_active_js_file()
    if not filename:
        return

    file_path = Path(filename)
    cwd = _detect_project_root(file_path)
    eslint_path = _resolve_eslint(cwd)

    if not eslint_path:
        _write_to_shell("ESLint not found. Run `npm i -D eslint` to add it to your project.\n", stream_name="stderr")
        return

    _stream_subprocess([eslint_path, "--format", "unix", filename], cwd)


def _require_active_js_file() -> Optional[str]:
    workbench = get_workbench()
    editor_notebook = workbench.get_editor_notebook()
    editor = editor_notebook.get_current_editor() if editor_notebook else None

    if editor is None:
        _write_to_shell("Open a .js, .mjs, or .cjs file to use JavaScript tools.\n", stream_name="stderr")
        return None

    filename = editor.get_filename()
    if filename is None:
        filename = editor.get_filename(True)

    if not filename:
        _write_to_shell("Save the current JavaScript file before running tools.\n", stream_name="stderr")
        return None

    if is_remote_path(filename):
        _write_to_shell("JavaScript tools only support local files at the moment.\n", stream_name="stderr")
        return None

    if not filename.lower().endswith(SUPPORTED_SUFFIXES):
        _write_to_shell("Active file is not a JavaScript module (.js, .mjs, .cjs).\n", stream_name="stderr")
        return None

    return os.path.abspath(filename)


def _current_editor_filename() -> Optional[str]:
    workbench = get_workbench()
    editor_notebook = workbench.get_editor_notebook()
    editor = editor_notebook.get_current_editor() if editor_notebook else None
    if editor is None:
        return None
    return editor.get_filename()


def _detect_project_root(file_path: Path) -> Path:
    current = file_path.parent.resolve()
    for _ in range(_PACKAGE_JSON_SEARCH_DEPTH):
        if (current / "package.json").is_file():
            return current
        if current.parent == current:
            break
        current = current.parent
    return file_path.parent.resolve()


def _resolve_eslint(project_root: Path) -> Optional[str]:
    local_bin = project_root / "node_modules" / ".bin"
    candidates = [
        "eslint.cmd",
        "eslint.CMD",
        "eslint.exe",
        "eslint.bat",
        "eslint",
    ]

    for candidate in candidates:
        candidate_path = local_bin / candidate
        if _is_executable(candidate_path):
            return str(candidate_path)

    return _find_executable(candidates)


def _is_executable(path: Path) -> bool:
    return path.is_file() and os.access(path, os.X_OK)


def _find_executable(candidates: Sequence[str]) -> Optional[str]:
    for candidate in candidates:
        if not candidate:
            continue
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    return None


def _stream_subprocess(cmd: Sequence[str], cwd: Path) -> None:
    workbench = get_workbench()
    queue_: "queue.Queue[tuple[str, object]]" = queue.Queue()

    def worker() -> None:
        queue_.put(("stdout", f"$ {_format_command_for_echo(cmd)}\n"))
        try:
            proc = subprocess.Popen(
                list(cmd),
                cwd=str(cwd),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
        except OSError as exc:
            queue_.put(("stderr", f"{exc}\n"))
            queue_.put(("exit", 1))
            return

        assert proc.stdout is not None
        for line in iter(proc.stdout.readline, ""):
            queue_.put(("stdout", line))
        proc.stdout.close()
        proc.wait()
        queue_.put(("exit", proc.returncode or 0))

    threading.Thread(target=worker, daemon=True).start()

    finished = {"value": False}

    def poll_queue() -> None:
        if finished["value"]:
            return

        try:
            while True:
                kind, payload = queue_.get_nowait()
                if kind == "stdout":
                    _write_to_shell(str(payload))
                elif kind == "stderr":
                    _write_to_shell(str(payload), stream_name="stderr")
                elif kind == "exit":
                    _write_to_shell(f"[exit {payload}]\n")
                    finished["value"] = True
                    break
        except queue.Empty:
            pass

        if not finished["value"]:
            workbench.after(50, poll_queue)

    poll_queue()


def _format_command_for_echo(cmd: Sequence[str]) -> str:
    if sys.platform == "win32":
        return subprocess.list2cmdline(list(cmd))
    return " ".join(shlex.quote(part) for part in cmd)


def _write_to_shell(text: str, stream_name: str = "stdout") -> None:
    if not text:
        return

    workbench = get_workbench()
    try:
        workbench.show_view("ShellView", False)
    except Exception:
        pass

    workbench.event_generate("ProgramOutput", stream_name=stream_name, data=text)
