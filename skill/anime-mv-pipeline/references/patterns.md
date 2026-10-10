# Prompt templates & compositor catalogue

## Wan 3.0 reference-to-video (480p)
```
Image 1 is the character sheet: animate exactly this <character> (<hair>, <ears>, <eyes>, <outfit>, <tail/props>).
Image 2 is the location and the art style: this <plate description>, premium Chinese 2D anime game cutscene art.
The music is <genre> at <BPM> BPM; she moves on the beat, <mood>.
Action, in order over <N> seconds: (0-1.5s) <big move>; (1.5-3s) <big move>; (3-5s) <payoff pose>.
Camera: <framing + move>.
Hair, sheer skirt panels, sleeves and tail move with soft realistic cloth and fur physics. Fully 2D hand-drawn anime, cel shading with painterly light, clean line art, consistent character design, no 3D render look, no morphing, no extra limbs.
```
Request JSON: `{"prompt", "refers":[{"type":"image","url":"@board.jpg"},{"type":"image","url":"@plates/x.jpg"}(,{"type":"audio","url":"@seg.mp3"})], "resolution":"480p", "duration":5, "audio":false, "ratio":"16:9", "seed":N}`

## Seedream plate
`Empty background plate, no people: <location>. <style>, cinematic composition, no text.` Use size `2048*1152`.

## Compositor (studio/fx.js)
- transitions: `ink` (sumi-e brush wipe), `moon` (iris), `flash`, `dissolve`, `black`, `shatter`, `cut`
- overlays: `letterbox`, `topTitle`, `lyricEN`, `display` (serif caps hook lyric), `seal` (moon seal stamp), `embers`, `wind`, `motes`, `speedLines`, `leak` (beat light leak), `flash`, `wash`, `cloudsOver`
- panels: `title`, `actcard`, `strings` (onset-driven guzheng strings), `sorrowjoy`, `phases`, `shards`, `moonrain`, `endcard`, `clouds`, `mandala`
- segment keys: `kind`, `t0`/`t1`, `dir`, `fps`, `n`, `in`, `rate` (auto slow-mo), `mode`, `cam`, `over`, `trans`
