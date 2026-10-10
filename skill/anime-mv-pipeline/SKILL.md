---
name: anime-mv-pipeline
description: Produce a beat-locked 2D-anime music video from a song and a character sheet. Seedream designs scene plates, Wan 3.0 (Atlas Cloud) generates 480p shots from text choreography, and an HTML/JS compositor adds lyric typography, graphic panels and beat-synced transitions, then renders 1080p (code repaint, crisp repaint, or original footage). Use when the user wants an anime/game-cutscene style MV, a lyric video with generated character footage, or to extend this project.
---

# Anime MV pipeline

Song + character sheet + budget in, finished 1080p MV out. Everything is driven by one shot list on the song's beat grid.

## 0. Requirements
- `atlas` CLI logged in (Atlas Cloud). Models: `alibaba/wan-3.0/reference-to-video` ($0.04/s at 480p), `bytedance/seedream-v5.0-pro/text-to-image` (~$0.036 per 2048×1152 plate).
- ffmpeg, Python 3 with numpy (Blender's bundled Python works), Node 18+, Google Chrome (set `CHROME` if not at the macOS default path).
- Env: `HSIN_SONG` (song path), `FFMPEG`, `ATLAS_CLI`, `ATLAS_BUDGET` (hard cap, default 25), `ATLAS_LEDGER`.

## 1. Beat grid
`python3 scripts/tools/analyze_beats.py song.pcm analysis.json` (decode first: `ffmpeg -i song.mp3 -ac 1 -ar 22050 -f s16le song.pcm`).
Fit BPM and the beat-0 phase. Check that lyric line starts land on 4- or 8-beat phrases. Put `BPM`/`PH` into `shots.py`. Every shot boundary is a beat number, never seconds.

## 2. Story → storyboard
Edit `scripts/production/shots.py`:
- `SCENES`: one *empty background plate* prompt per location (no people).
- `SHOTS`: id, beats `(b0,b1)`, `kind` (`wan` / `panel` / `reuse`), scene, Wan duration (2–12 s), act, camera; set `lip=True` for singing close-ups.
- `choreo_v2.py`: **time-coded** choreography per shot (see Prompt rules).
- `lyrics.json` (copy `lyrics.example.json`): timed lines, display hooks and panel text. Keep real lyrics out of git.
`python3 storyboard.py` writes the shot-breakdown Markdown.

## 3. Generate
```bash
python3 produce.py plates                   # Seedream plates
python3 produce.py clips --take 1 --dry     # cost preview
python3 produce.py clips --take 1 --workers 8
./review.sh S02_t1 S03_t1 ...               # 5x2 contact sheets -> sheets/batch.jpg
python3 produce.py clips --take 2 --ids S05,S11   # retakes
```
- The driver logs every job to the ledger and refuses any job that would cross the budget.
- Review every clip. Retake if she is missing, cropped, static, off-model, or shows forbidden props.
- Record chosen takes in `picks.json`. A clip can also have `in` (in-point) and `cam` (code camera move).
- If a run is interrupted, resume accepted jobs with `atlas generate wait <id> -o file` (`atlas generate ops list`). Never resubmit, because a new submission is a new charge.

## 4. Compose and render
```bash
python3 build_project.py                    # -> studio/projects/full.json, extracts frames
cd ../studio && npm i && node server.mjs &
node render.mjs --project=full --stills=36,90,150     # spot-check
node render.mjs --project=full --range=0:216.6 --fps=30 --workers=4
ffmpeg -framerate 30 -i out/full/%05d.jpg -i song.mp3 -map 0:v -map 1:a -c:v libx264 -crf 17 -pix_fmt yuv420p -c:a aac -shortest mv.mp4
```
Picture modes, set per project:
- `mode: "redraw"` (`gl.js`): light code repaint.
- `pipeline: "vector"` (`gl2.js`): bilateral flatten + shock-filter edges + FXAA + XDoG lines, the crispest code repaint.
- `mode: "raw"`: original footage, Lanczos-prescaled to 1080p, no grade.

## Prompt rules (learned the hard way)
1. Reference mode: image 1 = character sheet, image 2 = plate. **Describe the plate in words** ("Image 2 is the location and the art style: this …").
2. Write motion as `Action, in order over N seconds: (0-1.5s) … (1.5-3s) …` with **big locomotion** (run, leap, spin, travel). Gentle actions such as swaying, pointing or holding still make Wan hold the reference pose and return a nearly static clip.
3. Quiet emotional beats: accept a calmer take and add a code camera move (`cam: {z0,z1,x0,x1,y0,y1,r0,r1}`).
4. Lip sync: pass the song segment as an `audio` refer and say "Audio 1 is the song for this moment: she sings this vocal line with accurate lip sync."
5. Seedream and Seedance may reject a character sheet under copyright filters. Do not work around the filter. Use Wan with the sheet, and Seedream only for empty plates.
6. Symbolic story props stay symbolic. Example: "a crown that is not hers" means borrowed power and duty, so show a seal, chains of light or a mantle, and add "no crown, no tiara, no headwear".
7. Never let the model render text. All typography comes from the compositor (`fx.js`).

See `references/patterns.md` for full prompt templates and the compositor effect catalogue.
