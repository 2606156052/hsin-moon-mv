# Ode to Hsin and Moon: dance & camera design

Blender 5.2 scene: `hsin_dance.blend` (fps 24, frames 1–5199, music strip in the VSE, one timeline marker per move).
Video: `hsin_dance_720p.mp4` (1280×720, 24 fps, with music).

## How it's built
- **Timing:** the track runs at about **115.96 BPM**, with beat 0 at 0.335 s. Each lyric line starts an 8-beat phrase, so every move is keyed in beats (`hsin_engine.py`).
- **Figure (心):** a 1.6 m base-mesh fox girl with a cel shader and outline. She has fox ears, a 7-bone tail, a hanfu skirt that follows the legs, and wide sleeves.
  - Legs use IK to world-space foot targets, so planted feet never slide.
  - Arms use IK to hand targets in the chest frame.
  - Secondary motion is procedural: tail spring physics driven by her travel and turns, ear flicks, breathing, and an on-beat "groove" bounce.
- **Story props:** the crown descends at 1:37 and shatters at 2:33. The burning 情匣 (box) appears at 2:12, takes over her hands at 2:17, flares at 2:27 and burns away at 2:31.
- **The double (TrueSelf):** in Act 2 it is a violet reflection one beat late, and turns its head toward her when she looks away. In Act 4 it is the luminous 本体, dancing in sync as a mirror image; their palms meet, then it walks into her and merges.
- **Lighting by act:** cool moonlight, then the crown's purple darkness, then firelight, then the rebirth flash, then warm lanterns. The lanterns pull back in Act 2 and rise in Act 5. Embers, a rebirth burst and moonlight rain are particles.
- **Camera:** 50 shots baked per frame, with cuts on phrase downbeats. Shot types include a crane from the moon, low hero angles, overhead spins, a handheld dutch angle for the struggle, a profile two-shot for the mirror duet, a moon-behind-the-head close-up for "[L35]", and a final crane up and away.

## Move timeline (song time · beat · move)
| time | beat | move |
|---|---|---|
| 0:00.34 | 0 | ACT1 月下化形 · Moon up high – fox crouched under the moon |
| 0:04.47 | 8 | Who is peeking down today – peeking left/right, turns to the viewer |
| 0:08.61 | 16 | [L03] – lantern sway motif |
| 0:16.89 | 32 | Instrumental – fox sneak (on toes, paws) |
| 0:21.03 | 40 | Pounce! |
| 0:25.17 | 48 | Tail chase spin |
| 0:27.50 | 52.5 | Peek-a-boo |
| 0:29.31 | 56 | Chaîné turns across the stage |
| 0:35.52 | 68 | [L05] – wind run + grand jeté |
| 0:39.66 | 76 | [L06] – arm circles, step-touch |
| 0:43.80 | 84 | Bathe me in tender moonbeams – open to the moon, piqué turn |
| 0:47.94 | 92 | how carefree – chassés, flicks |
| 0:50.01 | 96 | [L08] – kneel, guzheng plucking |
| 0:54.15 | 104 | [L09] – point L, point R, both up, double pirouette |
| 0:58.29 | 112 | [L10] – walk to the viewer, gather the lights |
| 1:02.43 | 120 | [L11] – hold to heart, release upward |
| 1:06.56 | 128 | [L12] – reach to the moon, arabesque |
| 1:09.67 | 134 | [L13] – run, high grand jeté, self-embrace |
| 1:14.84 | 144 | [L14] – curl down, bloom up, soutenu |
| 1:18.98 | 152 | [L15] – bourrée glide, reaching for a companion |
| 1:23.12 | 160 | [L16] – vertical line, slow promenade |
| 1:37.61 | 188 | ACT2 戴上不属于自己的冠 · Crown descends |
| 1:39.68 | 192 | Struggle against the crown |
| 1:47.96 | 208 | 镜中不是自己的脸 · The mirror: a reflection one beat late |
| 1:58.31 | 228 | Tries the old playful fox steps – the crown drags her down |
| 2:02.45 | 236 | [L19] – facing the town, walking toward it |
| 2:06.59 | 244 | [L21] – eager, then pulled back |
| 2:12.79 | 256 | A glow appears – the 情匣 |
| 2:16.93 | 264 | ACT3 璇情燃尽 · Shimmering fire – receiving the burning box |
| 2:19.00 | 268 | a speaking heart – box to the chest, sharp twist |
| 2:21.07 | 272 | [L23] – whip turns with the box overhead |
| 2:25.21 | 280 | [L24] – box lifted overhead, it flares |
| 2:29.35 | 288 | [L25] – she kneels, the box burns away in her hands |
| 2:33.49 | 296 | ACT4 溯心 · Crown shatters – rebirth |
| 2:34.01 | 297 | [L26] |
| 2:37.63 | 304 | [L27] – duet with her true self (本体) |
| 2:41.77 | 312 | [L28] – mirrored circling |
| 2:45.91 | 320 | [L29] – tour en l'air together |
| 2:50.05 | 328 | [L30] – palms meet, she merges with her true self |
| 2:54.19 | 336 | [L31] – reborn: jump-turn, triple pirouette, jeté |
| 2:58.33 | 344 | Breath – moonlight rain, she walks toward us |
| 3:04.54 | 356 | ACT5 心有所归 · Moon up high (reprise) – lantern sway, warmer |
| 3:08.68 | 364 | [L33] – joyful run around the stage |
| 3:12.82 | 372 | [L34] – slow promenade, hand on heart |
| 3:16.95 | 380 | [L35] – offering to the moon, a bow to the people |
| 3:21.09 | 388 | Home – she sits facing the moon, tail wrapped around her |
| 3:36.10 | 417 | END |

## Editing / re-rendering
- **Change moves:** edit `hsin_dance.py`. `c.k(beat, …)` keys pose channels, `c.go()` moves her across the floor, `c.plant()`/`c.air()` place the feet, and `SHOTS` is the camera list. Then rebuild:
  `Blender -b --factory-startup -P hsin_dance.py -- --out hsin_dance.blend --audio "<song.mp3>"`
- **Render (720p):** `Blender -b hsin_dance.blend -P render_preview.py -- hsin_dance_720p.mp4 720 16`. Takes roughly 1–1.5 h on this M1.
