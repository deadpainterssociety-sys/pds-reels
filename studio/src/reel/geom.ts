export const W = 1080;
export const H = 1920;
export type Pose = { x: number; y: number; z: number };

/** Image placement for a camera pose. z = 1 means "cover" (fills the 9:16 frame); z < 1 shows the whole image smaller.
 *  x, y = the image point (0..1) the camera centres on. Edges are clamped so the frame never shows past an image
 *  that is larger than the frame (that's why a point near an edge won't be centred at low zoom). */
export function place(iw: number, ih: number, pose: Pose, clampEdges = true) {
  const base = Math.max(W / iw, H / ih);
  const dw = iw * base * pose.z, dh = ih * base * pose.z;
  let left = W / 2 - pose.x * dw, top = H / 2 - pose.y * dh;
  if (clampEdges) {
    left = dw >= W ? Math.min(0, Math.max(W - dw, left)) : (W - dw) / 2;
    top = dh >= H ? Math.min(0, Math.max(H - dh, top)) : (H - dh) / 2;
  }
  return { left, top, dw, dh };
}
