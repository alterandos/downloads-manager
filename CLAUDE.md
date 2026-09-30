# Downloads Manager — Project Overview

## Purpose
An always-on Windows background utility that watches the Downloads folder and automatically routes or processes files as they arrive. Minimal user interaction is the goal — prompts appear only when the system cannot determine what to do automatically.

## Tech Stack
| Package | Purpose |
|---|---|
| `watchdog` | Filesystem event monitoring |
| `customtkinter` | Modern UI dialogs (replaces raw tkinter) |
| `pdfplumber` | PDF text extraction for invoice classification |
| `pystray` + `Pillow` | System tray icon |
| `psutil` | Resource usage monitoring |
| `python-dateutil` | Date arithmetic (month subtraction for statement naming) |

## Architecture

### Entry point
`main.py` — sets up logging, starts the watchdog observer on the Downloads folder, starts the system tray icon and resource monitor, then sleeps until quit is requested.

### Handler system (hierarchical)
Files are routed through a registry keyed by extension (`HANDLER_REGISTRY` in `config.py`). Each handler subclasses `BaseHandler` (ABC in `handlers/base.py`) and implements two methods: `handle(event)` and `handle_error(event, error)`.

Handlers are hierarchical — a top-level handler inspects a file and delegates to a more specific handler. Unknown subtypes fall through to `DefaultFileHandler` via `BaseHandler.handle_unknown_subtype()`.

```
Extension        → Handler           → Sub-handler
─────────────────────────────────────────────────────────
.zip             → ZIPHandler        → HeroesMapHandler (if contains .h3m)
.pdf             → PDFHandler        → InvoiceHandler   (if "invoice" in filename)
                                     → (Rosemary statement regex match)
.gpx/.gp4/.gp5  → GPHandler         → MoveFileHandler
*                → DefaultFileHandler  (prompts user with location selector)
```

### Ignored extensions
`IGNORED_EXTENSIONS` in `config.py` — files with these extensions are silently skipped with no prompts. Used for in-progress downloads (`.crdownload`, `.part`), system files, executables, etc.

### Debouncing
File modifications are debounced with a 1-second delay (`threading.Timer`) to avoid triggering on in-progress writes. A newer event for the same file cancels the pending timer.

### Modes
- `MODE = 0` — one-shot: process all existing files in Downloads and exit
- `MODE = 1` — daemon: watch folder and process new/modified files continuously

## Key Files

| File | Role |
|---|---|
| `main.py` | Entry point, watchdog setup, `_dispatch_file()` |
| `config.py` | `HANDLER_REGISTRY`, `IGNORED_EXTENSIONS`, resource monitor config |
| `config_locations.py` | Pre-loaded destination lists for UI pickers; `resolve_locations()` |
| `paths.py` | **Gitignored.** User-specific `DirectoryPaths` class. Copy from `paths.example.py`. |
| `handlers/base.py` | `BaseHandler` ABC |
| `handlers/invoice/` | Tiered invoice classification pipeline |
| `ui/ctk_utils.py` | Shared customtkinter dialog utilities |
| `ui/location_selector.py` | Multi-option destination picker dialog |
| `utils/file_ops.py` | `move_file()` with auto-rename on collision |

## Configuration

### `paths.py` (gitignored — do not commit)
Defines `DirectoryPaths` with all destination folder paths. Copy `paths.example.py`, rename to `paths.py`, and fill in your actual paths.

### `config.py`
- `HANDLER_REGISTRY` — maps extension strings to handler classes
- `IGNORED_EXTENSIONS` — set of extensions to skip entirely
- `MODE` — 0 or 1
- Resource monitor thresholds (CPU %, RSS MB, intervals)

### `config_locations.py`
Lists of `DirectoryPaths` attribute name strings used to populate location pickers in dialogs. `resolve_locations(keys)` converts these to `(label, path)` tuples at runtime. Stays in git; actual paths live in `paths.py`.

## UI (`ui/`)
All dialogs use **customtkinter** with `appearance_mode = "system"` (auto dark/light). Shared low-level utilities (`ask_yes_no`, `show_info`, `show_error`, `pick_folder`) live in `ui/ctk_utils.py`. Multi-option destination picker is in `ui/location_selector.py`.

## Invoice Classification (`handlers/invoice/`)
Tiered pipeline — each stage only runs if the previous one didn't produce a confident match:

1. **Filename keywords** (`keyword_rules.FILENAME_KEYWORDS`) — instant, no file read
2. **PDF text keywords** (`keyword_rules.TEXT_KEYWORDS`) — extracts first ~2000 chars via `pdfplumber`
3. **LLM fallback** (`llm_client.classify()`) — **stub, not yet implemented.** See `backlog.md`.

The result is always presented to the user as a suggestion in the location picker — never silently auto-routed for financial documents.

To add a new invoice type:
1. Add keyword lists to `handlers/invoice/keyword_rules.py`
2. Add the type → `DirectoryPaths` key mapping to `config_locations.py` → `INVOICE_TYPE_TO_KEY`
3. Add the matching path to your `paths.py`

## Adding a New Top-Level Handler
1. Create `handlers/my_type.py` subclassing `BaseHandler`
2. Implement `handle(event)` and `handle_error(event, error)`
3. Register in `config.py` → `HANDLER_REGISTRY`
4. Optionally add a `MY_TYPE_LOCATION_KEYS` list to `config_locations.py`

## Running
```powershell
python main.py
```
Requires `paths.py` to exist (copy from `paths.example.py`).

Install dependencies:
```powershell
pip install -r requirements.in
```
