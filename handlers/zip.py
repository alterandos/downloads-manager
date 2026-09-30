from .base import BaseHandler
from .heroes_map import HeroesMapHandler
import os
from utils.logging_setup import get_logger
from utils.zip_utils import zip_contains_extension

logger = get_logger(__name__)

class ZIPHandler(BaseHandler):
    def handle(self, event):
        try:
            if zip_contains_extension(event.src_path, {'.h3m'}):
                logger.info(f'ZIP contains Heroes map: {os.path.basename(event.src_path)}')
                HeroesMapHandler().handle(event)
            else:
                logger.info(f'ZIP checked: {os.path.basename(event.src_path)} (no heroes map found)')
        except Exception as e:
            self.handle_error(event, e)

    def handle_error(self, event, error):
        logger.error(f'Error handling ZIP {os.path.basename(event.src_path)}: {error}')

    def handle_unknown_subtype(self, event, filename):
        logger.info(f'Unknown ZIP subtype: {filename}')
        super().handle_unknown_subtype(event, filename)
