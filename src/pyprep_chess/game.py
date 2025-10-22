"""High level game management utilities."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List, Optional

from .board import BOARD_SIZE, Board, Color, Piece, PieceType, parse_square


@dataclass
class Move:
    """Simple record describing a move."""

    start: str
    end: str
    promotion: Optional[PieceType] = None

    def __str__(self) -> str:  # pragma: no cover - repr convenience
        if self.promotion:
            return f"{self.start}{self.end}{self.promotion.value.lower()}"
        return f"{self.start}{self.end}"


@dataclass
class ChessGame:
    """Manage a single chess game."""

    board: Board = field(default_factory=Board.from_initial_position)
    turn: Color = Color.WHITE
    history: List[Move] = field(default_factory=list)

    def apply_move(self, move: Move) -> None:
        start = parse_square(move.start)
        end = parse_square(move.end)

        piece = self.board.get_piece(start)
        if piece is None:
            raise ValueError(f"No piece on {move.start}")
        if piece.color is not self.turn:
            raise ValueError(f"It is {self.turn.name.lower()} to move")

        self.board.move_piece(start, end, promotion=move.promotion)
        self.history.append(move)
        self.turn = self.turn.opponent()

    def apply_sanless(self, notation: str) -> None:
        """Apply moves written in coordinate notation (``e2e4``).

        Promotions can be specified by appending the piece character (``e7e8q``).
        """

        notation = notation.strip().lower()
        if len(notation) not in {4, 5}:
            raise ValueError(f"Unsupported notation: {notation}")

        promotion: Optional[PieceType] = None
        if len(notation) == 5:
            promotion_char = notation[-1]
            promotion = _promotion_from_char(promotion_char)
            notation = notation[:4]

        move = Move(start=notation[:2], end=notation[2:], promotion=promotion)
        self.apply_move(move)

    def load_moves(self, moves: Iterable[str]) -> None:
        """Apply a series of coordinate moves."""

        for notation in moves:
            self.apply_sanless(notation)

    def board_as_matrix(self) -> List[List[Optional[Piece]]]:
        """Return a matrix representation of the board for quick inspection."""

        matrix: List[List[Optional[Piece]]] = [
            [None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)
        ]
        for (file_index, rank_index), piece in self.board:
            matrix[rank_index][file_index] = piece
        return matrix


def _promotion_from_char(char: str) -> PieceType:
    mapping = {
        "q": PieceType.QUEEN,
        "r": PieceType.ROOK,
        "b": PieceType.BISHOP,
        "n": PieceType.KNIGHT,
    }
    try:
        return mapping[char]
    except KeyError as exc:  # pragma: no cover - defensive
        raise ValueError(f"Unsupported promotion: {char}") from exc
