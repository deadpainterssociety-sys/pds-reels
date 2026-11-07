import React from "react";
import { AbsoluteFill, Audio, Img, staticFile, random } from "remotion";
import { useT, useFonts, Grain, ease, easeOut, easeIn, backOut, ramp, pulse, lerp, clamp, FontSpec } from "../reel/lib";
import { DepthImage } from "../reel/DepthImage";
import { Pose, place } from "../reel/geom";
import { STORIES } from "../reel/stories";

/* The long-form (16:9) engine: same look as the Shorts (living 2.5D paintings, grain, serif type, red accent),
   paced for 10+ minutes: crossfades, chapter cards, lower thirds, quotes, a 3D reconstruction of a room, an end screen.
   Data contract = the reel's (pipeline/build_story.py), plus shot kinds "pair" and "room", shot.fade, and these overlays. */
export const W = 1920, H = 1080;
type V3 = [number, number, number];
type Img = { src: string; w: number; h: number; depth?: string };
type Shot = {
  t: number; img: string; kind?: string; from: V3; to: V3; gray?: number; dim?: number; contrast?: number; dolly?: [number, number]; sway?: number;
  frame?: boolean; fade?: number; img2?: string; labels?: [string, string];
  map?: { id: string; pins: { city: string; t: number; label?: string }[]; route?: { from: string; to: string; t0: number; t1: number } };
  room?: { back?: string[]; left?: string[]; right?: string[]; front?: string[]; move?: [number, number]; yaw?: [number, number]; door?: boolean; dim?: number };
  peel?: { t0: number; t1: number; under: string };
};
type Overlay = {
  type: string; t0: number; t1: number; text?: string; kicker?: string; sub?: string; point?: { x: number; y: number }; rx?: number; ry?: number; rot?: number;
  color?: string; box?: [number, number, number, number]; shade?: number; side?: "left" | "right";
};
const lerpPose = (a: V3, b: V3, p: number): Pose => ({ x: lerp(a[0], b[0], p), y: lerp(a[1], b[1], p), z: Math.exp(lerp(Math.log(a[2]), Math.log(b[2]), p)) });

export const Long: React.FC<{ slug: string }> = ({ slug }) => {
  const S = STORIES[slug] as any;
  const st = { bg: "#0B0B0B", ink: "#F4F0E8", accent: "#D8463A", titleFont: "Newsreader", uiFont: "Inter", labelFont: "Space Mono", grain: 0.07,
    fonts: [] as FontSpec[], ...(S.style || {}) };
  useFonts(st.fonts);
  const t = useT();
  const shots: Shot[] = S.shots;
  let si = 0; for (let k = 0; k < shots.length; k++) if (t >= shots[k].t) si = k;
  const sh = shots[si], prev = shots[si - 1];
  const fade = sh.fade ?? 0;
  const inFade = prev && fade > 0 && t < sh.t + fade;
  const flash = Math.max(0, ...S.flashes.map((c: number) => pulse(t, c, 0.02, 0.4)));
  const shake = Math.max(0, ...S.shakes.map((c: number) => pulse(t, c, 0.01, 0.28))) * 10;
  const sx = (random(`x${Math.floor(t * 30)}`) - 0.5) * shake, sy = (random(`y${Math.floor(t * 30)}`) - 0.5) * shake;
  const end = (i: number) => (shots[i + 1] ? shots[i + 1].t : S.duration);
  const cur = shotPose(sh, t, end(si));
  const img = S.images[sh.img] as Img;
  const pt = (q: { x: number; y: number }) => { const pl = place(img.w, img.h, cur, true, W, H); return { x: pl.left + q.x * pl.dw, y: pl.top + q.y * pl.dh }; };
  const gray = sh.gray ?? 0;
  const flat = sh.kind === "map" || sh.kind === "room";
  return (
    <AbsoluteFill style={{ background: st.bg }}>
      <AbsoluteFill style={{ transform: `translate(${sx}px, ${sy}px)` }}>
        {inFade && <ShotView key={`s${si - 1}`} S={S} sh={prev} t={t} te={end(si - 1)} st={st} />}
        <AbsoluteFill key={`w${si}`} style={{ opacity: inFade ? easeOut(ramp(t, sh.t, sh.t + fade)) : 1 }}>
          <ShotView key={`s${si}`} S={S} sh={sh} t={t} te={end(si)} st={st} />
        </AbsoluteFill>
      </AbsoluteFill>
      {!flat && <AbsoluteFill style={{ background: "radial-gradient(ellipse 78% 74% at 50% 48%, rgba(0,0,0,0) 52%, rgba(0,0,0,0.62) 100%)" }} />}
      {S.overlays.filter((o: Overlay) => t >= o.t0 - 0.001 && t < o.t1).map((o: Overlay, i: number) => <Over key={i} o={o} t={t} pt={pt} st={st} S={S} />)}
      <AbsoluteFill style={{ background: "#fff", opacity: flash * 0.45, pointerEvents: "none" }} />
      <Grain opacity={gray > 0.5 ? st.grain * 2.2 : st.grain} />
      <Audio src={staticFile(S.audio)} />
    </AbsoluteFill>
  );
};

function shotPose(sh: Shot, t: number, te: number): Pose {
  const p = clamp((t - sh.t) / Math.max(0.2, te - sh.t));
  const e = ease(p) * 0.5 + p * 0.5;
  const pose = lerpPose(sh.from, sh.to, e);
  return { ...pose, z: pose.z * (1 + 0.02 * Math.exp(-(t - sh.t) * 5)) };
}

const ShotView: React.FC<{ S: any; sh: Shot; t: number; te: number; st: any }> = ({ S, sh, t, te, st }) => {
  const img = S.images[sh.img] as Img;
  const pose = shotPose(sh, t, te);
  const p = clamp((t - sh.t) / Math.max(0.2, te - sh.t)); const e = ease(p) * 0.5 + p * 0.5;
  const sway = sh.sway ?? 0.006;
  const shift: [number, number] = [Math.sin(t * 0.8) * sway, Math.cos(t * 0.6) * sway * 0.6];
  const dolly = sh.dolly ? lerp(sh.dolly[0], sh.dolly[1], e) : 0;
  const gray = sh.gray ?? 0;
  if (sh.kind === "pair") return <Pair S={S} sh={sh} t={t} te={te} st={st} />;
  if (sh.kind === "grid") return <Grid S={S} sh={sh} t={t} te={te} />;
  if (sh.kind === "room") return <Room S={S} sh={sh} t={t} te={te} />;
  if (sh.kind === "map") return <MapCut t={t} s={sh.t} data={S.maps[sh.map!.id]} spec={sh.map!} st={st} />;
  if (sh.kind === "peel") return <Peel t={t} im={img} under={S.images[sh.peel!.under]} pose={pose} gray={gray} a={sh.peel!.t0} b={sh.peel!.t1} />;
  return <AbsoluteFill>
    {!sh.kind && img.depth && <DepthImage src={img.src} depth={img.depth} iw={img.w} ih={img.h} pose={pose} shift={shift} dolly={dolly} fw={W} fh={H}
      gray={gray} contrast={sh.contrast ?? (gray ? 1.15 : 1.04)} bright={1 - (sh.dim ?? 0)} />}
    {(sh.kind === "image" || (!sh.kind && !img.depth)) && <Still im={img} pose={pose} gray={gray} dim={sh.dim ?? 0} contrast={sh.contrast ?? (gray ? 1.12 : 1.03)} />}
    {sh.frame && <Frame im={img} pose={pose} />}
  </AbsoluteFill>;
};

const Still: React.FC<{ im: Img; pose: Pose; gray: number; dim: number; contrast: number }> = ({ im, pose, gray, dim, contrast }) => {
  const pl = place(im.w, im.h, pose, true, W, H);
  return <Img src={staticFile(im.src)} style={{ position: "absolute", left: pl.left, top: pl.top, width: pl.dw, height: pl.dh,
    filter: `grayscale(${gray}) contrast(${contrast}) brightness(${1 - dim})` }} />;
};

const Frame: React.FC<{ im: Img; pose: Pose }> = ({ im, pose }) => {
  const pl = place(im.w, im.h, pose, true, W, H);
  return <div style={{ position: "absolute", left: pl.left - 12, top: pl.top - 12, width: pl.dw + 24, height: pl.dh + 24, border: "12px solid #2a2118",
    boxShadow: "0 40px 90px rgba(0,0,0,0.85), inset 0 0 0 2px rgba(201,168,106,0.55)", pointerEvents: "none" }} />;
};

/** the painting lifts off the wall like a peeled sheet, revealing bare plaster (`under`) */
const Peel: React.FC<{ t: number; im: Img; under: Img; pose: Pose; gray: number; a: number; b: number }> = ({ t, im, under, pose, gray, a, b }) => {
  const k = easeIn(ramp(t, a, b)); const pl = place(im.w, im.h, pose, true, W, H);
  return <AbsoluteFill style={{ perspective: 2200, perspectiveOrigin: "50% 0%" }}>
    <Img src={staticFile(under.src)} style={{ position: "absolute", left: 0, top: 0, width: W, height: H, objectFit: "cover", filter: "grayscale(1) brightness(0.62) contrast(1.1)" }} />
    <div style={{ position: "absolute", left: pl.left, top: pl.top, width: pl.dw, height: pl.dh, transformOrigin: "50% 0%",
      transform: `translateY(${-k * 1300}px) rotateX(${k * 62}deg) rotateZ(${k * -5}deg)`, boxShadow: `0 ${30 + 90 * k}px ${60 + 80 * k}px rgba(0,0,0,${0.35 + 0.4 * k})` }}>
      <Img src={staticFile(im.src)} style={{ width: "100%", height: "100%", filter: `grayscale(${gray}) contrast(1.1) brightness(${1 - 0.35 * k})` }} />
    </div>
  </AbsoluteFill>;
};

/** two images side by side (a comparison), each slowly pushing in, a small caps label under each */
const Pair: React.FC<{ S: any; sh: Shot; t: number; te: number; st: any }> = ({ S, sh, t, te, st }) => {
  const k = ease(clamp((t - sh.t) / Math.max(1, te - sh.t)));
  const one = (name: string, cx: number, label: string | undefined, i: number) => {
    const im = S.images[name] as Img; const s = Math.min(800 / im.w, 860 / im.h); const w = im.w * s, h = im.h * s;
    const a = easeOut(ramp(t, sh.t + i * 0.35, sh.t + i * 0.35 + 0.6));
    return <div key={name} style={{ position: "absolute", left: cx - w / 2, top: 500 - h / 2, width: w, height: h, opacity: a,
      transform: `scale(${1 + 0.035 * k})`, boxShadow: "0 30px 80px rgba(0,0,0,0.8)" }}>
      <Img src={staticFile(im.src)} style={{ width: "100%", height: "100%", filter: "contrast(1.04)" }} />
      {label && <div style={{ position: "absolute", left: -200, right: -200, top: h + 26, textAlign: "center", fontFamily: st.uiFont, fontWeight: 600, fontSize: 22,
        letterSpacing: 6, color: "rgba(244,240,232,0.82)" }}>{label}</div>}
    </div>;
  };
  return <AbsoluteFill style={{ background: "#0d0c0b" }}>
    {one(sh.img, 500, sh.labels?.[0], 0)}{one(sh.img2!, 1420, sh.labels?.[1], 1)}
  </AbsoluteFill>;
};

/** a whole series at once: images in justified rows (same height per row, rows filling the width), appearing one by
    one like pictures being hung, the wall of them slowly closing in */
const Grid: React.FC<{ S: any; sh: Shot; t: number; te: number }> = ({ S, sh, t, te }) => {
  const names = (sh as any).imgs as string[]; const gap = 18, avail = W - 200;
  const asp = (n: string) => S.images[n].w / S.images[n].h; const all = names.reduce((x, n) => x + asp(n), 0);
  const nrows = names.length >= 9 ? 3 : names.length >= 4 ? 2 : 1;            // balanced rows: split at equal shares of the total width
  const rows: string[][] = Array.from({ length: nrows }, () => []); let acc = 0;
  for (const n of names) { const r = Math.min(nrows - 1, Math.floor(((acc + asp(n) / 2) / all) * nrows)); rows[r].push(n); acc += asp(n); }
  const target = 9999;
  const rowH = rows.map((r) => { const a = r.reduce((x, n) => x + S.images[n].w / S.images[n].h, 0); return Math.min(target * 1.25, (avail - gap * (r.length - 1)) / a); });
  const total = rowH.reduce((x, h) => x + h, 0) + gap * (rows.length - 1); const fit = Math.min(1, (H - 160) / total);
  const k = ease(clamp((t - sh.t) / Math.max(1, te - sh.t)));
  let y = (H - total * fit) / 2, idx = 0;
  const out: React.ReactNode[] = [];
  rows.forEach((r, ri) => {
    const h = rowH[ri] * fit; const wsum = r.reduce((x, n) => x + (S.images[n].w / S.images[n].h) * h, 0) + gap * fit * (r.length - 1);
    let x = (W - wsum) / 2;
    for (const n of r) {
      const im = S.images[n] as Img; const w = (im.w / im.h) * h; const i = idx++;
      const a = easeOut(ramp(t, sh.t + 0.07 * i, sh.t + 0.07 * i + 0.45));
      out.push(<Img key={n} src={staticFile(im.src)} style={{ position: "absolute", left: x, top: y, width: w, height: h, opacity: a,
        transform: `translateY(${(1 - a) * 16}px)`, boxShadow: "0 18px 40px rgba(0,0,0,0.7)", filter: "contrast(1.04)" }} />);
      x += w + gap * fit;
    }
    y += h + gap * fit;
  });
  return <AbsoluteFill style={{ background: "#0d0c0b", transform: `scale(${1 + 0.04 * k})` }}>{out}</AbsoluteFill>;
};

/** a room rebuilt in CSS 3D: paintings on its walls, the camera walking in (approximate reconstruction) */
const Room: React.FC<{ S: any; sh: Shot; t: number; te: number }> = ({ S, sh, t, te }) => {
  const r = sh.room!; const p = ease(clamp((t - sh.t) / Math.max(1, te - sh.t)));
  const RW = 1500, RH = 780, RD = 2300;
  const camZ = lerp(r.move?.[0] ?? 0, r.move?.[1] ?? 700, p), yaw = lerp(r.yaw?.[0] ?? 0, r.yaw?.[1] ?? 0, p);
  const wall = (w: number, transform: string, imgs: string[] = [], door = false) => {
    const n = imgs.length; const hh = RH * 0.64;
    return <div style={{ position: "absolute", left: -w / 2, top: -RH / 2, width: w, height: RH, transform, backfaceVisibility: "hidden",
      background: `linear-gradient(rgba(20,16,12,0.4), rgba(20,16,12,0.4)), url(${staticFile("tex/plaster.jpg")}) center/cover` }}>
      {door && <div style={{ position: "absolute", left: w / 2 - 120, bottom: 0, width: 240, height: RH * 0.78, background: "linear-gradient(#2b2017,#17110c)",
        boxShadow: "inset 0 0 0 6px #3a2c20" }} />}
      {imgs.map((name, i) => {
        const im = S.images[name] as Img; const ww = Math.min(im.w / im.h * hh, (w * 0.86) / Math.max(1, n));
        const h2 = ww * im.h / im.w; const slot = w / n; const cx = door && n === 2 ? (i === 0 ? w / 2 - 140 - ww / 2 - 40 : w / 2 + 140 + ww / 2 + 40) : slot * (i + 0.5);
        return <Img key={name} src={staticFile(im.src)} style={{ position: "absolute", left: cx - ww / 2, top: RH * 0.42 - h2 / 2, width: ww, height: h2,
          filter: "brightness(0.92) contrast(1.05)", boxShadow: "0 0 40px rgba(0,0,0,0.6)" }} />;
      })}
      <div style={{ position: "absolute", inset: 0, background: "radial-gradient(ellipse 70% 80% at 50% 45%, rgba(0,0,0,0) 40%, rgba(0,0,0,0.55) 100%)" }} />
    </div>;
  };
  return <AbsoluteFill style={{ background: "#070605", perspective: 1000, perspectiveOrigin: "50% 46%", overflow: "hidden" }}>
    <div style={{ position: "absolute", left: W / 2, top: H / 2, transformStyle: "preserve-3d", transform: `translateZ(${camZ}px) rotateY(${yaw}deg)` }}>
      {wall(RW, `translateZ(${-RD / 2}px)`, r.back)}
      {wall(RD, `translateX(${-RW / 2}px) rotateY(90deg)`, r.left)}
      {wall(RD, `translateX(${RW / 2}px) rotateY(-90deg)`, r.right)}
      {wall(RW, `translateZ(${RD / 2}px) rotateY(180deg)`, r.front, r.door)}
      <div style={{ position: "absolute", left: -RW / 2, top: -RD / 2, width: RW, height: RD, transform: `translateY(${RH / 2}px) rotateX(90deg)`,
        background: "linear-gradient(#120e0a, #1d1610 50%, #120e0a)" }} />
      <div style={{ position: "absolute", left: -RW / 2, top: -RD / 2, width: RW, height: RD, transform: `translateY(${-RH / 2}px) rotateX(-90deg)`,
        background: "#0c0a08" }} />
    </div>
    <AbsoluteFill style={{ background: `rgba(0,0,0,${r.dim ?? 0})` }} />
  </AbsoluteFill>;
};

/** outline map (precomputed for 1920x1080 by tools/map.mjs with "size"), pins, optional route arc */
const MapCut: React.FC<{ t: number; s: number; data: any; spec: NonNullable<Shot["map"]>; st: any }> = ({ t, s, data, spec, st }) => {
  const d = easeOut(ramp(t, s, s + 1.0)); const r = spec.route; const rk = r ? easeOut(ramp(t, r.t0, r.t1)) : 0;
  let arc = "";
  if (r) {
    const A = data.cities[r.from], B = data.cities[r.to];
    const mx = (A[0] + B[0]) / 2 + (B[1] - A[1]) * 0.25, my = (A[1] + B[1]) / 2 - Math.abs(B[0] - A[0]) * 0.25;
    arc = `M ${A[0]} ${A[1]} Q ${mx} ${my} ${B[0]} ${B[1]}`;
  }
  return <AbsoluteFill style={{ background: "#0E0D0C" }}>
    <svg width={W} height={H} style={{ position: "absolute" }}>
      {data.land.map((p: string, i: number) => <path key={i} d={p} fill="none" stroke="rgba(233,230,224,0.13)" strokeWidth={1.6} />)}
      {data.focus.map((p: string, i: number) => <path key={i} d={p} fill={`rgba(233,230,224,${0.06 * d})`} stroke="#E9E6E0" strokeWidth={2.4} pathLength={1} strokeDasharray="1" strokeDashoffset={1 - d} />)}
      {r && rk > 0 && <path d={arc} fill="none" stroke={st.accent} strokeWidth={4} strokeLinecap="round" pathLength={1} strokeDasharray="1" strokeDashoffset={1 - rk} />}
      {spec.pins.map((pn, i) => {
        if (t < pn.t) return null;
        const c = data.cities[pn.city]; const k = backOut(ramp(t, pn.t, pn.t + 0.35), 2);
        return <g key={i}><circle cx={c[0]} cy={c[1]} r={12 * k} fill={st.accent} />
          <circle cx={c[0]} cy={c[1]} r={12 + 36 * ((t * 1.4) % 1)} fill="none" stroke={st.accent} strokeWidth={2.5} opacity={k * (1 - ((t * 1.4) % 1))} /></g>;
      })}
    </svg>
    {spec.pins.map((pn, i) => {
      const c = data.cities[pn.city]; if (t < pn.t || !pn.label) return null;
      const right = c[0] < W * 0.62;
      return <div key={i} style={{ position: "absolute", top: c[1] - 34, ...(right ? { left: c[0] + 28 } : { right: W - c[0] + 28 }), fontFamily: st.titleFont, fontStyle: "italic",
        fontSize: 54, color: st.ink, opacity: ramp(t, pn.t, pn.t + 0.3), whiteSpace: "nowrap" }}>{pn.label}</div>;
    })}
    <Grain opacity={0.12} />
  </AbsoluteFill>;
};

/* ---------- overlays (16:9 positions) ---------- */
const Rule: React.FC<{ w: number; color: string }> = ({ w, color }) => <div style={{ width: w, height: 2, background: color }} />;

const Over: React.FC<{ o: Overlay; t: number; pt: (q: { x: number; y: number }) => { x: number; y: number }; st: any; S: any }> = ({ o, t, pt, st }) => {
  const kin = ramp(t, o.t0, o.t0 + 0.35), kout = 1 - ramp(t, o.t1 - 0.35, o.t1); const k = Math.min(kin, kout);
  const shadow = "0 2px 18px rgba(0,0,0,0.85)";
  switch (o.type) {
    case "label":   // small mono caps, top-left: place · date · object
      return <div style={{ position: "absolute", left: 96, top: 76, fontFamily: st.labelFont, fontSize: 26, letterSpacing: 4, color: "rgba(233,230,224,0.9)", opacity: k,
        textShadow: shadow }}>{o.text}</div>;
    case "credit":  // tiny credit, bottom-left (licences, archive photos)
      return <div style={{ position: "absolute", left: 96, bottom: 58, fontFamily: st.uiFont, fontWeight: 600, fontSize: 17, letterSpacing: 3.5,
        color: "rgba(233,230,224,0.62)", opacity: k, textShadow: shadow }}>{o.text}</div>;
    case "lower": { // lower third: a name and what they are
      const kk = easeOut(ramp(t, o.t0, o.t0 + 0.6));
      return <div style={{ position: "absolute", left: 96, bottom: 120, opacity: k, transform: `translateX(${(1 - kk) * -24}px)` }}>
        <div style={{ width: 64 * kk, height: 3, background: st.accent, marginBottom: 16 }} />
        <div style={{ fontFamily: st.titleFont, fontWeight: 500, fontSize: 54, lineHeight: 1.05, color: st.ink, textShadow: shadow }}>{o.text}</div>
        {o.sub && <div style={{ fontFamily: st.uiFont, fontWeight: 600, fontSize: 19, letterSpacing: 5, color: "rgba(233,230,224,0.78)", marginTop: 12, textShadow: shadow }}>{o.sub}</div>}
      </div>;
    }
    case "chapter": case "title": { // chapter card: kicker between two red rules + big serif title (+ optional italic line)
      const kk = backOut(ramp(t, o.t0 - 0.05, o.t0 + 0.5), 1.3); const big = o.type === "title";
      return <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", background: `rgba(6,6,6,${0.55 * k})` }}>
        <div style={{ textAlign: "center", opacity: k, transform: `scale(${0.96 + 0.04 * kk})`, padding: "0 140px" }}>
          {o.kicker && <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 22, marginBottom: 26 }}>
            <Rule w={70 * kk} color={st.accent} />
            <div style={{ fontFamily: st.uiFont, fontWeight: 600, fontSize: 24, letterSpacing: 10, color: "rgba(244,240,232,0.86)" }}>{o.kicker}</div>
            <Rule w={70 * kk} color={st.accent} /></div>}
          <div style={{ fontFamily: st.titleFont, fontWeight: 500, fontSize: big ? 156 : 112, lineHeight: 1.02, letterSpacing: big ? -4 : -2.5, color: st.ink,
            textShadow: "0 6px 40px rgba(0,0,0,0.85)" }} dangerouslySetInnerHTML={{ __html: o.text || "" }} />
          {o.sub && <div style={{ fontFamily: st.titleFont, fontStyle: "italic", fontSize: 42, color: "rgba(244,240,232,0.85)", marginTop: 22 }}>{o.sub}</div>}
        </div>
      </AbsoluteFill>;
    }
    case "quote": { // a sentence in italic serif with its source, over a darkened frame
      return <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", background: `rgba(6,6,6,${0.5 * k})` }}>
        <div style={{ maxWidth: 1340, textAlign: "center", opacity: k, transform: `translateY(${(1 - kin) * 14}px)` }}>
          <div style={{ fontFamily: st.titleFont, fontStyle: "italic", fontWeight: 500, fontSize: 66, lineHeight: 1.16, letterSpacing: -1, color: st.ink, textShadow: shadow }}
            dangerouslySetInnerHTML={{ __html: `“${o.text}”` }} />
          {o.sub && <div style={{ fontFamily: st.uiFont, fontWeight: 600, fontSize: 21, letterSpacing: 6, color: "rgba(233,230,224,0.75)", marginTop: 30 }}>{o.sub}</div>}
        </div>
      </AbsoluteFill>;
    }
    case "year": {  // a big date that fades in at the bottom left (time jumps)
      return <div style={{ position: "absolute", left: 90, bottom: 70, fontFamily: st.titleFont, fontWeight: 500, fontSize: 190, letterSpacing: -6, lineHeight: 1,
        color: "rgba(244,240,232,0.92)", opacity: k * 0.92, textShadow: "0 6px 40px rgba(0,0,0,0.8)", transform: `translateY(${(1 - easeOut(kin)) * 20}px)` }}>{o.text}</div>;
    }
    case "pin": {
      const kk = backOut(ramp(t, o.t0, o.t0 + 0.35), 2);
      return <div style={{ position: "absolute", left: 0, right: 0, top: 84, display: "flex", justifyContent: "center", transform: `scale(${kk})`, opacity: kout }}>
        <div style={{ padding: "12px 24px", borderRadius: 999, background: "rgba(20,18,15,0.6)", border: "1px solid rgba(255,255,255,0.18)", fontFamily: st.uiFont,
          fontWeight: 600, fontSize: 24, letterSpacing: 4, color: st.ink, display: "flex", gap: 12, alignItems: "center" }}>
          <svg width="22" height="27" viewBox="0 0 24 30"><path d="M12 0C5.4 0 0 5.2 0 11.7 0 20.5 12 30 12 30s12-9.5 12-18.3C24 5.2 18.6 0 12 0z" fill={st.accent} /><circle cx="12" cy="11.5" r="4.5" fill={st.ink} /></svg>
          {o.text}</div></div>;
    }
    case "ring": {
      const q = pt(o.point!); const kk = easeOut(ramp(t, o.t0, o.t0 + 0.55));
      return <div style={{ opacity: kout }}>
        <svg width={W} height={H} style={{ position: "absolute", left: 0, top: 0 }}>
          <ellipse cx={q.x} cy={q.y} rx={o.rx ?? 170} ry={o.ry ?? 120} transform={`rotate(${o.rot ?? -14} ${q.x} ${q.y})`} fill="none" stroke={st.ink} strokeWidth={4}
            pathLength={1} strokeDasharray="1" strokeDashoffset={1 - kk} />
        </svg>
        {o.text && <div style={{ position: "absolute", left: q.x - 360, top: q.y - (o.ry ?? 120) - 92, width: 720, textAlign: "center", fontFamily: st.titleFont,
          fontStyle: "italic", fontSize: 52, color: st.ink, opacity: ramp(t, o.t0 + 0.3, o.t0 + 0.6), textShadow: shadow }}>{o.text}</div>}
      </div>;
    }
    case "hotspot": {
      const q = pt(o.point!); const kk = backOut(ramp(t, o.t0, o.t0 + 0.3), 2.4);
      return <div style={{ position: "absolute", left: q.x - 54, top: q.y - 54, width: 108, height: 108, borderRadius: 54, border: `3px solid ${st.ink}`,
        transform: `scale(${kk})`, opacity: kout, boxShadow: "0 0 24px rgba(0,0,0,0.5)" }} />;
    }
    case "stamp": {
      const kk = easeIn(ramp(t, o.t0, o.t0 + 0.14)); const col = o.color ?? st.accent;
      return <div style={{ position: "absolute", left: 0, right: 0, top: 440, textAlign: "center", transform: `scale(${2 - kk}) rotate(-8deg)`, opacity: kk * 0.92 * kout }}>
        <span style={{ fontFamily: st.labelFont, fontWeight: 700, fontSize: 104, color: col, border: `10px solid ${col}`, padding: "0 30px", letterSpacing: 8 }}>{o.text}</span></div>;
    }
    case "end": {   // end screen: calm, with room for YouTube's end-screen elements (video on the left, subscribe on the right)
      const kk = easeOut(ramp(t, o.t0, o.t0 + 1.2));
      return <AbsoluteFill style={{ background: `rgba(6,6,6,${0.72 * kk})` }}>
        <div style={{ position: "absolute", left: 0, right: 0, top: 150, textAlign: "center", opacity: kk }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 22 }}>
            <Rule w={70} color={st.accent} />
            <div style={{ fontFamily: st.uiFont, fontWeight: 600, fontSize: 24, letterSpacing: 10, color: "rgba(244,240,232,0.86)" }}>{o.kicker ?? "NEXT"}</div>
            <Rule w={70} color={st.accent} /></div>
          {o.text && <div style={{ fontFamily: st.titleFont, fontStyle: "italic", fontSize: 58, color: st.ink, marginTop: 22, textShadow: shadow }}>{o.text}</div>}
        </div>
      </AbsoluteFill>;
    }
  }
  return null;
};
