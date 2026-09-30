from .base import BaseHandler
import os
import shutil
from config_locations import resolve_locations, DEFAULT_LOCATION_KEYS
from ui.location_selector import select_location
from ui.ctk_utils import show_error
from utils.logging_setup import get_logger
from utils.skip_store import mark_skipped

logger = get_logger(__name__)


class DefaultFileHandler(BaseHandler):
    def handle(self, event):
        filename = os.path.basename(event.src_path)
        logger.info(f"Default handler for: {filename}")

        options = resolve_locations(DEFAULT_LOCATION_KEYS)
        dest_dir = select_location(
            options,
            title=f"Unhandled file type: {filename}\nSelect a destination, or Skip to leave it in Downloads",
            allow_browse=True,
            save_to_list="DEFAULT_LOCATION_KEYS",
        )

        if not dest_dir:
            logger.info(f"User skipped: {filename}")
            mark_skipped(event.src_path)
            return

        dest_path = os.path.join(dest_dir, filename)

        if os.path.exists(dest_path):
            from ui.ctk_utils import ask_yes_no
            if not ask_yes_no("File Exists", f"{filename} already exists in the destination.\nOverwrite?"):
                logger.info(f"User cancelled overwrite for {filename}")
                return

        try:
            shutil.move(event.src_path, dest_path)
            logger.info(f"Moved {filename} to {dest_dir}")
        except Exception as e:
            logger.error(f"Error moving {filename}: {e}")
            show_error("Move Failed", f"Failed to move {filename}:\n{e}")

    def handle_error(self, event, error):
        logger.error(f"Error in default handler for {os.path.basename(event.src_path)}: {error}")

    def handle_unknown_subtype(self, event, filename):
        logger.info(f"DefaultFileHandler handling unknown subtype: {filename}")
        self.handle(event)
