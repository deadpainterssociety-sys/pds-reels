import React from "react";
import { AbsoluteFill, staticFile, useCurrentFrame, useVideoConfig, delayRender, continueRender, random } from "remotion";

/* ---------- fonts (files copied from @fontsource by setup.sh into public/fonts) ---------- */
export type FontSpec = [family: string, file: string, weight: string, style: string];
export const BASE_FONTS: FontSpec[] = [
  ["Newsreader", "newsreader-latin-400-normal", "400", "normal"], ["Newsreader", "newsreader-latin-500-normal", "500", "normal"],
  ["Newsreader", "newsreader-latin-600-normal", "600", "normal"], ["Newsreader", "newsreader-latin-500-italic", "500", "italic"],
  ["Newsreader", "newsreader-latin-600-italic", "600", "italic"],
  ["Inter", "inter-latin-500-normal", "500", "normal"], ["Inter", "inter-latin-600-normal", "600", "normal"], ["Inter", "inter-latin-800-normal", "800", "normal"],
  ["Space Mono", "space-mono-latin-400-normal", "400", "normal"], ["Space Mono", "space-mono-latin-700-normal", "700", "normal"],
];
const loaded = new Set<string>();
/** loads fonts once per render tab; blocks the frame until they are ready (no fallback-font flashes in the video) */
export function useFonts(extra: FontSpec[] = []) {
  React.useState(() => {
    const todo = [...BASE_FONTS, ...extra].filter((f) => !loaded.has(f.join("|")));
    if (!todo.length || typeof FontFace === "undefined") return 0;
    const h = delayRender("fonts");
    Promise.all(todo.map(([fam, file, weight, style]) => new FontFace(fam, `url(${staticFile(`fonts/${file}.woff2`)}) format('woff2')`, { weight, style })
      .load().then((f) => { (document.fonts as any).add(f); loaded.add([fam, file, weight, style].join("|")); })))
      .then(() => continueRender(h)).catch((e) => { console.error(e); continueRender(h); });
    return 0;
  });
}

/* ---------- time & easing ---------- */
export const useT = () => { const f = useCurrentFrame(); const { fps } = useVideoConfig(); return f / fps; };
export const clamp = (x: number, a = 0, b = 1) => Math.max(a, Math.min(b, x));
export const lerp = (a: number, b: number, p: number) => a + (b - a) * p;
export const ease = (p: number) => (p < 0.5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2);
export const easeOut = (p: number) => 1 - Math.pow(1 - clamp(p), 3);
export const easeIn = (p: number) => Math.pow(clamp(p), 3);
export const backOut = (p: number, s = 1.7) => { const x = clamp(p) - 1; return x * x * ((s + 1) * x + s) + 1; };
export const ramp = (t: number, a: number, b: number) => clamp((t - a) / (b - a));
/** 0→1→0 around time c (fast attack `up`, slower release `down`) */
export const pulse = (t: number, c: number, up = 0.06, down = 0.35) => (t < c ? clamp(1 - (c - t) / up) : clamp(1 - (t - c) / down));

/** animated film grain (tile from public/tex/grain.png, re-positioned every frame) */
export const Grain: React.FC<{ opacity?: number; blend?: any }> = ({ opacity = 0.12, blend = "overlay" }) => {
  const f = useCurrentFrame();
  const x = Math.floor(random(`gx${f}`) * 512), y = Math.floor(random(`gy${f}`) * 512);
  return <AbsoluteFill style={{ backgroundImage: `url(${staticFile("tex/grain.png")})`, backgroundPosition: `${x}px ${y}px`,
    opacity, mixBlendMode: blend, pointerEvents: "none" }} />;
};
