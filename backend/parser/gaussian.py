"""Gaussian .log / .out parser.

Primary path: cclib (handles the messy real-world variants).
Fallback path: regex, so the module works even when cclib is absent and so the
synthetic test fixtures parse without a heavy dependency.

Public surface: parse_gaussian(filepath) -> dict and GaussianParser.
"""

from __future__ import annotations

import re

from .base import ParseResult, empty_result
from .elements import symbol

HARTREE = "hartree"
ANGSTROM = "angstrom"

# "SCF Done:  E(RHF) =  -76.0263190476     A.U. after   10 cycles"
_SCF_DONE = re.compile(
    r"SCF Done:\s+E\([^)]+\)\s+=\s+(-?\d+\.\d+)\s+A\.U\. after\s+(\d+)\s+cycles"
)
# "Frequencies --   1638.0312  3811.1289  3933.4207"
_FREQ = re.compile(r"Frequencies --\s+(.*)")
_NUM = re.compile(r"-?\d+\.\d+")


def _orientation_blocks(text: str) -> list[list[tuple[int, float, float, float]]]:
    """Return every Standard/Input orientation coordinate block, in order."""
    blocks: list[list[tuple[int, float, float, float]]] = []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        if "orientation:" in lines[i].lower():
            # skip the header rows until the dashed line that opens the table body
            j = i + 1
            dashes = 0
            rows: list[tuple[int, float, float, float]] = []
            while j < len(lines):
                line = lines[j]
                if set(line.strip()) == {"-"}:
                    dashes += 1
                    if dashes == 3:  # third dashed line closes the table
                        break
                    j += 1
                    continue
                if dashes == 2:  # inside the data region
                    parts = line.split()
                    # center#, atomic#, atomic type, X, Y, Z
                    if len(parts) >= 6 and parts[0].isdigit():
                        z = int(parts[1])
                        x, y, zc = float(parts[3]), float(parts[4]), float(parts[5])
                        rows.append((z, x, y, zc))
                j += 1
            if rows:
                blocks.append(rows)
            i = j
        i += 1
    return blocks


def _parse_with_regex(text: str) -> ParseResult:
    result = empty_result("gaussian")

    scf_matches = _SCF_DONE.findall(text)
    if scf_matches:
        energies = [float(e) for e, _ in scf_matches]
        result["final_energy"] = energies[-1]
        result["scf"] = {
            "converged": "Optimization completed" in text
            or "Normal termination" in text,
            "n_cycles": int(scf_matches[-1][1]),
            "last_energies": energies[-3:],
        }

    blocks = _orientation_blocks(text)
    if blocks:
        last = blocks[-1]
        result["geometry"] = {
            "atoms": [symbol(z) for z, *_ in last],
            "coordinates": [[x, y, zc] for _, x, y, zc in last],
            "units": ANGSTROM,
        }

    freqs: list[float] = []
    for line in _FREQ.findall(text):
        freqs.extend(float(v) for v in _NUM.findall(line))
    result["frequencies"] = freqs or None

    result["metadata"] = {
        "normal_termination": "Normal termination" in text,
        "parser": "regex",
    }
    return result


def _parse_with_cclib(filepath: str) -> ParseResult | None:
    try:
        import cclib  # noqa: F401
        from cclib.io import ccread
    except Exception:
        return None
    try:
        data = ccread(filepath)
    except Exception:
        return None
    if data is None:
        return None

    result = empty_result("gaussian")
    # cclib scfenergies are eV; convert back to Hartree for chemistry parity.
    ev_to_hartree = 1.0 / 27.211386245988
    if getattr(data, "scfenergies", None) is not None and len(data.scfenergies):
        result["final_energy"] = float(data.scfenergies[-1]) * ev_to_hartree
        result["scf"] = {
            "converged": True,
            "n_cycles": len(data.scfenergies),
            "last_energies": [float(e) * ev_to_hartree for e in data.scfenergies[-3:]],
        }
    if getattr(data, "atomcoords", None) is not None and len(data.atomcoords):
        coords = data.atomcoords[-1]
        result["geometry"] = {
            "atoms": [symbol(int(z)) for z in data.atomnos],
            "coordinates": [[float(c) for c in row] for row in coords],
            "units": ANGSTROM,
        }
    if getattr(data, "vibfreqs", None) is not None and len(data.vibfreqs):
        result["frequencies"] = [float(f) for f in data.vibfreqs]
    result["metadata"] = {"parser": "cclib", **getattr(data, "metadata", {})}
    return result


def parse_gaussian(filepath: str) -> ParseResult:
    cclib_result = _parse_with_cclib(filepath)
    if cclib_result and cclib_result.get("final_energy") is not None:
        return cclib_result
    with open(filepath, "r", errors="ignore") as fh:
        return _parse_with_regex(fh.read())


class GaussianParser:
    format_name = "gaussian"

    def detect(self, text: str) -> bool:
        head = text[:4000]
        return (
            "Gaussian, Inc." in head
            or "Entering Gaussian System" in head
            or "This is part of the Gaussian" in head
            or "Gaussian 16" in head
            or "Gaussian 09" in head
        )

    def parse(self, filepath: str) -> ParseResult:
        return parse_gaussian(filepath)
