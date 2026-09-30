# Copy this file to paths.py and adjust to your environment.
# Do NOT commit your real paths.py to version control.

from pathlib import Path

USER = 'Tom Johnson'

class DirectoryPaths:
    # Base directories
    USERS = r'C:\\Users\\'
    ANSON = f'{USERS}{USER}\\'
    DOCUMENTS = f'{ANSON}Documents\\'
    DOWNLOADS = f'{ANSON}Downloads\\'

    # Admin/Health example
    ADMIN = f"{DOCUMENTS}Admin\\"
    RECEIPTS = F"{ADMIN}Receipts\\"
    HEALTH = f"{ADMIN}Health\\"
    PHYSIO = f"{HEALTH}Physio\\"

    # Games example
    GAMES = f"{DOCUMENTS}Games\\"

