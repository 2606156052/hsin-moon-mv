"""Image-to-video pass: python3 i2v.py --ids S06,S15 [--take 5] [--workers 8]. First frame = keys/<id>.png"""
import sys, os, json, subprocess, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shots import *
from choreo_v2 import CHOREO
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
A = os.environ.get('ATLAS_CLI', 'atlas'); LEDGER = os.environ.get('ATLAS_LEDGER', os.path.join(HERE, 'spend_ledger.tsv')); BUDGET = float(os.environ.get('ATLAS_BUDGET', '25'))
def spent(): return sum(float(l.split('\t')[2]) for l in open(LEDGER) if l.strip())
arg = lambda k, d=None: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
ids = arg('--ids').split(','); take = int(arg('--take', '5')); N = int(arg('--workers', '8'))
DESC = ("The fox goddess in the image (ice-blue hair in braided buns with long side strands, tall blue fox ears with black tips, crimson eyes, "
        "off-shoulder black and crimson dress with translucent ice-blue layered skirt panels, red fur-trimmed half sleeves, silver star ornaments, "
        "bare feet in silver sandals, one huge ice-blue fox tail fading to a black tip with silver star charms) keeps exactly this design. ")
MUSIC = {1: "The music is a bright, flowing 116 BPM orchestral pop song with plucked guzheng and strings; she moves on the beat, light and playful like a fox spirit riding the wind. ",
         2: "The music turns heavy and dark at 116 BPM; she moves on the beat, weighed down, hesitant and anguished. ",
         3: "The music swells with passionate strings at 116 BPM; she moves on the beat, fierce, decisive and tragic. ",
         4: "The music soars to its climax at 116 BPM; she moves on the beat, expansive, luminous and liberated. ",
         5: "The music is warm and nostalgic at 116 BPM; she moves on the beat, gentle, joyful and at peace. "}
TAIL = (" Hair, sheer skirt panels, sleeves and tail move with soft realistic cloth and fur physics and follow-through. Premium Chinese 2D anime game cutscene, "
        "fully 2D hand-drawn anime, cel shading with painterly light, clean line art, consistent character design, smooth fluid motion, no morphing, no extra limbs, no text.")
jobs = []
for s in SHOTS:
    if s['id'] not in ids: continue
    out = f"clips/{s['id']}_t{take}.mp4"
    if os.path.exists(out): continue
    dur = s['dur']
    prompt = DESC + MUSIC[s['act']] + f"Action, in order over {dur} seconds: " + CHOREO.get(s['id'], s['action']) + " Camera: " + s['camera'] + TAIL
    cmd = [A, 'generate', 'video', 'alibaba/wan-3.0/image-to-video', '--image', f"@keys/{s['id']}.png", '-p', prompt, '--resolution', '480p',
           '--duration', str(dur), '--param', 'audio=false', '--seed', str(500 + take * 100 + int(s['id'][1:])), '-o', out, '--overwrite', '--json', '--timeout', '40m']
    jobs.append((s['id'], round(0.04 * dur, 3), out, cmd))
print(len(jobs), 'jobs', f'est ${sum(j[1] for j in jobs):.2f}', f'spent ${spent():.2f}', flush=True)
running = []; q = list(jobs)
while q or running:
    while q and len(running) < N:
        sid, cost, out, cmd = q.pop(0)
        if spent() + cost + sum(r[1] for r in running) > BUDGET: print('BUDGET STOP'); q.clear(); break
        running.append((sid, cost, out, subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True))); print('submitted', sid, flush=True)
    for r in list(running):
        sid, cost, out, p = r
        if p.poll() is None: continue
        running.remove(r); txt = p.stdout.read()
        if os.path.exists(out) and os.path.getsize(out) > 1000:
            open(LEDGER, 'a').write(f"{time.strftime('%F %T')}\tclip {sid} i2v take{take}\t{cost}\talibaba/wan-3.0/image-to-video\t{out}\t\n"); print(f'OK {sid} total ${spent():.2f}', flush=True)
        else: print('FAILED', sid, txt[-300:], flush=True)
    time.sleep(3)
print('DONE', f'spent ${spent():.2f}')
