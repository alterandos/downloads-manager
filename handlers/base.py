from abc import ABC, abstractmethod

class BaseHandler(ABC):
    @abstractmethod
    def handle(self, event):
        pass

    @abstractmethod
    def handle_error(self, event, error):
        pass

    @abstractmethod
    def call_external(self, event):
        pass
