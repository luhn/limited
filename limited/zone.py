from .backend import Backend


class Zone:
    name: str
    size: int
    rate: float
    backend: Backend
