from pyprep_chess.board import Board, Color, PieceType, parse_square


def test_initial_position_contains_kings():
    board = Board.from_initial_position()
    assert board.get_piece(parse_square("e1")).kind is PieceType.KING
    assert board.get_piece(parse_square("e1")).color is Color.WHITE
    assert board.get_piece(parse_square("e8")).kind is PieceType.KING
    assert board.get_piece(parse_square("e8")).color is Color.BLACK


def test_pawn_forward_move():
    board = Board.from_initial_position()
    board.move_piece(parse_square("e2"), parse_square("e4"))
    assert board.get_piece(parse_square("e4")).kind is PieceType.PAWN
    assert board.get_piece(parse_square("e2")) is None


def test_knight_can_jump():
    board = Board.from_initial_position()
    board.move_piece(parse_square("g1"), parse_square("f3"))
    assert board.get_piece(parse_square("f3")).kind is PieceType.KNIGHT


def test_blocked_path_prevents_rook_move():
    board = Board.from_initial_position()
    try:
        board.move_piece(parse_square("a1"), parse_square("a3"))
    except ValueError as exc:
        assert "Illegal move" in str(exc)
    else:  # pragma: no cover - defensive
        raise AssertionError("Expected move to be illegal")
