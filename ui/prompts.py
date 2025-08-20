import tkinter as tk
from tkinter import messagebox


def confirm_overwrite(filename: str, dest_dir: str) -> bool:
    root = tk.Tk()
    root.withdraw()
    return messagebox.askyesno(
        "File Exists",
        f"{filename} already exists in {dest_dir}\nReplace the existing file?"
    )


def confirm_delete_zip_no_extracted() -> bool:
    root = tk.Tk()
    root.withdraw()
    return messagebox.askyesno(
        "No Maps Extracted",
        "No target files were extracted from this zip.\nDelete the zip file anyway?"
    ) 