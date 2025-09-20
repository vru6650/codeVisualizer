# -*- coding: utf-8 -*-
"""Find in files dialog."""

from __future__ import annotations

import fnmatch
import os
import queue
import threading
import tokenize
from dataclasses import dataclass
from pathlib import Path
import tkinter as tk
from tkinter import ttk
from typing import Dict, Iterable, List, Optional, Sequence

from thonny import get_runner, get_workbench
from thonny.common import IGNORED_FILES_AND_DIRS, TextRange
from thonny.editors import get_target_dirname_from_editor_filename
from thonny.languages import tr
from thonny.misc_utils import running_on_mac_os
from thonny.ui_utils import CommonDialogEx, create_string_var, select_sequence, show_dialog


@dataclass
class SearchMatch:
    path: str
    lineno: int
    col: int
    line: str


@dataclass
class RootOption:
    path: str
    label: str
    kind: str  # "local" or "remote"
    uses_local_filesystem: bool = False


_ACTIVE_DIALOG: Optional["FindInFilesDialog"] = None

_RECENT_TERMS_OPTION = "find_in_files.recent_terms"
_RECENT_FILTERS_OPTION = "find_in_files.recent_filters"
_MAX_HISTORY = 20


class FindInFilesDialog(CommonDialogEx):
    def __init__(self, master: tk.Misc):
        super().__init__(master=master, skip_tk_dialog_attributes=running_on_mac_os())

        self.title(tr("Find in Files…"))
        self.resizable(width=tk.TRUE, height=tk.TRUE)

        margin = self.get_medium_padding()
        spacing = self.get_small_padding()
        self.main_frame.configure(padding=margin)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.columnconfigure(2, weight=1)
        self.main_frame.rowconfigure(6, weight=1)

        self._search_history: List[str] = list(self._load_history(_RECENT_TERMS_OPTION))
        self._filter_history: List[str] = list(self._load_history(_RECENT_FILTERS_OPTION))

        self._search_var = create_string_var("")
        self._filter_var = create_string_var("")
        self._root_var = create_string_var("")
        self._status_var = create_string_var("")
        self._match_case_var = tk.BooleanVar(value=False)

        self._root_options: Dict[str, RootOption] = {}

        self._search_text: Optional[str] = None
        self._current_root: Optional[RootOption] = None

        self._search_thread: Optional[threading.Thread] = None
        self._results_queue: Optional["queue.Queue[object]"] = None
        self._cancel_requested = False
        self._search_running = False

        self._poll_after: Optional[str] = None
        self._root_refresh_after: Optional[str] = None

        self._theme_binding = self.bind("<<ThemeChanged>>", self._on_theme_changed, True)

        self._prepare_widgets(spacing)
        self._load_initial_values()
        self._refresh_root_options()
        self._schedule_root_poll()
        self._on_theme_changed()

    def destroy(self) -> None:
        self._cancel_search()
        if self._poll_after:
            try:
                self.after_cancel(self._poll_after)
            except Exception:
                pass
            self._poll_after = None
        if self._root_refresh_after:
            try:
                self.after_cancel(self._root_refresh_after)
            except Exception:
                pass
            self._root_refresh_after = None

        get_workbench().unbind("BackendRestart", self._on_backend_event)
        get_workbench().unbind("BackendTerminated", self._on_backend_event)
        get_workbench().unbind("RemoteFilesChanged", self._on_backend_event)

        if self._theme_binding is not None:
            self.unbind("<<ThemeChanged>>", self._theme_binding)
            self._theme_binding = None

        self._save_history(_RECENT_TERMS_OPTION, self._search_history)
        self._save_history(_RECENT_FILTERS_OPTION, self._filter_history)

        global _ACTIVE_DIALOG
        _ACTIVE_DIALOG = None

        super().destroy()

    def set_initial_focus(self, node=None) -> bool:
        if self._search_combo.winfo_ismapped():
            self._search_combo.focus_set()
            self._search_combo.selection_range(0, tk.END)
            return True
        return super().set_initial_focus(node)

    def _prepare_widgets(self, spacing: int) -> None:
        label = ttk.Label(self.main_frame, text=tr("Find:"))
        label.grid(row=0, column=0, sticky="w", pady=(0, spacing))

        self._search_combo = ttk.Combobox(
            self.main_frame,
            textvariable=self._search_var,
            values=self._search_history,
            height=12,
        )
        self._search_combo.grid(row=0, column=1, columnspan=2, sticky="ew", padx=(0, 0), pady=(0, spacing))
        self._search_combo.bind("<Return>", self._start_search, True)
        self._search_combo.bind("<KP_Enter>", self._start_search, True)

        filter_label = ttk.Label(self.main_frame, text=tr("Filter:"))
        filter_label.grid(row=1, column=0, sticky="w", pady=(0, spacing))

        self._filter_combo = ttk.Combobox(
            self.main_frame,
            textvariable=self._filter_var,
            values=self._filter_history,
            height=12,
        )
        self._filter_combo.grid(row=1, column=1, columnspan=2, sticky="ew", pady=(0, spacing))
        self._filter_combo.bind("<Return>", self._start_search, True)
        self._filter_combo.bind("<KP_Enter>", self._start_search, True)

        root_label = ttk.Label(self.main_frame, text=tr("Root:"))
        root_label.grid(row=2, column=0, sticky="w", pady=(0, spacing))

        self._root_combo = ttk.Combobox(
            self.main_frame,
            textvariable=self._root_var,
            state="readonly",
            height=10,
        )
        self._root_combo.grid(row=2, column=1, sticky="ew", pady=(0, spacing))

        browse_button = ttk.Button(
            self.main_frame,
            text=tr("Browse…"),
            command=self._choose_local_root,
        )
        browse_button.grid(row=2, column=2, sticky="e", padx=(spacing, 0), pady=(0, spacing))

        options_frame = ttk.Frame(self.main_frame)
        options_frame.grid(row=3, column=0, columnspan=3, sticky="w", pady=(0, spacing))

        match_case = ttk.Checkbutton(
            options_frame,
            text=tr("Match case"),
            variable=self._match_case_var,
        )
        match_case.grid(row=0, column=0, sticky="w")

        self._search_button = ttk.Button(
            self.main_frame,
            text=tr("Search"),
            command=self._on_search_button_click,
            default="active",
        )
        self._search_button.grid(row=4, column=2, sticky="e", pady=(0, spacing))

        self._status_label = ttk.Label(self.main_frame, textvariable=self._status_var, anchor="w")
        self._status_label.grid(row=4, column=0, columnspan=2, sticky="w", pady=(0, spacing))

        tree_frame = ttk.Frame(self.main_frame)
        tree_frame.grid(row=5, column=0, columnspan=3, sticky="nsew")
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        self._tree = ttk.Treeview(
            tree_frame,
            show="headings",
            columns=("file", "line", "snippet"),
            selectmode="browse",
        )
        self._tree.heading("file", text=tr("File"))
        self._tree.heading("line", text=tr("Line"))
        self._tree.heading("snippet", text=tr("Snippet"))
        self._tree.column("file", width=200, anchor="w")
        self._tree.column("line", width=60, anchor="center")
        self._tree.column("snippet", width=400, anchor="w")

        self._tree.grid(row=0, column=0, sticky="nsew")

        yscroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self._tree.yview)
        yscroll.grid(row=0, column=1, sticky="ns")
        xscroll = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self._tree.xview)
        xscroll.grid(row=1, column=0, sticky="ew")
        self._tree.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)

        self._tree.bind("<Return>", self._open_selected_match, True)
        self._tree.bind("<KP_Enter>", self._open_selected_match, True)
        self._tree.bind("<Double-Button-1>", self._open_selected_match, True)

        self._matches: List[SearchMatch] = []

        get_workbench().bind("BackendRestart", self._on_backend_event, True)
        get_workbench().bind("BackendTerminated", self._on_backend_event, True)
        get_workbench().bind("RemoteFilesChanged", self._on_backend_event, True)

    def _on_theme_changed(self, event=None) -> None:
        style = ttk.Style()
        background = style.lookup("TFrame", "background")
        if background:
            self.configure(background=background)

    def _load_initial_values(self) -> None:
        seed_text = ""
        try:
            widget = get_workbench().focus_get()
            if isinstance(widget, tk.Text):
                if len(widget.tag_ranges("sel")) > 0:
                    selection = widget.selection_get().splitlines()
                    if selection:
                        seed_text = selection[0]
        except Exception:
            pass

        if not seed_text and self._search_history:
            seed_text = self._search_history[0]

        self._search_var.set(seed_text)
        if self._filter_history:
            self._filter_var.set(self._filter_history[0])

    def _load_history(self, option_name: str) -> Sequence[str]:
        value = get_workbench().get_option(option_name, [])
        if isinstance(value, list):
            return value
        return []

    def _save_history(self, option_name: str, history: Sequence[str]) -> None:
        unique = []
        for item in history:
            if item and item not in unique:
                unique.append(item)
        get_workbench().set_option(option_name, unique[:_MAX_HISTORY])

    def _add_to_history(self, history: List[str], value: str) -> None:
        value = value.strip()
        if not value:
            return
        if value in history:
            history.remove(value)
        history.insert(0, value)
        del history[_MAX_HISTORY:]

    def _choose_local_root(self) -> None:
        from tkinter import filedialog

        initial_dir = self._root_var.get() or os.getcwd()
        try:
            path = filedialog.askdirectory(parent=self, initialdir=initial_dir)
        except Exception:
            path = None
        if path:
            option = RootOption(path=path, label=path, kind="local")
            self._root_options[path] = option
            self._root_var.set(path)
            self._root_combo.configure(values=list(self._root_options.keys()))

    def _on_backend_event(self, event=None) -> None:
        self._refresh_root_options()

    def _schedule_root_poll(self) -> None:
        self._root_refresh_after = self.after(2000, self._on_root_poll)

    def _on_root_poll(self) -> None:
        self._root_refresh_after = None
        self._refresh_root_options()
        self._schedule_root_poll()

    def _refresh_root_options(self) -> None:
        previous = self._root_var.get()

        options: Dict[str, RootOption] = {}

        local_dir = self._get_active_local_dir()
        if local_dir:
            options[local_dir] = RootOption(path=local_dir, label=local_dir, kind="local")

        remote_option = self._create_remote_option()
        if remote_option:
            options[remote_option.label] = remote_option

        if not options:
            fallback = os.getcwd()
            options[fallback] = RootOption(path=fallback, label=fallback, kind="local")

        previous_options = dict(self._root_options)
        self._root_options = options
        self._root_combo.configure(values=list(options.keys()))

        if previous and previous in options:
            self._root_var.set(previous)
        elif previous and previous in previous_options:
            self._root_options[previous] = previous_options[previous]
            self._root_combo.configure(values=list(self._root_options.keys()))
            self._root_var.set(previous)
        else:
            labels = list(options.keys())
            if labels:
                self._root_var.set(labels[0])

    def _get_active_local_dir(self) -> Optional[str]:
        files_view = get_workbench().get_view("FilesView")
        if files_view:
            directory = files_view.get_active_local_dir()
            if directory:
                return directory

        notebook = get_workbench().get_editor_notebook()
        editor = notebook.get_current_editor() if notebook else None
        if editor:
            filename = editor.get_filename()
            if filename:
                directory = get_target_dirname_from_editor_filename(filename)
                if directory:
                    return directory

        return None

    def _create_remote_option(self) -> Optional[RootOption]:
        files_view = get_workbench().get_view("FilesView")
        if not files_view:
            return None

        remote_dir = files_view.get_active_remote_dir()
        if not remote_dir:
            return None

        runner = get_runner()
        uses_local_fs = False
        label_prefix = tr("Remote")
        if runner:
            proxy = runner.get_backend_proxy()
            if proxy:
                uses_local_fs = proxy.uses_local_filesystem()
                try:
                    label_prefix = proxy.get_node_label()
                except Exception:
                    label_prefix = tr("Remote")

        label = f"{label_prefix}: {remote_dir}"
        kind = "local" if uses_local_fs else "remote"
        return RootOption(
            path=remote_dir,
            label=label,
            kind=kind,
            uses_local_filesystem=uses_local_fs,
        )

    def _on_search_button_click(self) -> None:
        if self._search_running:
            self._cancel_search()
        else:
            self._start_search()

    def _start_search(self, event=None):
        if self._search_running:
            return "break"

        root_label = self._root_var.get()
        if not root_label or root_label not in self._root_options:
            self._status_var.set(tr("Select a valid root folder."))
            return "break"

        root_option = self._root_options[root_label]
        if root_option.kind == "remote" and not root_option.uses_local_filesystem:
            self._status_var.set(tr("Searching remote files is not supported for this backend."))
            return "break"

        search_text = self._search_var.get().strip()
        if not search_text:
            self._status_var.set(tr("Enter search text"))
            self._search_combo.focus_set()
            return "break"

        file_filter = self._filter_var.get().strip() or "*"

        root_path = Path(root_option.path)
        if not root_path.exists():
            self._status_var.set(tr("The selected root folder does not exist."))
            return "break"

        self._add_to_history(self._search_history, search_text)
        self._add_to_history(self._filter_history, file_filter)
        self._search_combo.configure(values=self._search_history)
        self._filter_combo.configure(values=self._filter_history)

        self._tree.delete(*self._tree.get_children())
        self._matches.clear()
        self._status_var.set(tr("Searching…"))

        self._search_text = search_text
        self._current_root = root_option
        self._cancel_requested = False
        self._search_running = True
        self._search_button.configure(text=tr("Stop"))
        self._root_combo.configure(state="disabled")
        self._filter_combo.configure(state="disabled")
        self._search_combo.configure(state="disabled")

        pattern = file_filter
        match_case = self._match_case_var.get()
        self._results_queue = queue.Queue()

        def worker():
            try:
                self._run_search(root_path, pattern, search_text, match_case)
            finally:
                if self._results_queue is not None:
                    self._results_queue.put(("done", None))

        self._search_thread = threading.Thread(target=worker, daemon=True)
        self._search_thread.start()
        self._poll_queue()
        return "break"

    def _cancel_search(self) -> None:
        self._cancel_requested = True
        if self._search_thread and self._search_thread.is_alive():
            self._search_thread.join(timeout=0.1)
        self._search_thread = None
        self._finalize_search(tr("Search cancelled"))

    def _run_search(self, root_path: Path, pattern: str, search_text: str, match_case: bool) -> None:
        total_matches = 0
        total_files = 0
        for path in self._iter_files(root_path, pattern):
            if self._cancel_requested:
                break

            try:
                text = self._read_text(path)
            except Exception:
                text = None
            if text is None:
                continue

            total_files += 1
            lines = text.splitlines()
            if not match_case:
                needle = search_text.lower()
            else:
                needle = search_text

            for lineno, line in enumerate(lines, start=1):
                haystack = line if match_case else line.lower()
                start = 0
                while True:
                    if self._cancel_requested:
                        break
                    index = haystack.find(needle, start)
                    if index == -1:
                        break
                    snippet = line.strip()
                    total_matches += 1
                    if self._results_queue is not None:
                        self._results_queue.put(
                            (
                                "match",
                                str(path),
                                lineno,
                                index,
                                line,
                            )
                        )
                    start = index + max(len(needle), 1)
                if self._cancel_requested:
                    break

        if self._results_queue is not None:
            self._results_queue.put(("summary", total_files, total_matches))

    def _iter_files(self, root: Path, pattern: str) -> Iterable[Path]:
        if not root.exists():
            return []

        def walker(current: Path) -> Iterable[Path]:
            if self._cancel_requested:
                return
            try:
                entries = list(current.iterdir())
            except OSError:
                return

            for entry in entries:
                if entry.name in IGNORED_FILES_AND_DIRS:
                    continue
                if entry.is_dir():
                    yield from walker(entry)
                elif entry.is_file():
                    if fnmatch.fnmatch(entry.name, pattern):
                        yield entry

        if root.is_file():
            if fnmatch.fnmatch(root.name, pattern):
                return [root]
            return []

        return walker(root)

    def _read_text(self, path: Path) -> Optional[str]:
        try:
            with tokenize.open(str(path)) as fp:
                return fp.read()
        except (SyntaxError, UnicodeError, OSError):
            try:
                return path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                return None

    def _poll_queue(self) -> None:
        if not self._results_queue:
            return

        try:
            while True:
                item = self._results_queue.get_nowait()
                kind = item[0]
                if kind == "match":
                    _, path, lineno, col, line = item
                    self._add_match(str(path), int(lineno), int(col), str(line))
                elif kind == "summary":
                    _, files, matches = item
                    if self._search_running:
                        if matches:
                            self._status_var.set(
                                tr("Found %d matches in %d files") % (matches, files)
                            )
                        else:
                            self._status_var.set(tr("No matches found"))
                elif kind == "done":
                    self._finalize_search()
        except queue.Empty:
            pass

        if self._search_running:
            self._poll_after = self.after(100, self._poll_queue)
        else:
            self._poll_after = None

    def _finalize_search(self, message: Optional[str] = None) -> None:
        self._search_running = False
        self._cancel_requested = False
        self._search_button.configure(text=tr("Search"))
        self._root_combo.configure(state="readonly")
        self._filter_combo.configure(state="normal")
        self._search_combo.configure(state="normal")
        self._results_queue = None
        self._search_thread = None
        if message:
            self._status_var.set(message)

    def _add_match(self, path: str, lineno: int, col: int, line: str) -> None:
        if self._current_root:
            try:
                display_path = os.path.relpath(path, self._current_root.path)
            except ValueError:
                display_path = path
        else:
            display_path = path

        snippet = line.strip()
        if len(snippet) > 200:
            snippet = snippet[:197] + "…"

        match = SearchMatch(path=path, lineno=lineno, col=col, line=line)
        self._matches.append(match)
        iid = str(len(self._matches) - 1)
        self._tree.insert("", tk.END, iid=iid, values=(display_path, lineno, snippet))

    def _get_selected_match(self) -> Optional[SearchMatch]:
        selection = self._tree.selection()
        if not selection:
            return None
        try:
            index = int(selection[0])
        except (ValueError, IndexError):
            return None
        if 0 <= index < len(self._matches):
            return self._matches[index]
        return None

    def _open_selected_match(self, event=None):
        match = self._get_selected_match()
        if not match:
            return "break"

        editor_notebook = get_workbench().get_editor_notebook()
        if not editor_notebook:
            return "break"

        search_len = len(self._search_text or "")
        if search_len == 0:
            search_len = len(match.line) - match.col

        end_col = match.col + max(search_len, 1)
        text_range = TextRange(match.lineno, match.col, match.lineno, end_col)

        editor = editor_notebook.show_file(match.path, text_range=text_range)
        if editor:
            editor.see_line(match.lineno)

        return "break"


def _show_dialog():
    global _ACTIVE_DIALOG
    workbench = get_workbench()
    if _ACTIVE_DIALOG is None or not _ACTIVE_DIALOG.winfo_exists():
        _ACTIVE_DIALOG = FindInFilesDialog(workbench)
        show_dialog(_ACTIVE_DIALOG, master=workbench, modal=False)
    else:
        _ACTIVE_DIALOG.lift()
        _ACTIVE_DIALOG.focus_force()
        _ACTIVE_DIALOG.set_initial_focus()


def load_plugin() -> None:
    workbench = get_workbench()

    workbench.add_command(
        "find_in_files",
        "edit",
        tr("Find in Files…"),
        _show_dialog,
        tester=None,
        default_sequence=select_sequence("<Control-Shift-F>", "<Command-Shift-F>"),
        group=80,
    )
