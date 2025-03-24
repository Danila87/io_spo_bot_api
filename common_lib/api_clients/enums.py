from enum import Enum

class RenderType(Enum):
    D_SOLO = 'd-solo'
    D = 'd'

    def __str__(self):
        return self.value

class Protocols(Enum):
    HTTP = 'http'
    HTTPS = 'https'