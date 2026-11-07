export const W = 1080;
export const H = 1920;
export type Pose = { x: number; y: number; z: number };

/** Image placement for a camera pose (frame FW x FH, default the 9:16 reel). z = 1 means "cover" (fills the frame); z < 1 shows the whole image smaller.
 *  x, y = the image point (0..1) the camera centres on. Edges are clamped so the frame never shows past an image
 *  that is larger than the frame (that's why a point near an edge won't be centred at low zoom). */
export function place(iw: number, ih: number, pose: Pose, clampEdges = true, FW = W, FH = H) {
  const base = Math.max(FW / iw, FH / ih);
  const dw = iw * base * pose.z, dh = ih * base * pose.z;
  let left = FW / 2 - pose.x * dw, top = FH / 2 - pose.y * dh;
  if (clampEdges) {
    left = dw >= FW ? Math.min(0, Math.max(FW - dw, left)) : (FW - dw) / 2;
    top = dh >= FH ? Math.min(0, Math.max(FH - dh, top)) : (FH - dh) / 2;
  }
  return { left, top, dw, dh };
}
