"""LAMMPS log + dump parser. Sibling of gaussian.py sharing the same interface.

Pure-regex (no heavy deps). Extracts the thermo table from a log, and atoms /
coordinates / forces / box from a dump if those sections are present.
"""

from __future__ import annotations

import re

from .base import ParseResult, empty_result

# Thermo header: a line that starts with "Step" and names energy columns.
_THERMO_HEADER = re.compile(r"^\s*Step\b.*$", re.MULTILINE)
_NUMERIC_ROW = re.compile(r"^\s*-?\d[\d\s\.\+\-eE]*$")


def _parse_thermo(text: str) -> dict | None:
    m = _THERMO_HEADER.search(text)
    if not m:
        return None
    lines = text[m.start():].splitlines()
    columns = lines[0].split()
    rows: list[dict] = []
    for line in lines[1:]:
        if not _NUMERIC_ROW.match(line):
            break  # thermo block ends at the first non-numeric line
        values = line.split()
        if len(values) != len(columns):
            break
        rows.append({c: float(v) for c, v in zip(columns, values)})
    if not rows:
        return None
    return {"columns": columns, "steps": rows, "final": rows[-1]}


def _parse_dump(text: str) -> dict:
    """Pull the last frame from a LAMMPS dump: box, atoms, coords, forces."""
    out: dict = {}
    # Box bounds
    box = re.search(
        r"ITEM: BOX BOUNDS.*\n"
        r"\s*(-?\d\S*)\s+(-?\d\S*).*\n"
        r"\s*(-?\d\S*)\s+(-?\d\S*).*\n"
        r"\s*(-?\d\S*)\s+(-?\d\S*)",
        text,
    )
    if box:
        xlo, xhi, ylo, yhi, zlo, zhi = (float(v) for v in box.groups())
        out["cell"] = [
            [xhi - xlo, 0.0, 0.0],
            [0.0, yhi - ylo, 0.0],
            [0.0, 0.0, zhi - zlo],
        ]
    # Atoms block (use the last one in the file)
    atom_blocks = list(re.finditer(r"ITEM: ATOMS (.*)\n", text))
    if atom_blocks:
        last = atom_blocks[-1]
        cols = last.group(1).split()
        body = text[last.end():]
        atoms: list[str] = []
        coords: list[list[float]] = []
        forces: list[list[float]] = []
        for line in body.splitlines():
            if line.startswith("ITEM:") or not line.strip():
                break
            parts = line.split()
            if len(parts) != len(cols):
                break
            row = dict(zip(cols, parts))
            atoms.append(str(row.get("type", "?")))
            if {"x", "y", "z"} <= row.keys():
                coords.append([float(row["x"]), float(row["y"]), float(row["z"])])
            if {"fx", "fy", "fz"} <= row.keys():
                forces.append([float(row["fx"]), float(row["fy"]), float(row["fz"])])
        if coords:
            out["geometry"] = {"atoms": atoms, "coordinates": coords, "units": "lammps"}
        if forces:
            out["forces"] = forces
    return out


class LammpsParser:
    format_name = "lammps"

    def detect(self, text: str) -> bool:
        head = text[:4000]
        return (
            "LAMMPS" in head
            or bool(_THERMO_HEADER.search(head))
            or "ITEM: TIMESTEP" in head
        )

    def parse(self, filepath: str) -> ParseResult:
        result = empty_result("lammps")
        with open(filepath, "r", errors="ignore") as fh:
            text = fh.read()

        thermo = _parse_thermo(text)
        if thermo:
            result["thermo"] = thermo
            final = thermo["final"]
            # Prefer total energy column, then potential energy.
            for key in ("TotEng", "PotEng", "etotal", "pe"):
                if key in final:
                    result["final_energy"] = final[key]
                    break

        dump = _parse_dump(text)
        result.update(dump)  # geometry / forces / cell

        result["metadata"] = {
            "parser": "regex",
            "has_thermo": thermo is not None,
            "has_dump": "geometry" in dump,
        }
        return result
