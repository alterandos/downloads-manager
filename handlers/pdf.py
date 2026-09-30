from .base import BaseHandler
import os
import shutil
import re
from ui.ctk_utils import show_info
from paths import DirectoryPaths
from utils.date_utils import format_year_month_for_filename, subtract_one_month
from utils.logging_setup import get_logger
from handlers.invoice.invoice_handler import handle_invoice

logger = get_logger(__name__)

class PDFHandler(BaseHandler):
    def handle(self, event):
        filename = os.path.basename(event.src_path)

        if re.match(r'^ES(\d{8})\d{6}_\d+\.pdf$', filename):
            self._handle_rosemary_statement(event, filename)
        elif 'invoice' in filename.lower():
            handle_invoice(event)
        else:
            self.handle_unknown_subtype(event, filename)

    def _handle_rosemary_statement(self, event, filename):
        match = re.match(r'^ES(\d{8})\d{6}_\d+\.pdf$', filename)
        date_str = match.group(1)
        year, month, day = date_str[:4], date_str[4:6], date_str[6:8]
        prev_year, prev_month, _ = subtract_one_month(year, month, day)
        year_month_part = format_year_month_for_filename(prev_year, prev_month)
        new_filename = f'Rosemary_Maybank_Statement_{year_month_part}.pdf'
        dest_folder = DirectoryPaths.ROSEMARY_STATEMENTS
        dest_path = os.path.join(dest_folder, new_filename)

        logger.info(f'[Rosemary Statement] {filename} → {new_filename}')

        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder)

        if os.path.exists(dest_path):
            logger.warning(f'Already exists for {year_month_part}: {new_filename}')
            show_info("Duplicate Statement", f"A statement for {year_month_part} already exists:\n{new_filename}")
            return

        shutil.move(event.src_path, dest_path)
        logger.info(f'Moved to {new_filename}')

    def handle_error(self, event, error):
        logger.error(f'Error handling PDF {os.path.basename(event.src_path)}: {error}')

    def handle_unknown_subtype(self, event, filename):
        logger.info(f'Unknown PDF subtype: {filename}')
        super().handle_unknown_subtype(event, filename)
