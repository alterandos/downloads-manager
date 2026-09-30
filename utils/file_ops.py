import os
import shutil
from utils.logging_setup import get_logger

logger = get_logger(__name__)

def move_file(src_path, target_dir):
    """
    Move a file to target_dir, automatically renaming if a file with the same name exists.
    Logs the action and returns the final destination path.
    """
    os.makedirs(target_dir, exist_ok=True)
    
    base_name = os.path.basename(src_path)
    dest_path = os.path.join(target_dir, base_name)
    
    # Auto-rename if file exists
    counter = 1
    name, ext = os.path.splitext(base_name)
    while os.path.exists(dest_path):
        dest_path = os.path.join(target_dir, f"{name} ({counter}){ext}")
        counter += 1

    shutil.move(src_path, dest_path)
    
    logger.info(f"Moved file: {src_path} → {dest_path}")
    
    return dest_path
