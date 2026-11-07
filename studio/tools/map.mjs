// Precompute a map cutaway for a reel.  usage: node tools/map.mjs <spec.json> <out.json>
// spec: { bbox: [[lonW, latS], [lonE, latN]], focus: ["724"], cities: { madrid: [-3.70, 40.42] }, extent?: [[x0,y0],[x1,y1]] }
// focus = ISO-3166 numeric ids (world-atlas). Output: { land: [svg paths], focus: [svg paths], cities: { name: [x, y] } } in 1080x1920 px.
import fs from "fs";
import { geoMercator, geoPath } from "d3-geo";
import { feature } from "topojson-client";
const [, , specPath, outPath] = process.argv;
const spec = JSON.parse(fs.readFileSync(specPath));
const topo = JSON.parse(fs.readFileSync(new URL("../node_modules/world-atlas/countries-50m.json", import.meta.url)));
const countries = feature(topo, topo.objects.countries).features;
const [[w, s], [e, n]] = spec.bbox;
const corners = { type: "MultiPoint", coordinates: [[w, s], [e, s], [e, n], [w, n]] };
const [FW, FH] = spec.size ?? [1080, 1920];   // 16:9 long-form maps pass "size": [1920, 1080]
const proj = geoMercator().fitExtent(spec.extent ?? (FW > FH ? [[260, 120], [1660, 960]] : [[90, 330], [990, 1330]]), corners).clipExtent([[0, 0], [FW, FH]]);
const path = geoPath(proj);
const focusIds = new Set(spec.focus.map(String));
const out = { land: [], focus: [], cities: {} };
for (const f of countries) {
  const d = path(f); if (!d) continue;
  (focusIds.has(String(f.id)) ? out.focus : out.land).push(d);
}
for (const [k, ll] of Object.entries(spec.cities)) out.cities[k] = proj(ll).map((v) => Math.round(v * 10) / 10);
fs.writeFileSync(outPath, JSON.stringify(out));
console.log("map", outPath, "land", out.land.length, "focus", out.focus.length, out.cities);
