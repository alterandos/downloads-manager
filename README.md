# Downloads Manager

A lightweight Windows utility that auto-organizes new downloads and applies file-specific actions, with a modular architecture, minimal UI, and safe-by-default config.

## What it does
- Monitors your Downloads folder (or runs on-demand) and routes files to handlers.
- Moves, renames, and deduplicates files according to smart rules; prompts when needed.
- Runs quietly in the background with a system tray icon and logging.

## Key features
- **Modular handlers**: Add per-file-type logic (ZIP, PDF, etc.) via `handlers/` implementing `BaseHandler`.
- **Manual or automatic**: Batch process all files in Downloads or watch in real time via watchdog.
- **UI prompts**: Tkinter popups for overwrite/duplicates; optional tray icon with Quit.
- **Resource-aware**: psutil-based monitor warns on high CPU/RAM; daily 24h average logging.
- **Logging**: Timestamped, module-scoped logs to `logs/downloads_manager.log`.

## Architecture
- **Handlers**: `handlers/` with shared `BaseHandler` (`handle`, `handle_error`, `call_external`).
- **Paths and config**: Machine-specific paths in `paths.py` (gitignored); app settings and registry in `config.py`.
- **Utilities**: `utils/` for logging, date formatting, ZIP helpers, resource monitor; `ui/` for prompts and tray.

## Setup
1) Copy `paths.example.py` to `paths.py` and adjust for your machine (kept out of Git).
2) Create a venv and install deps:
```powershell
cd "<project_dir>"
./scripts/setup_venv.ps1
```
3) Activate (optional for manual runs):
```powershell
./.venv/Scripts/Activate.ps1
```

## Run
- Manual batch:
```powershell
# ensure MODE=0 in config.py
python main.py
```
- Automatic watcher:
```powershell
# ensure MODE=1 in config.py
python main.py
```

## Auto-start on login (Windows)
- Create a Startup shortcut (Win+R → `shell:startup`) with Target:
```
"%PROJECT_DIR%\.venv\Scripts\pythonw.exe" "%PROJECT_DIR%\main.py"
```
- Start in:
```
%PROJECT_DIR%
```
Note: Replace `%PROJECT_DIR%` with your actual project path.

## Security & privacy
- `paths.py` is gitignored; commit `paths.example.py` only.
- Logs stored locally under `logs/` (gitignored). Configure in `config.py`.

## Add a new handler
1) Implement a class in `handlers/` that extends `BaseHandler`.
2) Register the extension in `config.py` (`HANDLER_REGISTRY`).
3) (Optional) Use shared helpers from `utils/` and `ui/`.

## Tech stack
- Python, watchdog, Tkinter, psutil, pystray, Pillow.
