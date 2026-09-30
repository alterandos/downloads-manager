from handlers.pdf import PDFHandler
from handlers.zip import ZIPHandler
from handlers.gp import GPHandler
from paths import DirectoryPaths
import os

# Runtime configuration
MODE = 1  # 0 = manual, 1 = automated
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
LOG_FILE = os.path.join(PROJECT_ROOT, "logs", "downloads_manager.log")
TRAY_ICON_PATH = os.path.join(PROJECT_ROOT, "assets", "tray_icon.png")

# Completely ignored file extensions (no processing, no prompts)
IGNORED_EXTENSIONS = {
    '.tmp',      # Temporary files
    '.crdownload',  # Chrome download in progress
    '.part',    # Firefox download in progress
    '.download', # Safari download in progress
    '.aria2',   # Aria2 download in progress
    '.torrent', # BitTorrent files
    '.lnk',     # Windows shortcuts
    '.url',     # Internet shortcuts
    '.desktop', # Linux desktop files
    '.DS_Store', # macOS system files
    '.Thumbs.db', # Windows thumbnail cache
    '.tmp',     # General temporary files
    '.bak',     # Backup files
    '.old',     # Old/backup files
    '.swp',     # Vim swap files
    '.lock',    # Lock files
    '.ini',     # Ini files
    '.exe',     # Executable files
}

# Resource monitor configuration
MONITOR_CPU_THRESHOLD_PERCENT = 5.0
MONITOR_RSS_THRESHOLD_MB = 35.0
MONITOR_INTERVAL_SECONDS = 30
MONITOR_REPORT_INTERVAL_SECONDS = 86400.0
MONITOR_WINDOW_SECONDS = 86400.0

GP_EXTENSIONS = {'.gpx', '.gp4', '.gp5'}

# Handler registry
HANDLER_REGISTRY = {
    '.zip': ZIPHandler,
    '.pdf': PDFHandler,
    **{ext: GPHandler for ext in GP_EXTENSIONS},
    # DefaultFileHandler will be used for any extension not explicitly handled
} 