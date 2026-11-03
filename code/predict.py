"""Entry point of the project.

Usage (from the code/ folder):
    uv run predict.py <district file> <facts file>

Writes felling_list.csv and check_list.csv into the current folder.
Pipeline steps are added as Tasks 1-5 are finished. Still a stub.
"""

import sys


def main(district_path: str, facts_path: str) -> None:
    raise NotImplementedError("Pipeline not built yet (Tasks 1-5)")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage: uv run predict.py <district file> <facts file>")
    main(sys.argv[1], sys.argv[2])
