import React, { useEffect, useRef } from "react";

// Build an XYZ string from the parser's geometry block.
function toXyz(geometry) {
  const { atoms, coordinates } = geometry;
  const lines = [String(atoms.length), "parsed by ChemParse"];
  atoms.forEach((a, i) => {
    const [x, y, z] = coordinates[i];
    lines.push(`${a} ${x} ${y} ${z}`);
  });
  return lines.join("\n");
}

// Renders optimized geometry with 3Dmol.js (loaded via CDN -> window.$3Dmol).
export default function MolViewer({ geometry }) {
  const ref = useRef(null);

  // Only element-symbol geometries render meaningfully (LAMMPS gives type ids).
  const renderable =
    geometry &&
    geometry.atoms.length > 0 &&
    geometry.atoms.every((a) => /^[A-Za-z]{1,2}$/.test(a));

  useEffect(() => {
    if (!renderable || !window.$3Dmol || !ref.current) return;
    ref.current.innerHTML = "";
    const viewer = window.$3Dmol.createViewer(ref.current, {
      backgroundColor: "#0f172a",
    });
    viewer.addModel(toXyz(geometry), "xyz");
    viewer.setStyle({}, { stick: { radius: 0.12 }, sphere: { scale: 0.28 } });
    viewer.zoomTo();
    viewer.render();
    return () => viewer.clear();
  }, [geometry, renderable]);

  if (!geometry) return null;
  if (!renderable) {
    return (
      <p className="mt-4 text-sm text-slate-500">
        3D view unavailable for this geometry (non-element atom labels).
      </p>
    );
  }

  return (
    <div className="mt-6">
      <h3 className="text-sm font-medium text-slate-300">3D geometry</h3>
      <div
        ref={ref}
        className="relative mt-2 h-72 w-full overflow-hidden rounded-xl border border-slate-800"
      />
      <p className="mt-1 text-xs text-slate-500">Drag to rotate · scroll to zoom</p>
    </div>
  );
}
