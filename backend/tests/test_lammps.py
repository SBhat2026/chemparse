import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from parser import detect_format, parse_file  # noqa: E402

SAMPLE = os.path.join(os.path.dirname(__file__), "sample_data", "run.lammps.log")


def test_detect():
    with open(SAMPLE) as fh:
        assert detect_format(fh.read()) == "lammps"


def test_thermo_final_energy():
    result = parse_file(SAMPLE)
    assert result["format"] == "lammps"
    assert result["thermo"]["columns"][0] == "Step"
    assert len(result["thermo"]["steps"]) == 3
    # final TotEng row
    assert abs(result["final_energy"] - (-6.5)) < 1e-9
    assert result["thermo"]["final"]["Temp"] == 150.0
