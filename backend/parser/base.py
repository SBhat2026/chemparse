"""Shared parser interface. Every format parser implements this contract so the
registry can detect + dispatch uniformly, and so the output schema stays stable
across Gaussian / LAMMPS / CP2K / future formats."""

from __future__ import annotations

from typing import Protocol, TypedDict


class Geometry(TypedDict):
    atoms: list[str]            # element symbols, length N
    coordinates: list[list[float]]  # N x 3, units below
    units: str


class ParseResult(TypedDict, total=False):
    format: str
    final_energy: float | None       # Hartree (QM) / energy units of the code
    geometry: Geometry | None
    scf: dict                        # {converged, n_cycles, last_energies}
    frequencies: list[float] | None  # cm^-1
    cell: list[list[float]] | None   # 3x3 lattice vectors (MD/periodic codes)
    forces: list[list[float]] | None  # N x 3
    thermo: dict | None              # MD thermo summary (final + series)
    metadata: dict


class Parser(Protocol):
    format_name: str

    def detect(self, text: str) -> bool:
        """Cheap signature check on the file head."""
        ...

    def parse(self, filepath: str) -> ParseResult:
        ...


def empty_result(fmt: str) -> ParseResult:
    return {
        "format": fmt,
        "final_energy": None,
        "geometry": None,
        "scf": {"converged": False, "n_cycles": 0, "last_energies": []},
        "frequencies": None,
        "metadata": {},
    }
