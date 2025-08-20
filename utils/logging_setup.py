import logging
import sys
import os
from typing import Optional

_LOG_CONFIGURED = False


def setup_logging(level: str = "INFO", log_file: Optional[str] = None) -> None:
	global _LOG_CONFIGURED
	if _LOG_CONFIGURED:
		return

	root_logger = logging.getLogger()
	log_level = getattr(logging, level.upper(), logging.INFO)
	root_logger.setLevel(log_level)

	formatter = logging.Formatter(
		fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
		datefmt="%Y-%m-%d %H:%M:%S",
	)

	console_handler = logging.StreamHandler(sys.stdout)
	console_handler.setLevel(log_level)
	console_handler.setFormatter(formatter)
	root_logger.addHandler(console_handler)

	if log_file:
		try:
			log_dir = os.path.dirname(log_file)
			if log_dir:
				os.makedirs(log_dir, exist_ok=True)
		except Exception:
			pass
		file_handler = logging.FileHandler(log_file, encoding="utf-8")
		file_handler.setLevel(log_level)
		file_handler.setFormatter(formatter)
		root_logger.addHandler(file_handler)

	_LOG_CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
	return logging.getLogger(name) 