from abc import ABC, abstractmethod

class AudioSource(ABC):
    def __init__(self, url, title):
        self.url = url
        self.title = title

    @abstractmethod
    async def get_player(self):
        pass
