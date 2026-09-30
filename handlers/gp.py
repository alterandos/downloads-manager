from .base import BaseHandler
from .move import MoveFileHandler
from paths import DirectoryPaths
import os

class GPHandler(BaseHandler):
    TARGET_DIR = DirectoryPaths.GUITAR_PRO

    def handle(self, event):
        ext = os.path.splitext(event.src_path)[1].lower()
        if ext in {'.gpx', '.gp4', '.gp5'}:
            MoveFileHandler(self.TARGET_DIR).handle(event)
        else:
            self.handle_unknown_subtype(event)

    def handle_error(self, event, error):
        raise error
