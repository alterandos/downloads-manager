from .base import BaseHandler
import os
import zipfile
from tkinter import messagebox
from paths import DirectoryPaths
from utils.logging_setup import get_logger
from utils.zip_utils import extract_and_rename, finalize_zip

logger = get_logger(__name__)

class HeroesMapHandler(BaseHandler):
    def handle(self, event):
        try:
            def rename_fn(original_basename: str) -> str:
                filename = os.path.basename(original_basename)
                if not filename.lower().startswith('[hota]'):
                    filename = f'[HotA] {filename}'
                return filename

            extracted_any, unknown_files = extract_and_rename(
                zip_path=event.src_path,
                entries=None,
                target_ext='.h3m',
                dest_dir=DirectoryPaths.HEROES_MAPS,
                rename_fn=rename_fn,
            )

            if unknown_files:
                msg = 'Unknown files found in zip folder\n' + ('\n\t').join([f'{i}' for i in unknown_files])
                logger.info(msg)

            finalize_zip(event.src_path, extracted_any)
        except Exception as e:
            self.handle_error(event, e)

    def handle_error(self, event, error):
        logger.error(f'Error handling Heroes Map {os.path.basename(event.src_path)}: {error}') 

    def call_external(self, event):
        logger.info(f'Calling external functionality for {os.path.basename(event.src_path)}')
