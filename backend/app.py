"""FastAPI wrapper around the parser package.

One real endpoint: POST /parse  (multipart file upload -> structured JSON).
No auth by design at this stage. CORS open for local dev.
"""

from __future__ import annotations

import csv
import io
import json
import os
import tempfile
import zipfile
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response, StreamingResponse

from converters import gtf_to_gff3
from parser import UnknownFormatError, parse_file

app = FastAPI(title="ChemParse API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten before production
    allow_methods=["*"],
    allow_headers=["*"],
)


def _run_parser(upload: UploadFile) -> dict:
    suffix = os.path.splitext(upload.filename or "upload.log")[1] or ".log"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(upload.file.read())
        path = tmp.name
    try:
        return parse_file(path)
    finally:
        os.unlink(path)


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/parse")
async def parse_endpoint(file: UploadFile = File(...)):
    try:
        result = _run_parser(file)
    except UnknownFormatError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:  # surface parse failures cleanly to the UI
        raise HTTPException(status_code=500, detail=f"Parse failed: {exc}")
    return JSONResponse(result)


@app.post("/parse.csv")
async def parse_csv_endpoint(file: UploadFile = File(...)):
    """Flat CSV of the geometry table — convenient for spreadsheet users."""
    result = _run_parser(file)
    geom = result.get("geometry") or {"atoms": [], "coordinates": []}
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["atom", "x", "y", "z", "units"])
    for atom, (x, y, z) in zip(geom["atoms"], geom["coordinates"]):
        writer.writerow([atom, x, y, z, geom.get("units", "")])
    buf.seek(0)
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=geometry.csv"},
    )


# --- Phase 4: format conversion micro-service -----------------------------
@app.post("/convert/gtf-to-gff3")
async def convert_gtf_gff3(file: UploadFile = File(...)):
    """Single file = free tier; the frontend gates batch behind payment."""
    text = (await file.read()).decode("utf-8", errors="ignore")
    gff3 = gtf_to_gff3(text)
    name = (file.filename or "annotation.gtf").rsplit(".", 1)[0] + ".gff3"
    return Response(
        content=gff3,
        media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename={name}"},
    )


# --- Phase 4: premium batch parsing (.zip in -> .zip out) -----------------
def _parse_bytes(name: str, data: bytes) -> tuple[str, dict | str]:
    suffix = os.path.splitext(name)[1] or ".log"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(data)
        path = tmp.name
    try:
        return name, parse_file(path)
    except Exception as exc:  # one bad file shouldn't fail the whole batch
        return name, f"ERROR: {exc}"
    finally:
        os.unlink(path)


@app.post("/batch-parse")
async def batch_parse(file: UploadFile = File(...)):
    """Accept a .zip of output files, parse in parallel, return a .zip of JSON.

    Premium feature — gate it behind the monthly tier in production.
    """
    raw = await file.read()
    try:
        zin = zipfile.ZipFile(io.BytesIO(raw))
    except zipfile.BadZipFile:
        raise HTTPException(status_code=422, detail="Upload must be a .zip file.")

    members = [n for n in zin.namelist() if not n.endswith("/")]
    payloads = [(n, zin.read(n)) for n in members]

    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(lambda p: _parse_bytes(*p), payloads))

    out_buf = io.BytesIO()
    with zipfile.ZipFile(out_buf, "w", zipfile.ZIP_DEFLATED) as zout:
        for name, result in results:
            base = os.path.basename(name)
            zout.writestr(f"{base}.json", json.dumps(result, indent=2, default=str))
    out_buf.seek(0)
    return StreamingResponse(
        iter([out_buf.getvalue()]),
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=parsed.zip"},
    )
