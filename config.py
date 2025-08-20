from handlers.pdf import PDFHandler
from handlers.zip import ZIPHandler
from paths import DirectoryPaths
import os

# Runtime configuration
MODE = 1  # 0 = manual, 1 = automated
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
LOG_FILE = os.path.join(PROJECT_ROOT, "logs", "downloads_manager.log")
TRAY_ICON_PATH = os.path.join(PROJECT_ROOT, "assets", "tray_icon.png")

# Resource monitor configuration
MONITOR_CPU_THRESHOLD_PERCENT = 5.0
MONITOR_RSS_THRESHOLD_MB = 35.0
MONITOR_INTERVAL_SECONDS = 30
MONITOR_REPORT_INTERVAL_SECONDS = 86400.0
MONITOR_WINDOW_SECONDS = 86400.0

# Handler registry
HANDLER_REGISTRY = {
    '.zip': ZIPHandler,
    '.pdf': PDFHandler,
    # Add more as needed
} 