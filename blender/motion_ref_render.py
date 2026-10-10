# Pose-only motion reference: flat-shaded figure on dark grey, tighter lens. Usage: -- out.mp4 lens
import bpy, sys
a = sys.argv[sys.argv.index('--') + 1:]
scn = bpy.context.scene
cam = scn.camera
ad = cam.data.animation_data
if ad and ad.action:
    from bpy_extras import anim_utils
    cb = anim_utils.action_get_channelbag_for_slot(ad.action, ad.action_slot)
    for fc in list(cb.fcurves):
        if fc.data_path == 'lens':
            for k in fc.keyframe_points: k.co.y = float(a[1]); k.handle_left.y = k.co.y; k.handle_right.y = k.co.y
for o in scn.objects:
    if o.type in ('MESH',) and not (o.name.startswith('Hsin_body') or o.name == 'Floor' or o.name == 'StageRing'):
        o.hide_render = True
scn.render.engine = 'BLENDER_WORKBENCH'
sh = scn.display.shading
sh.light = 'STUDIO'; sh.color_type = 'MATERIAL'; sh.show_shadows = True
scn.world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.05, 0.05, 0.07, 1)
sh.background_type = 'WORLD' if hasattr(sh, 'background_type') else None
r = scn.render
r.resolution_x, r.resolution_y, r.resolution_percentage = 854, 480, 100
r.image_settings.media_type = 'VIDEO'; r.image_settings.file_format = 'FFMPEG'
r.ffmpeg.format = 'MPEG4'; r.ffmpeg.codec = 'H264'; r.ffmpeg.audio_codec = 'NONE'
r.filepath = a[0]
bpy.ops.render.render(animation=True)
