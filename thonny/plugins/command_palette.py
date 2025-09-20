import logging
import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Optional

from thonny import get_workbench, ui_utils
from thonny.languages import tr
from thonny.misc_utils import running_on_mac_os
from thonny.ui_utils import CommonDialogEx, ThemedListbox

logger = logging.getLogger(__name__)

_active_palette: Optional["CommandPaletteDialog"] = None


class CommandPaletteDialog(CommonDialogEx):
    def __init__(self, master: tk.Tk):
        super().__init__(master=master, skip_tk_dialog_attributes=running_on_mac_os())

        self.title(tr("Command Palette…"))
        self.resizable(width=tk.TRUE, height=tk.TRUE)

        self.main_frame.configure(padding=self.get_medium_padding())
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=1)

        self._search_var = tk.StringVar()
        self._search_var.trace_add("write", self._on_search_change)

        self._search_entry = ttk.Entry(self.main_frame, textvariable=self._search_var)
        self._search_entry.grid(row=0, column=0, columnspan=2, sticky="ew")
        self._search_entry.bind("<Down>", self._focus_listbox, True)
        self._search_entry.bind("<Return>", self._activate_from_entry, True)
        self._search_entry.bind("<KP_Enter>", self._activate_from_entry, True)

        self._listbox = ThemedListbox(
            self.main_frame,
            activestyle="none",
            exportselection=False,
            selectmode=tk.SINGLE,
            height=12,
        )
        self._listbox.grid(
            row=1,
            column=0,
            sticky="nsew",
            pady=(self.get_small_padding(), 0),
        )
        self._listbox.bind("<Return>", self._activate_selection, True)
        self._listbox.bind("<KP_Enter>", self._activate_selection, True)
        self._listbox.bind("<Double-Button-1>", self._activate_selection, True)

        scrollbar = ttk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self._listbox.yview)
        scrollbar.grid(row=1, column=1, sticky="nsw")
        self._listbox.configure(yscrollcommand=scrollbar.set)

        self._theme_binding = self.bind("<<ThemeChanged>>", self._on_theme_changed, True)
        self._on_theme_changed()

        self._all_commands: List[Dict[str, object]] = []
        self._filtered_commands: List[Dict[str, object]] = []
        self._refresh_commands()

    def destroy(self) -> None:
        if hasattr(self, "_theme_binding") and self._theme_binding is not None:
            self.unbind("<<ThemeChanged>>", self._theme_binding)
            self._theme_binding = None
        super().destroy()

    def set_initial_focus(self, node=None) -> bool:
        self._search_entry.focus_set()
        self._search_entry.selection_range(0, tk.END)
        return True

    def _on_theme_changed(self, event=None) -> None:
        style = ttk.Style()
        background = style.lookup("TFrame", "background")
        if background:
            self.configure(background=background)

    def _on_search_change(self, *args) -> None:
        self._refresh_commands()

    def _refresh_commands(self) -> None:
        self._all_commands = self._prepare_commands()
        terms = [part for part in self._search_var.get().lower().split() if part]
        self._filtered_commands = []
        selected_id = self._get_selected_command_id()

        self._listbox.delete(0, tk.END)
        for command in self._all_commands:
            if terms and not all(term in command["search_text"] for term in terms):
                continue

            if not self._command_is_enabled(command):
                continue

            self._filtered_commands.append(command)
            self._listbox.insert(tk.END, command["display_text"])

        if not self._filtered_commands:
            return

        index = 0
        if selected_id is not None:
            for i, command in enumerate(self._filtered_commands):
                if command["id"] == selected_id:
                    index = i
                    break

        self._select_index(index)

    def _prepare_commands(self) -> List[Dict[str, object]]:
        workbench = get_workbench()
        prepared: List[Dict[str, object]] = []
        for command in workbench.get_registered_commands():
            dispatcher = command.get("dispatcher")
            if dispatcher is None:
                continue

            label = command.get("label") or command.get("command_id") or ""
            menu_name = command.get("menu_name") or ""
            menu_display = self._get_menu_display(menu_name)
            accelerator = command.get("accelerator") or ""
            command_id = command.get("command_id") or ""
            tester = command.get("tester")

            display_parts = [label]
            if menu_display:
                display_parts.append(f"[{menu_display}]")
            if accelerator:
                display_parts.append(accelerator)

            search_text = " ".join(
                part.lower()
                for part in [label, command_id, menu_name, menu_display, accelerator]
                if part
            )

            prepared.append(
                {
                    "id": command_id,
                    "label": label,
                    "menu_name": menu_name,
                    "menu_display": menu_display,
                    "accelerator": accelerator,
                    "tester": tester,
                    "dispatcher": dispatcher,
                    "display_text": "    ".join(display_parts),
                    "search_text": search_text,
                }
            )

        prepared.sort(key=lambda item: (item["label"].lower(), item["id"].lower()))
        return prepared

    def _get_menu_display(self, name: str) -> str:
        if not name:
            return ""
        return name.replace("_", " ").title()

    def _command_is_enabled(self, command: Dict[str, object]) -> bool:
        tester = command.get("tester")
        if tester is None:
            return True

        try:
            return bool(tester())
        except Exception:
            logger.exception("Command tester failed for %s", command.get("id"))
            return False

    def _get_selected_command_id(self) -> Optional[str]:
        selection = self._listbox.curselection()
        if not selection or not self._filtered_commands:
            return None
        try:
            return self._filtered_commands[selection[0]]["id"]
        except IndexError:
            return None

    def _select_index(self, index: int) -> None:
        if not self._filtered_commands:
            return
        index = max(0, min(index, len(self._filtered_commands) - 1))
        self._listbox.selection_clear(0, tk.END)
        self._listbox.selection_set(index)
        self._listbox.activate(index)
        self._listbox.see(index)

    def _focus_listbox(self, event=None):
        if self._filtered_commands:
            self._select_index(0)
            self._listbox.focus_set()
        return "break"

    def _activate_from_entry(self, event=None):
        if not self._filtered_commands:
            return "break"
        self._select_index(0)
        self._execute_selected()
        return "break"

    def _activate_selection(self, event=None):
        self._execute_selected()
        return "break"

    def _execute_selected(self) -> None:
        if not self._filtered_commands:
            return

        selection = self._listbox.curselection()
        index = selection[0] if selection else 0
        command = self._filtered_commands[index]

        if not self._command_is_enabled(command):
            return

        dispatcher = command.get("dispatcher")
        if dispatcher is None:
            return

        self.destroy()
        try:
            dispatcher(None)
        except Exception:
            logger.exception("Error executing command palette action %s", command.get("id"))


def open_command_palette() -> None:
    global _active_palette
    workbench = get_workbench()
    if _active_palette and _active_palette.winfo_exists():
        _active_palette.lift()
        _active_palette.focus_force()
        _active_palette.set_initial_focus()
        return

    dialog = CommandPaletteDialog(workbench)
    _active_palette = dialog
    try:
        ui_utils.show_dialog(dialog, master=workbench, modal=True)
    finally:
        _active_palette = None


def load_plugin() -> None:
    default_sequence = "<Command-Shift-P>" if running_on_mac_os() else "<Control-Shift-P>"
    get_workbench().add_command(
        "open_command_palette",
        "view",
        tr("Command Palette…"),
        open_command_palette,
        default_sequence=default_sequence,
        group=5,
    )
