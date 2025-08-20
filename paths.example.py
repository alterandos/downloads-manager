# Copy this file to paths.py and adjust to your environment.
# Do NOT commit your real paths.py to version control.

from pathlib import Path

class DirectoryPaths:
    # Base directories
    HOME = str(Path.home()).replace('/', '\\') + '\\'
    DOCUMENTS = f"{HOME}Documents\\"
    DOWNLOADS = f"{HOME}Downloads\\"

    # Admin/Health example
    ADMIN = f"{DOCUMENTS}Admin\\"
    RECEIPTS = F"{ADMIN}Receipts\\"
    HEALTH = f"{ADMIN}Health\\"
    PHYSIO = f"{HEALTH}Physio\\"

    # Games example
    GAMES = f"{DOCUMENTS}Games\\"

