from .base import BaseHandler
import os
import shutil
import re
from tkinter import messagebox
from paths import DirectoryPaths
from utils.date_utils import format_year_month_for_filename, subtract_one_month
from utils.logging_setup import get_logger

logger = get_logger(__name__)

class PDFHandler(BaseHandler):
    def handle(self, event):
        filename = os.path.basename(event.src_path)
        # Check for Rosemary's bank statement first
        if re.match(r'^ES(\d{8})\d{6}_\d+\.pdf$', filename):
            self.handle_rosemary_statement(event, filename)
        elif 'invoice' in filename.lower():
            self.handle_invoice_pdf(event)
        elif 'report' in filename.lower():
            self.handle_report_pdf(event)
        else:
            self.handle_unknown_pdf(event)

    def handle_rosemary_statement(self, event, filename):
        match = re.match(r'^ES(\d{8})\d{6}_\d+\.pdf$', filename)
        if not match:
            return
        date_str = match.group(1)  # YYYYMMDD
        year, month, day = date_str[:4], date_str[4:6], date_str[6:8]
        prev_year, prev_month, _ = subtract_one_month(year, month, day)
        year_month_part = format_year_month_for_filename(prev_year, prev_month)
        new_filename = f'Rosemary_Maybank_Statement_{year_month_part}.pdf'
        dest_folder = DirectoryPaths.ROSEMARY_STATEMENTS
        dest_path = os.path.join(dest_folder, new_filename)
        logger.info(f'[Rosemary Statement] {filename}')
        logger.info(f'  -> {new_filename}')
        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder)
        if os.path.exists(dest_path):
            logger.warning(f'Already exists for {year_month_part}: {new_filename}')
            messagebox.showinfo("Duplicate Statement", f"A statement for {year_month_part} already exists: {new_filename}")
            return
        shutil.move(event.src_path, dest_path)
        logger.info(f'  moved to {new_filename}')

    def handle_invoice_pdf(self, event):
        logger.info(f'Handling invoice PDF: {os.path.basename(event.src_path)}')
        # Add logic here

    def handle_report_pdf(self, event):
        logger.info(f'Handling report PDF: {os.path.basename(event.src_path)}')
        # Add logic here

    def handle_unknown_pdf(self, event):
        logger.info(f'Unknown PDF type: {os.path.basename(event.src_path)}')
        # Add logic here

    def handle_error(self, event, error):
        logger.error(f'Error handling PDF {os.path.basename(event.src_path)}: {error}')

    def call_external(self, event):
        logger.info(f'Calling external functionality for {os.path.basename(event.src_path)}') 