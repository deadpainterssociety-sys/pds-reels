"""Hand a finished long video to the `long` workflow through a short-lived git branch.

Claude's session can push to git but may not create releases, so the files travel on an orphan branch long-<slug>
(videos split into 90 MB parts: GitHub refuses files over 100 MB). The workflow reassembles them, uploads to YouTube as
a private, scheduled video, and deletes the branch at the end, so the files are on GitHub only for the few minutes
between the push and the upload. Dispatch the workflow right after parking.

usage: python automation/long_park.py park <slug>    (local)  out/ -> branch long-<slug> (force-pushed)
       python automation/long_park.py fetch <slug>   (CI)     branch long-<slug> -> stories/<slug>/out/
       python automation/long_park.py drop <slug>    (CI)     delete the branch
"""
import glob, os, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES = ["thumb_a.jpg", "thumb_b.jpg", "captions.srt", "description.txt", "titles.txt"]
PART = 90 * 1024 * 1024


def git(*a, cwd=ROOT, **kw): return subprocess.run(["git", *a], cwd=cwd, check=True, **kw)


def video_of(out, slug):
    """the YouTube upload file: the ~370 MB upload copy when there is one (the master can be 1.5 GB), else the master"""
    for f in (f"{slug}_upload_1080p.mp4", f"{slug}.mp4"):
        if os.path.exists(os.path.join(out, f)): return f
    raise SystemExit(f"no video in {out}: run long_finalize.py first")


def park(slug):
    out = os.path.join(ROOT, "stories", slug, "out"); vid = video_of(out, slug)
    url = subprocess.run(["git", "remote", "get-url", "origin"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
    with tempfile.TemporaryDirectory(dir=os.path.join(ROOT, "..")) as tmp:
        for f in FILES + [vid]:
            src = os.path.join(out, f)
            if not os.path.exists(src): raise SystemExit(f"missing {src}")
            dst = f"{slug}.mp4" if f == vid else f   # the workflow always finds the video as <slug>.mp4
            with open(src, "rb") as fi:
                if os.path.getsize(src) <= PART: shutil.copyfileobj(fi, open(os.path.join(tmp, dst), "wb")); continue
                k = 0
                while chunk := fi.read(PART):
                    open(os.path.join(tmp, f"{dst}.part{k:02d}"), "wb").write(chunk); k += 1
        git("init", "-q", "-b", f"long-{slug}", cwd=tmp); git("add", "-A", cwd=tmp)
        git("-c", "user.name=Claude", "-c", "user.email=noreply@anthropic.com", "commit", "-qm", f"long video {slug} (temporary)", cwd=tmp)
        git("push", "-qf", url, f"long-{slug}", cwd=tmp)
    print(f"parked {vid} + {len(FILES)} files on branch long-{slug}")


def fetch(slug):
    out = os.path.join(ROOT, "stories", slug, "out"); os.makedirs(out, exist_ok=True)
    git("fetch", "-q", "--depth", "1", "origin", f"long-{slug}")
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(f"git archive FETCH_HEAD | tar -x -C {tmp}", shell=True, cwd=ROOT, check=True)
        for f in sorted(os.listdir(tmp)):
            if ".part" in f: continue
            shutil.move(os.path.join(tmp, f), os.path.join(out, f))
        for base in sorted({f.split(".part")[0] for f in os.listdir(tmp) if ".part" in f}):
            with open(os.path.join(out, base), "wb") as fo:
                for p in sorted(glob.glob(os.path.join(tmp, base + ".part*"))): shutil.copyfileobj(open(p, "rb"), fo)
    for f in sorted(os.listdir(out)): print(f, os.path.getsize(os.path.join(out, f)))


def drop(slug): git("push", "-q", "origin", "--delete", f"long-{slug}")


if __name__ == "__main__":
    {"park": park, "fetch": fetch, "drop": drop}[sys.argv[1]](sys.argv[2])
