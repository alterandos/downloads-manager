from abc import ABC, abstractmethod
import os

class BaseHandler(ABC):
    @abstractmethod
    def handle(self, event):
        pass

    @abstractmethod
    def handle_error(self, event, error):
        pass

    def handle_unknown_subtype(self, event, filename=None):
        """Delegate to DefaultFileHandler for subtypes this handler doesn't recognise."""
        from utils.logging_setup import get_logger
        logger = get_logger(__name__)
        if filename is None:
            filename = os.path.basename(event.src_path)
        logger.info(f"BaseHandler.handle_unknown_subtype delegating to DefaultFileHandler: {filename}")
        from handlers.default import DefaultFileHandler
        DefaultFileHandler().handle(event)
