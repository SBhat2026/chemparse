import React, { useEffect, useRef, useState } from "react";
import { API_BASE, STRIPE_PAYMENT_LINK } from "./config.js";
import JsonView from "./JsonView.jsx";
import MolViewer from "./MolViewer.jsx";

// Stateless unlock: Stripe success URL carries ?paid=1 back to this page.
function useUnlocked() {
  const [unlocked, setUnlocked] = useState(false);
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get("paid") === "1") setUnlocked(true);
  }, []);
  return [unlocked, setUnlocked];
}

function toCsv(result) {
  const geom = result.geometry || { atoms: [], coordinates: [] };
  const rows = [["atom", "x", "y", "z", "units"]];
  geom.atoms.forEach((a, i) => {
    const [x, y, z] = geom.coordinates[i] || [];
    rows.push([a, x, y, z, geom.units || ""]);
  });
  return rows.map((r) => r.join(",")).join("\n");
}

function download(filename, text, type) {
  const blob = new Blob([text], { type });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

export default function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [dragging, setDragging] = useState(false);
  const [unlocked] = useUnlocked();
  const inputRef = useRef(null);

  async function handleFile(file) {
    if (!file) return;
    setError(null);
    setResult(null);
    setLoading(true);
    try {
      const form = new FormData();
      form.append("file", file);
      const res = await fetch(`${API_BASE}/parse`, { method: "POST", body: form });
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || `Server error ${res.status}`);
      }
      setResult(await res.json());
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  function onDrop(e) {
    e.preventDefault();
    setDragging(false);
    handleFile(e.dataTransfer.files?.[0]);
  }

  return (
    <div className="min-h-screen text-slate-100 max-w-3xl mx-auto px-6 py-12">
      <h1 className="text-3xl font-bold">
        Chem<span className="text-emerald-400">Parse</span>
      </h1>
      <p className="mt-2 text-slate-400">
        Drop a Gaussian / LAMMPS / CP2K output file to extract structured data.
      </p>

      {/* DROP ZONE */}
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        onClick={() => inputRef.current?.click()}
        className={`mt-8 cursor-pointer rounded-xl border-2 border-dashed p-12 text-center transition ${
          dragging ? "border-emerald-400 bg-emerald-500/5" : "border-slate-700"
        }`}
      >
        <input
          ref={inputRef}
          type="file"
          className="hidden"
          onChange={(e) => handleFile(e.target.files?.[0])}
        />
        <p className="text-slate-300">
          Drag a file here, or <span className="text-emerald-400">browse</span>
        </p>
        <p className="mt-1 text-xs text-slate-500">.log / .out / dump</p>
      </div>

      {loading && (
        <div className="mt-6 flex items-center gap-3 text-slate-300">
          <span className="h-4 w-4 animate-spin rounded-full border-2 border-slate-600 border-t-emerald-400" />
          Parsing…
        </div>
      )}

      {error && (
        <div className="mt-6 rounded-lg border border-red-800 bg-red-950/40 p-4 text-sm text-red-300">
          {error}
        </div>
      )}

      {result && (
        <div className="mt-8">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">
              Parsed result{" "}
              <span className="text-sm font-normal text-slate-400">
                ({result.format})
              </span>
            </h2>
          </div>

          {/* Free preview: always visible */}
          <div className="mt-4 rounded-xl border border-slate-800 bg-slate-900/40 p-4 overflow-x-auto">
            <JsonView data={result} name="result" />
          </div>

          {/* Free value-add: interactive 3D geometry */}
          <MolViewer geometry={result.geometry} />

          {/* Gated downloads */}
          <div className="mt-6">
            {unlocked ? (
              <div className="flex gap-3">
                <button
                  onClick={() =>
                    download(
                      "result.json",
                      JSON.stringify(result, null, 2),
                      "application/json"
                    )
                  }
                  className="rounded-lg bg-emerald-500 px-4 py-2 text-sm font-medium text-slate-950 hover:bg-emerald-400"
                >
                  Download JSON
                </button>
                <button
                  onClick={() => download("geometry.csv", toCsv(result), "text/csv")}
                  className="rounded-lg border border-slate-700 px-4 py-2 text-sm hover:border-slate-500"
                >
                  Download CSV
                </button>
              </div>
            ) : (
              <div className="rounded-xl border border-slate-800 p-5">
                <p className="text-sm text-slate-300">
                  Preview is free. Unlock full JSON + CSV download.
                </p>
                <a
                  href={STRIPE_PAYMENT_LINK}
                  className="mt-3 inline-block rounded-lg bg-emerald-500 px-5 py-2 text-sm font-medium text-slate-950 hover:bg-emerald-400"
                >
                  Unlock download
                </a>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
