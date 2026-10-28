"""The interactive 3D page for the whole machine: product.py's web model, animated the way the drive moves it.

Reads out/product.glb and out/product_kinematics.json (run product.py first) and writes out/product_view.html, one
self-contained page: the GLB is embedded as base64, three.js loads from jsDelivr. Drag to turn the model; the stroke
and speed sliders are BugSorter's web-app settings, and the page shows the tilt, the period and the closest gap
between neighbouring boxes for them (the closed form in WORKING_DIMENSIONS.md). Standard library only, so it runs
from the Windows .venv too.

Run from this folder:  python product_view.py
"""
import base64
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"

# glTF (x, y, z) = CAD (x, z, -y) / 1000, as product.py writes the GLB
ZUP_TO_GLB = [[1, 0, 0], [0, 0, 1], [0, -1, 0]]

LEGEND = [
    {"node": "level0", "material": "breaker", "title": "Breaker B-164f355a",
     "text": "11.3 mm grid with 40 blunt pins. Holds leaves back; freed specimens fall through."},
    {"node": "level1", "material": "screen", "title": "5 mm sieve",
     "text": "Keeps the largest class. Low ribs run across the tilt."},
    {"node": "level2", "material": "screen", "title": "2 mm sieve", "text": "Keeps the middle class."},
    {"node": "level3", "material": "holder", "title": "Catch pan",
     "text": "Collects the smallest class. An inward lip keeps bounced grains in."},
    {"node": "drive", "material": "drive", "title": "Push rods, yoke and buzz puck",
     "text": "Hang from BugSorter's stage. Rod A tips levels 1 and 3, rod B levels 2 and 4."},
    {"node": "frame", "material": "frame", "title": "Base and pivot posts",
     "text": "Hold each level's pivot pins, 55 mm apart."},
]


def main():
    kin = json.loads((OUT / "product_kinematics.json").read_text(encoding="utf-8"))
    kin["glb_scale_per_mm"] = 0.001
    kin["zup_to_glb"] = ZUP_TO_GLB
    glb = base64.b64encode((OUT / "product.glb").read_bytes()).decode("ascii")
    page = (HERE / "product_view_template.html").read_text(encoding="utf-8")
    for key, val in (("__KIN_JSON__", json.dumps(kin)), ("__LEGEND_JSON__", json.dumps(LEGEND)), ("__GLB_B64__", glb)):
        assert page.count(key) == 1, key
        page = page.replace(key, val)
    out = OUT / "product_view.html"
    out.write_text(page, encoding="utf-8")
    print(f"{out}: {out.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
