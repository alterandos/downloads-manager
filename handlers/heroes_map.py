from .base import BaseHandler
import os
from paths import DirectoryPaths
from utils.logging_setup import get_logger
from utils.zip_utils import extract_and_rename, finalize_zip

logger = get_logger(__name__)

class HeroesMapHandler(BaseHandler):
    def handle(self, event):
        try:
            def rename_fn(original_basename: str) -> str:
                if not original_basename.lower().startswith('[hota]'):
                    return f'[HotA] {original_basename}'
                return original_basename

            extracted_any, unknown_files = extract_and_rename(
                zip_path=event.src_path,
                target_ext='.h3m',
                dest_dir=DirectoryPaths.HEROES_MAPS,
                rename_fn=rename_fn,
            )

            if unknown_files:
                msg = 'Unknown files found in zip:\n\t' + '\n\t'.join(unknown_files)
                logger.info(msg)

            finalize_zip(event.src_path, extracted_any)
        except Exception as e:
            self.handle_error(event, e)

    def handle_error(self, event, error):
        logger.error(f'Error handling Heroes Map {os.path.basename(event.src_path)}: {error}')
