from abc import ABC, abstractmethod


class Video(ABC):

    def __init__(self, subjects, session, timeouts):
        self.session = session
        self.timeouts = timeouts
        self.subjects = subjects

    @abstractmethod
    def get_lectures(self):
        pass
