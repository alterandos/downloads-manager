"""
Multi-option destination picker built with customtkinter.

select_location() shows one button per option.
  - suggestion:    highlights + sorts the recommended choice to the top; Enter confirms it.
  - allow_browse:  adds a Browse button that opens a native folder picker.
  - save_to_list:  if set (e.g. "DEFAULT_LOCATION_KEYS"), a post-browse dialog offers to
                   save the chosen folder as a named quick-access location.
"""
import os
import customtkinter as ctk
from tkinter import filedialog
from typing import Iterable, Optional, Tuple
from utils.logging_setup import get_logger

logger = get_logger(__name__)

LocationOption = Tuple[str, str]

_SUGGEST_FG    = ("#1a73e8", "#4a9eff")
_SUGGEST_HOVER = ("#1558b0", "#3a8eef")


def select_location(
    options: Iterable[LocationOption],
    title: str = "Select destination",
    allow_browse: bool = False,
    browse_initial_dir: Optional[str] = None,
    suggestion: Optional[str] = None,
    save_to_list: Optional[str] = None,
) -> Optional[str]:
    """
    Show a picker window with one button per option.

    options:       iterable of (label, path)
    suggestion:    path from options to highlight and sort to top; Enter confirms it
    allow_browse:  adds a Browse button that opens a native folder picker
    save_to_list:  variable name in config_locations.py to offer saving a browsed path to
    returns:       selected path, or None if cancelled/closed
    """
    opts = list(options)

    # Sort: suggestion first, everything else in original order
    if suggestion:
        opts.sort(key=lambda o: 0 if o[1] == suggestion else 1)

    if not opts and not allow_browse:
        logger.warning("select_location called with no options and allow_browse=False")
        return None

    selected: list[str] = []

    root = ctk.CTk()
    root.withdraw()
    root.attributes('-topmost', True)

    win = ctk.CTkToplevel(root)
    win.title("Downloads Manager")
    win.resizable(False, False)
    win.attributes('-topmost', True)
    win.grab_set()
    try:
        win.focus_force()
    except Exception:
        pass

    # ── Header ────────────────────────────────────────────────────────────────
    header = ctk.CTkFrame(win, fg_color="transparent")
    header.pack(fill='x', padx=20, pady=(16, 4))

    lines = title.split('\n', 1)
    ctk.CTkLabel(header, text=lines[0],
                 font=ctk.CTkFont(size=14, weight="bold"), anchor='w').pack(fill='x')
    if len(lines) > 1:
        ctk.CTkLabel(header, text=lines[1], font=ctk.CTkFont(size=12),
                     text_color=("gray40", "gray70"), anchor='w').pack(fill='x', pady=(2, 0))

    ctk.CTkFrame(win, height=1, fg_color=("gray80", "gray30")).pack(fill='x', padx=20, pady=(8, 4))

    # ── Option buttons ─────────────────────────────────────────────────────────
    opts_frame = ctk.CTkFrame(win, fg_color="transparent")
    opts_frame.pack(fill='x', padx=20, pady=4)

    top_handler = None  # Will hold the callable for the Enter binding

    def make_handler(path: str):
        def _h():
            selected.clear()
            selected.append(path)
            root.quit()
        return _h

    for idx, (label, path) in enumerate(opts):
        is_top = (idx == 0 and suggestion is not None and path == suggestion)
        row = ctk.CTkFrame(opts_frame, fg_color="transparent")
        row.pack(fill='x', pady=3)

        btn_label = label
        if is_top:
            btn_label += "  ↵"   # visual hint that Enter confirms this

        btn_kwargs: dict = dict(
            text=btn_label,
            command=make_handler(path),
            anchor='w',
            width=200,
        )
        if is_top:
            btn_kwargs["fg_color"]    = _SUGGEST_FG
            btn_kwargs["hover_color"] = _SUGGEST_HOVER

        btn = ctk.CTkButton(row, **btn_kwargs)
        btn.pack(side='left')

        if is_top:
            top_handler = make_handler(path)
            win.after(50, btn.focus_set)

        ctk.CTkLabel(row, text=path, text_color=("gray40", "gray70"),
                     font=ctk.CTkFont(size=11), anchor='w').pack(side='left', padx=(10, 0))

    # ── Browse & Skip ──────────────────────────────────────────────────────────
    ctk.CTkFrame(win, height=1, fg_color=("gray80", "gray30")).pack(fill='x', padx=20, pady=(8, 4))

    footer = ctk.CTkFrame(win, fg_color="transparent")
    footer.pack(fill='x', padx=20, pady=(4, 16))

    if allow_browse:
        existing_paths = {path for _, path in opts}

        def on_browse():
            folder = filedialog.askdirectory(
                title="Select destination folder",
                initialdir=browse_initial_dir,
                parent=root,
            )
            if not folder:
                return

            folder = os.path.normpath(folder)

            # Offer to save only if this is a new location
            if save_to_list and folder not in existing_paths:
                _show_save_dialog(root, folder, save_to_list)

            selected.clear()
            selected.append(folder)
            root.quit()

        ctk.CTkButton(
            footer, text="Browse...", command=on_browse, width=110,
            fg_color=("gray70", "gray30"), hover_color=("gray60", "gray40"),
            text_color=("gray10", "gray90"),
        ).pack(side='left')

    def on_skip():
        logger.info("Location selection skipped")
        root.quit()

    ctk.CTkButton(
        footer, text="Skip", command=on_skip, width=90,
        fg_color="transparent", hover_color=("gray85", "gray25"),
        text_color=("gray30", "gray70"), border_width=1,
        border_color=("gray70", "gray40"),
    ).pack(side='right')

    win.protocol("WM_DELETE_WINDOW", on_skip)

    # Bind Enter to the top/suggested option (if one exists)
    if top_handler:
        win.bind('<Return>', lambda e: top_handler())

    try:
        root.mainloop()
    finally:
        root.destroy()

    result = selected[0] if selected else None
    if result:
        logger.info(f"Location selected: {result}")
    return result


def _show_save_dialog(parent: ctk.CTk, folder: str, list_name: str) -> None:
    """
    Show a blocking child dialog offering to save a browsed folder as a quick-access location.
    Calls location_manager.save_location() if the user confirms.
    """
    from utils.location_manager import save_location, name_to_key

    default_name = os.path.basename(folder).replace('_', ' ').title()

    dialog = ctk.CTkToplevel(parent)
    dialog.title("Save to quick access?")
    dialog.resizable(False, False)
    dialog.attributes('-topmost', True)
    dialog.grab_set()
    try:
        dialog.focus_force()
    except Exception:
        pass

    # ── Save checkbox ──────────────────────────────────────────────────────────
    save_var = ctk.BooleanVar(value=True)

    top = ctk.CTkFrame(dialog, fg_color="transparent")
    top.pack(fill='x', padx=20, pady=(16, 4))

    ctk.CTkCheckBox(
        top,
        text="Save to quick access",
        variable=save_var,
        font=ctk.CTkFont(size=13),
        command=lambda: _toggle_name_frame(save_var, name_frame),
    ).pack(anchor='w')

    ctk.CTkLabel(
        top,
        text=folder,
        font=ctk.CTkFont(size=11),
        text_color=("gray40", "gray70"),
        anchor='w',
    ).pack(fill='x', pady=(4, 0))

    ctk.CTkFrame(dialog, height=1, fg_color=("gray80", "gray30")).pack(fill='x', padx=20, pady=(10, 4))

    # ── Name field (shown when checkbox is ticked) ─────────────────────────────
    name_frame = ctk.CTkFrame(dialog, fg_color="transparent")
    name_frame.pack(fill='x', padx=20, pady=4)

    ctk.CTkLabel(name_frame, text="Name:", anchor='w').pack(fill='x')
    name_var = ctk.StringVar(value=default_name)
    name_entry = ctk.CTkEntry(name_frame, textvariable=name_var, width=280)
    name_entry.pack(fill='x', pady=(4, 0))
    name_entry.focus_set()
    name_entry.select_range(0, 'end')

    # ── Buttons ────────────────────────────────────────────────────────────────
    ctk.CTkFrame(dialog, height=1, fg_color=("gray80", "gray30")).pack(fill='x', padx=20, pady=(10, 4))

    btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
    btn_frame.pack(fill='x', padx=20, pady=(4, 16))

    def on_save():
        if save_var.get():
            label = name_var.get().strip()
            if label:
                ok = save_location(label, folder, list_name)
                if not ok:
                    logger.warning(f"save_location failed for {folder!r}")
        dialog.destroy()

    def on_skip():
        dialog.destroy()

    ctk.CTkButton(btn_frame, text="Save", command=on_save, width=90).pack(side='left', padx=(0, 8))
    ctk.CTkButton(
        btn_frame, text="Not now", command=on_skip, width=90,
        fg_color="transparent", hover_color=("gray85", "gray25"),
        text_color=("gray30", "gray70"), border_width=1,
        border_color=("gray70", "gray40"),
    ).pack(side='left')

    dialog.bind('<Return>', lambda e: on_save())
    parent.wait_window(dialog)


def _toggle_name_frame(save_var: ctk.BooleanVar, name_frame: ctk.CTkFrame) -> None:
    if save_var.get():
        name_frame.pack(fill='x', padx=20, pady=4)
    else:
        name_frame.pack_forget()
