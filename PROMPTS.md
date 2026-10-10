# Prompts: Ode to Hsin and Moon MV

Part 1 is the director's own prompts, in order. Part 2 is every prompt the pipeline sent to the generation models for the final film.

Redactions: the song's lyrics (copyrighted) and an API key. The style-reference video and the character sheet are referenced but not included.

---

# Part 1: Director prompts

## Phase 1 · Blender dance and camera design

### 1. Initial brief (prompt.docx + song mp3)

> I'd like you to design a complete set of dance movements in Blender based on the melody and content of this piece of music that I've provided, along with the character settings related to this song that I've added. The model can be represented with a simple base-mesh figure, and the movements should be nimble and accurate; you should also design the camera work independently based on the music and the dance movements.
> Below are the supplementary character settings （Because its a Chinese game so the character settings is in Chinese）:
> 第一幕：月下化形，游戏人间
> 心月狐是瑝珑梦州的岁主——一方水土的守护神，名号取自二十八宿"心月狐"。追月节的传说里写着：她常化作人形游戏人间，最爱逗弄凡人。她爱听玄翎鸟讲八卦，是个嘴硬的吃货，喜欢与民同乐。这一幕的她，是"神"最轻盈的样子——狐狸的狡黠、月亮的皎洁，全写在俏皮里。
> 情绪：轻快、灵动 | 意象：月光、狐尾、人间的灯火
> 第二幕：戴上不属于自己的冠
> 真正的转折是：心月狐本体早已被残星会刺杀——三位会监联手，蛇菰的寄生做局多年，一击得手。你今天看到的"心"（玄翎鸟给她取的名字），只是她一缕意志的分形化身，带着"文明之匣"行走人间。所有人都把她当成心月狐，可她清楚自己不是。玩家有一句精准的概括："欲戴其冠，必承其重——但谁知道，冠是莫名其妙被戴上去的，戴上之后反而被压到喘不过气。"
> 情绪：压抑、自我怀疑 | 意象：沉重的冠、镜中不是自己的脸
> 第三幕：璇情燃尽
> 她的岁主共鸣者——少女璇情，不肯接受岁主已死，强行进行二次共鸣，最终把自己彻底燃尽，只留下一只"情匣"交给漂泊者，消散在人前。这是 3.7 最大的"刀"：一个凡人用最笨的方式，替神明赴死。心背负的冠，从此又多了一条命的重量。
> 情绪：决绝、悲壮 | 意象：燃烧的匣、消散的光尘
> 第四幕：溯心——与自己的和解
> 漂泊者陪她深入"梦枢天罗"——由岁主记忆交织成的梦境之地。在名为"溯心"的一战里，她终于不再逃避替身的身份，与本体的意志正面相见。本体对她说："你已能独行至此……不必再沉溺此梦了。"那一刻她完成了涅槃——不是"成为心月狐"，而是接纳了"以'心'之名守护"。
> 情绪：释然、破茧 | 意象：碎裂的梦境、重生的火焰、月光洒落
> 第五幕：心有所归
> 官方给她的判词是：「遍尝世间万念，方知……心有所归。」她的归处不是神座，而是具体的人间——动画短片《寻心》里祖孙两代人的灯火，追月节街巷的烟火气。最后她回到梦州，仇远、景燃、吟霖同行。"同赏人间欢喜，共守灯火长明"——一个冒名顶替的神明，比真神更动人。
> 情绪：温暖、辽远 | 意象：万家灯火、明月为眸
> 
> Below are the lyrics with the timeline:
> 
> *[timed lyrics from the song's LRC file. Not reproduced here (copyrighted); kept locally in `production/lyrics.json`.]*

### 2. Render resolution

> don't render at 1080p,720p is enough

### 3. Progress check

> how much longer i need

## Phase 2 · Full MV brief (Atlas Cloud: Wan 3.0 + Seedream 5.0)

### 4. MV brief

> You have already completed the motion reference, and you also know the character's setting and story. I need you to create a complete MV based on the motions you designed. For the visual style, I want you to directly reference the style of the following link: "https://www.bilibili.com/video/BV1BBad6iEjz/". I do not want this MV to be merely a dancing video; it should have JavaScript animations made up of graphic design elements that match the song's style interspersed throughout to express the theme of the lyrics, along with lyric designs rich in a style corresponding to the song. Every transition must fit the rhythm and be smooth and natural. When there is a close-up of the character's face, the lip movements should match the song. The character's clothing should also appear soft and follow the laws of physics.
> 
> I have already had you connect to atlascloud. You need to use the wan3.0 model to generate the video, and use seedream5.0 to generate the reference board for the character "心月狐". You can also use seedream5.0 to generate static frames for reference based on the dance moves you designed, so that you can use wan3.0 for the final video generation. I have a budget of 25 USD; you need to autonomously and repeatedly judge the correctness of the movements as well as the consistency of the character until it is perfect. You may use the entire 25 USD, but there will be no additional budget, so please arrange the use of the budget reasonably.
> 
> I want you to aim the final video quality directly at the video in the style reference link I gave you, that is, the quality level of a mature, world's first-tier commercial game cutscene animation.
> 
> Regarding the final film, I have two ideas, and I need you to first submit a 5-second sample with relatively large on-screen motion for each, so that I can judge which one to ultimately use.
> 
> Option One: After wan3.0 generates the video using the lowest resolution it can use, the code redraws the JavaScript animation based on the video, and finally renders it out in a 1080p video state.
> 
> Option Two: After wan3.0 generates the video using the lowest resolution it can use, you find an open-source super-resolution tool yourself, upscale the low-resolution video to 1080p, add the lyrics I asked you to add on these frames, and edit in the JavaScript animations interspersed in the video that I mentioned earlier, and finally export it in a 1080p video state.

### 5. Credentials

> *[API key message — redacted. The Atlas CLI was already authenticated through the OS keychain.]*

### 6. Decision + new character board

> i decide to use option1 ,and don't use your character board, use this one i gave, make sure u can use both pic and video reference. and try to make sample again. this time i wanna compare wan3 and seedance2.0, so still two version this time
> 
> *(attached: the user's own 心月狐 character design sheet; not included in this repository)*

### 7. Workflow change

> Stop using that Blender motion reference; let's switch workflows. Use SeaDream for the scene design, and describe the character's movements via text prompts based on your interpretation of the music's melody. For camera direction, take a comprehensive look at the overall flow and describe it in text as well—you can also generate keyframe references using SeaDream. Please generate another preview sample; I really hope this is the final take.

### 8. Question

> Were the text generated by Wan3, or did you hardcode/render them on afterward programmatically?

## Phase 3 · Production

### 9. Go

> All right, we can start the actual work now. I need a complete storyboard and shot breakdown plan. At the same time, you must execute according to these specifications. Also, make sure all text is in English—do not use Chinese. remind me when u finish the final job i'm gonna sleep

### 10. Story clarification

> Given that I've lived in China, I need to make a clarification: in the story's setting, "wearing a crown that does not belong to her" is not meant literally as putting on a physical crown. Rather, it signifies taking on power and responsibilities that were never meant to be hers. I would like the visuals to be adjusted accordingly—please make sure a traditional Western crown does not appear again.

## Phase 4 · Picture versions and delivery

### 11. v2 crisp repaint

> I need you to improve the code-driven animation. I want the video-based repainting to be as clean, crisp, and sharp as standard JavaScript animations. Please keep the current version of the video and create a new version.

### 12. v3 original footage

> I feel the code-redraw version is still too blurry. How about making another version that directly uses the original video footage? That way, I can decide which one to use in the end.

### 13. Repository + skill

> Please reorganize my prompts into a complete Markdown (.md) file, tidy up the other project files, and help me push the project to the GitHub repo. At the same time, package the workflow into a skill and attach it to the release.
> 
> i mean create a new repo for this project

---

# Part 2: Generation prompts

## Character reference

All Wan 3.0 shots use the director's character sheet as **image 1** (reference-to-video). Seedream and Seedance refused that sheet under their copyright filters, so it only ever went to Wan.

## Scene plates (Seedream 5.0 Pro text-to-image, 2048×1152)

Shared style suffix: *Premium Chinese 2D anime game cutscene art, cel shading with painterly light, clean line art, rich blue-violet night palette with warm lantern glow, cinematic composition, no text.*

- **rooftop**: Empty background plate, no people: a curved ceramic-tiled temple rooftop ridge high above a vast night city of warm lantern-lit streets, an enormous full moon close behind, sky lanterns rising past the eaves, starry blue-violet sky.
- **street**: Empty background plate, no people: a lantern-lined festival street in an old Chinese city at night, red and gold paper lanterns strung overhead, food stalls with steam, warm windows, petals and confetti in the air, deep perspective toward a pagoda and the moon.
- **plaza**: Empty background plate, no people. Cinematic low side angle across a long moonlit stone plaza... strong warm night wind: streams of glowing orange embers and loose red ribbons and petals blowing from left to right, paper sky lanterns swaying... enormous low full moon... layered Chinese pagoda rooftops (shot-specific plate made for the sample).
- **moonplaza**: Empty background plate, no people: a wide circular stone plaza at night inlaid with a silver crescent-moon circle pattern, enormous glowing full moon, hundreds of warm sky lanterns, distant pagoda town (plate made for the sample).
- **skysea**: Empty background plate, no people: high above a sea of moonlit clouds, thousands of glowing sky lanterns drifting at every depth, an enormous full moon, the faint glow of a city visible through gaps in the clouds far below.
- **lake**: Empty background plate, no people: a perfectly still mirror lake at night reflecting a giant full moon and floating lanterns, a small wooden pavilion on stilts, lotus leaves, light mist on the water, distant mountains.
- **throne**: Empty background plate, no people: a vast dark palace hall with towering pillars, an empty golden throne on a dais under a cold violet light shaft, heavy silk drapes, deep shadows, oppressive and solemn mood, faint purple haze.
- **mirrorhall**: Empty background plate, no people: a dim ancient chamber with a giant round bronze mirror on a carved stand, its surface faintly glowing, candles, violet and gold light, floating dust, eerie mood.
- **cliff**: Empty background plate, no people: the top of an old city wall on a cliff at night, looking across a dark valley at a distant warm glowing festival town with fireworks, cold blue moonlight on the stones, lonely mood.
- **firevoid**: Empty background plate, no people: a dark dreamlike void filled with swirling ribbons of orange and crimson fire and drifting embers, glowing cinders spiraling upward, a faint full moon seen through the smoke.
- **nexus**: Empty background plate, no people: a surreal dream realm of floating broken fragments of palaces, lanterns and memories suspended in a starry indigo sky, rivers of pale moonlight flowing between them, a colossal glowing moon.
- **river**: Empty background plate, no people: a festival riverbank at night with hundreds of floating river lanterns, an arched stone bridge, warm glowing houses and hanging lanterns, sky lanterns rising toward a big full moon, joyful warm atmosphere.

## Shot prompts (Wan 3.0 reference-to-video, 480p, prompts as sent for the takes used in the film)

### S02 · beats 8–16 · take 4

```text
Image 1 is the character sheet: animate exactly this fox goddess (ice-blue hair in braided buns with long side strands, tall blue fox ears with black tips, crimson eyes, off-shoulder black and crimson dress with translucent ice-blue layered skirt panels, red fur-trimmed half sleeves, silver star ornaments, bare feet in silver sandals, one huge ice-blue fox tail fading to a black tip with silver star charms). Image 2 is the location and the art style: this curved temple rooftop high above a lantern-lit night city under a giant moon, premium Chinese 2D anime game cutscene art. The music is a bright, flowing 116 BPM orchestral pop song with plucked guzheng and strings; she moves on the beat, light and playful like a fox spirit riding the wind. Action, in order over 5 seconds: (0-1.5s) She crouches low on the rooftop ridge in the center of the frame, silhouetted against the huge moon, and creeps forward on hands and feet like a fox, tail swishing; (1.5-3s) she leans far over the edge, ears flicking, peering down at the glowing city; (3-5s) she sits back on her heels, turns her head to the camera with a mischievous grin and flicks her tail. Camera: Wide shot with her clearly in frame from the first frame, slow crane down and push-in toward her until she fills half the frame. Hair, sheer skirt panels, sleeves and tail move with soft realistic cloth and fur physics. Fully 2D hand-drawn anime, cel shading with painterly light, clean line art, consistent character design, no 3D render look, no morphing, no extra limbs.
```

### S03 · beats 16–24 · take 2

```text
Image 1 is the character sheet: animate exactly this fox goddess (ice-blue hair in braided buns with long side strands, tall blue fox ears with black tips, crimson eyes, off-shoulder black and crimson dress with translucent ice-blue layered skirt panels, red fur-trimmed half sleeves, silver star ornaments, bare feet in silver sandals, one huge ice-blue fox tail fading to a black tip with silver star charms). Image 2 is the location and the art style. The music is a bright, flowing 116 BPM orchestral pop with guzheng and strings; she moves on the beat, light and playful like a fox spirit. She is clearly visible in the shot from the very first frame to the last, never cropped out of frame. Action: She stands on the ridge and sways her hips and shoulders clearly from side to side with the music, arms lifting and drifting like floating lanterns; she reaches out and taps a passing sky lantern with a fingertip so it spins away, then twirls once, her big tail swinging in rhythm. Camera: Medium shot, slow arc around her from the side to the front, lanterns drifting through the foreground.  Hair, sheer skirt panels, sleeves and tail move with soft realistic cloth and fur physics and follow-through. Fully 2D hand-drawn anime, cel shading with painterly light, clean line art, consistent character design, no text, no watermark, no 3D render look, no morphing, no extra limbs.
```

### S04 · beats 24–32 · take 1

```text
Image 1 is the character sheet: animate exactly this fox goddess (ice-blue hair in braided buns with long side strands, tall blue fox ears with black tips, crimson eyes, off-shoulder black and crimson dress with translucent ice-blue layered skirt panels, red fur-trimmed half sleeves, silver star ornaments, bare feet in silver sandals, one huge ice-blue fox tail fading to a black tip with silver star charms). Image 2 is the location and the art style. Audio 1 is the song for this moment: she sings this vocal line with accurate lip sync, mouth shapes matching the words and rhythm. The music is a bright, flowing 116 BPM orchestral pop with guzheng and strings; she moves on the beat, light and playful like a fox spirit. Action: Close-up portrait: she softly sings, then lifts a finger to her lips with a sly smile and winks, ears perking. Camera: Slow push-in to a close-up on her face, shallow depth of field, lantern bokeh behind.  Hair, sheer skirt panels, sleeves and tail move with soft realistic cloth and fur physics and follow-through. Fully 2D hand-drawn anime, cel shading with painterly light, clean line art, consistent character design, no text, no watermark, no 3D render look, no morphing, no extra limbs.
```

### S06 · beats 40–48 · take 6

```text
Image 1 is the character sheet: animate exactly this fox goddess (ice-blue hair in braided buns with long side strands, tall blue fox ears with black tips, crimson eyes, off-shoulder black and crimson dress with translucent ice-blue layered skirt panels, red fur-trimmed half sleeves, silver star ornaments, bare feet in silver sandals, one huge ice-blue fox tail fading to a black tip with silver star charms). Image 2 is the location and the art style: this lantern-lined festival street at night, premium Chinese 2D anime game cutscene art. The music is a bright, flowing 116 BPM orchestral pop song with plucked guzheng and strings; she moves on the beat, light and playful like a fox spirit riding the wind. Action, in order over 5 seconds: (0-1.5s) she runs fast down the middle of the festival street toward the camera, arms swinging, tail streaming; (1.5-3s) she leaps into a high spinning jump, sleeves flaring like wings; (3-5s) she lands, spins twice more and throws her arms open with a laugh, petals swirling around her. Camera: Full-body shot from a low angle, her whole figure visible the entire time, the camera tilts down with her as she lands. Hair, sheer skirt panels, sleeves and tail move with soft realistic cloth and fur physics. Fully 2D hand-drawn anime, cel shading with painterly light, clean line art, consistent character design, no 3D render look, no morphing, no extra limbs.
```

### S07 · beats 48–56 · take 1

```text
Image 1 is the character sheet: animate exactly this fox goddess (ice-blue hair in braided buns with long side strands, tall blue fox ears with black tips, crimson eyes, off-shoulder black and crimson dress with translucent ice-blue layered skirt panels, red fur-trimmed half sleeves, silver star ornaments, bare feet in silver sandals, one huge ice-blue fox tail fading to a black tip with silver star charms). Image 2 is the location and the art style. The music is a bright, flowing 116 BPM orchestral pop with guzheng and strings; she moves on the beat, light and playful like a fox spirit. Action: Mischievous fox spirit: she spins in a circle chasing her own fluffy tail, catches it, hugs it and giggles, then peeks over it toward the camera. Camera: Medium-wide shot, camera circles slowly around her, warm lantern light.  Hair, sheer skirt panels, sleeves and tail move with soft realistic cloth and fur physics and follow-through. Fully 2D hand-drawn anime, cel shading with painterly light, clean line art, consistent character design, no text, no watermark, no 3D render look, no morphing, no extra limbs.
```

### S08 · beats 56–68 · take 4

```text
Image 1 is the character sheet: animate exactly this fox goddess (ice-blue hair in braided buns with long side strands, tall blue fox ears with black tips, crimson eyes, off-shoulder black and crimson dress with translucent ice-blue layered skirt panels, red fur-trimmed half sleeves, silver star ornaments, bare feet in silver sandals, one huge ice-blue fox tail fading to a black tip with silver star charms). Image 2 is the location and the art style: this lantern-lined festival street at night, premium Chinese 2D anime game cutscene art. The music is a bright, flowing 116 BPM orchestral pop song with plucked guzheng and strings; she moves on the beat, light and playful like a fox spirit riding the wind. Action, in order over 7 seconds: (0-2s) She dances down the middle of the lantern street toward the camera in fast spinning chaine turns, skirt panels and tail fanning out; (2-4s) three running skips, arms swinging; (4-5.5s) she crouches deeply; (5.5-7s) she leaps high up into the air toward the moon, sleeves trailing. Camera: Full-body medium-wide shot with her whole body and head always in frame, camera backs up in front of her, then tilts up as she jumps. Hair, sheer skirt panels, sleeves and tail move with soft realistic cloth and fur physics. Fully 2D hand-drawn anime, cel shading with painterly light, clean line art, consistent character design, no 3D render look, no morphing, no extra limbs.
```

### S09 · beats 68–76 · take sample

```text
Image 1 is the character sheet: animate exactly this fox goddess (ice-blue hair in braided buns with long side strands, tall blue fox ears with black tips, crimson eyes, off-shoulder black and crimson dress with translucent ice-blue layered skirt panels, red fur-trimmed half sleeves, silver star ornaments, bare feet in silver sandals, one huge ice-blue fox tail fading to a black tip with silver star charms). Image 2 is the location and the art style: this windy moonlit lantern plaza with streaming embers and red ribbons, premium Chinese 2D anime game cutscene art. The music is a bright, flowing 116 BPM orchestral pop verse with plucked guzheng and strings; she moves on the beat, light and playful like a fox spirit riding the wind. Action, in order over 5 seconds: (0-1s) she springs up from a low crouch as a gust hits, sleeves and skirt panels billowing; (1-2.5s) four light skipping steps on the beat running left to right across the plaza, arms swept back, tail streaming behind; (2.5-3.5s) she leaps high into a mid-air spin, legs split, the long tail sweeping a full arc through the flying embers; (3.5-5s) she lands softly on one foot, the cloth and tail settling with follow-through, then turns toward the camera and lifts both arms upward as if stirring the clouds, with a playful smile. Camera: low-angle side tracking shot that moves with her run, swings in a half orbit around her during the leap so the moon is behind her at the top of the jump, then eases into a medium shot of her facing the camera. Hair, sheer skirt panels, sleeves and tail move with soft realistic cloth and fur physics. Fully 2D hand-drawn anime, cel shading with painterly light, clean line art, consistent character design, no 3D render look, no morphing, no extra limbs.
```

### S10 · beats 76–84 · take 9

```text
Image 1 is the character sheet: animate exactly this fox goddess (ice-blue hair in braided buns with long side strands, tall blue fox ears with black tips, crimson eyes, off-shoulder black and crimson dress with translucent ice-blue layered skirt panels, red fur-trimmed half sleeves, silver star ornaments, bare feet in silver sandals, one huge ice-blue fox tail fading to a black tip with silver star charms). Image 2 is the location and the art style: this windy moonlit lantern plaza with streaming embers and red ribbons, premium Chinese 2D anime game cutscene art. The music is a bright, flowing 116 BPM orchestral pop verse with plucked guzheng and strings; she moves on the beat, light and playful like a fox spirit riding the wind. Action, in order over 5 seconds: (0-1.5s) she swings both wide sleeves in a huge circle over her head, spinning on the spot; (1.5-3s) she spins faster, embers and red ribbons whipping into a spiral around her; (3-5s) she thrusts both arms up to the sky and the swirling clouds above part, her hair and tail blasting upward in the wind. Camera: low hero angle, slow orbit around her, the moon framed behind her. Hair, sheer skirt panels, sleeves and tail move with soft realistic cloth and fur physics. Fully 2D hand-drawn anime, cel shading with painterly light, clean line art, consistent character design, no 3D render look, no morphing, no extra limbs.
```

### S11 · beats 84–96 · take 6

```text
Image 1 is the character sheet: animate exactly this fox goddess (ice-blue hair in braided buns with long side strands, tall blue fox ears with black tips, crimson eyes, off-shoulder black and crimson dress with translucent ice-blue layered skirt panels, red fur-trimmed half sleeves, silver star ornaments, bare feet in silver sandals, one huge ice-blue fox tail fading to a black tip with silver star charms). Image 2 is the location and the art style: this circular moon-marked stone plaza under a giant full moon and floating lanterns, premium Chinese 2D anime game cutscene art. The music is a bright, flowing 116 BPM orchestral pop song with plucked guzheng and strings; she moves on the beat, light and playful like a fox spirit riding the wind. Action, in order over 7 seconds: (0-1.5s) she runs across the moon circle and spreads her arms wide; (1.5-3.5s) she spins round and round in big fast turns, head tilted up to the moon, sleeves and tail fanning out; (3.5-5.5s) she skips in three big bounding hops; (5.5-7s) she leaps and twirls in the air and lands laughing. Camera: Starts behind her looking toward the moon, swings around to the front as she twirls. Hair, sheer skirt panels, sleeves and tail move with soft realistic cloth and fur physics. Fully 2D hand-drawn anime, cel shading with painterly light, clean line art, consistent character design, no 3D render look, no morphing, no extra limbs.
```

### S13 · beats 104–112 · take 6

```text
Image 1 is the character sheet: animate exactly this fox goddess (ice-blue hair in braided buns with long side strands, tall blue fox ears with black tips, crimson eyes, off-shoulder black and crimson dress with translucent ice-blue layered skirt panels, red fur-trimmed half sleeves, silver star ornaments, bare feet in silver sandals, one huge ice-blue fox tail fading to a black tip with silver star charms). Image 2 is the location and the art style: this lantern-lined festival street at night, premium Chinese 2D anime game cutscene art. The music is a bright, flowing 116 BPM orchestral pop song with plucked guzheng and strings; she moves on the beat, light and playful like a fox spirit riding the wind. Action, in order over 5 seconds: (0-1.5s) she skips down the street pointing up at the lanterns; (1.5-3.5s) she runs along under them sweeping her arm and they burst alight one after another behind her; (3.5-5s) she leaps into a fast pirouette, laughing, tail whipping around. Camera: Medium shot, camera tilts and pans following the chain of lighting lanterns, then returns to her. Hair, sheer skirt panels, sleeves and tail move with soft realistic cloth and fur physics. Fully 2D hand-drawn anime, cel shading with painterly light, clean line art, consistent character design, no 3D render look, no morphing, no extra limbs.
```

### S14 · beats 112–120 · take 4

```text
Image 1 is the character sheet: animate exactly this fox goddess (ice-blue hair in braided buns with long side strands, tall blue fox ears with black tips, crimson eyes, off-shoulder black and crimson dress with translucent ice-blue layered skirt panels, red fur-trimmed half sleeves, silver star ornaments, bare feet in silver sandals, one huge ice-blue fox tail fading to a black tip with silver star charms). Image 2 is the location and the art style: this still mirror lake at night with floating lanterns and a pavilion, premium Chinese 2D anime game cutscene art. The music is a bright, flowing 116 BPM orchestral pop song with plucked guzheng and strings; she moves on the beat, light and playful like a fox spirit riding the wind. Action, in order over 5 seconds: (0-1.5s) She walks slowly across the mirror lake surface, ripples spreading from each bare step; (1.5-3.5s) tiny drifting motes of light float toward her and she gathers them by sweeping her cupped hands through the air; (3.5-5s) she draws the glowing light close to her chest and bows her head tenderly. Camera: Slow dolly in from medium to medium close-up. Hair, sheer skirt panels, sleeves and tail move with soft realistic cloth and fur physics. Fully 2D hand-drawn anime, cel shading with painterly light, clean line art, consistent character design, no 3D render look, no morphing, no extra limbs.
```

### S15 · beats 120–128 · take 4

```text
Image 1 is the character sheet: animate exactly this fox goddess (ice-blue hair in braided buns with long side strands, tall blue fox ears with black tips, crimson eyes, off-shoulder black and crimson dress with translucent ice-blue layered skirt panels, red fur-trimmed half sleeves, silver star ornaments, bare feet in silver sandals, one huge ice-blue fox tail fading to a black tip with silver star charms). Image 2 is the location and the art style: this still mirror lake at night with floating lanterns and a pavilion, premium Chinese 2D anime game cutscene art. The music is a bright, flowing 116 BPM orchestral pop song with plucked guzheng and strings; she moves on the beat, light and playful like a fox spirit riding the wind. Action, in order over 5 seconds: (0-1.5s) She holds a glowing light against her heart, eyes closed; (1.5-3s) she spins once and throws both arms wide open; (3-5s) the light bursts upward into dozens of small lanterns that rise around her into the sky as she watches them, arms still raised. Camera: Medium shot that tilts up with the rising lanterns toward the moon. Hair, sheer skirt panels, sleeves and tail move with soft realistic cloth and fur physics. Fully 2D hand-drawn anime, cel shading with painterly light, clean line art, consistent character design, no 3D render look, no morphing, no extra limbs.
```

### S16 · beats 128–136 · take 4

```text
Image 1 is the character sheet: animate exactly this fox goddess (ice-blue hair in braided buns with long side strands, tall blue fox ears with black tips, crimson eyes, off-shoulder black and crimson dress with translucent ice-blue layered skirt panels, red fur-trimmed half sleeves, silver star ornaments, bare feet in silver sandals, one huge ice-blue fox tail fading to a black tip with silver star charms). Image 2 is the location and the art style: this curved temple rooftop high above a lantern-lit night city under a giant moon, premium Chinese 2D anime game cutscene art. The music is a bright, flowing 116 BPM orchestral pop song with plucked guzheng and strings; she moves on the beat, light and playful like a fox spirit riding the wind. Action, in order over 5 seconds: (0-1.5s) She runs along the roof ridge in strong wind, hair and sleeves streaming; (1.5-3s) she stops at the very edge and rises onto her toes; (3-5s) she stretches one hand up toward the giant moon, leaning forward, her tail lashing in the wind. Camera: Dramatic low angle hero shot from below, slow push-in. Hair, sheer skirt panels, sleeves and tail move with soft realistic cloth and fur physics. Fully 2D hand-drawn anime, cel shading with painterly light, clean line art, consistent character design, no 3D render look, no morphing, no extra limbs.
```

### S17 · beats 136–144 · take 1

```text
Image 1 is the character sheet: animate exactly this fox goddess (ice-blue hair in braided buns with long side strands, tall blue fox ears with black tips, crimson eyes, off-shoulder black and crimson dress with translucent ice-blue layered skirt panels, red fur-trimmed half sleeves, silver star ornaments, bare feet in silver sandals, one huge ice-blue fox tail fading to a black tip with silver star charms). Image 2 is the location and the art style. The music is a bright, flowing 116 BPM orchestral pop with guzheng and strings; she moves on the beat, light and playful like a fox spirit. Action: She runs off the edge and flies through the night sky among sky lanterns, arms spread wide, sleeves and tail streaming like a comet, reaching toward the moon. Camera: Flying tracking shot alongside her, then she passes the camera.  Hair, sheer skirt panels, sleeves and tail move with soft realistic cloth and fur physics and follow-through. Fully 2D hand-drawn anime, cel shading with painterly light, clean line art, consistent character design, no text, no watermark, no 3D render look, no morphing, no extra limbs.
```

### S19 · beats 152–160 · take 4

```text
Image 1 is the character sheet: animate exactly this fox goddess (ice-blue hair in braided buns with long side strands, tall blue fox ears with black tips, crimson eyes, off-shoulder black and crimson dress with translucent ice-blue layered skirt panels, red fur-trimmed half sleeves, silver star ornaments, bare feet in silver sandals, one huge ice-blue fox tail fading to a black tip with silver star charms). Image 2 is the location and the art style: this sky above a sea of moonlit clouds full of drifting sky lanterns, premium Chinese 2D anime game cutscene art. The music is a bright, flowing 116 BPM orchestral pop song with plucked guzheng and strings; she moves on the beat, light and playful like a fox spirit riding the wind. Action, in order over 5 seconds: (0-2s) She glides slowly on her back among floating sky lanterns, hair and skirt panels drifting weightlessly; (2-3.5s) she rolls upright and drifts sideways; (3.5-5s) she reaches out her hand to a lantern floating beside her and cups it gently like holding someone's hand. Camera: Gentle side tracking shot, dreamy slow movement. Hair, sheer skirt panels, sleeves and tail move with soft realistic cloth and fur physics. Fully 2D hand-drawn anime, cel shading with painterly light, clean line art, consistent character design, no 3D render look, no morphing, no extra limbs.
```

### S20 · beats 160–168 · take 4

```text
Image 1 is the character sheet: animate exactly this fox goddess (ice-blue hair in braided buns with long side strands, tall blue fox ears with black tips, crimson eyes, off-shoulder black and crimson dress with translucent ice-blue layered skirt panels, red fur-trimmed half sleeves, silver star ornaments, bare feet in silver sandals, one huge ice-blue fox tail fading to a black tip with silver star charms). Image 2 is the location and the art style: this circular moon-marked stone plaza under a giant full moon and floating lanterns, premium Chinese 2D anime game cutscene art. The music is a bright, flowing 116 BPM orchestral pop song with plucked guzheng and strings; she moves on the beat, light and playful like a fox spirit riding the wind. Action, in order over 5 seconds: (0-5s) Standing on the moon circle she spins continuously, one arm raised to the sky and one pointing to the earth, accelerating; her skirt panels, sleeves and long tail fan out in a wide spinning circle around her. Camera: Top-down overhead shot slowly rotating with her spin, then tilting down to a high angle. Hair, sheer skirt panels, sleeves and tail move with soft realistic cloth and fur physics. Fully 2D hand-drawn anime, cel shading with painterly light, clean line art, consistent character design, no 3D render look, no morphing, no extra limbs.
```

### S22 · beats 180–188 · take 6

```text
Image 1 is the character sheet: animate exactly this fox goddess (ice-blue hair in braided buns with long side strands, tall blue fox ears with black tips, crimson eyes, off-shoulder black and crimson dress with translucent ice-blue layered skirt panels, red fur-trimmed half sleeves, silver star ornaments, bare feet in silver sandals, one huge ice-blue fox tail fading to a black tip with silver star charms). Image 2 is the location and the art style: this still mirror lake at night with floating lanterns and a pavilion, premium Chinese 2D anime game cutscene art. The music is a bright, flowing 116 BPM orchestral pop song with plucked guzheng and strings; she moves on the beat, light and playful like a fox spirit riding the wind. Action, in order over 5 seconds: (0-1.5s) she dances across the water with big flowing body waves, stepping far forward; (1.5-3s) she spins and sweeps backward like a receding tide, sleeves trailing in an arc, ripples bursting under her feet; (3-4s) one more big spinning step forward; (4-5s) she stops abruptly and looks up, startled. Camera: Side medium-wide shot drifting with her, ending on her upturned face. Hair, sheer skirt panels, sleeves and tail move with soft realistic cloth and fur physics. Fully 2D hand-drawn anime, cel shading with painterly light, clean line art, consistent character design, no 3D render look, no morphing, no extra limbs.
```

### S24 · beats 192–200 · take 10

```text
Image 1 is the character sheet: animate exactly this fox goddess (ice-blue hair in braided buns with long side strands, tall blue fox ears with black tips, crimson eyes, off-shoulder black and crimson dress with translucent ice-blue layered skirt panels, red fur-trimmed half sleeves, silver star ornaments, bare feet in silver sandals, one huge ice-blue fox tail fading to a black tip with silver star charms). Image 2 is the location and the art style: this vast dark violet palace hall with a golden throne, premium Chinese 2D anime game cutscene art. The music turns heavy and dark at 116 BPM; she moves on the beat, weighed down, hesitant and anguished. Action, in order over 5 seconds: (0-1.5s) in the dark throne hall she spins around and looks up in alarm as a vast glowing golden moon seal, a circular divine sigil, descends from the light shaft above her; (1.5-2.5s) the seal sinks into her chest in a flash and heavy golden chains of light coil around her shoulders like an oversized ceremonial mantle that drags across the floor; (2.5-5s) the weight drives her down to her knees, ears flattening, gasping, the empty throne looming behind her. She wears no crown, no tiara and no headwear of any kind; her head shows only her own hair, fox ears and hairpins. Camera: High angle looking down at her, oppressive, slow push-in. Hair, sheer skirt panels, sleeves and tail move with soft realistic cloth and fur physics. Fully 2D hand-drawn anime, cel shading with painterly light, clean line art, consistent character design, no 3D render look, no morphing, no extra limbs.
```

### S25 · beats 200–208 · take 10

```text
Image 1 is the character sheet: animate exactly this fox goddess (ice-blue hair in braided buns with long side strands, tall blue fox ears with black tips, crimson eyes, off-shoulder black and crimson dress with translucent ice-blue layered skirt panels, red fur-trimmed half sleeves, silver star ornaments, bare feet in silver sandals, one huge ice-blue fox tail fading to a black tip with silver star charms). Image 2 is the location and the art style: this vast dark violet palace hall with a golden throne, premium Chinese 2D anime game cutscene art. The music turns heavy and dark at 116 BPM; she moves on the beat, weighed down, hesitant and anguished. Action, in order over 5 seconds: (0-1.5s) she staggers up, bound by glowing golden chains of light wrapped around her arms and shoulders; (1.5-3.5s) she twists and strains desperately against the chains, the oversized mantle of light dragging her backward, violet sparks bursting; (3.5-5s) she stumbles sideways, exhausted, still bound. She wears no crown, no tiara and no headwear of any kind; her head shows only her own hair, fox ears and hairpins. Camera: Handheld close-medium shot with a tilted dutch angle, jittery. Hair, sheer skirt panels, sleeves and tail move with soft realistic cloth and fur physics. Fully 2D hand-drawn anime, cel shading with painterly light, clean line art, consistent character design, no 3D render look, no morphing, no extra limbs.
```

### S26 · beats 208–220 · take 10

```text
Image 1 is the character sheet: animate exactly this fox goddess (ice-blue hair in braided buns with long side strands, tall blue fox ears with black tips, crimson eyes, off-shoulder black and crimson dress with translucent ice-blue layered skirt panels, red fur-trimmed half sleeves, silver star ornaments, bare feet in silver sandals, one huge ice-blue fox tail fading to a black tip with silver star charms). Image 2 is the location and the art style: this dim chamber with a giant glowing bronze mirror, premium Chinese 2D anime game cutscene art. The music turns heavy and dark at 116 BPM; she moves on the beat, weighed down, hesitant and anguished. Action, in order over 7 seconds: (0-2s) full-body wide shot: she walks quickly up to the giant bronze mirror, her whole figure visible; (2-4.5s) inside the mirror stands the original goddess with her same face but a serene, cold, regal expression, wrapped in a grand flowing ceremonial mantle of light with a glowing moon sigil on her brow, while she herself recoils a step in fright; (4.5-7s) she steps forward again and presses her trembling palm to the glass. She wears no crown, no tiara and no headwear of any kind; her head shows only her own hair, fox ears and hairpins. Camera: Wide side shot showing her whole body and the mirror, slow push-in on the reflection. Hair, sheer skirt panels, sleeves and tail move with soft realistic cloth and fur physics. Fully 2D hand-drawn anime, cel shading with painterly light, clean line art, consistent character design, no 3D render look, no morphing, no extra limbs.
```

### S27 · beats 220–228 · take 6

```text
Image 1 is the character sheet: animate exactly this fox goddess (ice-blue hair in braided buns with long side strands, tall blue fox ears with black tips, crimson eyes, off-shoulder black and crimson dress with translucent ice-blue layered skirt panels, red fur-trimmed half sleeves, silver star ornaments, bare feet in silver sandals, one huge ice-blue fox tail fading to a black tip with silver star charms). Image 2 is the location and the art style: this dim chamber with a giant glowing bronze mirror, premium Chinese 2D anime game cutscene art. The music turns heavy and dark at 116 BPM; she moves on the beat, weighed down, hesitant and anguished. Action, in order over 5 seconds: (0-1.5s) close-up: her eyes fill with tears as she stares ahead; (1.5-3s) a tear rolls down her cheek and she trembles; (3-5s) she squeezes her eyes shut and turns her head sharply away, ears drooping. Camera: Static close-up, shallow focus, slow rack focus from the mirror to her face. Hair, sheer skirt panels, sleeves and tail move with soft realistic cloth and fur physics. Fully 2D hand-drawn anime, cel shading with painterly light, clean line art, consistent character design, no 3D render look, no morphing, no extra limbs.
```

### S29 · beats 236–248 · take 4 (resumed)

```text
Image 1 is the character sheet: animate exactly this fox goddess (ice-blue hair in braided buns with long side strands, tall blue fox ears with black tips, crimson eyes, off-shoulder black and crimson dress with translucent ice-blue layered skirt panels, red fur-trimmed half sleeves, silver star ornaments, bare feet in silver sandals, one huge ice-blue fox tail fading to a black tip with silver star charms). Image 2 is the location and the art style: this lonely city wall on a cliff overlooking a distant glowing festival town, premium Chinese 2D anime game cutscene art. The music turns heavy and dark at 116 BPM; she moves on the beat, weighed down, hesitant and anguished. Action, in order over 7 seconds: (0-2s) She sits on the edge of the city wall hugging her knees, tail curled around her; (2-4.5s) fireworks burst over the distant town and she lifts her head to watch, the light flickering on her; (4.5-7s) she rests her chin on her knees and sighs, ears drooping. Camera: Wide shot from behind her, slow push-in over her shoulder toward the distant lights. Hair, sheer skirt panels, sleeves and tail move with soft realistic cloth and fur physics. Fully 2D hand-drawn anime, cel shading with painterly light, clean line art, consistent character design, no 3D render look, no morphing, no extra limbs.
```

### S30 · beats 248–256 · take 4 (resumed)

```text
Image 1 is the character sheet: animate exactly this fox goddess (ice-blue hair in braided buns with long side strands, tall blue fox ears with black tips, crimson eyes, off-shoulder black and crimson dress with translucent ice-blue layered skirt panels, red fur-trimmed half sleeves, silver star ornaments, bare feet in silver sandals, one huge ice-blue fox tail fading to a black tip with silver star charms). Image 2 is the location and the art style: this lonely city wall on a cliff overlooking a distant glowing festival town, premium Chinese 2D anime game cutscene art. The music turns heavy and dark at 116 BPM; she moves on the beat, weighed down, hesitant and anguished. Action, in order over 5 seconds: (0-1.5s) She stands up and reaches longingly toward the distant festival lights; (1.5-3s) she takes two eager steps forward; (3-5s) an invisible force yanks her back by the crown and she stumbles, her outstretched hand closing on empty air. Camera: Medium shot that ends on a close-up of her empty reaching hand against the distant lights. Hair, sheer skirt panels, sleeves and tail move with soft realistic cloth and fur physics. Fully 2D hand-drawn anime, cel shading with painterly light, clean line art, consistent character design, no 3D render look, no morphing, no extra limbs.
```

*Note: this prompt predates the crown clarification. The take used shows her seated on the wall with no crown visible. Any regeneration should use the chains-of-light wording.*

### S31 · beats 256–264 · take 4 (resumed)

```text
Image 1 is the character sheet: animate exactly this fox goddess (ice-blue hair in braided buns with long side strands, tall blue fox ears with black tips, crimson eyes, off-shoulder black and crimson dress with translucent ice-blue layered skirt panels, red fur-trimmed half sleeves, silver star ornaments, bare feet in silver sandals, one huge ice-blue fox tail fading to a black tip with silver star charms). Image 2 is the location and the art style: this dark dream void full of swirling fire and embers, premium Chinese 2D anime game cutscene art. The music turns heavy and dark at 116 BPM; she moves on the beat, weighed down, hesitant and anguished. Action, in order over 5 seconds: (0-1.5s) A small ornate box made of glowing embers floats down in front of her; (1.5-3.5s) she leans close, wide-eyed, the flame reflected in her eyes; (3.5-5s) she slowly lifts both hands toward it. Camera: Slow push-in from medium to close-up on her face lit by the warm firelight. Hair, sheer skirt panels, sleeves and tail move with soft realistic cloth and fur physics. Fully 2D hand-drawn anime, cel shading with painterly light, clean line art, consistent character design, no 3D render look, no morphing, no extra limbs.
```

### S32 · beats 264–272 · take 4 (resumed)

```text
Image 1 is the character sheet: animate exactly this fox goddess (ice-blue hair in braided buns with long side strands, tall blue fox ears with black tips, crimson eyes, off-shoulder black and crimson dress with translucent ice-blue layered skirt panels, red fur-trimmed half sleeves, silver star ornaments, bare feet in silver sandals, one huge ice-blue fox tail fading to a black tip with silver star charms). Image 2 is the location and the art style: this dark dream void full of swirling fire and embers, premium Chinese 2D anime game cutscene art. The music swells with passionate strings at 116 BPM; she moves on the beat, fierce, decisive and tragic. Action, in order over 5 seconds: (0-1.5s) She takes the burning box into both hands; (1.5-3s) flames erupt and spiral around her body in ribbons; (3-5s) she plants her feet in a wide powerful stance and lifts her chin, determined, fire roaring around her. Camera: Low angle medium shot, camera slowly circles her as the fire spirals. Hair, sheer skirt panels, sleeves and tail move with soft realistic cloth and fur physics. Fully 2D hand-drawn anime, cel shading with painterly light, clean line art, consistent character design, no 3D render look, no morphing, no extra limbs.
```

### S33 · beats 272–280 · take 6

```text
Image 1 is the character sheet: animate exactly this fox goddess (ice-blue hair in braided buns with long side strands, tall blue fox ears with black tips, crimson eyes, off-shoulder black and crimson dress with translucent ice-blue layered skirt panels, red fur-trimmed half sleeves, silver star ornaments, bare feet in silver sandals, one huge ice-blue fox tail fading to a black tip with silver star charms). Image 2 is the location and the art style: this dark dream void full of swirling fire and embers, premium Chinese 2D anime game cutscene art. The music swells with passionate strings at 116 BPM; she moves on the beat, fierce, decisive and tragic. Action, in order over 5 seconds: (0-5s) she whirls in big powerful spinning turns, traveling across the frame, the burning box held high above her head, flames trailing behind it in huge spirals, her tail and sleeves whipping around her, sparks flying. Camera: Dynamic orbit around her at waist height, fast. Hair, sheer skirt panels, sleeves and tail move with soft realistic cloth and fur physics. Fully 2D hand-drawn anime, cel shading with painterly light, clean line art, consistent character design, no 3D render look, no morphing, no extra limbs.
```

### S34 · beats 280–288 · take 4 (resumed)

```text
Image 1 is the character sheet: animate exactly this fox goddess (ice-blue hair in braided buns with long side strands, tall blue fox ears with black tips, crimson eyes, off-shoulder black and crimson dress with translucent ice-blue layered skirt panels, red fur-trimmed half sleeves, silver star ornaments, bare feet in silver sandals, one huge ice-blue fox tail fading to a black tip with silver star charms). Image 2 is the location and the art style: this dark dream void full of swirling fire and embers, premium Chinese 2D anime game cutscene art. The music swells with passionate strings at 116 BPM; she moves on the beat, fierce, decisive and tragic. Action, in order over 5 seconds: (0-2s) She slowly raises the burning box overhead toward the faint moon; (2-3.5s) her arms extend fully, trembling with effort; (3.5-5s) the box flares into a blinding brilliant light that floods the scene. Camera: Extreme low angle from below looking up at her and the moon, slow push-in. Hair, sheer skirt panels, sleeves and tail move with soft realistic cloth and fur physics. Fully 2D hand-drawn anime, cel shading with painterly light, clean line art, consistent character design, no 3D render look, no morphing, no extra limbs.
```

### S35 · beats 288–296 · take 6

```text
Image 1 is the character sheet: animate exactly this fox goddess (ice-blue hair in braided buns with long side strands, tall blue fox ears with black tips, crimson eyes, off-shoulder black and crimson dress with translucent ice-blue layered skirt panels, red fur-trimmed half sleeves, silver star ornaments, bare feet in silver sandals, one huge ice-blue fox tail fading to a black tip with silver star charms). Image 2 is the location and the art style: this dark dream void full of swirling fire and embers, premium Chinese 2D anime game cutscene art. Audio 1 is the song for this moment: she sings this vocal line with accurate lip sync, mouth shapes matching the words and rhythm. The music swells with passionate strings at 116 BPM; she moves on the beat, fierce, decisive and tragic. Action, in order over 5 seconds: (0-1.5s) she drops to her knees singing through tears; (1.5-3.5s) the burning box crumbles into glowing embers in her cupped hands; (3.5-5s) the embers drift up past her face and she bows her head, shoulders shaking. Camera: High angle close-medium shot slowly descending to her face. Hair, sheer skirt panels, sleeves and tail move with soft realistic cloth and fur physics. Fully 2D hand-drawn anime, cel shading with painterly light, clean line art, consistent character design, no 3D render look, no morphing, no extra limbs.
```

### S36 · beats 296–304 · take 11

```text
Image 1 is the character sheet: animate exactly this fox goddess (ice-blue hair in braided buns with long side strands, tall blue fox ears with black tips, crimson eyes, off-shoulder black and crimson dress with translucent ice-blue layered skirt panels, red fur-trimmed half sleeves, silver star ornaments, bare feet in silver sandals, one huge ice-blue fox tail fading to a black tip with silver star charms). Image 2 is the location and the art style: this surreal dream realm of floating palace fragments and rivers of moonlight, premium Chinese 2D anime game cutscene art. The music soars to its climax at 116 BPM; she moves on the beat, expansive, luminous and liberated. Action, in order over 5 seconds: (0-1s) kneeling, she is bound by golden chains of light with a huge glowing moon seal pressing down above her; (1-2s) the chains and the seal shatter into golden light fragments that fly outward; (2-5s) she leaps up from the ground in a burst of white light, spinning, arms flung wide, hair, sleeves and tail blasting outward, free. She wears no crown, no tiara and no headwear of any kind; her head shows only her own hair, fox ears and hairpins. Camera: Starts close, pulls back fast to a wide shot as the light bursts. Hair, sheer skirt panels, sleeves and tail move with soft realistic cloth and fur physics. Fully 2D hand-drawn anime, cel shading with painterly light, clean line art, consistent character design, no 3D render look, no morphing, no extra limbs.
```

### S37 · beats 304–312 · take 6

```text
Image 1 is the character sheet: animate exactly this fox goddess (ice-blue hair in braided buns with long side strands, tall blue fox ears with black tips, crimson eyes, off-shoulder black and crimson dress with translucent ice-blue layered skirt panels, red fur-trimmed half sleeves, silver star ornaments, bare feet in silver sandals, one huge ice-blue fox tail fading to a black tip with silver star charms). Image 2 is the location and the art style: this surreal dream realm of floating palace fragments and rivers of moonlight, premium Chinese 2D anime game cutscene art. Audio 1 is the song for this moment: she sings this vocal line with accurate lip sync, mouth shapes matching the words and rhythm. The music soars to its climax at 116 BPM; she moves on the beat, expansive, luminous and liberated. Action, in order over 5 seconds: (0-1.5s) Extreme close-up of her crimson eyes reflecting the full moon; (1.5-5s) she sings with calm resolve, lips moving with the words, as her hands frame her face and the camera reveals her serene expression. Camera: Starts on an extreme close-up of the eyes, slowly pulls back to a close-up. Hair, sheer skirt panels, sleeves and tail move with soft realistic cloth and fur physics. Fully 2D hand-drawn anime, cel shading with painterly light, clean line art, consistent character design, no 3D render look, no morphing, no extra limbs.
```

### S38 · beats 312–320 · take 8

```text
Image 1 is the character sheet: animate exactly this fox goddess (ice-blue hair in braided buns with long side strands, tall blue fox ears with black tips, crimson eyes, off-shoulder black and crimson dress with translucent ice-blue layered skirt panels, red fur-trimmed half sleeves, silver star ornaments, bare feet in silver sandals, one huge ice-blue fox tail fading to a black tip with silver star charms). Image 2 is the location and the art style: this sky above a sea of moonlit clouds full of drifting sky lanterns, premium Chinese 2D anime game cutscene art. The music soars to its climax at 116 BPM; she moves on the beat, expansive, luminous and liberated. Action, in order over 5 seconds: (0-2s) she is already in the center of the frame, swimming forward through the clouds, sleeves streaming; (2-3.5s) she rolls onto her back and drifts, looking down at the city lights far below; (3.5-5s) she spins upright and places a hand over her heart, smiling. Camera: Slow crane from beside her down past her toward the city lights below. Hair, sheer skirt panels, sleeves and tail move with soft realistic cloth and fur physics. Fully 2D hand-drawn anime, cel shading with painterly light, clean line art, consistent character design, no 3D render look, no morphing, no extra limbs.
```

### S39 · beats 320–328 · take 6

```text
Image 1 is the character sheet: animate exactly this fox goddess (ice-blue hair in braided buns with long side strands, tall blue fox ears with black tips, crimson eyes, off-shoulder black and crimson dress with translucent ice-blue layered skirt panels, red fur-trimmed half sleeves, silver star ornaments, bare feet in silver sandals, one huge ice-blue fox tail fading to a black tip with silver star charms). Image 2 is the location and the art style: this surreal dream realm of floating palace fragments and rivers of moonlight, premium Chinese 2D anime game cutscene art. The music soars to its climax at 116 BPM; she moves on the beat, expansive, luminous and liberated. Action, in order over 5 seconds: (0-1.5s) she faces a translucent glowing white version of herself made of moonlight; (1.5-5s) the two dance energetically in perfect mirror symmetry, spinning and circling around each other, arms sweeping in big arcs in unison. Camera: Wide side profile two-shot, slow lateral track. Hair, sheer skirt panels, sleeves and tail move with soft realistic cloth and fur physics. Fully 2D hand-drawn anime, cel shading with painterly light, clean line art, consistent character design, no 3D render look, no morphing, no extra limbs.
```

### S40 · beats 328–336 · take 6

```text
Image 1 is the character sheet: animate exactly this fox goddess (ice-blue hair in braided buns with long side strands, tall blue fox ears with black tips, crimson eyes, off-shoulder black and crimson dress with translucent ice-blue layered skirt panels, red fur-trimmed half sleeves, silver star ornaments, bare feet in silver sandals, one huge ice-blue fox tail fading to a black tip with silver star charms). Image 2 is the location and the art style: this surreal dream realm of floating palace fragments and rivers of moonlight, premium Chinese 2D anime game cutscene art. The music soars to its climax at 116 BPM; she moves on the beat, expansive, luminous and liberated. Action, in order over 5 seconds: (0-1.5s) she and her glowing moonlight self rush toward each other; (1.5-3s) they press their palms together; (3-5s) the glowing self bursts into streams of light that pour into her chest, and she arches back, eyes shining. Camera: Medium two-shot pushing in to their joined hands, then to her face. Hair, sheer skirt panels, sleeves and tail move with soft realistic cloth and fur physics. Fully 2D hand-drawn anime, cel shading with painterly light, clean line art, consistent character design, no 3D render look, no morphing, no extra limbs.
```

### S41 · beats 336–344 · take 6

```text
Image 1 is the character sheet: animate exactly this fox goddess (ice-blue hair in braided buns with long side strands, tall blue fox ears with black tips, crimson eyes, off-shoulder black and crimson dress with translucent ice-blue layered skirt panels, red fur-trimmed half sleeves, silver star ornaments, bare feet in silver sandals, one huge ice-blue fox tail fading to a black tip with silver star charms). Image 2 is the location and the art style: this surreal dream realm of floating palace fragments and rivers of moonlight, premium Chinese 2D anime game cutscene art. The music soars to its climax at 116 BPM; she moves on the beat, expansive, luminous and liberated. Action, in order over 5 seconds: (0-2s) she leaps and spins upward off the ground through a spiral of moonlight and petals; (2-3.5s) she keeps rising and spinning faster, sleeves and tail blazing with silver light; (3.5-5s) she throws her arms wide open in triumph at the top. Camera: Rising spiral camera move around her, ending on a wide heroic shot. Hair, sheer skirt panels, sleeves and tail move with soft realistic cloth and fur physics. Fully 2D hand-drawn anime, cel shading with painterly light, clean line art, consistent character design, no 3D render look, no morphing, no extra limbs.
```

### S43 · beats 356–364 · take 6

```text
Image 1 is the character sheet: animate exactly this fox goddess (ice-blue hair in braided buns with long side strands, tall blue fox ears with black tips, crimson eyes, off-shoulder black and crimson dress with translucent ice-blue layered skirt panels, red fur-trimmed half sleeves, silver star ornaments, bare feet in silver sandals, one huge ice-blue fox tail fading to a black tip with silver star charms). Image 2 is the location and the art style: this lantern-lined festival street at night, premium Chinese 2D anime game cutscene art. The music is warm and nostalgic at 116 BPM; she moves on the beat, gentle, joyful and at peace. Action, in order over 5 seconds: (0-5s) she skips and dances down the busy festival street toward the camera, spinning once, smiling warmly, swinging the hanging lanterns with her fingertips as she passes, petals swirling around her. Camera: Smooth front tracking shot walking backward in front of her. Hair, sheer skirt panels, sleeves and tail move with soft realistic cloth and fur physics. Fully 2D hand-drawn anime, cel shading with painterly light, clean line art, consistent character design, no 3D render look, no morphing, no extra limbs.
```

### S44 · beats 364–372 · take 6

```text
Image 1 is the character sheet: animate exactly this fox goddess (ice-blue hair in braided buns with long side strands, tall blue fox ears with black tips, crimson eyes, off-shoulder black and crimson dress with translucent ice-blue layered skirt panels, red fur-trimmed half sleeves, silver star ornaments, bare feet in silver sandals, one huge ice-blue fox tail fading to a black tip with silver star charms). Image 2 is the location and the art style: this festival riverbank with floating river lanterns and an arched bridge, premium Chinese 2D anime game cutscene art. The music is warm and nostalgic at 116 BPM; she moves on the beat, gentle, joyful and at peace. Action, in order over 5 seconds: (0-5s) she sprints joyfully along the riverbank chasing the moon's reflection, laughing, leaping over the floating lanterns in big bounding strides, sleeves and tail flying behind her. Camera: Side tracking shot running with her, the moon racing in the background. Hair, sheer skirt panels, sleeves and tail move with soft realistic cloth and fur physics. Fully 2D hand-drawn anime, cel shading with painterly light, clean line art, consistent character design, no 3D render look, no morphing, no extra limbs.
```

### S45 · beats 372–380 · take 6

```text
Image 1 is the character sheet: animate exactly this fox goddess (ice-blue hair in braided buns with long side strands, tall blue fox ears with black tips, crimson eyes, off-shoulder black and crimson dress with translucent ice-blue layered skirt panels, red fur-trimmed half sleeves, silver star ornaments, bare feet in silver sandals, one huge ice-blue fox tail fading to a black tip with silver star charms). Image 2 is the location and the art style: this festival riverbank with floating river lanterns and an arched bridge, premium Chinese 2D anime game cutscene art. The music is warm and nostalgic at 116 BPM; she moves on the beat, gentle, joyful and at peace. Action, in order over 5 seconds: (0-1.5s) she runs to the river edge holding a paper sky lantern; (1.5-3s) she spins and tosses it upward with both hands; (3-5s) it rises toward the moon and she jumps once with joy, waving after it. Camera: Medium shot that tilts up following the lantern to the moon. Hair, sheer skirt panels, sleeves and tail move with soft realistic cloth and fur physics. Fully 2D hand-drawn anime, cel shading with painterly light, clean line art, consistent character design, no 3D render look, no morphing, no extra limbs.
```

### S46 · beats 380–388 · take 6

```text
Image 1 is the character sheet: animate exactly this fox goddess (ice-blue hair in braided buns with long side strands, tall blue fox ears with black tips, crimson eyes, off-shoulder black and crimson dress with translucent ice-blue layered skirt panels, red fur-trimmed half sleeves, silver star ornaments, bare feet in silver sandals, one huge ice-blue fox tail fading to a black tip with silver star charms). Image 2 is the location and the art style: this festival riverbank with floating river lanterns and an arched bridge, premium Chinese 2D anime game cutscene art. Audio 1 is the song for this moment: she sings this vocal line with accurate lip sync, mouth shapes matching the words and rhythm. The music is warm and nostalgic at 116 BPM; she moves on the beat, gentle, joyful and at peace. Action, in order over 5 seconds: (0-5s) Close-up: she sings gently with a warm smile, lips moving with the words, hand over her heart, swaying slightly, lantern light glowing on her face, ears relaxed. Camera: Slow push-in to a close-up, warm bokeh. Hair, sheer skirt panels, sleeves and tail move with soft realistic cloth and fur physics. Fully 2D hand-drawn anime, cel shading with painterly light, clean line art, consistent character design, no 3D render look, no morphing, no extra limbs.
```

### S47 · beats 388–408 · take S03 take 2, reused

```text
Image 1 is the character sheet: animate exactly this fox goddess (ice-blue hair in braided buns with long side strands, tall blue fox ears with black tips, crimson eyes, off-shoulder black and crimson dress with translucent ice-blue layered skirt panels, red fur-trimmed half sleeves, silver star ornaments, bare feet in silver sandals, one huge ice-blue fox tail fading to a black tip with silver star charms). Image 2 is the location and the art style. The music is a bright, flowing 116 BPM orchestral pop with guzheng and strings; she moves on the beat, light and playful like a fox spirit. She is clearly visible in the shot from the very first frame to the last, never cropped out of frame. Action: She stands on the ridge and sways her hips and shoulders clearly from side to side with the music, arms lifting and drifting like floating lanterns; she reaches out and taps a passing sky lantern with a fingertip so it spins away, then twirls once, her big tail swinging in rhythm. Camera: Medium shot, slow arc around her from the side to the front, lanterns drifting through the foreground.  Hair, sheer skirt panels, sleeves and tail move with soft realistic cloth and fur physics and follow-through. Fully 2D hand-drawn anime, cel shading with painterly light, clean line art, consistent character design, no text, no watermark, no 3D render look, no morphing, no extra limbs.
```

## Lessons that shaped these prompts

- Gentle one-line actions (sway, point, hold a light) made Wan 3.0 hold the reference pose almost motionless. Time-coded choreography ("Action, in order over N seconds: (0-1.5s) …") with big locomotion such as running, leaping and spinning produced real motion.
- Describing the location in words ("Image 2 is the location and the art style: this …") worked better than only pointing at image 2.
- The Act II "crown" is symbolic: power and duty that were never hers. It is shown as a moon seal, chains of light and a ceremonial mantle, and the prompts state *no crown, no tiara, no headwear*.
- Close-ups that should sing pass the matching song segment as an audio reference (Audio 1).