"""Production driver: python3 produce.py plates | clips [--ids S02,S03] [--take N] [--workers 5]"""
import sys, os, json, subprocess, time, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shots import *
from choreo_v2 import CHOREO
HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
A = os.environ.get('ATLAS_CLI', 'atlas')
FF = os.environ.get('FFMPEG', 'ffmpeg')
SONG = os.environ.get('HSIN_SONG', os.path.join(HERE, '..', 'song.mp3'))
LEDGER = os.environ.get('ATLAS_LEDGER', os.path.join(HERE, 'spend_ledger.tsv'))
BUDGET = float(os.environ.get('ATLAS_BUDGET', '25'))
def spent():
    try: return sum(float(l.split('\t')[2]) for l in open(LEDGER) if l.strip())
    except FileNotFoundError: return 0.0
def log(label, cost, model, out, pid=''):
    with open(LEDGER, 'a') as f: f.write(f"{time.strftime('%F %T')}\t{label}\t{cost}\t{model}\t{out}\t{pid}\n")
def arg(k, d=None):
    return sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d

jobs = []   # (label, cost, model, out, cmd)
mode = sys.argv[1]
if mode == 'plates':
    for name, p in SCENES.items():
        if p.startswith('existing'): continue
        out = f'plates/{name}.png'
        if os.path.exists(out): continue
        jobs.append((f'plate {name}', 0.036, 'bytedance/seedream-v5.0-pro/text-to-image', out,
                     [A, 'generate', 'image', 'bytedance/seedream-v5.0-pro/text-to-image', '-p', p + ' ' + STYLE + ', cinematic composition, no text.',
                      '--param', 'size=2048*1152', '--param', 'output_format=png', '-o', out, '--overwrite', '--json', '--timeout', '20m']))
elif mode == 'clips':
    ids = arg('--ids', '').split(',') if arg('--ids') else None
    take = int(arg('--take', '1'))
    extra = arg('--extra', '')
    for s in SHOTS:
        if s['kind'] != 'wan' or (ids and s['id'] not in ids): continue
        out = f"clips/{s['id']}_t{take}.mp4"
        if os.path.exists(out): continue
        b0, b1 = s['b']; dur = s['dur']
        refers = [{"type": "image", "url": "@board.jpg"}, {"type": "image", "url": f"@plates/{s['scene']}.jpg"}]
        lip = ''
        if s.get('lip'):
            au = f"audio/{s['id']}.mp3"
            subprocess.run([FF, '-y', '-loglevel', 'error', '-ss', str(T(b0)), '-t', str(dur), '-i', SONG, '-ac', '2', '-b:a', '192k', au], check=True)
            refers.append({"type": "audio", "url": f"@{au}"})
            lip = "Audio 1 is the song for this moment: she sings this vocal line with accurate lip sync, mouth shapes matching the words and rhythm. "
        SHORT = {'rooftop': 'this curved temple rooftop high above a lantern-lit night city under a giant moon',
                 'street': 'this lantern-lined festival street at night', 'plaza': 'this windy moonlit lantern plaza with streaming embers and red ribbons',
                 'moonplaza': 'this circular moon-marked stone plaza under a giant full moon and floating lanterns', 'skysea': 'this sky above a sea of moonlit clouds full of drifting sky lanterns',
                 'lake': 'this still mirror lake at night with floating lanterns and a pavilion', 'throne': 'this vast dark violet palace hall with a golden throne',
                 'mirrorhall': 'this dim chamber with a giant glowing bronze mirror', 'cliff': 'this lonely city wall on a cliff overlooking a distant glowing festival town',
                 'firevoid': 'this dark dream void full of swirling fire and embers', 'nexus': 'this surreal dream realm of floating palace fragments and rivers of moonlight',
                 'river': 'this festival riverbank with floating river lanterns and an arched bridge'}
        music = {1: "The music is a bright, flowing 116 BPM orchestral pop song with plucked guzheng and strings; she moves on the beat, light and playful like a fox spirit riding the wind. ",
                 2: "The music turns heavy and dark at 116 BPM; she moves on the beat, weighed down, hesitant and anguished. ",
                 3: "The music swells with passionate strings at 116 BPM; she moves on the beat, fierce, decisive and tragic. ",
                 4: "The music soars to its climax at 116 BPM; she moves on the beat, expansive, luminous and liberated. ",
                 5: "The music is warm and nostalgic at 116 BPM; she moves on the beat, gentle, joyful and at peace. "}[s['act']]
        head = CHAR.replace("Image 2 is the location and the art style. ", "") + f"Image 2 is the location and the art style: {SHORT[s['scene']]}, premium Chinese 2D anime game cutscene art. "
        tail = (" Hair, sheer skirt panels, sleeves and tail move with soft realistic cloth and fur physics. Fully 2D hand-drawn anime, cel shading with painterly light, "
                "clean line art, consistent character design, no 3D render look, no morphing, no extra limbs.")
        act = CHOREO.get(s['id'], s['action'])
        prompt = head + lip + music + f"Action, in order over {dur} seconds: " + act + " Camera: " + s['camera'] + tail
        req = {"prompt": prompt, "refers": refers, "resolution": "480p", "duration": dur, "audio": False, "ratio": "16:9", "seed": 1000 * take + int(s['id'][1:])}
        jf = f"clips/{s['id']}_t{take}.json"; json.dump(req, open(jf, 'w'), indent=1)
        jobs.append((f"clip {s['id']} take{take}", round(0.04 * dur, 3), 'alibaba/wan-3.0/reference-to-video', out,
                     [A, 'generate', 'video', 'alibaba/wan-3.0/reference-to-video', '--input', jf, '-o', out, '--overwrite', '--json', '--timeout', '40m']))
print(f'{len(jobs)} jobs, est ${sum(j[1] for j in jobs):.2f}, spent so far ${spent():.2f}')
if '--dry' in sys.argv: sys.exit()
N = int(arg('--workers', '5')); running = []; queue = list(jobs); failed = []
while queue or running:
    while queue and len(running) < N:
        label, cost, model, out, cmd = queue.pop(0)
        if spent() + cost + sum(r[1] for r in running) > BUDGET:
            print('BUDGET STOP before', label); queue.clear(); break
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=HERE)
        running.append((label, cost, model, out, p)); print('submitted', label, flush=True)
    for r in list(running):
        label, cost, model, out, p = r
        if p.poll() is None: continue
        running.remove(r); txt = p.stdout.read()
        pid = ''
        try:
            d = json.loads(txt[txt.index('{'):]); pid = (d.get('data', {}).get('prediction') or {}).get('id', '')
            err = (d.get('data', {}).get('prediction') or {}).get('error') or (d.get('errors') or [{}])[0].get('message', '')
        except Exception: err = txt[-300:]
        if os.path.exists(out) and os.path.getsize(out) > 1000:
            log(label, cost, model, out, pid); print(f'OK {label} ${cost}  total ${spent():.2f}', flush=True)
            if out.endswith('.png'):
                subprocess.run([FF, '-y', '-loglevel', 'error', '-i', out, '-vf', 'scale=1600:-1', '-q:v', '3', out[:-4] + '.jpg'])
        else:
            failed.append((label, err)); print(f'FAILED {label}: {err}', flush=True)
    time.sleep(3)
print('DONE. failed:', failed, f'spent ${spent():.2f}')
