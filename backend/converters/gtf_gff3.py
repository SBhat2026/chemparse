"""GTF -> GFF3 conversion.

GTF and GFF3 are both 9-column TSV; the real work is the attributes column
(GTF: `key "value";`  ->  GFF3: `key=value;`) plus deriving GFF3 ID/Parent
relationships from gene_id / transcript_id.

Pure-Python so it has no install footprint and is deterministic for tests. For
heavy/edge-case real-world GTFs, swap in biopython/gffutils — the interface
(text in, text out) stays the same.
"""

from __future__ import annotations

import re
from urllib.parse import quote

_ATTR = re.compile(r'(\w+)\s+"([^"]*)"')

# feature type -> how to assign GFF3 ID/Parent
_PARENT_OF = {"transcript": "gene", "mrna": "gene"}


def _parse_attrs(field: str) -> dict[str, str]:
    return {k: v for k, v in _ATTR.findall(field)}


def _encode(value: str) -> str:
    # GFF3 reserves ; = & , — percent-encode them, keep the rest readable.
    return quote(value, safe=" :/._-|()")


def gtf_to_gff3(gtf_text: str) -> str:
    out: list[str] = ["##gff-version 3"]
    exon_counters: dict[str, int] = {}

    for line in gtf_text.splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        cols = line.split("\t")
        if len(cols) < 9:
            continue
        seqid, source, ftype, start, end, score, strand, frame, attr_field = cols[:9]
        attrs = _parse_attrs(attr_field)
        gene_id = attrs.get("gene_id")
        tx_id = attrs.get("transcript_id")

        ordered: list[tuple[str, str]] = []
        ft = ftype.lower()
        if ft == "gene" and gene_id:
            ordered.append(("ID", gene_id))
        elif ft in _PARENT_OF and tx_id:
            ordered.append(("ID", tx_id))
            if gene_id:
                ordered.append(("Parent", gene_id))
        elif tx_id:  # exon / CDS / start_codon / etc.
            n = exon_counters.get(tx_id, 0) + 1
            exon_counters[tx_id] = n
            ordered.append(("ID", f"{tx_id}:{ft}:{n}"))
            ordered.append(("Parent", tx_id))

        # carry remaining GTF attributes through (skip the two used for IDs)
        for k, v in attrs.items():
            if k in ("gene_id", "transcript_id") and any(k2 in ("ID", "Parent") for k2, _ in ordered):
                ordered.append((k, _encode(v)))
            elif k not in ("gene_id", "transcript_id"):
                ordered.append((k, _encode(v)))

        gff_attrs = ";".join(f"{k}={v}" for k, v in ordered)
        out.append("\t".join([seqid, source, ftype, start, end, score,
                              strand, frame, gff_attrs]))
    return "\n".join(out) + "\n"
