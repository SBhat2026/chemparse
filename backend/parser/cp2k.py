"""CP2K output parser. Sibling of gaussian.py sharing the same interface.

Pure-regex (no heavy deps). Extracts total energy, cell vectors, atomic
coordinates, and atomic forces from a CP2K output (.out).
"""

from __future__ import annotations

import re

from .base import ParseResult, empty_result

# "ENERGY| Total FORCE_EVAL ( QS ) energy [a.u.]:   -17.1234567890"
_ENERGY = re.compile(r"ENERGY\|\s*Total FORCE_EVAL.*?:\s*(-?\d+\.\d+)")
# "CELL| Vector a [angstrom]:    10.000   0.000   0.000"
_CELL = re.compile(
    r"CELL\| Vector [abc] \[angstrom\]:\s*"
    r"(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)"
)


def _parse_block(text: str, header: str, ncols_min: int) -> list[list[str]]:
    """Return rows under a header line until a blank/section break."""
    idx = text.find(header)
    if idx < 0:
        return []
    rows: list[list[str]] = []
    started = False
    for line in text[idx:].splitlines()[1:]:
        parts = line.split()
        if not parts:
            if started:
                break
            continue
        if parts[0].startswith("#") or not parts[0].lstrip("-").isdigit():
            if started:
                break
            continue
        if len(parts) >= ncols_min:
            started = True
            rows.append(parts)
        elif started:
            break
    return rows


class Cp2kParser:
    format_name = "cp2k"

    def detect(self, text: str) -> bool:
        head = text[:6000]
        return "CP2K| version" in head or "CP2K version" in head or "DBCSR|" in head

    def parse(self, filepath: str) -> ParseResult:
        result = empty_result("cp2k")
        with open(filepath, "r", errors="ignore") as fh:
            text = fh.read()

        energies = _ENERGY.findall(text)
        if energies:
            result["final_energy"] = float(energies[-1])

        cell = [[float(x) for x in m] for m in _CELL.findall(text)]
        if len(cell) >= 3:
            result["cell"] = cell[:3]

        # Coordinates: "# Atom Kind Element X Y Z ..." -> element + 3 floats
        coord_rows = _parse_block(text, "ATOMIC COORDINATES", ncols_min=6)
        if coord_rows:
            atoms, coords = [], []
            for r in coord_rows:
                # columns: idx kind element X Y Z [...]; element is col 2
                atoms.append(r[2])
                coords.append([float(r[3]), float(r[4]), float(r[5])])
            result["geometry"] = {"atoms": atoms, "coordinates": coords,
                                  "units": "angstrom"}

        # Forces: "# Atom Kind Element X Y Z" under "ATOMIC FORCES in [a.u.]"
        force_rows = _parse_block(text, "ATOMIC FORCES", ncols_min=6)
        if force_rows:
            result["forces"] = [[float(r[3]), float(r[4]), float(r[5])]
                                for r in force_rows]

        result["metadata"] = {"parser": "regex"}
        return result
