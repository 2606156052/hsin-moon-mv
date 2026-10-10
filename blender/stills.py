import bpy, sys, os
sys.path.insert(0, os.path.dirname(bpy.data.filepath))
import hsin_engine as E
argv = sys.argv[sys.argv.index('--')+1:]
outdir = argv[0]; beats = [float(x) for x in argv[1].split(',')]
pct = int(argv[2]) if len(argv) > 2 else 33
scn = bpy.context.scene
scn.render.resolution_percentage = pct
scn.eevee.taa_render_samples = 8
os.makedirs(outdir, exist_ok=True)
for b in beats:
    f = int(round(E.FR(b)))
    scn.frame_set(f)
    scn.render.filepath = os.path.join(outdir, f'b{b:06.1f}.png')
    bpy.ops.render.render(write_still=True)
g = bpy.types.CompositorNodeGlare
n = bpy.data.node_groups.new('t','CompositorNodeTree').nodes.new('CompositorNodeGlare')
print("GLARE", [(i.name, getattr(i,'default_value',None)) for i in n.inputs])
