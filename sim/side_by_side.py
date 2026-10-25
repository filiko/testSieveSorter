"""Real-vs-sim side-by-side clip: scale both to one height, hstack, label each half.

Run from sim\\:
  python side_by_side.py --real <phone clip> --sim <sim clip> [-o ../media/demo_side_by_side.mp4]
      [--real-start S] [--sim-start S] [--duration S] [--height 720]
The sim clip is record_view.py's MP4 or a .webm from the replay page's Record button. Chrome's
MediaRecorder writes full-range pixels into a WebM tagged limited-range, which decodes with the
light greys clipped to white; that is detected from a background pixel and undone. Both halves are
resampled to --fps and the output bitrate is capped so the file stays under --max-mb.
"""
import argparse
import json
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
FONT = Path(r"C:\Windows\Fonts\segoeuib.ttf")


def probe(path: Path) -> dict:
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=codec_name,width,height,color_range:format=duration", "-of", "json", str(path)],
                         capture_output=True, text=True, check=True).stdout
    j = json.loads(out)
    s = j["streams"][0]
    dur = j.get("format", {}).get("duration")
    s["duration"] = float(dur) if dur not in (None, "N/A") else None
    return s


def duration(path: Path) -> float:
    """Container duration, or the last frame's timestamp (MediaRecorder WebMs have no duration)."""
    d = probe(path)["duration"]
    if d:
        return d
    ts = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "frame=pts_time",
                         "-of", "csv=p=0", str(path)], capture_output=True, text=True, check=True).stdout.split()
    return float(ts[-1]) if ts else 0.0


def mislabeled_full_range(path: Path, start: float) -> bool:
    """True if the clip carries full-range luma but decodes as limited range: the raw Y of the corner (scene
    background, #eef1f5) is above 235. The tags can't be trusted either way: Chrome's VP9 WebM says tv, its
    VP8 WebM says pc at the container level, and ffmpeg's VP8 decoder still hands the frames on as tv."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{start}", "-i", str(path), "-frames:v", "1",
                          "-vf", "crop=8:8:8:8", "-f", "rawvideo", "-pix_fmt", "yuv420p", "-"],
                         capture_output=True, check=True).stdout
    y = raw[:64]                          # the 8x8 luma plane comes first, unconverted
    return bool(y) and sum(y) / len(y) > 235


def ff_path(p: Path) -> str:
    """A path inside a filtergraph option: forward slashes, drive colon escaped, quoted."""
    return "'" + p.as_posix().replace(":", r"\:") + "'"


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--real", type=Path, required=True)
    ap.add_argument("--sim", type=Path, required=True)
    ap.add_argument("-o", "--out", type=Path, default=HERE.parent / "media" / "demo_side_by_side.mp4")
    ap.add_argument("--real-start", type=float, default=0.0, help="s into the real clip where the output starts")
    ap.add_argument("--sim-start", type=float, default=0.0, help="s into the sim clip where the output starts")
    ap.add_argument("--duration", type=float, help="output length, s (default: the shorter clip)")
    ap.add_argument("--height", type=int, default=720)
    ap.add_argument("--fps", type=float, default=30.0)
    ap.add_argument("--real-label", default="Real BugSorter")
    ap.add_argument("--sim-label", default="MuJoCo sim, uncalibrated")
    ap.add_argument("--max-mb", type=float, default=19.0)
    args = ap.parse_args()

    span = min(duration(args.real) - args.real_start, duration(args.sim) - args.sim_start)
    if args.duration:
        span = min(span, args.duration)
    if span <= 0:
        raise SystemExit("side_by_side: nothing to render (check the start times)")
    h = args.height // 2 * 2
    sim_fix = "setparams=range=pc," if mislabeled_full_range(args.sim, args.sim_start) else ""
    kbps = int(min(8000, args.max_mb * 8e3 * 0.95 / span))      # cap so the file stays under --max-mb

    with tempfile.TemporaryDirectory() as tmp:
        # labels go through textfile= so commas and colons in them need no filtergraph escaping
        (Path(tmp) / "real.txt").write_text(args.real_label, encoding="utf-8")
        (Path(tmp) / "sim.txt").write_text(args.sim_label, encoding="utf-8")
        font = f"fontfile={ff_path(FONT)}:" if FONT.exists() else ""
        label = (f"drawtext={font}textfile={{}}.txt:fontsize={round(h / 24)}:fontcolor=white:box=1:boxcolor=black@0.6:"
                 f"boxborderw={round(h / 70)}:x={round(h / 40)}:y={round(h / 40)}")
        graph = (f"[0:v]fps={args.fps:g},scale=-2:{h}:flags=lanczos,setsar=1,{label.format('real')}[r];"
                 f"[1:v]{sim_fix}fps={args.fps:g},scale=-2:{h}:flags=lanczos:out_range=tv,setsar=1,{label.format('sim')}[s];"
                 f"[r][s]hstack=inputs=2,format=yuv420p[v]")
        args.out.parent.mkdir(parents=True, exist_ok=True)
        cmd = ["ffmpeg", "-v", "error", "-y",
               "-ss", f"{args.real_start}", "-t", f"{span}", "-i", str(args.real.resolve()),
               "-ss", f"{args.sim_start}", "-t", f"{span}", "-i", str(args.sim.resolve()),
               "-filter_complex", graph, "-map", "[v]", "-an", "-c:v", "libx264", "-preset", "slow", "-crf", "21",
               "-maxrate", f"{kbps}k", "-bufsize", f"{2 * kbps}k", "-movflags", "+faststart", str(args.out.resolve())]
        subprocess.run(cmd, check=True, cwd=tmp)
    p = probe(args.out)
    print(f"side_by_side: wrote {args.out} ({p['width']}x{p['height']}, {p['duration']:.2f} s, "
          f"{args.out.stat().st_size / 1e6:.1f} MB){' [sim range fixed: full-range WebM]' if sim_fix else ''}")


if __name__ == "__main__":
    main()
