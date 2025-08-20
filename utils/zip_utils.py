import os
import zipfile
from typing import Iterable, List, Tuple
from ui.prompts import confirm_overwrite, confirm_delete_zip_no_extracted
from utils.logging_setup import get_logger

logger = get_logger(__name__)


def zip_contains_extension(zip_path: str, extensions: Iterable[str]) -> bool:
    exts = tuple(ext.lower() for ext in extensions)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        return any(name.lower().endswith(exts) for name in zip_ref.namelist())


def extract_and_rename(
    zip_path: str,
    entries: Iterable[str],
    target_ext: str,
    dest_dir: str,
    rename_fn,
) -> Tuple[bool, List[str]]:
    """
    Extract entries with target_ext to dest_dir, applying rename_fn(basename) -> new_name.
    Returns (extracted_any, unknown_entries)
    """
    unknown: List[str] = []
    extracted_any = False
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for name in zip_ref.namelist():
            ext = name.split('.')[-1].lower()
            if f'.{ext}' != target_ext.lower():
                if ext != 'txt':
                    unknown.append(name)
                continue
            filename = os.path.basename(name)
            new_name = rename_fn(filename)
            dest = os.path.join(dest_dir, new_name)
            if os.path.exists(dest):
                if not confirm_overwrite(new_name, dest_dir):
                    logger.info(f"-- skipped replacing existing file: {new_name}")
                    continue
                try:
                    os.remove(dest)
                except Exception as rm_err:
                    logger.error(f"Failed to remove existing file {new_name}: {rm_err}")
                    continue
            zip_ref.extract(name, path=dest_dir)
            os.rename(os.path.join(dest_dir, name), dest)
            extracted_any = True
    return extracted_any, unknown


def finalize_zip(zip_path: str, extracted_any: bool) -> None:
    try:
        if extracted_any:
            os.remove(zip_path)
            logger.info(f"-- deleted processed zip: {os.path.basename(zip_path)}")
        else:
            if confirm_delete_zip_no_extracted():
                os.remove(zip_path)
                logger.info(f"-- deleted zip (no target extracted): {os.path.basename(zip_path)}")
    except Exception as e:
        logger.error(f"Error finalizing zip {os.path.basename(zip_path)}: {e}") 