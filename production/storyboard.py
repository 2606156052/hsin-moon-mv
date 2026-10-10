import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shots import *
PANELS = {
 'title': "Title card. Moon-phase mandala blooms from a single gold line; 'ODE TO HSIN AND MOON' and 'Endless Yearning' letter-reveal; first lyric types in.",
 'actcard': "Act card. Ink brush stroke sweeps across paper texture, act number and title reveal in Cinzel, gold rule draws under it, cut on the downbeat.",
 'strings': "Guzheng strings. 21 gold strings across the frame vibrate and glow, plucked in time with the actual onsets of the music; lyric rides the strings.",
 'sorrowjoy': "Sorrow / Joy. Split screen of a waning (cool) and waxing (warm) moon that swap sides on the beat; the two lyric halves slide in from each side.",
 'phases': "Wax and wane. Eight moon phases orbit a central crescent, rotating one phase per beat; tide lines ripple outward.",
 'shards': "Broken mirror. The frame cracks into shards that drift apart, showing fragments of the moon; 'Whose face is this?' assembles from the shards.",
 'moonrain': "Breath. Slow falling moonlight motes on deep indigo, the story line lingers; Act V card fades up at the end.",
 'endcard': "End card. Moon mandala closes to a single point of light; title and credits.",
}
L = ["# Ode to Hsin and Moon: Storyboard & Shot Breakdown", "",
     "**Song:** *Ode to Hsin and Moon (Endless Yearning)*, 3:36, 115.96 BPM. Every cut sits on a beat; act changes sit on bar downbeats.", "",
     "**Pipeline:** Seedream 5.0 Pro designs each location as an empty plate. Wan 3.0 reference-to-video generates each shot at 480p from the user's character sheet (image 1) and the plate (image 2), with choreography and camera written as text. For close-ups where she sings, the song segment is passed as an audio reference for lip sync. The HTML/JS compositor then redraws the footage at 1080p (Option 1) and adds all typography, graphic panels and beat-locked transitions. All on-screen text is English.", "",
     "Lyric ids refer to the timed lines in `production/lyrics.json` (supplied locally from the song's LRC, not committed).", "", "**Look:** 2D anime cutscene, blue-violet nights with warm lantern light, letterbox bars, gold line ornament, ink-brush transitions, embers and moonlight motes.", ""]
act = 0
for s in SHOTS:
    if s['act'] != act:
        act = s['act']; a = ACTS[act]
        L += ["", f"## {a[0]}: {a[1]} ({a[2]})", "", "| Shot | Time | Beats | Type | Location | Action | Camera | Lyric (line id) |", "|---|---|---|---|---|---|---|---|"]
    t0, t1 = T(s['b'][0]), T(s['b'][1])
    lyr = " ".join(f"L{i+1:02d}" for i, (t, l) in enumerate(LYRICS) if t0 - 0.2 <= t < t1 - 0.2) or "—"
    tm = f"{int(t0//60)}:{t0%60:05.2f}–{int(t1//60)}:{t1%60:05.2f}"
    if s['kind'] == 'panel':
        L.append(f"| {s['id']} | {tm} | {s['b'][0]}–{s['b'][1]} | JS graphic | — | {PANELS[s['panel']]} | — | {lyr} |")
    else:
        typ = 'Wan 3.0' + (' (lip sync)' if s.get('lip') else '') if s['kind'] == 'wan' else 'Wan 3.0 (approved sample)'
        L.append(f"| {s['id']} | {tm} | {s['b'][0]}–{s['b'][1]} | {typ} | {s['scene']} | {s.get('action','Drop-in landing, run and spinning leap (approved sample take).')} | {s.get('camera','Low side tracking, half orbit, push-in.')} | {lyr} |")
L += ["", "## Transitions", "",
      "- Hard cuts on beats inside a phrase. Whip-flash (white 2-frame flash + motion blur) on accent beats.",
      "- Ink-brush wipe into and out of every JS graphic panel, centred on the downbeat.",
      "- Act changes: moon iris (Act I→II), chains-of-light slam to black (II), fire flash (III), chains shatter to white (IV), slow dissolve (V).", "",
      "## Budget", "", "- Plates: 12 × ~$0.036. Shots: 38 × $0.20–0.44 (480p, $0.04/s). First pass ≈ $8.5; retakes for wrong motion or character drift from the remaining budget; hard cap $25 enforced by the driver.", ""]
open('STORYBOARD.md', 'w').write("\n".join(L))
print(len(L))
