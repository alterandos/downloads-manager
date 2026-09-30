"""
Shared customtkinter dialog utilities.

All dialogs in this app go through these helpers so the root window lifecycle,
topmost flag, and appearance mode are handled consistently in one place.
"""
import customtkinter as ctk
from tkinter import filedialog

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")


def _make_hidden_root() -> ctk.CTk:
    root = ctk.CTk()
    root.withdraw()
    root.attributes('-topmost', True)
    return root


def ask_yes_no(title: str, message: str) -> bool:
    """Show a Yes/No dialog. Returns True if the user clicks Yes."""
    result = [False]
    root = _make_hidden_root()

    dialog = ctk.CTkToplevel(root)
    dialog.title(title)
    dialog.resizable(False, False)
    dialog.attributes('-topmost', True)
    dialog.grab_set()
    dialog.focus_force()

    ctk.CTkLabel(dialog, text=message, wraplength=320).pack(padx=24, pady=(18, 8))

    btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
    btn_frame.pack(padx=24, pady=(8, 18))

    def yes():
        result[0] = True
        root.quit()

    def no():
        root.quit()

    ctk.CTkButton(btn_frame, text="Yes", command=yes, width=90).pack(side='left', padx=6)
    ctk.CTkButton(btn_frame, text="No", command=no, width=90).pack(side='left', padx=6)
    dialog.protocol("WM_DELETE_WINDOW", no)

    try:
        root.mainloop()
    finally:
        root.destroy()

    return result[0]


def show_info(title: str, message: str) -> None:
    """Show a dismissable info dialog."""
    root = _make_hidden_root()

    dialog = ctk.CTkToplevel(root)
    dialog.title(title)
    dialog.resizable(False, False)
    dialog.attributes('-topmost', True)
    dialog.grab_set()
    dialog.focus_force()

    ctk.CTkLabel(dialog, text=message, wraplength=320).pack(padx=24, pady=(18, 8))
    ctk.CTkButton(dialog, text="OK", command=root.quit, width=90).pack(pady=(8, 18))
    dialog.protocol("WM_DELETE_WINDOW", root.quit)

    try:
        root.mainloop()
    finally:
        root.destroy()


def show_error(title: str, message: str) -> None:
    show_info(title, message)


def pick_folder(title: str = "Select destination folder", initial_dir: str | None = None) -> str | None:
    """Show a native folder-picker dialog. Returns the selected path or None if cancelled."""
    from utils.logging_setup import get_logger
    logger = get_logger(__name__)

    root = _make_hidden_root()
    root.focus_force()

    try:
        kwargs = {"title": title, "parent": root}
        if initial_dir:
            kwargs["initialdir"] = initial_dir
        folder = filedialog.askdirectory(**kwargs)
        if folder:
            logger.info(f"User selected folder: {folder}")
            return folder
        logger.info("User cancelled folder selection")
        return None
    finally:
        root.destroy()
