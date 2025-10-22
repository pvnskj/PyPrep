"""Chess board representation and movement logic.

The goal of this module is to keep the rules intentionally simple so that
additional behaviour (learning from data sources, advanced move validation, or
search) can be layered on later without rewriting the foundational types.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Iterable, Iterator, Optional, Tuple


FILES = "abcdefgh"
BOARD_SIZE = 8


class Color(str, Enum):
    """Simple enumeration for chess piece colours."""

    WHITE = "white"
    BLACK = "black"

    def opponent(self) -> "Color":
        return Color.BLACK if self is Color.WHITE else Color.WHITE


class PieceType(str, Enum):
    """Enumeration of supported chess pieces."""

    KING = "K"
    QUEEN = "Q"
    ROOK = "R"
    BISHOP = "B"
    KNIGHT = "N"
    PAWN = "P"


@dataclass(frozen=True)
class Piece:
    """A single chess piece."""

    color: Color
    kind: PieceType

    def symbol(self) -> str:
        base = self.kind.value
        return base if self.color is Color.WHITE else base.lower()


Square = Tuple[int, int]


class Board:
    """Represents the state of a chess board.

    The board stores squares as a mapping between (file, rank) coordinates and a
    :class:`Piece`. Files and ranks are zero indexed internally; helpers are
    provided for translating to common chess notation (``"e4"``).
    """

    def __init__(self) -> None:
        self._grid: Dict[Square, Piece] = {}

    # ------------------------------------------------------------------
    # Creation helpers
    # ------------------------------------------------------------------
    @classmethod
    def from_initial_position(cls) -> "Board":
        board = cls()
        board.reset()
        return board

    def reset(self) -> None:
        """Reset the board to the standard starting position."""

        self._grid.clear()

        back_rank = [
            PieceType.ROOK,
            PieceType.KNIGHT,
            PieceType.BISHOP,
            PieceType.QUEEN,
            PieceType.KING,
            PieceType.BISHOP,
            PieceType.KNIGHT,
            PieceType.ROOK,
        ]

        for file_index, kind in enumerate(back_rank):
            self._grid[(file_index, 0)] = Piece(Color.WHITE, kind)
            self._grid[(file_index, 1)] = Piece(Color.WHITE, PieceType.PAWN)
            self._grid[(file_index, 6)] = Piece(Color.BLACK, PieceType.PAWN)
            self._grid[(file_index, 7)] = Piece(Color.BLACK, kind)

    # ------------------------------------------------------------------
    # Accessors and utility methods
    # ------------------------------------------------------------------
    def pieces(self) -> Iterable[Tuple[Square, Piece]]:
        return self._grid.items()

    def get_piece(self, square: Square) -> Optional[Piece]:
        return self._grid.get(square)

    def set_piece(self, square: Square, piece: Optional[Piece]) -> None:
        if piece is None:
            self._grid.pop(square, None)
        else:
            self._grid[square] = piece

    # ------------------------------------------------------------------
    # Move handling
    # ------------------------------------------------------------------
    def move_piece(
        self,
        start: Square,
        end: Square,
        *,
        promotion: Optional[PieceType] = None,
    ) -> None:
        piece = self.get_piece(start)
        if piece is None:
            raise ValueError(f"No piece at square {square_name(start)}")

        if not self.is_legal_move(piece, start, end):
            raise ValueError(
                f"Illegal move for {piece.kind.name} from {square_name(start)} to {square_name(end)}"
            )

        target = self.get_piece(end)
        if target is not None and target.color is piece.color:
            raise ValueError("Cannot capture own piece")

        # Execute move
        self.set_piece(end, piece)
        self.set_piece(start, None)

        # Handle simple promotion (always promote to the provided piece, default queen)
        if (
            piece.kind is PieceType.PAWN
            and (end[1] == 0 or end[1] == BOARD_SIZE - 1)
        ):
            promoted = promotion or PieceType.QUEEN
            if promoted is PieceType.PAWN or promoted is PieceType.KING:
                raise ValueError("Cannot promote to pawn or king")
            self.set_piece(end, Piece(piece.color, promoted))

    def is_legal_move(self, piece: Piece, start: Square, end: Square) -> bool:
        if start == end:
            return False

        if not in_bounds(end):
            return False

        target = self.get_piece(end)
        if target is not None and target.color is piece.color:
            return False

        file_delta = end[0] - start[0]
        rank_delta = end[1] - start[1]

        if piece.kind is PieceType.PAWN:
            direction = 1 if piece.color is Color.WHITE else -1
            start_rank = 1 if piece.color is Color.WHITE else 6

            # Forward movement
            if file_delta == 0:
                if rank_delta == direction:
                    return target is None
                if rank_delta == 2 * direction and start[1] == start_rank:
                    intermediate = (start[0], start[1] + direction)
                    return target is None and self.get_piece(intermediate) is None
                return False

            # Captures
            if abs(file_delta) == 1 and rank_delta == direction:
                return target is not None and target.color is piece.color.opponent()

            return False

        if piece.kind is PieceType.KNIGHT:
            return (abs(file_delta), abs(rank_delta)) in {(1, 2), (2, 1)}

        if piece.kind is PieceType.KING:
            return max(abs(file_delta), abs(rank_delta)) == 1

        if piece.kind is PieceType.BISHOP:
            return abs(file_delta) == abs(rank_delta) and self._is_path_clear(start, end)

        if piece.kind is PieceType.ROOK:
            return (file_delta == 0 or rank_delta == 0) and self._is_path_clear(start, end)

        if piece.kind is PieceType.QUEEN:
            if abs(file_delta) == abs(rank_delta) or file_delta == 0 or rank_delta == 0:
                return self._is_path_clear(start, end)
            return False

        return False

    def _is_path_clear(self, start: Square, end: Square) -> bool:
        file_delta = end[0] - start[0]
        rank_delta = end[1] - start[1]

        step_file = (file_delta > 0) - (file_delta < 0)
        step_rank = (rank_delta > 0) - (rank_delta < 0)

        current = (start[0] + step_file, start[1] + step_rank)
        while current != end:
            if self.get_piece(current) is not None:
                return False
            current = (current[0] + step_file, current[1] + step_rank)
        return True

    # ------------------------------------------------------------------
    # Rendering helpers
    # ------------------------------------------------------------------
    def render(self) -> str:
        """Return an ASCII representation of the board."""

        rows = []
        for rank in reversed(range(BOARD_SIZE)):
            row = [str(rank + 1)]
            for file_index in range(BOARD_SIZE):
                piece = self.get_piece((file_index, rank))
                row.append(piece.symbol() if piece else ".")
            rows.append(" ".join(row))
        rows.append("  " + " ".join(FILES))
        return "\n".join(rows)

    def __iter__(self) -> Iterator[Tuple[Square, Piece]]:
        return iter(self._grid.items())


# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------
def parse_square(name: str) -> Square:
    if len(name) != 2 or name[0] not in FILES or name[1] not in "12345678":
        raise ValueError(f"Invalid square name: {name}")
    file_index = FILES.index(name[0])
    rank_index = int(name[1]) - 1
    return (file_index, rank_index)


def square_name(square: Square) -> str:
    file_index, rank_index = square
    if not in_bounds(square):
        raise ValueError("Square out of bounds")
    return f"{FILES[file_index]}{rank_index + 1}"


def in_bounds(square: Square) -> bool:
    file_index, rank_index = square
    return 0 <= file_index < BOARD_SIZE and 0 <= rank_index < BOARD_SIZE
