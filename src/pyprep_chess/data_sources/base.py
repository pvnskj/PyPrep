"""Base interfaces for move sources."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable


class MoveSource(ABC):
    """Abstract source that yields SAN-less coordinate moves."""

    @abstractmethod
    def load(self) -> Iterable[str]:
        """Return an iterable of coordinate moves (``e2e4``)."""


class IterableMoveSource(MoveSource):
    """Wrap a plain iterable to expose the :class:`MoveSource` interface."""

    def __init__(self, moves: Iterable[str]):
        self._moves = moves

    def load(self) -> Iterable[str]:
        return self._moves
