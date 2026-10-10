"""Build studio/projects/full.json from shots.py + generated clips. Extracts frames for chosen takes.
usage: python3 build_project.py [--picks picks.json]"""
import sys, os, json, subprocess, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shots import *
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
FF = os.environ.get('FFMPEG', 'ffmpeg')
STUDIO = os.path.join(HERE, '..', 'studio')
W, H = 1920, 1080
picks = json.load(open('picks.json')) if os.path.exists('picks.json') else {}   # id -> {"take":n, "in":sec}
TRANS = {  # transition INTO shot id
 'S02': dict(type='dissolve', dur=1.0, lead=0.5), 'S05': dict(type='ink', dur=0.55, lead=0.22, seed=3), 'S06': dict(type='ink', dur=0.55, lead=0.22, seed=5, dir=-1),
 'S09': dict(type='flash', dur=0.3, lead=0.15), 'S12': dict(type='ink', dur=0.55, lead=0.22, seed=8), 'S13': dict(type='ink', dur=0.55, lead=0.22, seed=9, dir=-1),
 'S16': dict(type='flash', dur=0.3, lead=0.15), 'S18': dict(type='ink', dur=0.55, lead=0.22, seed=12), 'S19': dict(type='ink', dur=0.55, lead=0.22, seed=13, dir=-1),
 'S21': dict(type='ink', dur=0.55, lead=0.22, seed=14), 'S22': dict(type='ink', dur=0.55, lead=0.22, seed=15, dir=-1),
 'S23': dict(type='black', dur=0.5, lead=0.25), 'S24': dict(type='black', dur=0.4, lead=0.2), 'S28': dict(type='shatter', dur=0.8, lead=0.1),
 'S29': dict(type='dissolve', dur=0.8, lead=0.4), 'S32': dict(type='flash', dur=0.35, lead=0.17), 'S36': dict(type='shatter', dur=0.7, lead=0.05),
 'S42': dict(type='dissolve', dur=1.0, lead=0.5), 'S43': dict(type='dissolve', dur=1.0, lead=0.5), 'S48': dict(type='dissolve', dur=1.5, lead=0.75),
 'S11': dict(type='flash', dur=0.25, lead=0.12), 'S36x': None,
}
CAM = {  # virtual camera moves for quieter takes (zoom z, offset x/y in frame units, roll r degrees)
 'S02': dict(z0=1.0, z1=1.28, y0=0.0, y1=0.04), 'S03': dict(z0=1.05, z1=1.22, x0=0.02, x1=-0.02), 'S14': dict(z0=1.0, z1=1.3, x0=0.0, x1=0.06),
 'S15': dict(z0=1.3, z1=1.0, x0=0.06, x1=0.0, y0=0.03, y1=0.0), 'S19': dict(z0=1.12, z1=1.12, x0=0.03, x1=-0.03), 'S20': dict(z0=1.25, z1=1.6, r0=0, r1=30),
 'S29': dict(z0=1.0, z1=1.25, x0=0.0, x1=0.05), 'S30': dict(z0=1.25, z1=1.0, x0=0.05, x1=0.0), 'S31': dict(z0=1.0, z1=1.3), 'S32': dict(z0=1.1, z1=1.3, r0=0, r1=-4),
 'S34': dict(z0=1.3, z1=1.05, y0=0.06, y1=0.0), 'S16': dict(z0=1.0, z1=1.12),
 'S24': dict(z0=1.0, z1=1.12), 'S47': dict(z0=1.35, z1=1.0, y0=0.04, y1=0.0), 'S39': dict(z0=1.0, z1=1.15), 'S46': dict(z0=1.0, z1=1.15, y0=0.0, y1=0.05),
 'S06': dict(z0=1.0, z1=1.35, y0=0.0, y1=0.06), 'S40': dict(z0=1.0, z1=1.2), 'S27': dict(z0=1.0, z1=1.12),
}
ACT_OVER = {
 1: [{"fx": "embers", "seed": 11, "n": 40, "wind": [1, -0.3], "alpha": 0.6}, {"fx": "wash", "color": "#3a2a80", "a": 0.18}],
 2: [{"fx": "wash", "color": "#2a1050", "a": 0.35, "op": "multiply"}, {"fx": "motes", "n": 30, "alpha": 0.4, "seed": 3}],
 3: [{"fx": "embers", "seed": 33, "n": 90, "wind": [0.2, -0.8], "alpha": 0.85}, {"fx": "wash", "color": "#ff7030", "a": 0.18}],
 4: [{"fx": "motes", "n": 80, "alpha": 0.8, "seed": 9}, {"fx": "wash", "color": "#5070ff", "a": 0.15}],
 5: [{"fx": "embers", "seed": 55, "n": 35, "wind": [0.4, -0.4], "alpha": 0.6}, {"fx": "wash", "color": "#ffa040", "a": 0.16}],
}
segs = []
for s in SHOTS:
    t0 = T(s['b'][0])
    seg = {"id": s["id"], "t0": t0, "t1": T(s["b"][1]), "act": s["act"]}
    if s['kind'] == 'panel':
        seg.update(kind='panel', panel=s['panel'])
        if s['panel'] in PANEL_TEXT: seg['text'] = PANEL_TEXT[s['panel']]
    else:
        pk = picks.get(s['id'], {})
        if s['kind'] == 'reuse':
            src = os.path.join(HERE, '..', s['src'])
        else:
            src = f"clips/{s['id']}_t{pk.get('take', 1)}.mp4"
        if not os.path.exists(src):
            print('MISSING', src); seg.update(kind='panel', panel='moonrain'); segs.append(seg); continue
        fdir = os.path.join(STUDIO, 'frames', 'mv', s['id'])
        stamp = os.path.join(fdir, '.src')
        if not os.path.exists(stamp) or open(stamp).read() != src:
            os.makedirs(fdir, exist_ok=True)
            for f in glob.glob(fdir + '/*.jpg'): os.remove(f)
            subprocess.run([FF, '-y', '-loglevel', 'error', '-i', src, '-q:v', '2', f'{fdir}/%05d.jpg'], check=True)
            open(stamp, 'w').write(src)
        n = len(glob.glob(fdir + '/*.jpg'))
        cin = pk.get('in', s.get('src_in', 0.0)); avail = n / 30 - cin; need = T(s['b'][1]) - t0
        seg.update(kind='clip', dir=f"frames/mv/{s['id']}", fps=30, n=n, mode='redraw', grade={"ink": 0.4}, rate=round(min(1.0, avail / need), 3), **{"in": cin})
        seg['over'] = list(ACT_OVER[s['act']])
        if s['id'] in CAM: seg['cam'] = CAM[s['id']]
        if s['id'] == 'S09': seg['over'] += [{"fx": "speedLines", "t0": 37.55, "t1": 38.15, "cx": W * 0.55, "cy": H * 0.4}]
        if s['id'] == 'S10': seg['over'] += [{"fx": "cloudsOver", "t0": t0 + 0.1, "alpha": 0.85}]
    if s['id'] in TRANS and TRANS[s['id']]: seg['trans'] = TRANS[s['id']]
    segs.append(seg)
# beat accents: leak flashes on every 8-beat phrase downbeat in footage acts, flashes on big hits
glob_over = [{"fx": "letterbox", "h": 0.072}]
for act, (num, title, sub) in ACTS.items():
    a_shots = [s for s in SHOTS if s['act'] == act]
    glob_over.append({"fx": "topTitle", "text": f"{num}  ·  {title.upper()}", "t0": T(a_shots[0]['b'][0]) + 0.5, "t1": T(a_shots[-1]['b'][1])})
glob_over.append({"fx": "leak", "beats": [b for b in range(0, 420, 8)]})
glob_over.append({"fx": "flash", "beats": [68, 128, 192, 296, 336]})
# English lyric track (bottom) + display lyrics for hooks
for i, (t, line) in enumerate(LYRICS):
    nxt = LYRICS[i + 1][0] if i + 1 < len(LYRICS) else t + 5
    t1 = min(nxt - 0.25, t + 5.5)
    glob_over.append({"fx": "lyricEN", "text": line, "t0": t, "t1": t1, "y": H * 0.958, "size": 48})
for i, (t, line) in enumerate(LYRICS):
    if t in DISPLAY:
        txt, al = DISPLAY[t]; nxt = LYRICS[i + 1][0] if i + 1 < len(LYRICS) else t + 5
        x = W * 0.94 if al == 'right' else W * 0.06
        glob_over.append({"fx": "display", "text": txt, "x": x, "y": H * 0.16, "align": al, "t0": t + 0.05, "t1": min(nxt - 0.3, t + 4.2), "size": 54})
        glob_over.append({"fx": "seal", "x": (x - 40 if al == 'right' else x + 40), "y": H * 0.16 + 150, "t0": t + 0.6, "t1": min(nxt - 0.3, t + 4.2)})
P = {"name": "full", "segments": segs, "global": glob_over}
json.dump(P, open(os.path.join(STUDIO, 'projects', 'full.json'), 'w'), indent=1)
print('segments', len(segs), 'overlays', len(glob_over))
