from ui.ctk_utils import pick_folder as _pick_folder
from paths import DirectoryPaths


def pick_folder(title: str = "Select destination folder") -> str | None:
    """Show a folder-picker dialog starting at DOCUMENTS. Returns path or None."""
    return _pick_folder(title=title, initial_dir=DirectoryPaths.DOCUMENTS)
