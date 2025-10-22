"""Load move data from a simple JSON file."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List

from .base import MoveSource


class JsonFileMoveSource(MoveSource):
    """Load SAN-less moves from a JSON file.

    The expected format is a JSON array containing strings::

        ["e2e4", "e7e5", "g1f3"]
    """

    def __init__(self, path: Path | str):
        self._path = Path(path)

    def load(self) -> Iterable[str]:
        with self._path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        if not isinstance(data, list):
            raise ValueError("Move file must contain a JSON list")

        moves: List[str] = []
        for index, entry in enumerate(data):
            if not isinstance(entry, str):
                raise ValueError(f"Move at index {index} is not a string")
            moves.append(entry)
        return moves
