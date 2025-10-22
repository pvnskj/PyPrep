import pytest

from pyprep_chess.game import ChessGame


def test_apply_sanless_sequence():
    game = ChessGame()
    game.apply_sanless("e2e4")
    game.apply_sanless("e7e5")
    game.apply_sanless("g1f3")
    assert len(game.history) == 3
    assert game.board.get_piece((4, 3)) is not None  # white pawn on e4


def test_turn_enforced():
    game = ChessGame()
    game.apply_sanless("e2e4")
    with pytest.raises(ValueError):
        game.apply_sanless("d2d4")


def test_invalid_notation_rejected():
    game = ChessGame()
    with pytest.raises(ValueError):
        game.apply_sanless("invalid")
