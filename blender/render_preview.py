# Render the full MV with music: Blender -b hsin_dance.blend -P render_preview.py -- out.mp4 [height e.g. 720] [samples]
import bpy, sys
a = sys.argv[sys.argv.index('--') + 1:]
scn = bpy.context.scene; r = scn.render
h = int(a[1]) if len(a) > 1 else 720
r.resolution_x, r.resolution_y, r.resolution_percentage = (h * 16 // 9) // 2 * 2, h, 100
scn.eevee.taa_render_samples = int(a[2]) if len(a) > 2 else 16
r.image_settings.media_type = 'VIDEO'
r.image_settings.file_format = 'FFMPEG'
r.ffmpeg.format = 'MPEG4'; r.ffmpeg.codec = 'H264'; r.ffmpeg.constant_rate_factor = 'HIGH'
r.ffmpeg.audio_codec = 'AAC'; r.ffmpeg.audio_bitrate = 256; r.ffmpeg.audio_channels = 'STEREO'
r.filepath = a[0]
bpy.ops.render.render(animation=True)
