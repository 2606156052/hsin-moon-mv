"""Single source of truth for the MV: scenes (Seedream plates) and shots (Wan clips / JS panels).
Beat grid: 115.96 BPM, beat 0 = 0.335 s. Every shot boundary sits on a beat.
"""
BPM, PH = 115.96, 0.335
SPB = 60 / BPM
def T(b): return round(PH + b * SPB, 3)

STYLE = ("Premium Chinese 2D anime game cutscene art, cel shading with painterly light, clean line art, "
         "rich blue-violet night palette with warm lantern glow")

# ------------------------------------------------------------------ scenes (Seedream 5.0 Pro plates, no people)
SCENES = {
 'rooftop':   "Empty background plate, no people: a curved ceramic-tiled temple rooftop ridge high above a vast night city of warm lantern-lit streets, an enormous full moon close behind, sky lanterns rising past the eaves, starry blue-violet sky.",
 'street':    "Empty background plate, no people: a lantern-lined festival street in an old Chinese city at night, red and gold paper lanterns strung overhead, food stalls with steam, warm windows, petals and confetti in the air, deep perspective toward a pagoda and the moon.",
 'plaza':     "existing:scene_s1b.jpg",
 'moonplaza': "existing:scene_bg.jpg",
 'skysea':    "Empty background plate, no people: high above a sea of moonlit clouds, thousands of glowing sky lanterns drifting at every depth, an enormous full moon, the faint glow of a city visible through gaps in the clouds far below.",
 'lake':      "Empty background plate, no people: a perfectly still mirror lake at night reflecting a giant full moon and floating lanterns, a small wooden pavilion on stilts, lotus leaves, light mist on the water, distant mountains.",
 'throne':    "Empty background plate, no people: a vast dark palace hall with towering pillars, an empty golden throne on a dais under a cold violet light shaft, heavy silk drapes, deep shadows, oppressive and solemn mood, faint purple haze.",
 'mirrorhall':"Empty background plate, no people: a dim ancient chamber with a giant round bronze mirror on a carved stand, its surface faintly glowing, candles, violet and gold light, floating dust, eerie mood.",
 'cliff':     "Empty background plate, no people: the top of an old city wall on a cliff at night, looking across a dark valley at a distant warm glowing festival town with fireworks, cold blue moonlight on the stones, lonely mood.",
 'firevoid':  "Empty background plate, no people: a dark dreamlike void filled with swirling ribbons of orange and crimson fire and drifting embers, glowing cinders spiraling upward, a faint full moon seen through the smoke.",
 'nexus':     "Empty background plate, no people: a surreal dream realm of floating broken fragments of palaces, lanterns and memories suspended in a starry indigo sky, rivers of pale moonlight flowing between them, a colossal glowing moon.",
 'river':     "Empty background plate, no people: a festival riverbank at night with hundreds of floating river lanterns, an arched stone bridge, warm glowing houses and hanging lanterns, sky lanterns rising toward a big full moon, joyful warm atmosphere.",
}

CHAR = ("Image 1 is the character sheet: animate exactly this fox goddess (ice-blue hair in braided buns with long side strands, "
        "tall blue fox ears with black tips, crimson eyes, off-shoulder black and crimson dress with translucent ice-blue layered skirt panels, "
        "red fur-trimmed half sleeves, silver star ornaments, bare feet in silver sandals, one huge ice-blue fox tail fading to a black tip with silver star charms). "
        "Image 2 is the location and the art style. ")
TAIL = (" Hair, sheer skirt panels, sleeves and tail move with soft realistic cloth and fur physics and follow-through. "
        "Fully 2D hand-drawn anime, cel shading with painterly light, clean line art, consistent character design, "
        "no text, no watermark, no 3D render look, no morphing, no extra limbs.")

# Each shot: id, beats (b0,b1), kind 'wan'|'panel'|'reuse', scene, gen duration (s), action, camera, lyric shown, act
# 'lip': close-up that should mouth the lyric -> the song segment is passed as an audio reference.
SHOTS = [
 # ---------------- ACT I · MOON-BORN
 dict(id='S01', b=(0, 8), kind='panel', panel='title', act=1),
 dict(id='S02', b=(8, 16), kind='wan', scene='rooftop', dur=5, act=1,
      action="Night. She is crouching on the rooftop ridge in the center of the frame, silhouetted against the huge moon, peeking curiously down at the glowing city like a fox; her ears twitch, she leans forward on her hands, then tilts her head with a mischievous grin and swishes her tail.",
      camera="Wide shot with her clearly in frame from the first frame, slow crane down and push-in toward her until she fills half the frame."),
 dict(id='S03', b=(16, 24), kind='wan', scene='rooftop', dur=5, act=1,
      action="She stands on the ridge and sways her hips and shoulders clearly from side to side with the music, arms lifting and drifting like floating lanterns; she reaches out and taps a passing sky lantern with a fingertip so it spins away, then twirls once, her big tail swinging in rhythm.",
      camera="Medium shot, slow arc around her from the side to the front, lanterns drifting through the foreground."),
 dict(id='S04', b=(24, 32), kind='wan', scene='rooftop', dur=5, act=1, lip=True,
      action="Close-up portrait: she softly sings, then lifts a finger to her lips with a sly smile and winks, ears perking.",
      camera="Slow push-in to a close-up on her face, shallow depth of field, lantern bokeh behind."),
 dict(id='S05', b=(32, 40), kind='panel', panel='actcard', act=1),
 dict(id='S06', b=(40, 48), kind='wan', scene='street', dur=5, act=1,
      action="She is in the frame from the start, floating down into the middle of the festival street from just above the lanterns, wide sleeves spread like wings and tail streaming upward, then lands lightly on her toes and spins in a playful twirl, laughing.",
      camera="Full-body shot from a low angle, her whole figure visible the entire time, the camera tilts down with her as she lands."),
 dict(id='S07', b=(48, 56), kind='wan', scene='street', dur=5, act=1,
      action="Mischievous fox spirit: she spins in a circle chasing her own fluffy tail, catches it, hugs it and giggles, then peeks over it toward the camera.",
      camera="Medium-wide shot, camera circles slowly around her, warm lantern light."),
 dict(id='S08', b=(56, 68), kind='wan', scene='street', dur=7, act=1,
      action="She dances down the middle of the lantern street toward the camera in a series of fast spinning chaine turns, skirt panels and tail fanning out, then crouches and springs high up into the air toward the moon.",
      camera="Full-body medium-wide shot with her whole body and head always in frame, camera backs up in front of her, then tilts up as she jumps."),
 dict(id='S09', b=(68, 76), kind='reuse', src='production/clips/S09_sample.mp4', src_in=0.0, scene='plaza', act=1),
 dict(id='S10', b=(76, 84), kind='wan', scene='plaza', dur=5, act=1,
      action="She swirls both wide sleeves in big circles overhead as if stirring the sky; the wind whips embers and red ribbons into a spiral around her, clouds churning above.",
      camera="Low hero angle, slow orbit around her, the moon framed behind her."),
 dict(id='S11', b=(84, 96), kind='wan', scene='moonplaza', dur=7, act=1,
      action="She turns her face up to the moon and opens her arms, bathing in a beam of moonlight, eyes closed and smiling; then she skips and twirls carefree across the moon circle.",
      camera="Starts behind her looking toward the moon, swings around to the front as she twirls."),
 dict(id='S12', b=(96, 104), kind='panel', panel='strings', act=1),
 dict(id='S13', b=(104, 112), kind='wan', scene='street', dur=5, act=1,
      action="She points to the lanterns overhead and they light up one after another along the street following her finger; she laughs and does a quick pirouette.",
      camera="Medium shot, camera tilts and pans following the chain of lighting lanterns, then returns to her."),
 dict(id='S14', b=(112, 120), kind='wan', scene='lake', dur=5, act=1,
      action="Standing on the mirror lake surface, she gently gathers tiny drifting motes of light from the air into her cupped hands, tender and calm, ripples spreading from her feet.",
      camera="Slow dolly in from medium to medium close-up."),
 dict(id='S15', b=(120, 128), kind='wan', scene='lake', dur=5, act=1,
      action="She holds the glowing light to her heart, then throws her arms open and releases it upward as a burst of dozens of small lanterns that rise into the sky.",
      camera="Medium shot that tilts up with the rising lanterns toward the moon."),
 dict(id='S16', b=(128, 136), kind='wan', scene='rooftop', dur=5, act=1,
      action="On the highest roof edge, wind blowing hard, she reaches one hand up toward the giant moon, standing on tiptoe, hair and sleeves streaming.",
      camera="Dramatic low angle hero shot from below, slow push-in."),
 dict(id='S17', b=(136, 144), kind='wan', scene='skysea', dur=5, act=1,
      action="She runs off the edge and flies through the night sky among sky lanterns, arms spread wide, sleeves and tail streaming like a comet, reaching toward the moon.",
      camera="Flying tracking shot alongside her, then she passes the camera."),
 dict(id='S18', b=(144, 152), kind='panel', panel='sorrowjoy', act=1),
 dict(id='S19', b=(152, 160), kind='wan', scene='skysea', dur=5, act=1,
      action="She glides slowly on her back among floating lanterns, then reaches out sideways as if holding someone's hand, a lantern drifting beside her like a companion.",
      camera="Gentle side tracking shot, dreamy slow movement."),
 dict(id='S20', b=(160, 168), kind='wan', scene='moonplaza', dur=5, act=1,
      action="On the moon circle she spins slowly with one arm raised to the sky and one pointing to the earth, her skirt panels and tail fanning out in a wide circle.",
      camera="Top-down overhead shot slowly rotating with her spin, then tilting down to a high angle."),
 dict(id='S21', b=(168, 180), kind='panel', panel='phases', act=1),
 dict(id='S22', b=(180, 188), kind='wan', scene='lake', dur=5, act=1,
      action="She dances on the water with flowing body waves, stepping forward and back like tides, ripples blooming under every step; at the end she freezes and looks up, startled, as a cold shadow falls over her.",
      camera="Side medium-wide shot drifting with her, ending on her upturned face."),
 # ---------------- ACT II · A MANTLE NOT HER OWN
 dict(id='S23', b=(188, 192), kind='panel', panel='actcard', act=2),
 dict(id='S24', b=(192, 200), kind='wan', scene='throne', dur=5, act=2,
      action="The fallen goddess's vast glowing moon seal descends and golden chains of light settle on her shoulders like an oversized ceremonial mantle; the weight forces her down to her knees, ears flattening, she gasps.",
      camera="High angle looking down at her, oppressive, slow push-in."),
 dict(id='S25', b=(200, 208), kind='wan', scene='throne', dur=5, act=2,
      action="She struggles and staggers against the golden chains of light binding her, the oversized mantle dragging her back, violet sparks pulsing.",
      camera="Handheld close-medium shot with a tilted dutch angle, jittery."),
 dict(id='S26', b=(208, 220), kind='wan', scene='mirrorhall', dur=7, act=2,
      action="She stands before the giant bronze mirror; her reflection is the original goddess, wrapped in a grand ceremonial mantle with a moon sigil on her brow and a cold, regal expression that does not match her own frightened face; she slowly reaches out and touches the glass.",
      camera="Wide side shot showing her whole body and the mirror, slow push-in on the reflection."),
 dict(id='S27', b=(220, 228), kind='wan', scene='mirrorhall', dur=5, act=2,
      action="Close-up: a tear rolls down her cheek; she turns her face away from the mirror, eyes closed, the weight of duty heavy on her.",
      camera="Static close-up, shallow focus, slow rack focus from the mirror to her face."),
 dict(id='S28', b=(228, 236), kind='panel', panel='shards', act=2),
 dict(id='S29', b=(236, 248), kind='wan', scene='cliff', dur=7, act=2,
      action="She sits alone on the edge of the city wall hugging her knees, faint chains of light trailing from her shoulders, tail curled around her, watching the distant glowing festival town and fireworks.",
      camera="Wide shot from behind her, slow push-in over her shoulder toward the distant lights."),
 dict(id='S30', b=(248, 256), kind='wan', scene='cliff', dur=5, act=2,
      action="She stands and reaches longingly toward the distant lights and takes a step, but the chains of light tug her back; her outstretched hand closes on nothing.",
      camera="Medium shot that ends on a close-up of her empty reaching hand against the distant lights."),
 dict(id='S31', b=(256, 264), kind='wan', scene='firevoid', dur=5, act=2,
      action="A small ornate box made of glowing embers floats down in front of her, burning softly; she watches it with wide eyes, the flame reflected in them, slowly lifting her hands toward it.",
      camera="Slow push-in from medium to close-up on her face lit by the warm firelight."),
 # ---------------- ACT III · BURNING DEVOTION
 dict(id='S32', b=(264, 272), kind='wan', scene='firevoid', dur=5, act=3,
      action="She takes the burning box into both hands; flames erupt and swirl around her in ribbons; she stands firm in a wide stance, determined.",
      camera="Low angle medium shot, camera slowly circles her as the fire spirals."),
 dict(id='S33', b=(272, 280), kind='wan', scene='firevoid', dur=5, act=3,
      action="She whirls in powerful spinning turns holding the burning box high above her head, the flames trailing in spirals, tail and sleeves whipping.",
      camera="Dynamic orbit around her at waist height, fast."),
 dict(id='S34', b=(280, 288), kind='wan', scene='firevoid', dur=5, act=3,
      action="She slowly raises the burning box overhead toward the faint moon with fully extended arms, trembling; it flares into a blinding brilliant light.",
      camera="Extreme low angle from below looking up at her and the moon, slow push-in."),
 dict(id='S35', b=(288, 296), kind='wan', scene='firevoid', dur=5, act=3, lip=True,
      action="She sinks to her knees singing softly through tears as the box crumbles into glowing embers in her cupped hands; the embers drift up past her face; she bows her head.",
      camera="High angle close-medium shot slowly descending to her face."),
 # ---------------- ACT IV · RETURN TO THE HEART
 dict(id='S36', b=(296, 304), kind='wan', scene='nexus', dur=5, act=4,
      action="The chains of light and the moon seal shatter into golden fragments that fly outward; she rises from her knees in an explosion of white moonlight, hair and sleeves blasting outward, eyes opening.",
      camera="Starts close, pulls back fast to a wide shot as the light bursts."),
 dict(id='S37', b=(304, 312), kind='wan', scene='nexus', dur=5, act=4, lip=True,
      action="Extreme close-up of her crimson eyes reflecting the full moon, then she sings with calm resolve as the camera reveals her serene face framed by her hands.",
      camera="Starts on an extreme close-up of the eyes, slowly pulls back to a close-up."),
 dict(id='S38', b=(312, 320), kind='wan', scene='skysea', dur=5, act=4,
      action="She hovers above the sea of clouds looking down at the warm lights of the city far below, her hand over her heart, robes and tail floating weightlessly.",
      camera="Slow crane from beside her down past her toward the city lights below."),
 dict(id='S39', b=(320, 328), kind='wan', scene='nexus', dur=5, act=4,
      action="She faces a translucent glowing white version of herself, her true self made of moonlight; the two dance in perfect mirror symmetry, circling each other.",
      camera="Wide side profile two-shot, slow lateral track."),
 dict(id='S40', b=(328, 336), kind='wan', scene='nexus', dur=5, act=4,
      action="She and her glowing moonlight true self press their palms together; the glowing self smiles gently and dissolves into streams of light that flow into her chest; she gasps softly.",
      camera="Medium two-shot pushing in to their joined hands, then to her face."),
 dict(id='S41', b=(336, 344), kind='wan', scene='nexus', dur=5, act=4,
      action="Reborn, she spins upward through a spiral of moonlight and petals, arms opening wide in triumph, her tail and sleeves blazing with silver light.",
      camera="Rising spiral camera move around her, ending on a wide heroic shot."),
 dict(id='S42', b=(344, 356), kind='panel', panel='moonrain', act=4),
 # ---------------- ACT V · WHERE THE HEART BELONGS
 dict(id='S43', b=(356, 364), kind='wan', scene='street', dur=5, act=5,
      action="She walks through the busy festival street among blurred townspeople silhouettes, smiling warmly, gently touching hanging lanterns as she passes.",
      camera="Smooth front tracking shot walking backward in front of her."),
 dict(id='S44', b=(364, 372), kind='wan', scene='river', dur=5, act=5,
      action="She runs joyfully along the riverbank chasing the reflection of the moon, laughing, sleeves and tail flying, skipping over floating lantern light.",
      camera="Side tracking shot running with her, the moon racing in the background."),
 dict(id='S45', b=(372, 380), kind='wan', scene='river', dur=5, act=5,
      action="She kneels at the river edge, lights a sky lantern and releases it with both hands; it rises toward the moon and she watches it go with a soft smile.",
      camera="Medium shot that tilts up following the lantern to the moon."),
 dict(id='S46', b=(380, 388), kind='wan', scene='river', dur=5, act=5, lip=True,
      action="Close-up: she sings gently with a warm smile, hand over her heart, lantern light glowing on her face, ears relaxed.",
      camera="Slow push-in to a close-up, warm bokeh."),
 dict(id='S47', b=(388, 408), kind='wan', scene='rooftop', dur=11, act=5,
      action="Final scene: she sits on the rooftop ridge facing the giant moon with her tail wrapped around her, the city of lanterns glowing below; she rests her head on her knees, at peace, as sky lanterns rise around her.",
      camera="Wide shot with her whole body in frame, slowly cranes up and pulls back into an extreme wide shot of her small silhouette against the moon over the glowing city."),
 dict(id='S48', b=(408, 419), kind='panel', panel='endcard', act=5),
]

import json as _json, os as _os
_LF = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'lyrics.json')
_LD = _json.load(open(_LF)) if _os.path.exists(_LF) else _json.load(open(_LF.replace('lyrics.json', 'lyrics.example.json')))
LYRICS = [tuple(x) for x in _LD['lines']]   # (time_s, line) — supplied locally, not committed (copyrighted)
DISPLAY = {float(k): tuple(v) for k, v in _LD.get('display', {}).items()}
PANEL_TEXT = _LD.get('panels', {})
ACTS = {1: ("ACT I", "Moon-Born", "Playing Among Mortals"), 2: ("ACT II", "A Mantle Not Her Own", "Power She Never Asked to Bear"),
        3: ("ACT III", "Burning Devotion", "A Mortal's Last Flame"), 4: ("ACT IV", "Return to the Heart", "Reconciliation"),
        5: ("ACT V", "Where the Heart Belongs", "Lanterns Forever Bright")}
