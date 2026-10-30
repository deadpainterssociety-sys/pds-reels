import React, { useEffect, useLayoutEffect, useRef, useState } from "react";
import { continueRender, delayRender, staticFile } from "remotion";
import { Pose, place, W, H } from "./geom";

/** 2.5D painting: re-projected through its depth map so the foreground moves more than the background. */
const VS = `attribute vec2 p; varying vec2 v; void main(){ v = p * 0.5 + 0.5; v.y = 1.0 - v.y; gl_Position = vec4(p, 0.0, 1.0); }`;
const FS = `precision highp float;
varying vec2 v;
uniform sampler2D img; uniform sampler2D dep;
uniform vec4 place; uniform vec2 res; uniform vec2 shift; uniform float dolly; uniform vec2 focus;
uniform float gray; uniform float bright; uniform float contrast; uniform vec3 bg;
void main(){
  vec2 s = v * res;
  vec2 uv = (s - place.xy) / place.zw;
  vec2 q = uv;
  for (int i = 0; i < 6; i++) {
    float d = texture2D(dep, q).r;
    q = uv - (d - 0.45) * shift - (uv - focus) * (d * dolly);
  }
  if (q.x < 0.0 || q.y < 0.0 || q.x > 1.0 || q.y > 1.0) { gl_FragColor = vec4(bg, 1.0); return; }
  vec3 c = texture2D(img, q).rgb;
  float l = dot(c, vec3(0.299, 0.587, 0.114));
  c = mix(c, vec3(l), gray);
  c = (c - 0.5) * contrast + 0.5;
  gl_FragColor = vec4(c * bright, 1.0);
}`;

const loadImg = (src: string) => new Promise<HTMLImageElement>((res, rej) => { const i = new Image(); i.onload = () => res(i); i.onerror = rej; i.src = src; });

export const DepthImage: React.FC<{
  src: string; depth: string; iw: number; ih: number; pose: Pose; shift?: [number, number]; dolly?: number;
  gray?: number; bright?: number; contrast?: number; bg?: [number, number, number];
}> = ({ src, depth, iw, ih, pose, shift = [0, 0], dolly = 0, gray = 0, bright = 1, contrast = 1, bg = [0.04, 0.04, 0.04] }) => {
  const ref = useRef<HTMLCanvasElement>(null);
  const glRef = useRef<{ gl: WebGLRenderingContext; prog: WebGLProgram } | null>(null);
  const [handle] = useState(() => delayRender("depth-textures"));
  const [ready, setReady] = useState(false);
  const done = useRef(false);

  useEffect(() => {
    let dead = false;
    (async () => {
      const [a, b] = await Promise.all([loadImg(staticFile(src)), loadImg(staticFile(depth))]);
      if (dead) return;
      const gl = ref.current!.getContext("webgl", { preserveDrawingBuffer: true, antialias: false })!;
      const sh = (t: number, s: string) => { const o = gl.createShader(t)!; gl.shaderSource(o, s); gl.compileShader(o);
        if (!gl.getShaderParameter(o, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(o) || "shader"); return o; };
      const prog = gl.createProgram()!; gl.attachShader(prog, sh(gl.VERTEX_SHADER, VS)); gl.attachShader(prog, sh(gl.FRAGMENT_SHADER, FS));
      gl.linkProgram(prog); gl.useProgram(prog);
      const buf = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, buf);
      gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]), gl.STATIC_DRAW);
      const loc = gl.getAttribLocation(prog, "p"); gl.enableVertexAttribArray(loc); gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
      [a, b].forEach((im, i) => {
        const tex = gl.createTexture(); gl.activeTexture(gl.TEXTURE0 + i); gl.bindTexture(gl.TEXTURE_2D, tex);
        gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGB, gl.RGB, gl.UNSIGNED_BYTE, im);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
      });
      gl.uniform1i(gl.getUniformLocation(prog, "img"), 0); gl.uniform1i(gl.getUniformLocation(prog, "dep"), 1);
      glRef.current = { gl, prog }; setReady(true);
    })().catch((e) => { console.error(e); if (!done.current) { done.current = true; continueRender(handle); } });
    return () => { dead = true; };
  }, [src, depth]);

  useLayoutEffect(() => {
    const g = glRef.current; if (!g) return;
    const { gl, prog } = g; const u = (n: string) => gl.getUniformLocation(prog, n);
    const pl = place(iw, ih, pose);
    gl.viewport(0, 0, W, H);
    gl.uniform4f(u("place"), pl.left, pl.top, pl.dw, pl.dh);
    gl.uniform2f(u("res"), W, H);
    gl.uniform2f(u("shift"), shift[0], shift[1]);
    gl.uniform1f(u("dolly"), dolly);
    gl.uniform2f(u("focus"), pose.x, pose.y);
    gl.uniform1f(u("gray"), gray); gl.uniform1f(u("bright"), bright); gl.uniform1f(u("contrast"), contrast);
    gl.uniform3f(u("bg"), bg[0], bg[1], bg[2]);
    gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
    gl.finish();
    if (ready && !done.current) { done.current = true; continueRender(handle); }
  });
  return <canvas ref={ref} width={W} height={H} style={{ position: "absolute", left: 0, top: 0, width: W, height: H }} />;
};
