import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from parser import detect_format, parse_file, parse_gaussian  # noqa: E402

SAMPLE = os.path.join(os.path.dirname(__file__), "sample_data", "water.log")


def test_final_energy():
    result = parse_gaussian(SAMPLE)
    # last SCF Done value wins
    assert abs(result["final_energy"] - (-74.9659011447)) < 1e-6


def test_geometry_uses_last_orientation():
    result = parse_gaussian(SAMPLE)
    geom = result["geometry"]
    assert geom["atoms"] == ["O", "H", "H"]
    assert geom["units"] == "angstrom"
    assert len(geom["coordinates"]) == 3
    # last block O z-coordinate
    assert abs(geom["coordinates"][0][2] - 0.117790) < 1e-6


def test_scf_convergence():
    result = parse_gaussian(SAMPLE)
    assert result["scf"]["converged"] is True
    assert result["scf"]["n_cycles"] == 10


def test_frequencies():
    result = parse_gaussian(SAMPLE)
    assert result["frequencies"] == [1638.0312, 3811.1289, 3933.4207]


def test_detection_and_dispatch():
    with open(SAMPLE) as fh:
        assert detect_format(fh.read()) == "gaussian"
    assert parse_file(SAMPLE)["format"] == "gaussian"
