#!/usr/bin/env python3
"""Resolve k-graph leaf data keys to concrete locations via k-graph.toml.

Infrastructure sources (local, s3bucket, youtube, …) declare origin + mapping.
Data trees list reachable sources; leaf yaml stays abstract.

Library-style — import from site/tools or run as CLI for debugging.
"""
from __future__ import annotations

import sys

from kgraph_infra import resolve


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Resolve a k-graph data key")
    parser.add_argument("tree", help="e.g. media.videos, documents, media.scripts.scenes")
    parser.add_argument("key", help="k-graph key, e.g. T-cs/L-composite/F-01-carbon-binder")
    parser.add_argument("--source", help="infra source name (default: tree serve)")
    parser.add_argument("--ext", help="file extension override for path mapping")
    args = parser.parse_args(argv)
    try:
        loc = resolve(args.tree, args.key, source=args.source, ext=args.ext)
    except (KeyError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(loc)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
