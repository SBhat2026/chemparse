import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from parser import detect_format, parse_file  # noqa: E402

SAMPLE = os.path.join(os.path.dirname(__file__), "sample_data", "water.cp2k.out")


def test_detect():
    with open(SAMPLE) as fh:
        assert detect_format(fh.read()) == "cp2k"


def test_energy_cell_geometry_forces():
    result = parse_file(SAMPLE)
    assert result["format"] == "cp2k"
    assert abs(result["final_energy"] - (-17.1639008912)) < 1e-9
    assert result["cell"][0][0] == 10.0
    assert result["geometry"]["atoms"] == ["O", "H", "H"]
    assert abs(result["geometry"]["coordinates"][0][2] - 0.117790) < 1e-6
    assert len(result["forces"]) == 3
    assert abs(result["forces"][0][2] - 0.01234567) < 1e-9
