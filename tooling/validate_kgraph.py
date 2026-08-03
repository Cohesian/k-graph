#!/usr/bin/env python3
"""Validate the configured Directory Projection without writing output."""
from __future__ import annotations

import argparse
from pathlib import Path

from to_neo4j import load_directory_graph, print_report


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate the k-graph")
    parser.add_argument(
        "--source",
        type=Path,
        default=Path("."),
        help="k-graph repository root (default: current directory)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    migration = load_directory_graph(args.source)
    print_report(migration)
    return 1 if migration.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
