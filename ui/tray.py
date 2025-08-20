import threading
import os
from utils.logging_setup import get_logger

logger = get_logger(__name__)


def start_tray(on_quit, icon_path=None):
	"""Start a system tray icon with a Quit option. Returns the icon or None if unavailable."""
	try:
		import pystray
		from PIL import Image, ImageDraw
	except Exception:
		logger.warning("System tray not available (pystray/PIL missing)")
		return None

	# Load custom icon if provided; fallback to a simple placeholder
	if icon_path:
		# Resolve relative paths against the project root (module parent dir)
		resolved_path = icon_path
		try:
			if not os.path.isabs(resolved_path):
				base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
				candidate = os.path.join(base_dir, resolved_path)
				if os.path.exists(candidate):
					resolved_path = candidate
		except Exception:
			pass
		try:
			image = Image.open(resolved_path)
			image = image.resize((16, 16), getattr(Image, "LANCZOS", Image.BICUBIC))
		except Exception as e:
			logger.warning(f"Failed to load tray icon '{icon_path}': {e}; using default icon")
			image = Image.new('RGB', (16, 16), color=(0, 120, 215))
			draw = ImageDraw.Draw(image)
			draw.rectangle([3, 3, 13, 13], outline=(255, 255, 255))
	else:
		image = Image.new('RGB', (16, 16), color=(0, 120, 215))
		draw = ImageDraw.Draw(image)
		draw.rectangle([3, 3, 13, 13], outline=(255, 255, 255))

	def _quit(icon, item):
		on_quit(icon)

	menu = pystray.Menu(pystray.MenuItem("Quit", _quit))
	icon = pystray.Icon("DownloadsManager", image, "Downloads Manager", menu)

	thread = threading.Thread(target=icon.run, daemon=True)
	thread.start()
	return icon 