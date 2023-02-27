from __future__ import annotations

import typing
from abc import ABC, abstractmethod

from .settings import SettingMap

if typing.TYPE_CHECKING:
    from limited.zone import Zone


class Backend(ABC):
    SETTINGS: SettingMap = dict()

    @abstractmethod
    def count(self, zone: Zone, identity: str) -> float | int:
        """
        Return the number of tokens in the bucket.  Optionally may return
        partial tokens.

        """
        ...

    @abstractmethod
    def remove(self, zone: Zone, identity: str, count: int) -> bool:
        """
        Remove a number of tokens.  Return false if the bucket does not have
        sufficient tokens.

        """
        ...
