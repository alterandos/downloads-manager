import os
import time
import threading
import watchdog.events
import watchdog.observers
from config import HANDLER_REGISTRY, MODE, LOG_FILE, TRAY_ICON_PATH, MONITOR_CPU_THRESHOLD_PERCENT, MONITOR_RSS_THRESHOLD_MB, MONITOR_INTERVAL_SECONDS, MONITOR_REPORT_INTERVAL_SECONDS, MONITOR_WINDOW_SECONDS, IGNORED_EXTENSIONS
from paths import DirectoryPaths
from utils.logging_setup import setup_logging, get_logger
from utils.monitor import start_resource_monitor
from ui.tray import start_tray
from handlers.default import DefaultFileHandler
from utils.skip_store import is_skipped

logger = get_logger(__name__)

# Track pending processing timers and last modify times for debouncing
_pending_timers = {}  # {file_path: timer}
_last_modify_time = {}  # {file_path: timestamp}

# Last seen (size, mtime) per file. Windows fires modify events for mere reads
# (last-access / attribute updates, e.g. Explorer generating thumbnails when the
# folder is opened), so events whose signature hasn't changed are ignored.
_file_signatures = {}  # {file_path: (size, mtime_ns)}


def _signature(file_path: str):
    try:
        st = os.stat(file_path)
    except OSError:
        return None
    return (st.st_size, st.st_mtime_ns)


def _snapshot_existing_files(root: str) -> None:
    """Record signatures of files already present so they aren't reprocessed on access."""
    for dirpath, _dirs, files in os.walk(root):
        for name in files:
            path = os.path.join(dirpath, name)
            sig = _signature(path)
            if sig is not None:
                _file_signatures[path] = sig


def _dispatch_file(file_path: str) -> None:
    """Look up the appropriate handler for a file and invoke it."""
    ext = os.path.splitext(file_path)[1].lower()

    if ext in IGNORED_EXTENSIONS:
        logger.debug(f"Ignoring {ext} file: {os.path.basename(file_path)}")
        return

    if is_skipped(file_path):
        logger.debug(f"Ignoring previously skipped file: {os.path.basename(file_path)}")
        return

    handler_cls = HANDLER_REGISTRY.get(ext)
    handler = handler_cls() if handler_cls else DefaultFileHandler()

    class _Event:
        src_path = file_path

    event = _Event()
    logger.info(f"Dispatching {ext or '(no ext)'}: {os.path.basename(file_path)} → {type(handler).__name__}")
    try:
        handler.handle(event)
    except Exception as e:
        try:
            handler.handle_error(event, e)
        except Exception as err:
            logger.error(f"Unhandled exception in {type(handler).__name__}.handle_error for {os.path.basename(file_path)}: {err}")


def _process_file(event, scheduled_time):
    """Process a file after debounce delay."""
    file_path = event.src_path

    if not os.path.isfile(file_path):
        return

    # Discard if a newer modify event arrived after we were scheduled
    if _last_modify_time.get(file_path, 0) > scheduled_time:
        logger.debug(f"Skipping {os.path.basename(file_path)} - newer modify event detected")
        return

    _pending_timers.pop(file_path, None)
    _last_modify_time.pop(file_path, None)

    sig = _signature(file_path)
    if sig is not None and _file_signatures.get(file_path) == sig:
        return  # already handled this exact content
    _file_signatures[file_path] = sig

    _dispatch_file(file_path)


class DownloadHandler(watchdog.events.FileSystemEventHandler):
    def on_modified(self, event):
        self._schedule(event.src_path, "on_modified")

    def on_moved(self, event):
        # Browsers finish a download by renaming e.g. foo.pdf.crdownload -> foo.pdf
        _file_signatures.pop(event.src_path, None)
        self._schedule(event.dest_path, "on_moved")

    def on_deleted(self, event):
        _file_signatures.pop(event.src_path, None)

    def _schedule(self, file_path, event_name):
        if not os.path.isfile(file_path):
            return

        sig = _signature(file_path)
        if sig is not None and _file_signatures.get(file_path) == sig:
            return  # read/attribute-only event — content unchanged

        current_time = time.time()

        if file_path in _pending_timers:
            _pending_timers[file_path].cancel()

        _last_modify_time[file_path] = current_time

        class _Event:
            src_path = file_path

        timer = threading.Timer(1.0, _process_file, args=(_Event, current_time))
        timer.start()
        _pending_timers[file_path] = timer

        logger.info(f"Event: {event_name} | filename={os.path.basename(file_path)} | scheduled processing in 1s")


def process_all_files_in_downloads():
    for filename in os.listdir(DirectoryPaths.DOWNLOADS):
        filepath = os.path.join(DirectoryPaths.DOWNLOADS, filename)
        if os.path.isfile(filepath):
            _dispatch_file(filepath)


if __name__ == "__main__":
    setup_logging(log_file=LOG_FILE)
    if MODE == 0:
        process_all_files_in_downloads()
    else:
        fd_downloads = DirectoryPaths.DOWNLOADS
        _snapshot_existing_files(fd_downloads)
        event_handler = DownloadHandler()
        observer = watchdog.observers.Observer()
        observer.schedule(event_handler, path=fd_downloads, recursive=True)
        observer.start()

        stop_event = threading.Event()

        def request_quit(icon=None):
            logger.info("Quitting Downloads Manager...")
            stop_event.set()
            if icon is not None:
                try:
                    icon.stop()
                except Exception:
                    pass

        start_resource_monitor(
            cpu_threshold_percent=MONITOR_CPU_THRESHOLD_PERCENT,
            rss_threshold_mb=MONITOR_RSS_THRESHOLD_MB,
            interval_seconds=MONITOR_INTERVAL_SECONDS,
            stop_event=stop_event,
            report_interval_seconds=MONITOR_REPORT_INTERVAL_SECONDS,
            window_seconds=MONITOR_WINDOW_SECONDS,
        )

        start_tray(request_quit, icon_path=TRAY_ICON_PATH)

        try:
            while not stop_event.is_set():
                time.sleep(1)
        except KeyboardInterrupt:
            request_quit()
        finally:
            observer.stop()
            observer.join()
