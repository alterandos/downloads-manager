import os
import time
import threading
import watchdog.events
import watchdog.observers
from config import HANDLER_REGISTRY, MODE, LOG_FILE, TRAY_ICON_PATH, MONITOR_CPU_THRESHOLD_PERCENT, MONITOR_RSS_THRESHOLD_MB, MONITOR_INTERVAL_SECONDS, MONITOR_REPORT_INTERVAL_SECONDS, MONITOR_WINDOW_SECONDS
from paths import DirectoryPaths
from utils.logging_setup import setup_logging, get_logger
from utils.monitor import start_resource_monitor
from ui.tray import start_tray

logger = get_logger(__name__)

class DownloadHandler(watchdog.events.FileSystemEventHandler):
	def on_modified(self, event):
		if os.path.isfile(event.src_path):
			ext = os.path.splitext(event.src_path)[1].lower()
			handler_cls = HANDLER_REGISTRY.get(ext)
			if handler_cls:
				handler = handler_cls()
				try:
					logger.info(f"Handling {ext} file: {os.path.basename(event.src_path)}")
					handler.handle(event)
				except Exception as e:
					handler.handle_error(event, e)
			else:
				logger.warning(f'No handler for file type: {ext}')

def process_all_files_in_downloads():
	downloads_dir = DirectoryPaths.DOWNLOADS
	for filename in os.listdir(downloads_dir):
		filepath = os.path.join(downloads_dir, filename)
		if os.path.isfile(filepath):
			ext = os.path.splitext(filename)[1].lower()
			handler_cls = HANDLER_REGISTRY.get(ext)
			if handler_cls:
				handler = handler_cls()
				class DummyEvent:
					src_path = filepath
				try:
					logger.info(f"Manually handling {ext} file: {filename}")
					handler.handle(DummyEvent())
				except Exception as e:
					handler.handle_error(DummyEvent(), e)
			else:
				logger.warning(f'No handler for file type: {ext}')

if __name__ == "__main__":
	setup_logging(log_file=LOG_FILE)
	if MODE == 0:
		process_all_files_in_downloads()
	else:
		fd_downloads = DirectoryPaths.DOWNLOADS
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

		# Start resource monitor (warn if thresholds exceeded)
		start_resource_monitor(
			cpu_threshold_percent=MONITOR_CPU_THRESHOLD_PERCENT,
			rss_threshold_mb=MONITOR_RSS_THRESHOLD_MB,
			interval_seconds=MONITOR_INTERVAL_SECONDS,
			stop_event=stop_event,
			report_interval_seconds=MONITOR_REPORT_INTERVAL_SECONDS,
			window_seconds=MONITOR_WINDOW_SECONDS,
		)

		# Start tray (if available)
		start_tray(request_quit, icon_path=TRAY_ICON_PATH)

		try:
			while not stop_event.is_set():
				time.sleep(1)
		except KeyboardInterrupt:
			request_quit()
		finally:
			observer.stop()
			observer.join()
