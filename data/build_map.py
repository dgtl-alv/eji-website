"""Build static SVG maps (Indonesia + Jabodetabek inset) from world-atlas topojson + station points."""
import json, sys

topo_path, pts_path, out_path = sys.argv[1:4]
topo = json.load(open(topo_path))
pts = json.load(open(pts_path))
sx, sy = topo["transform"]["scale"]; tx, ty = topo["transform"]["translate"]

arcs = []
for arc in topo["arcs"]:
    x = y = 0; line = []
    for dx, dy in arc:
        x += dx; y += dy
        line.append((x * sx + tx, y * sy + ty))
    arcs.append(line)

def arc_coords(i):
    return arcs[i] if i >= 0 else arcs[~i][::-1]

def rings(geom):
    t = geom["type"]
    polys = [geom["arcs"]] if t == "Polygon" else geom["arcs"] if t == "MultiPolygon" else []
    for poly in polys:
        for ring in poly:
            pts_ = []
            for a in ring:
                c = arc_coords(a)
                pts_.extend(c if not pts_ else c[1:])
            yield pts_

geoms = topo["objects"]["countries"]["geometries"]

def render(bbox, width, dots_r, label_list, title):
    w0, s0, e0, n0 = bbox
    k = width / (e0 - w0); height = round((n0 - s0) * k)
    P = lambda lo, la: ((lo - w0) * k, (n0 - la) * k)
    paths_id, paths_other = [], []
    for g in geoms:
        is_id = str(g.get("id")) == "360"
        for r in rings(g):
            if not any(w0 - 2 <= lo <= e0 + 2 and s0 - 2 <= la <= n0 + 2 for lo, la in r):
                continue
            d, last = [], None
            for lo, la in r:
                x, y = P(lo, la)
                if last and abs(x - last[0]) < 0.6 and abs(y - last[1]) < 0.6:
                    continue
                d.append(f"{x:.1f},{y:.1f}"); last = (x, y)
            if len(d) < 3: continue
            (paths_id if is_id else paths_other).append("M" + "L".join(d) + "Z")
    dots = []
    for la, lo in pts:
        if w0 <= lo <= e0 and s0 <= la <= n0:
            x, y = P(lo, la)
            dots.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{dots_r}"/>')
    labels = []
    for name, lo, la, anchor, dx, dy in label_list:
        x, y = P(lo, la)
        labels.append(f'<text x="{x + dx:.0f}" y="{y + dy:.0f}" text-anchor="{anchor}">{name}</text>')
    return f'''<svg class="map-svg" viewBox="0 0 {width} {height}" role="img" aria-label="{title}" xmlns="http://www.w3.org/2000/svg">
<path class="land-other" d="{''.join(paths_other)}"/>
<path class="land" d="{''.join(paths_id)}"/>
<g class="dots">{''.join(dots)}</g>
<g class="labels">{''.join(labels)}</g>
</svg>'''

MAIN_LABELS = [
    ("Medan", 98.67, 3.59, "end", -10, -8),
    ("Palembang", 104.75, -2.99, "start", 10, 4),
    ("Jabodetabek", 106.82, -6.2, "end", -12, -10),
    ("Bandung", 107.6, -6.92, "start", 4, 22),
    ("Semarang", 110.42, -6.99, "middle", 0, -12),
    ("Yogyakarta & Solo", 110.37, -7.8, "middle", 0, 24),
    ("Surabaya", 112.75, -7.25, "start", 10, -6),
    ("Bali", 115.2, -8.65, "start", 10, 18),
    ("Makassar", 119.42, -5.14, "end", -10, 4),
]
INSET_LABELS = [
    ("Jakarta", 106.83, -6.17, "middle", 0, 0),
    ("Tangerang", 106.62, -6.2, "middle", 0, -28),
    ("Bekasi", 107.0, -6.24, "middle", 0, 34),
    ("Depok", 106.82, -6.4, "middle", 0, 30),
    ("Bogor", 106.8, -6.6, "middle", 0, 26),
]

main = render((97.0, -9.6, 121.5, 5.0), 1000, 4.6, MAIN_LABELS, "Map of ALVA charging locations in Indonesia")
inset = render((106.45, -6.72, 107.2, -6.02), 420, 3.4, INSET_LABELS, "Map of ALVA charging locations in Jabodetabek")
json.dump({"main": main, "inset": inset}, open(out_path, "w"))
print(len(main), len(inset))
