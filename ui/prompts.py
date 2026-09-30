from ui.ctk_utils import ask_yes_no


def confirm_overwrite(filename: str, dest_dir: str) -> bool:
    return ask_yes_no(
        "File Already Exists",
        f"{filename} already exists in:\n{dest_dir}\n\nReplace the existing file?",
    )


def confirm_delete_zip_no_extracted() -> bool:
    return ask_yes_no(
        "No Maps Extracted",
        "No target files were extracted from this zip.\nDelete the zip file anyway?",
    )
