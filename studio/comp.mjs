// Composition id for a story: "long-<slug>" for "format": "long" stories (16:9), else "reel-<slug>" (9:16).
import fs from "fs"; import path from "path";
export function compId(slug) {
  try { if (JSON.parse(fs.readFileSync(path.resolve("../stories", slug, "build", "resolved.json"))).format === "long") return `long-${slug}`; } catch {}
  return `reel-${slug}`;
}
