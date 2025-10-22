# PyPrep Chess Sample Project

This repository contains a lightweight chess engine intended as a starting point
for experiments around consuming external move data and building learning
pipelines. The initial version focuses on core board manipulation utilities,
basic move validation, and a small command line interface that can replay moves
from a JSON file or accept them interactively.

## Features

- Board representation with the standard chess starting position
- Basic legal move checking (no castling, en passant, or check detection yet)
- Coordinate move input (e.g. `e2e4`) with promotion support
- Extensible move source abstraction with a JSON file implementation
- Command line interface for replaying or manually entering moves

## Getting Started

Create a virtual environment and install the project in editable mode along with
the development dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[development]
```

Run the tests to make sure everything is wired correctly:

```bash
pytest
```

To replay a set of moves stored in `moves.json`:

```bash
python -m pyprep_chess.cli --moves moves.json
```

If you run the CLI without providing a move file it will prompt for moves on the
command line, allowing you to explore the engine manually.

## Next Steps

Future iterations can build on this base by adding richer rule enforcement,
integrations with public datasets (such as PGN archives), and simple learning
strategies for move selection.
