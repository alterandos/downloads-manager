from .base import BaseHandler
from .heroes_map import HeroesMapHandler
import os
import zipfile
from utils.logging_setup import get_logger

logger = get_logger(__name__)

class ZIPHandler(BaseHandler):
    def handle(self, event):
        try:
            has_heroes_map = False
            # Open and close the zip just to inspect contents
            with zipfile.ZipFile(event.src_path, 'r') as zip_ref:
                has_heroes_map = any(name.lower().endswith('.h3m') for name in zip_ref.namelist())
            # Now the zip is closed; delegate accordingly
            if has_heroes_map:
                logger.info(f'ZIP contains Heroes map: {os.path.basename(event.src_path)}')
                HeroesMapHandler().handle(event)
            else:
                logger.info(f'ZIP checked: {os.path.basename(event.src_path)} (no heroes map found)')
        except Exception as e:
            self.handle_error(event, e)

    def handle_error(self, event, error):
        logger.error(f'Error handling ZIP {os.path.basename(event.src_path)}: {error}')

    def call_external(self, event):
        logger.info(f'Calling external functionality for {os.path.basename(event.src_path)}')
