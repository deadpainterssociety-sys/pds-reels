// Which Chrome to render with. Order: $BROWSER_EXECUTABLE -> a Playwright chrome-headless-shell already on the machine
// (setup.sh installs one) -> null (Remotion downloads its own from remotion.media; blocked in some sandboxes).
import fs from "fs"; import os from "os"; import path from "path";
export function findBrowser() {
  if (process.env.BROWSER_EXECUTABLE) return process.env.BROWSER_EXECUTABLE;
  const roots = [process.env.PLAYWRIGHT_BROWSERS_PATH, path.join(os.homedir(), ".cache/ms-playwright"), "/opt/pw-browsers",
    path.join(os.homedir(), "Library/Caches/ms-playwright")].filter(Boolean);
  for (const r of roots) {
    if (!fs.existsSync(r)) continue;
    for (const d of fs.readdirSync(r).filter((x) => x.startsWith("chromium_headless_shell")).sort().reverse()) {
      for (const sub of ["chrome-headless-shell-linux64/chrome-headless-shell", "chrome-linux/headless_shell",
        "chrome-headless-shell-mac-arm64/chrome-headless-shell", "chrome-headless-shell-mac-x64/chrome-headless-shell"]) {
        const p = path.join(r, d, sub); if (fs.existsSync(p)) return p;
      }
    }
  }
  return null;
}
