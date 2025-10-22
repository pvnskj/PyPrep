"""Command line helpers for exploring the chess engine."""

from __future__ import annotations

import argparse
from typing import Iterable
from .data_sources import JsonFileMoveSource, MoveSource
from .game import ChessGame


def load_moves_from_args(args: argparse.Namespace) -> Iterable[str]:
    if args.moves is None:
        return []
    source: MoveSource = JsonFileMoveSource(args.moves)
    return source.load()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Play or inspect a simple chess game")
    parser.add_argument(
        "--moves",
        type=str,
        help="Optional path to a JSON file containing coordinate moves",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    game = ChessGame()

    moves = load_moves_from_args(args)
    if moves:
        game.load_moves(moves)

    print(game.board.render())

    if not moves:
        print("\nEnter moves in coordinate notation (e.g. e2e4). Type 'quit' to exit.")
        while True:
            try:
                notation = input(f"{game.turn.name.title()} to move: ")
            except EOFError:  # pragma: no cover - console convenience
                print()
                break

            notation = notation.strip()
            if notation.lower() in {"quit", "exit"}:
                break

            if not notation:
                continue

            try:
                game.apply_sanless(notation)
            except ValueError as exc:
                print(f"Error: {exc}")
            else:
                print(game.board.render())

    return 0


if __name__ == "__main__":  # pragma: no cover - manual execution
    raise SystemExit(main())
