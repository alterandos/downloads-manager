import os
import threading
import time
from collections import deque
from utils.logging_setup import get_logger

try:
	import psutil  # type: ignore
except Exception:
	psutil = None

logger = get_logger(__name__)


def start_resource_monitor(
	cpu_threshold_percent: float = 10.0,
	rss_threshold_mb: float = 30.0,
	interval_seconds: int = 60,
	stop_event: threading.Event | None = None,
	report_interval_seconds: float = 86400.0,
	window_seconds: float = 86400.0,
):
	"""Start a background thread that logs when resource usage exceeds thresholds and
	periodically logs a rolling-window average (default: last 24h).

	- cpu_threshold_percent: warn if instantaneous CPU exceeds this percent
	- rss_threshold_mb: warn if instantaneous RSS exceeds this many MB
	- interval_seconds: sample period in seconds
	- stop_event: signal to stop the thread
	- report_interval_seconds: how often to emit an average summary
	- window_seconds: time window for the rolling average (default 24h)
	"""
	if psutil is None:
		logger.warning("psutil not installed; resource monitoring disabled")
		return None
	if stop_event is None:
		stop_event = threading.Event()

	process = psutil.Process(os.getpid())

	# samples: deque[(timestamp, cpu_percent, rss_mb)]
	samples = deque()
	last_report_ts = time.time()

	def monitor_loop():
		# Prime CPU measurement window
		process.cpu_percent(interval=None)
		while not stop_event.is_set():
			time.sleep(interval_seconds)
			now = time.time()
			cpu = process.cpu_percent(interval=None)
			rss_mb = process.memory_info().rss / (1024 * 1024)
			samples.append((now, cpu, rss_mb))

			# Evict samples outside the rolling window
			cutoff = now - window_seconds
			while samples and samples[0][0] < cutoff:
				samples.popleft()

			# Instantaneous threshold warnings
			if cpu > cpu_threshold_percent or rss_mb > rss_threshold_mb:
				logger.warning(f"High usage: CPU={cpu:.1f}% RSS={rss_mb:.0f}MB")

			# Periodic rolling-average report
			if (now - last_report_ts) >= report_interval_seconds and samples:
				n = len(samples)
				avg_cpu = sum(s[1] for s in samples) / n
				avg_rss = sum(s[2] for s in samples) / n
				logger.info(f"24h avg usage: CPU={avg_cpu:.1f}% RSS={avg_rss:.0f}MB over {n} samples")
				last_report_ts = now

	thread = threading.Thread(target=monitor_loop, daemon=True)
	thread.start()
	return thread 