from .base import BaseHandler
from utils.file_ops import move_file

class MoveFileHandler(BaseHandler):
    def __init__(self, target_dir):
        self.target_dir = target_dir

    def handle(self, event):
        move_file(event.src_path, self.target_dir)

    def handle_error(self, event, error):
        raise error
