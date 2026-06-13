"""Format auto-detection + dispatch. Register new parsers here."""

from __future__ import annotations

from .base import ParseResult
from .cp2k import Cp2kParser
from .gaussian import GaussianParser
from .lammps import LammpsParser

PARSERS = [GaussianParser(), Cp2kParser(), LammpsParser()]


class UnknownFormatError(ValueError):
    pass


def detect_format(text: str) -> str | None:
    for parser in PARSERS:
        if parser.detect(text):
            return parser.format_name
    return None


def parse_file(filepath: str) -> ParseResult:
    with open(filepath, "r", errors="ignore") as fh:
        head = fh.read(8000)
    for parser in PARSERS:
        if parser.detect(head):
            return parser.parse(filepath)
    raise UnknownFormatError(
        "Could not detect format (supported: gaussian, cp2k, lammps)."
    )
