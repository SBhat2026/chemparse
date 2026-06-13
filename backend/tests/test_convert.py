import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from converters import gtf_to_gff3  # noqa: E402

SAMPLE = os.path.join(os.path.dirname(__file__), "sample_data", "sample.gtf")


def _convert():
    with open(SAMPLE) as fh:
        return gtf_to_gff3(fh.read())


def test_header_and_linecount():
    out = _convert().splitlines()
    assert out[0] == "##gff-version 3"
    assert len(out) == 6  # header + 5 features


def test_gene_gets_id():
    lines = _convert().splitlines()
    gene = [l for l in lines if "\tgene\t" in l][0]
    assert "ID=G1" in gene
    assert 'gene_id "G1"' not in gene  # GTF-style attrs removed


def test_transcript_parent():
    lines = _convert().splitlines()
    tx = [l for l in lines if "\ttranscript\t" in l][0]
    assert "ID=T1" in tx and "Parent=G1" in tx


def test_exons_parent_transcript_and_unique_ids():
    lines = _convert().splitlines()
    exons = [l for l in lines if "\texon\t" in l]
    assert len(exons) == 2
    assert all("Parent=T1" in e for e in exons)
    assert "ID=T1:exon:1" in exons[0] and "ID=T1:exon:2" in exons[1]
