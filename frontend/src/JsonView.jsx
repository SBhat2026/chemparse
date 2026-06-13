import React, { useState } from "react";

// Minimal collapsible JSON tree. Objects/arrays fold; primitives render inline.
export default function JsonView({ data, name = "result", depth = 0 }) {
  const [open, setOpen] = useState(depth < 2);
  const isObj = data && typeof data === "object";

  if (!isObj) {
    return (
      <div className="pl-4 font-mono text-sm">
        <span className="text-slate-400">{name}:</span>{" "}
        <span className="text-emerald-300">{JSON.stringify(data)}</span>
      </div>
    );
  }

  const entries = Array.isArray(data)
    ? data.map((v, i) => [i, v])
    : Object.entries(data);

  return (
    <div className="pl-4">
      <button
        onClick={() => setOpen((o) => !o)}
        className="font-mono text-sm text-slate-300 hover:text-white"
      >
        <span className="inline-block w-4">{open ? "▾" : "▸"}</span>
        {name}{" "}
        <span className="text-slate-500">
          {Array.isArray(data) ? `[${entries.length}]` : `{${entries.length}}`}
        </span>
      </button>
      {open &&
        entries.map(([k, v]) => (
          <JsonView key={k} name={String(k)} data={v} depth={depth + 1} />
        ))}
    </div>
  );
}
