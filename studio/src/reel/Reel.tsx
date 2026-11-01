import React from "react";
import { AbsoluteFill, Audio, Img, staticFile, random } from "remotion";
import { useT, useFonts, Grain, ease, easeOut, easeIn, backOut, ramp, pulse, lerp, clamp, FontSpec } from "./lib";
import { DepthImage } from "./DepthImage";
import { W, H, Pose, place } from "./geom";
import { STORIES } from "./stories";

/* ---------- data contract (written by pipeline/build_story.py; every time is in seconds) ---------- */
type V3 = [number, number, number];
export type Img = { src: string; w: number; h: number; depth?: string };
export type Shot = {
  t: number; img: string; kind?: "image" | "map" | "peel";
  from: V3; to: V3; gray?: number; dim?: number; contrast?: number; dolly?: [number, number]; sway?: number; frame?: boolean;
  map?: { id: string; pins: { city: string; t: number; label?: string }[]; route?: { from: string; to: string; t0: number; t1: number } };
  peel?: { t0: number; t1: number; under: string };
};
export type Overlay = {
  type: "label" | "title" | "pin" | "ring" | "hotspot" | "stamp" | "credit" | "cut" | "next"; t0: number; t1: number;
  text?: string; kicker?: string; sub?: string; point?: { x: number; y: number }; rx?: number; ry?: number; rot?: number; color?: string;
  box?: [number, number, number, number]; shade?: number;   // cut: kept area in image fractions [x0,y0,x1,y1]; shade = when the removed strips tint
};
export type MapData = { land: string[]; focus: string[]; cities: Record<string, [number, number]> };
export type Word = { w: string; s: number; e: number; em?: number };
export type Style = {
  bg?: string; ink?: string; accent?: string; captionFont?: string; captionWeight?: number; captionSize?: number; captionTop?: number;
  captionWords?: number; captionChars?: number; captionUpper?: boolean; titleFont?: string; uiFont?: string; labelFont?: string;
  grain?: number; fonts?: FontSpec[];
};
export type Story = {
  slug: string; duration: number; audio: string; images: Record<string, Img>; shots: Shot[]; overlays: Overlay[];
  flashes: number[]; shakes: number[]; words: { line: string; words: Word[] }[]; nocap: [number, number][]; maps: Record<string, MapData>; style?: Style;
};

const lerpPose = (a: V3, b: V3, p: number): Pose => ({ x: lerp(a[0], b[0], p), y: lerp(a[1], b[1], p), z: Math.exp(lerp(Math.log(a[2]), Math.log(b[2]), p)) });

/* ---------- captions: short chunks, emphasised words (*word* in the script) in italics ---------- */
type Chunk = { words: Word[]; s: number; e: number };
function chunks(lines: Story["words"], maxWords: number, maxChars: number): Chunk[] {
  const out: Chunk[] = [];
  for (const l of lines) {
    let cur: Word[] = [];
    const flush = () => { if (cur.length) out.push({ words: cur, s: cur[0].s, e: cur[cur.length - 1].e }); cur = []; };
    for (const w of l.words) {
      const len = cur.map((x) => x.w).join(" ").length + w.w.length;
      if (cur.length >= maxWords || (cur.length && len > maxChars)) flush();
      cur.push(w);
      if (/[.,:;!?…]$/.test(w.w) || /\.\.\.$/.test(w.w)) flush();   // punctuation ends a chunk: captions follow the phrasing
    }
    flush();
  }
  for (let i = 0; i < out.length; i++) { const nx = out[i + 1]; out[i].e = nx ? Math.min(nx.s, out[i].e + 0.9) : out[i].e + 0.6; }
  return out;
}
const clean = (w: string) => w.replace(/\.\.\.$/, "…");

export const Reel: React.FC<{ slug: string }> = ({ slug }) => {
  const S = STORIES[slug] as Story;
  const st: Required<Omit<Style, "fonts">> & { fonts: FontSpec[] } = {
    bg: "#0B0B0B", ink: "#F4F0E8", accent: "#D8463A", captionFont: "Newsreader", captionWeight: 500, captionSize: 86, captionTop: 1390,
    captionWords: 3, captionChars: 18, captionUpper: false, titleFont: "Newsreader", uiFont: "Inter", labelFont: "Space Mono", grain: 0.09, fonts: [],
    ...(S.style || {}),
  };
  useFonts(st.fonts);
  const t = useT();
  const shots = S.shots;
  let si = 0; for (let k = 0; k < shots.length; k++) if (t >= shots[k].t) si = k;
  const sh = shots[si], nx = shots[si + 1];
  const p = clamp((t - sh.t) / Math.max(0.2, (nx ? nx.t : S.duration) - sh.t));
  const e = ease(p) * 0.5 + p * 0.5;                                                   // half eased, half linear: never static
  let pose = lerpPose(sh.from, sh.to, e);
  pose = { ...pose, z: pose.z * (1 + 0.035 * Math.exp(-(t - sh.t) * 6)) };              // micro push-in that settles after every cut
  const sway = sh.sway ?? 0.007;
  const shift: [number, number] = [Math.sin(t * 0.9) * sway, Math.cos(t * 0.7) * sway * 0.6];   // slow 2.5D drift
  const dolly = sh.dolly ? lerp(sh.dolly[0], sh.dolly[1], e) : 0;
  const img = S.images[sh.img];
  const flash = Math.max(0, ...S.flashes.map((c) => pulse(t, c, 0.02, 0.4)));
  const shake = Math.max(0, ...S.shakes.map((c) => pulse(t, c, 0.01, 0.28))) * 14;
  const sx = (random(`x${Math.floor(t * 30)}`) - 0.5) * shake, sy = (random(`y${Math.floor(t * 30)}`) - 0.5) * shake;
  const cs = React.useMemo(() => chunks(S.words, st.captionWords, st.captionChars), [slug]);
  const c = cs.find((k) => t >= k.s - 0.03 && t < k.e) ?? null;
  const hideCap = S.nocap.some(([a, b]) => t >= a && t < b);
  const gray = sh.gray ?? 0;
  const pt = (q: { x: number; y: number }) => { const pl = place(img.w, img.h, pose); return { x: pl.left + q.x * pl.dw, y: pl.top + q.y * pl.dh }; };

  return (
    <AbsoluteFill style={{ background: st.bg }}>
      <AbsoluteFill style={{ transform: `translate(${sx}px, ${sy}px)` }}>
        {!sh.kind && img.depth && <DepthImage src={img.src} depth={img.depth} iw={img.w} ih={img.h} pose={pose} shift={shift} dolly={dolly}
          gray={gray} contrast={sh.contrast ?? (gray ? 1.15 : 1.04)} bright={1 - (sh.dim ?? 0)} />}
        {(sh.kind === "image" || (!sh.kind && !img.depth)) && <Still im={img} pose={pose} gray={gray} dim={sh.dim ?? 0} contrast={sh.contrast ?? (gray ? 1.12 : 1.03)} />}
        {sh.kind === "peel" && <Peel t={t} im={img} under={S.images[sh.peel!.under]} pose={pose} gray={gray} a={sh.peel!.t0} b={sh.peel!.t1} />}
        {sh.kind === "map" && <MapCut t={t} s={sh.t} data={S.maps[sh.map!.id]} spec={sh.map!} ink={st.ink} accent={st.accent} font={st.titleFont} />}
        {sh.frame && <Frame im={img} pose={pose} />}
      </AbsoluteFill>
      {sh.kind !== "map" && <AbsoluteFill style={{ background: "radial-gradient(ellipse 80% 62% at 50% 46%, rgba(0,0,0,0) 45%, rgba(0,0,0,0.72) 100%)" }} />}
      {sh.kind !== "map" && <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(0,0,0,0) 58%, rgba(0,0,0,0.8) 100%)" }} />}

      {S.overlays.filter((o) => t >= o.t0 - 0.001 && t < o.t1).map((o, i) => <Over key={i} o={o} t={t} pt={pt} st={st} />)}

      {c && !hideCap && (
        <div style={{ position: "absolute", left: 70, right: 70, top: st.captionTop, textAlign: "center", fontFamily: st.captionFont, fontWeight: st.captionWeight,
          fontSize: st.captionSize, lineHeight: 1.08, letterSpacing: -1.2, textTransform: st.captionUpper ? "uppercase" : "none" }}>
          {c.words.map((wd, i) => {
            const on = t >= wd.s - 0.03; const k = backOut(ramp(t, wd.s - 0.04, wd.s + 0.12), 2);
            return <span key={i} style={{ display: "inline-block", marginRight: 22, color: on ? st.ink : "rgba(244,240,232,0.28)", fontStyle: wd.em ? "italic" : "normal",
              transform: `scale(${on ? 0.92 + 0.08 * k : 0.92})`, textShadow: "0 3px 30px rgba(0,0,0,0.75)" }}>{clean(wd.w)}</span>;
          })}
        </div>
      )}
      <AbsoluteFill style={{ background: "#fff", opacity: flash * 0.55, pointerEvents: "none" }} />
      <Grain opacity={gray > 0.5 ? st.grain * 2.2 : st.grain} />
      <Audio src={staticFile(S.audio)} />
    </AbsoluteFill>
  );
};

/* ---------- layers ---------- */
const Still: React.FC<{ im: Img; pose: Pose; gray: number; dim: number; contrast: number }> = ({ im, pose, gray, dim, contrast }) => {
  const pl = place(im.w, im.h, pose);
  return <Img src={staticFile(im.src)} style={{ position: "absolute", left: pl.left, top: pl.top, width: pl.dw, height: pl.dh,
    filter: `grayscale(${gray}) contrast(${contrast}) brightness(${1 - dim})` }} />;
};

/** the image hung small on a dark wall: thin frame + soft shadow (use with z < 1) */
const Frame: React.FC<{ im: Img; pose: Pose }> = ({ im, pose }) => {
  const pl = place(im.w, im.h, pose);
  return <div style={{ position: "absolute", left: pl.left - 14, top: pl.top - 14, width: pl.dw + 28, height: pl.dh + 28, border: "14px solid #2a2118",
    boxShadow: "0 40px 90px rgba(0,0,0,0.85), inset 0 0 0 2px rgba(201,168,106,0.55)", pointerEvents: "none" }} />;
};

/** the image lifts off and flies up out of frame like a peeled sheet, revealing `under` (e.g. bare plaster) */
const Peel: React.FC<{ t: number; im: Img; under: Img; pose: Pose; gray: number; a: number; b: number }> = ({ t, im, under, pose, gray, a, b }) => {
  const k = easeIn(ramp(t, a, b)); const pl = place(im.w, im.h, pose);
  return <AbsoluteFill style={{ perspective: 1800, perspectiveOrigin: "50% 0%" }}>
    <Img src={staticFile(under.src)} style={{ position: "absolute", left: 0, top: 0, width: W, height: H, objectFit: "cover", filter: "grayscale(1) brightness(0.62) contrast(1.1)" }} />
    <div style={{ position: "absolute", left: pl.left, top: pl.top, width: pl.dw, height: pl.dh, transformOrigin: "50% 0%",
      transform: `translateY(${-k * 1500}px) rotateX(${k * 62}deg) rotateZ(${k * -6}deg)`, boxShadow: `0 ${30 + 90 * k}px ${60 + 80 * k}px rgba(0,0,0,${0.35 + 0.4 * k})` }}>
      <Img src={staticFile(im.src)} style={{ width: "100%", height: "100%", filter: `grayscale(${gray}) contrast(1.1) brightness(${1 - 0.35 * k})` }} />
    </div>
  </AbsoluteFill>;
};

/** outline map that draws itself, pins that pop with a pulse ring, optional route arc */
const MapCut: React.FC<{ t: number; s: number; data: MapData; spec: NonNullable<Shot["map"]>; ink: string; accent: string; font: string }> = ({ t, s, data, spec, ink, accent, font }) => {
  const d = easeOut(ramp(t, s, s + 1.0)); const r = spec.route; const rk = r ? easeOut(ramp(t, r.t0, r.t1)) : 0;
  let arc = "";
  if (r) {
    const A = data.cities[r.from], B = data.cities[r.to];
    const mx = (A[0] + B[0]) / 2 + (B[1] - A[1]) * 0.25, my = (A[1] + B[1]) / 2 - Math.abs(B[0] - A[0]) * 0.25;
    arc = `M ${A[0]} ${A[1]} Q ${mx} ${my} ${B[0]} ${B[1]}`;
  }
  return (
    <AbsoluteFill style={{ background: "#0E0D0C" }}>
      <svg width={W} height={H} style={{ position: "absolute" }}>
        {data.land.map((p, i) => <path key={i} d={p} fill="none" stroke="rgba(233,230,224,0.13)" strokeWidth={2} />)}
        {data.focus.map((p, i) => <path key={i} d={p} fill={`rgba(233,230,224,${0.06 * d})`} stroke="#E9E6E0" strokeWidth={3} pathLength={1} strokeDasharray="1" strokeDashoffset={1 - d} />)}
        {r && rk > 0 && <path d={arc} fill="none" stroke={accent} strokeWidth={5} strokeLinecap="round" pathLength={1} strokeDasharray="1" strokeDashoffset={1 - rk} />}
        {spec.pins.map((pn, i) => {
          if (t < pn.t) return null;
          const c = data.cities[pn.city]; const k = backOut(ramp(t, pn.t, pn.t + 0.35), 2);
          return <g key={i}>
            <circle cx={c[0]} cy={c[1]} r={18 * k} fill={accent} />
            <circle cx={c[0]} cy={c[1]} r={18 + 50 * ((t * 1.4) % 1)} fill="none" stroke={accent} strokeWidth={3} opacity={k * (1 - ((t * 1.4) % 1))} />
          </g>;
        })}
      </svg>
      {spec.pins.map((pn, i) => {
        const c = data.cities[pn.city]; if (t < pn.t || !pn.label) return null;
        const right = c[0] < W * 0.62;
        return <div key={i} style={{ position: "absolute", top: c[1] - 46, ...(right ? { left: c[0] + 36 } : { right: W - c[0] + 36 }), fontFamily: font, fontStyle: "italic",
          fontSize: 72, color: ink, opacity: ramp(t, pn.t, pn.t + 0.3), whiteSpace: "nowrap" }}>{pn.label}</div>;
      })}
      <Grain opacity={0.14} />
    </AbsoluteFill>
  );
};

/* ---------- overlays ---------- */
const Over: React.FC<{ o: Overlay; t: number; pt: (q: { x: number; y: number }) => { x: number; y: number }; st: any }> = ({ o, t, pt, st }) => {
  const k = ramp(t, o.t0, o.t0 + 0.25);
  switch (o.type) {
    case "label":   // small mono caps, top-left: place · date · source
      return <div style={{ position: "absolute", left: 64, top: 120, fontFamily: st.labelFont, fontSize: 30, letterSpacing: 4, color: "rgba(233,230,224,0.88)", opacity: k,
        textShadow: "0 2px 12px rgba(0,0,0,0.8)" }}>{o.text}</div>;
    case "credit":  // tiny centred credit just above the captions (archival photos)
      return <div style={{ position: "absolute", left: 64, right: 64, top: st.captionTop - 100, textAlign: "center", fontFamily: st.uiFont, fontWeight: 600, fontSize: 24,
        letterSpacing: 5, color: "rgba(233,230,224,0.7)", opacity: k, textShadow: "0 2px 10px rgba(0,0,0,0.9)" }}>{o.text}</div>;
    case "title": { // big centred title card (hide captions with "nocap" while it shows)
      const kk = backOut(ramp(t, o.t0 - 0.05, o.t0 + 0.3), 1.6);
      return <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", background: `rgba(8,8,8,${0.45 * k})` }}>
        <div style={{ textAlign: "center", transform: `scale(${0.88 + 0.12 * kk})`, opacity: k, padding: "0 70px" }}>
          {o.kicker && <div style={{ fontFamily: st.uiFont, fontWeight: 600, fontSize: 30, letterSpacing: 8, color: "rgba(244,240,232,0.78)", marginBottom: 24 }}>{o.kicker}</div>}
          <div style={{ fontFamily: st.titleFont, fontWeight: 500, fontSize: 132, lineHeight: 1.02, letterSpacing: -3, color: st.ink, textShadow: "0 6px 40px rgba(0,0,0,0.85)" }}
            dangerouslySetInnerHTML={{ __html: o.text || "" }} />
          {o.sub && <div style={{ fontFamily: st.titleFont, fontStyle: "italic", fontSize: 48, color: "rgba(244,240,232,0.85)", marginTop: 26 }}>{o.sub}</div>}
        </div>
      </AbsoluteFill>;
    }
    case "pin": {   // location pill near the top
      const kk = backOut(ramp(t, o.t0, o.t0 + 0.35), 2);
      return <div style={{ position: "absolute", left: 0, right: 0, top: 300, display: "flex", justifyContent: "center", transform: `scale(${kk})` }}>
        <div style={{ padding: "16px 30px", borderRadius: 999, background: "rgba(20,18,15,0.6)", border: "1px solid rgba(255,255,255,0.18)", fontFamily: st.uiFont, fontWeight: 600,
          fontSize: 34, letterSpacing: 5, color: st.ink, display: "flex", gap: 14, alignItems: "center" }}>
          <svg width="30" height="36" viewBox="0 0 24 30"><path d="M12 0C5.4 0 0 5.2 0 11.7 0 20.5 12 30 12 30s12-9.5 12-18.3C24 5.2 18.6 0 12 0z" fill={st.accent} /><circle cx="12" cy="11.5" r="4.5" fill={st.ink} /></svg>
          {o.text}</div></div>;
    }
    case "ring": {  // hand-drawn ellipse around a detail of the current image (+ optional label)
      const q = pt(o.point!); const kk = easeOut(ramp(t, o.t0, o.t0 + 0.55));
      return <>
        <svg width={W} height={H} style={{ position: "absolute", left: 0, top: 0 }}>
          <ellipse cx={q.x} cy={q.y} rx={o.rx ?? 250} ry={o.ry ?? 170} transform={`rotate(${o.rot ?? -20} ${q.x} ${q.y})`} fill="none" stroke={st.ink} strokeWidth={5}
            pathLength={1} strokeDasharray="1" strokeDashoffset={1 - kk} />
        </svg>
        {o.text && <div style={{ position: "absolute", left: q.x - 320, top: q.y - (o.ry ?? 170) - 150, width: 640, textAlign: "center", fontFamily: st.titleFont, fontStyle: "italic",
          fontSize: 80, color: st.ink, opacity: ramp(t, o.t0 + 0.3, o.t0 + 0.6), textShadow: "0 4px 24px rgba(0,0,0,0.85)" }}>{o.text}</div>}
      </>;
    }
    case "hotspot": {
      const q = pt(o.point!); const kk = backOut(ramp(t, o.t0, o.t0 + 0.3), 2.4);
      return <div style={{ position: "absolute", left: q.x - 70, top: q.y - 70, width: 140, height: 140, borderRadius: 70, border: `4px solid ${st.ink}`, transform: `scale(${kk})`,
        boxShadow: "0 0 30px rgba(0,0,0,0.5)" }} />;
    }
    case "cut": {   // "cut here": dashed line around the part that was KEPT; the removed strips (inside the image only) tint red
      const [x0, y0, x1, y1] = o.box!; const a = pt({ x: x0, y: y0 }), b = pt({ x: x1, y: y1 }), i0 = pt({ x: 0, y: 0 }), i1 = pt({ x: 1, y: 1 });
      const col = o.color ?? st.accent; const kd = easeOut(ramp(t, o.t0, o.t0 + 0.8));
      const sh0 = o.shade ?? o.t0 + 0.6; const ks = easeOut(ramp(t, sh0, sh0 + 0.6)); const per = 2 * ((b.x - a.x) + (b.y - a.y));
      return <svg width={W} height={H} style={{ position: "absolute", left: 0, top: 0 }}>
        <path d={`M${i0.x} ${i0.y}H${i1.x}V${i1.y}H${i0.x}Z M${a.x} ${a.y}V${b.y}H${b.x}V${a.y}Z`} fillRule="evenodd" fill={`rgba(216,70,58,${0.26 * ks})`} />
        <rect x={a.x} y={a.y} width={b.x - a.x} height={b.y - a.y} fill="none" stroke="rgba(0,0,0,0.55)" strokeWidth={10} strokeDasharray={`${per * kd} ${per}`} />
        <rect x={a.x} y={a.y} width={b.x - a.x} height={b.y - a.y} fill="none" stroke={col} strokeWidth={5} strokeDasharray={`${per * kd} ${per}`} />
        <rect x={a.x} y={a.y} width={b.x - a.x} height={b.y - a.y} fill="none" stroke="#0B0B0B" strokeWidth={5.5} strokeDasharray="20 16"
          strokeDashoffset={-t * 40} style={{ opacity: kd }} />
      </svg>;
    }
    case "next": {  // silent end card: "NEXT" + tomorrow's teaser, in the caption zone once the last caption has gone
      const kk = easeOut(ramp(t, o.t0, o.t0 + 0.45)); const kl = easeOut(ramp(t, o.t0 + 0.1, o.t0 + 0.7));
      return <AbsoluteFill style={{ background: `linear-gradient(180deg, rgba(0,0,0,0) 48%, rgba(0,0,0,${0.62 * kk}) 82%)` }}>
        <div style={{ position: "absolute", left: 90, right: 90, top: st.captionTop - 60, textAlign: "center", opacity: kk, transform: `translateY(${(1 - kk) * 26}px)` }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 22, marginBottom: 22 }}>
            <div style={{ width: 70 * kl, height: 3, background: st.accent }} />
            <div style={{ fontFamily: st.uiFont, fontWeight: 600, fontSize: 30, letterSpacing: 9, color: st.ink }}>{o.kicker ?? "NEXT"}</div>
            <div style={{ width: 70 * kl, height: 3, background: st.accent }} />
          </div>
          <div style={{ fontFamily: st.titleFont, fontStyle: "italic", fontWeight: 500, fontSize: 74, lineHeight: 1.08, letterSpacing: -1.5, color: st.ink,
            textShadow: "0 4px 30px rgba(0,0,0,0.9)" }}>{o.text}</div>
        </div>
      </AbsoluteFill>;
    }
    case "stamp": { // rubber stamp slam (max one per reel)
      const kk = easeIn(ramp(t, o.t0, o.t0 + 0.14)); const col = o.color ?? st.accent;
      return <div style={{ position: "absolute", left: 0, right: 0, top: 820, textAlign: "center", transform: `scale(${2 - kk}) rotate(-10deg)`, opacity: kk * 0.92 }}>
        <span style={{ fontFamily: st.labelFont, fontWeight: 700, fontSize: 130, color: col, border: `12px solid ${col}`, padding: "0 34px", letterSpacing: 10 }}>{o.text}</span></div>;
    }
  }
  return null;
};
