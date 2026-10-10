"""Hsin (心) base-mesh fox-girl rig + stage for the 'Ode to Hsin and Moon' dance.

Character faces -Y in rest; her left side is +X. Units are metres, 1.60 m tall.
Legs are IK to world-space foot targets (so planted feet never slide),
arms are IK to hand targets that live in the chest frame.
"""
import bpy, bmesh, math, random
from mathutils import Vector, Matrix, Quaternion, Euler

# ---------------------------------------------------------------- skeleton
TAIL_ELEV = [-38, -22, -6, 10, 24, 34, 40]          # tail segment pitch (deg) – droop then sweep up
TAIL_LEN = 0.11
TAIL_RAD = [0.05, 0.075, 0.095, 0.105, 0.10, 0.085, 0.055]


def tail_points():
    p = Vector((0, 0.085, 0.95))
    pts = [p.copy()]
    for e in TAIL_ELEV:
        a = math.radians(e)
        p = p + Vector((0, math.cos(a), math.sin(a))) * TAIL_LEN
        pts.append(p.copy())
    return pts


def bone_table():
    B = [
        ('hips', (0, 0, 0.92), (0, 0, 1.02), None, True),
        ('spine', (0, 0, 1.02), (0, 0, 1.15), 'hips', True),
        ('chest', (0, 0, 1.15), (0, 0, 1.33), 'spine', True),
        ('neck', (0, 0, 1.33), (0, 0, 1.41), 'chest', True),
        ('head', (0, 0, 1.41), (0, 0, 1.62), 'neck', True),
    ]
    for s, sx in (('L', 1), ('R', -1)):
        B += [
            (f'shoulder.{s}', (0.03 * sx, 0, 1.31), (0.15 * sx, 0, 1.31), 'chest', True),
            (f'upper_arm.{s}', (0.15 * sx, 0, 1.31), (0.41 * sx, 0, 1.31), f'shoulder.{s}', True),
            (f'forearm.{s}', (0.41 * sx, 0, 1.31), (0.65 * sx, 0, 1.31), f'upper_arm.{s}', True),
            (f'hand.{s}', (0.65 * sx, 0, 1.31), (0.74 * sx, 0, 1.31), f'forearm.{s}', True),
            (f'thigh.{s}', (0.09 * sx, 0, 0.92), (0.09 * sx, -0.012, 0.50), 'hips', True),
            (f'shin.{s}', (0.09 * sx, -0.012, 0.50), (0.09 * sx, 0, 0.08), f'thigh.{s}', True),
            (f'foot.{s}', (0.09 * sx, 0, 0.08), (0.09 * sx, -0.12, 0.02), f'shin.{s}', True),
            (f'ear.{s}', (0.055 * sx, 0.0, 1.585), (0.10 * sx, 0.015, 1.705), 'head', True),
            (f'ik_hand.{s}', (0.65 * sx, 0, 1.31), (0.65 * sx, 0.08, 1.31), 'chest', False),
            (f'pole_arm.{s}', (0.41 * sx, 0.30, 1.10), (0.41 * sx, 0.36, 1.10), 'chest', False),
        ]
    tp = tail_points()
    for i in range(7):
        B.append((f'tail.{i}', tuple(tp[i]), tuple(tp[i + 1]), 'hips' if i == 0 else f'tail.{i-1}', True))
    return B


CONNECTED = {'forearm.L', 'forearm.R', 'hand.L', 'hand.R', 'shin.L', 'shin.R', 'foot.L', 'foot.R',
             'spine', 'chest', 'neck', 'head'} | {f'tail.{i}' for i in range(1, 7)}

SHOULDER = {'L': Vector((0.15, 0, 1.31)), 'R': Vector((-0.15, 0, 1.31))}


# ---------------------------------------------------------------- materials
def _sock(node, ident, out=False):
    for s in (node.outputs if out else node.inputs):
        if s.identifier == ident:
            return s
    raise KeyError(ident)


def cel_mat(name, color, shade=0.42, rim=(0.6, 0.75, 1.0), rim_str=0.35, emit=0.0):
    """Two-tone anime cel shader (Shader-to-RGB) with a cool moon rim."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    N = nt.nodes.new
    out = N('ShaderNodeOutputMaterial')
    diff = N('ShaderNodeBsdfDiffuse')
    s2r = N('ShaderNodeShaderToRGB')
    ramp = N('ShaderNodeValToRGB')
    ramp.color_ramp.interpolation = 'CONSTANT'
    e = ramp.color_ramp.elements
    e[0].position = 0.0
    e[0].color = (shade * 0.85, shade * 0.85, shade * 1.05, 1)
    e[1].position = 0.12
    e[1].color = (0.82, 0.82, 0.86, 1)
    e3 = e.new(0.42)
    e3.color = (1, 1, 1, 1)
    base = N('ShaderNodeRGB')
    base.outputs[0].default_value = (*color, 1)
    mul = N('ShaderNodeMix')
    mul.data_type = 'RGBA'
    mul.blend_type = 'MULTIPLY'
    _sock(mul, 'Factor_Float').default_value = 1.0
    lw = N('ShaderNodeLayerWeight')
    lw.inputs['Blend'].default_value = 0.25
    rr = N('ShaderNodeValToRGB')
    rr.color_ramp.interpolation = 'CONSTANT'
    rr.color_ramp.elements[0].color = (0, 0, 0, 1)
    rr.color_ramp.elements[1].position = 0.72
    rr.color_ramp.elements[1].color = (*[c * rim_str for c in rim], 1)
    add = N('ShaderNodeMix')
    add.data_type = 'RGBA'
    add.blend_type = 'ADD'
    _sock(add, 'Factor_Float').default_value = 1.0
    em = N('ShaderNodeEmission')
    em.inputs['Strength'].default_value = 1.0 + emit
    L = nt.links.new
    L(diff.outputs[0], s2r.inputs[0])
    L(s2r.outputs['Color'], ramp.inputs['Fac'])
    L(base.outputs[0], _sock(mul, 'A_Color'))
    L(ramp.outputs['Color'], _sock(mul, 'B_Color'))
    L(lw.outputs['Facing'], rr.inputs['Fac'])
    L(_sock(mul, 'Result_Color', True), _sock(add, 'A_Color'))
    L(rr.outputs['Color'], _sock(add, 'B_Color'))
    L(_sock(add, 'Result_Color', True), em.inputs['Color'])
    L(em.outputs[0], out.inputs['Surface'])
    return m


def emit_mat(name, color, strength):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    em = nt.nodes.new('ShaderNodeEmission')
    em.inputs['Color'].default_value = (*color, 1)
    em.inputs['Strength'].default_value = strength
    nt.links.new(em.outputs[0], out.inputs['Surface'])
    return m


def outline_mat():
    m = emit_mat('Outline', (0.035, 0.03, 0.06), 1.0)
    m.use_backface_culling = True
    return m


def ghost_mat(name='Ghost', color=(0.55, 0.85, 1.0)):
    """Translucent glowing material for the true-self / mirror double. Keyed via the 'alpha'/'glow' Value nodes."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    m.surface_render_method = 'BLENDED'
    m.use_backface_culling = True
    nt = m.node_tree
    nt.nodes.clear()
    N = nt.nodes.new
    out = N('ShaderNodeOutputMaterial')
    lw = N('ShaderNodeLayerWeight')
    lw.inputs['Blend'].default_value = 0.45
    col = N('ShaderNodeRGB')
    col.name = 'tint'
    col.outputs[0].default_value = (*color, 1)
    glow = N('ShaderNodeValue')
    glow.name = 'glow'
    glow.outputs[0].default_value = 2.0
    alpha = N('ShaderNodeValue')
    alpha.name = 'alpha'
    alpha.outputs[0].default_value = 0.0
    mth = N('ShaderNodeMath')
    mth.operation = 'MULTIPLY_ADD'      # facing*1.2 + 0.25  -> edges brighter
    mth.inputs[1].default_value = 1.2
    mth.inputs[2].default_value = 0.25
    m2 = N('ShaderNodeMath')
    m2.operation = 'MULTIPLY'
    em = N('ShaderNodeEmission')
    tr = N('ShaderNodeBsdfTransparent')
    mix = N('ShaderNodeMixShader')
    am = N('ShaderNodeMath')
    am.operation = 'MULTIPLY'
    L = nt.links.new
    L(lw.outputs['Facing'], mth.inputs[0])
    L(mth.outputs[0], m2.inputs[0])
    L(glow.outputs[0], m2.inputs[1])
    L(col.outputs[0], em.inputs['Color'])
    L(m2.outputs[0], em.inputs['Strength'])
    L(alpha.outputs[0], am.inputs[0])
    L(mth.outputs[0], am.inputs[1])
    L(am.outputs[0], mix.inputs['Fac'])
    L(tr.outputs[0], mix.inputs[1])
    L(em.outputs[0], mix.inputs[2])
    L(mix.outputs[0], out.inputs['Surface'])
    return m


def make_materials():
    M = {}
    M['skin'] = cel_mat('Skin', (1.0, 0.86, 0.80), shade=0.55, rim_str=0.25)
    M['hair'] = cel_mat('Hair', (0.86, 0.87, 0.97), shade=0.5, rim_str=0.5)
    M['robe'] = cel_mat('Robe', (0.62, 0.05, 0.08), shade=0.38)
    M['white'] = cel_mat('RobeWhite', (0.93, 0.93, 0.97), shade=0.5)
    M['gold'] = cel_mat('Gold', (1.0, 0.72, 0.25), shade=0.45, rim=(1, 0.9, 0.6), rim_str=0.6)
    M['eye'] = emit_mat('Eye', (0.55, 0.12, 0.05), 0.9)
    M['mark'] = emit_mat('Mark', (1.0, 0.15, 0.1), 4.0)
    M['earin'] = cel_mat('EarInner', (1.0, 0.62, 0.66), shade=0.55)
    M['boot'] = cel_mat('Boot', (0.45, 0.04, 0.06), shade=0.35)
    M['tail'] = cel_mat('Tail', (0.96, 0.95, 0.98), shade=0.55, rim_str=0.55)
    M['tailtip'] = cel_mat('TailTip', (1.0, 0.55, 0.18), shade=0.5, emit=0.6)
    M['outline'] = outline_mat()
    return M


MAT_ORDER = ['skin', 'hair', 'robe', 'white', 'gold', 'eye', 'mark', 'earin', 'boot', 'tail', 'tailtip', 'outline']


# ---------------------------------------------------------------- mesh builder
class MB:
    def __init__(self, groups):
        self.bm = bmesh.new()
        self.dl = self.bm.verts.layers.deform.verify()
        self.gi = {g: i for i, g in enumerate(groups)}

    def _finish(self, verts, mat, weights):
        mi = MAT_ORDER.index(mat)
        vs = set(verts)
        for f in {f for v in verts for f in v.link_faces}:
            f.material_index = mi
            f.smooth = True
        for v in vs:
            w = weights(v.co) if callable(weights) else weights
            for g, val in w.items():
                if val > 0:
                    v[self.dl][self.gi[g]] = val

    def ellipsoid(self, c, r, mat, w, axis=None, seg=(18, 12)):
        """Ellipsoid centre c, radii r=(rx, ry_along_axis, rz). axis rotates local +Y onto it."""
        R = Matrix.Identity(3)
        if axis is not None:
            R = Vector((0, 1, 0)).rotation_difference(Vector(axis).normalized()).to_matrix()
        M = Matrix.Translation(c) @ R.to_4x4() @ Matrix.Diagonal((*r, 1))
        res = bmesh.ops.create_uvsphere(self.bm, u_segments=seg[0], v_segments=seg[1], radius=1.0, matrix=M)
        self._finish(res['verts'], mat, w)

    def capsule(self, p0, p1, r, mat, w, over=0.6):
        p0, p1 = Vector(p0), Vector(p1)
        d = p1 - p0
        self.ellipsoid((p0 + p1) / 2, (r, d.length / 2 + r * over, r), mat, w, axis=d)

    def cone(self, p0, p1, r0, r1, mat, w, seg=20, squash=1.0, caps=False):
        p0, p1 = Vector(p0), Vector(p1)
        d = p1 - p0
        R = Vector((0, 0, 1)).rotation_difference(d.normalized()).to_matrix().to_4x4()
        M = Matrix.Translation((p0 + p1) / 2) @ R @ Matrix.Diagonal((1, squash, 1, 1))
        res = bmesh.ops.create_cone(self.bm, cap_ends=caps, cap_tris=False, segments=seg,
                                    radius1=r0, radius2=r1, depth=d.length, matrix=M)
        self._finish(res['verts'], mat, w)

    def to_mesh(self, me):
        self.bm.to_mesh(me)
        self.bm.free()


def build_body_mesh(name, groups):
    mb = MB(groups)
    E, C = mb.ellipsoid, mb.capsule
    one = lambda b: {b: 1.0}
    # head
    E((0, 0.005, 1.505), (0.098, 0.105, 0.112), 'skin', one('head'))
    E((0, -0.022, 1.462), (0.074, 0.07, 0.058), 'skin', one('head'))
    E((0, 0.028, 1.535), (0.105, 0.102, 0.112), 'hair', one('head'))
    for x, z, rx in ((0.046, 1.566, 0.036), (-0.046, 1.566, 0.036), (0.0, 1.574, 0.032)):
        E((x, -0.077, z), (rx, 0.022, 0.046), 'hair', one('head'))
    for sx in (1, -1):
        E((0.086 * sx, -0.03, 1.43), (0.022, 0.026, 0.095), 'hair', one('head'))
        E((0.036 * sx, -0.093, 1.497), (0.016, 0.008, 0.022), 'eye', one('head'))
    E((0, -0.101, 1.565), (0.006, 0.004, 0.015), 'mark', one('head'))
    # long back hair bends between head and chest
    E((0, 0.088, 1.35), (0.092, 0.035, 0.21), 'hair',
      lambda co: {'head': min(1, max(0, (co.z - 1.25) / 0.25)), 'chest': 1 - min(1, max(0, (co.z - 1.25) / 0.25))})
    # ears
    for s, sx in (('L', 1), ('R', -1)):
        mb.cone((0.056 * sx, 0.006, 1.585), (0.10 * sx, 0.016, 1.712), 0.038, 0.002, 'hair', one(f'ear.{s}'),
                seg=10, squash=0.42)
        mb.cone((0.058 * sx, -0.006, 1.595), (0.097 * sx, 0.004, 1.69), 0.024, 0.002, 'earin', one(f'ear.{s}'),
                seg=10, squash=0.3)
    # neck / torso
    E((0, 0, 1.37), (0.033, 0.033, 0.06), 'skin', one('neck'))
    E((0, 0, 1.255), (0.115, 0.08, 0.12), 'robe', one('chest'))
    E((0, -0.012, 1.326), (0.078, 0.062, 0.03), 'white', one('chest'))
    E((0, -0.07, 1.25), (0.045, 0.02, 0.07), 'white', one('chest'))
    E((0, 0, 1.11), (0.095, 0.068, 0.08), 'robe', one('spine'))
    E((0, 0, 1.07), (0.106, 0.077, 0.03), 'gold', one('spine'))
    E((0, 0.085, 1.07), (0.07, 0.03, 0.045), 'gold', one('spine'))
    E((0, 0, 0.965), (0.12, 0.085, 0.085), 'robe', one('hips'))

    # skirt: blended to thighs so it follows the legs like cloth
    def skirt_w(co):
        h = min(1, max(0, (1.0 - co.z) / 0.42)) ** 1.5
        wl = max(0, min(1, co.x / 0.15)) * 0.75 * h
        wr = max(0, min(1, -co.x / 0.15)) * 0.75 * h
        return {'hips': 1 - wl - wr, 'thigh.L': wl, 'thigh.R': wr}
    mb.cone((0, 0, 1.04), (0, 0, 0.60), 0.112, 0.30, 'robe', skirt_w, seg=28)
    mb.cone((0, 0, 0.62), (0, 0, 0.57), 0.29, 0.315, 'white', skirt_w, seg=28)
    mb.cone((0, 0, 1.00), (0, 0, 0.66), 0.105, 0.24, 'white', skirt_w, seg=28)   # underskirt
    for s, sx in (('L', 1), ('R', -1)):
        X = lambda v: (v[0] * sx, v[1], v[2])
        E(X((0.15, 0, 1.305)), (0.052, 0.05, 0.05), 'white', one(f'shoulder.{s}'))
        C(X((0.16, 0, 1.31)), X((0.40, 0, 1.31)), 0.043, 'white', one(f'upper_arm.{s}'))
        E(X((0.41, 0, 1.31)), (0.037, 0.037, 0.037), 'white', {f'upper_arm.{s}': 0.5, f'forearm.{s}': 0.5})
        C(X((0.42, 0, 1.31)), X((0.64, 0, 1.31)), 0.031, 'skin', one(f'forearm.{s}'))
        # wide hanfu sleeve, droops a little below the forearm
        mb.cone(X((0.43, 0, 1.305)), X((0.63, 0, 1.29)), 0.047, 0.078, 'white', one(f'forearm.{s}'), seg=20, squash=1.0)
        mb.cone(X((0.625, 0, 1.29)), X((0.645, 0, 1.289)), 0.077, 0.082, 'robe', one(f'forearm.{s}'), seg=20)
        E(X((0.70, 0, 1.31)), (0.016, 0.05, 0.03), 'skin', one(f'hand.{s}'), axis=X((1, 0, 0)))
        E(X((0.68, -0.03, 1.305)), (0.01, 0.025, 0.011), 'skin', one(f'hand.{s}'), axis=X((0.6, -0.8, 0)))
        # legs
        C(X((0.09, -0.004, 0.90)), X((0.09, -0.012, 0.52)), 0.062, 'white', one(f'thigh.{s}'), over=0.3)
        E(X((0.09, -0.012, 0.50)), (0.046, 0.046, 0.046), 'white', {f'thigh.{s}': 0.5, f'shin.{s}': 0.5})
        C(X((0.09, -0.01, 0.48)), X((0.09, -0.004, 0.30)), 0.042, 'white', one(f'shin.{s}'), over=0.4)
        C(X((0.09, -0.003, 0.30)), X((0.09, 0, 0.09)), 0.045, 'boot', one(f'shin.{s}'), over=0.3)
        E(X((0.09, -0.055, 0.045)), (0.042, 0.085, 0.036), 'boot', one(f'foot.{s}'), axis=(0, -1, -0.25))
    tp = tail_points()
    for i in range(7):
        C(tp[i], tp[i + 1], TAIL_RAD[i], 'tailtip' if i >= 5 else 'tail', one(f'tail.{i}'), over=0.9)
    me = bpy.data.meshes.new(name)
    mb.to_mesh(me)
    return me


# ---------------------------------------------------------------- rig
def build_actor(prefix, mats=None, ghost=None):
    """Create armature + body + world-space IK targets. Returns dict of objects."""
    scn = bpy.context.scene
    arm_data = bpy.data.armatures.new(prefix + '_rig')
    arm = bpy.data.objects.new(prefix + '_rig', arm_data)
    scn.collection.objects.link(arm)
    arm.show_in_front = True
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode='EDIT')
    ebs = {}
    for name, h, t, parent, deform in bone_table():
        eb = arm_data.edit_bones.new(name)
        eb.head, eb.tail = h, t
        eb.roll = 0
        eb.use_deform = deform
        ebs[name] = eb
    for name, h, t, parent, deform in bone_table():
        if parent:
            ebs[name].parent = ebs[parent]
            ebs[name].use_connect = name in CONNECTED
    bpy.ops.object.mode_set(mode='OBJECT')
    for pb in arm.pose.bones:
        pb.rotation_mode = 'QUATERNION'

    # world-space foot targets & knee poles
    E = {}
    for s in 'LR':
        ft = bpy.data.objects.new(f'{prefix}_foot_ik.{s}', None)
        ft.empty_display_type = 'ARROWS'
        ft.empty_display_size = 0.08
        ft.rotation_mode = 'QUATERNION'
        kp = bpy.data.objects.new(f'{prefix}_knee_pole.{s}', None)
        kp.empty_display_size = 0.04
        for o in (ft, kp):
            scn.collection.objects.link(o)
            o.hide_render = True
        E['foot.' + s], E['pole.' + s] = ft, kp
        ik = arm.pose.bones[f'shin.{s}'].constraints.new('IK')
        ik.target, ik.pole_target, ik.chain_count = ft, kp, 2
        cr = arm.pose.bones[f'foot.{s}'].constraints.new('COPY_ROTATION')
        cr.target = ft
        aik = arm.pose.bones[f'forearm.{s}'].constraints.new('IK')
        aik.target, aik.subtarget = arm, f'ik_hand.{s}'
        aik.pole_target, aik.pole_subtarget = arm, f'pole_arm.{s}'
        aik.chain_count = 2
        aik.use_rotation = False

    groups = [b[0] for b in bone_table() if b[4]]
    me = build_body_mesh(prefix + '_mesh', groups)
    body = bpy.data.objects.new(prefix + '_body', me)
    scn.collection.objects.link(body)
    for g in groups:
        body.vertex_groups.new(name=g)
    # bmesh deform layer indexes map to vertex group order
    if ghost is None:
        for k in MAT_ORDER:
            me.materials.append(mats[k])
    else:
        me.materials.append(ghost)
    body.parent = arm
    mod = body.modifiers.new('Armature', 'ARMATURE')
    mod.object = arm
    if ghost is None:
        sol = body.modifiers.new('Outline', 'SOLIDIFY')
        sol.thickness = -0.007
        sol.use_flip_normals = True
        sol.use_rim = False
        sol.material_offset = 100
        sol.use_quality_normals = True
    return dict(arm=arm, body=body, **E)


def calibrate_poles(A):
    """Pick IK pole angles that make knees/elbows bend toward their pole targets."""
    arm = A['arm']
    vl = bpy.context.view_layer
    mw = arm.matrix_world
    best = {}
    # crouch pose for legs
    arm.pose.bones['hips'].location = (0, 0, 0)
    for s, sx in (('L', 1), ('R', -1)):
        A['foot.' + s].location = (0.09 * sx, -0.05, 0.08)
        A['foot.' + s].rotation_quaternion = arm.data.bones[f'foot.{s}'].matrix_local.to_quaternion()
        A['pole.' + s].location = (0.09 * sx, -0.8, 0.55)
        arm.pose.bones[f'ik_hand.{s}'].location = (-0.30 * sx, -0.25, -0.05)
        arm.pose.bones[f'pole_arm.{s}'].location = (0.1 * sx, 0.1, -0.1)
    arm.pose.bones['hips'].location = (0, 0, 0)
    # hips local axes: Y=up, Z=-Y(global) -> lower hips 0.3 m
    arm.pose.bones['hips'].location = (0, -0.3, 0)
    for s in 'LR':
        for chain, bone, pole in ((f'shin.{s}', f'shin.{s}', ('obj', A['pole.' + s])),
                                  (f'forearm.{s}', f'forearm.{s}', ('bone', f'pole_arm.{s}'))):
            con = arm.pose.bones[chain].constraints['IK']
            scores = []
            for ang in range(-180, 180, 15):
                con.pole_angle = math.radians(ang)
                vl.update()
                joint = mw @ arm.pose.bones[bone].head
                if pole[0] == 'obj':
                    pp = pole[1].matrix_world.translation
                else:
                    pp = mw @ arm.pose.bones[pole[1]].head
                scores.append(((joint - pp).length, ang))
            d, ang = min(scores)
            con.pole_angle = math.radians(ang)
            best[chain] = ang
    for pb in arm.pose.bones:
        pb.location = (0, 0, 0)
        pb.rotation_quaternion = (1, 0, 0, 0)
    return best


# ---------------------------------------------------------------- stage
def add_obj(name, me, mat=None, loc=(0, 0, 0), coll=None):
    o = bpy.data.objects.new(name, me)
    (coll or bpy.context.scene.collection).objects.link(o)
    o.location = loc
    if mat is not None:
        me.materials.append(mat)
    return o


def prim_mesh(kind, **kw):
    bm = bmesh.new()
    if kind == 'sphere':
        bmesh.ops.create_uvsphere(bm, u_segments=kw.get('u', 24), v_segments=kw.get('v', 16), radius=kw.get('r', 1))
    elif kind == 'ico':
        bmesh.ops.create_icosphere(bm, subdivisions=kw.get('sub', 1), radius=kw.get('r', 1))
    elif kind == 'cyl':
        bmesh.ops.create_cone(bm, cap_ends=True, segments=kw.get('seg', 16), radius1=kw['r'], radius2=kw.get('r2', kw['r']),
                              depth=kw['d'])
    elif kind == 'circle':
        bmesh.ops.create_circle(bm, cap_ends=True, segments=kw.get('seg', 64), radius=kw['r'])
    elif kind == 'cube':
        bmesh.ops.create_cube(bm, size=1)
        bmesh.ops.scale(bm, vec=kw.get('s', (1, 1, 1)), verts=bm.verts)
    for f in bm.faces:
        f.smooth = kw.get('smooth', True)
    me = bpy.data.meshes.new(kind)
    bm.to_mesh(me)
    bm.free()
    return me


def build_stage(rng):
    scn = bpy.context.scene
    S = {}
    world = bpy.data.worlds.new('Night')
    scn.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes['Background']
    bg.inputs['Color'].default_value = (0.012, 0.018, 0.045, 1)
    bg.inputs['Strength'].default_value = 1.0
    S['bg'] = bg

    # mirror-like night water floor
    gm = bpy.data.materials.new('Floor')
    gm.use_nodes = True
    p = gm.node_tree.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value = (0.012, 0.016, 0.032, 1)
    p.inputs['Roughness'].default_value = 0.12
    p.inputs['Specular IOR Level'].default_value = 0.6
    add_obj('Floor', prim_mesh('circle', r=90, seg=96), gm)
    # moon-ring stage marking
    ring = bpy.data.meshes.new('ring')
    bm = bmesh.new()
    for r0, r1 in ((3.4, 3.46), (3.62, 3.65), (1.2, 1.22)):
        a = bmesh.ops.create_circle(bm, segments=128, radius=r0)['verts']
        b = bmesh.ops.create_circle(bm, segments=128, radius=r1)['verts']
        for i in range(128):
            bm.faces.new((a[i], a[(i + 1) % 128], b[(i + 1) % 128], b[i]))
    bm.to_mesh(ring)
    bm.free()
    S['ring_mat'] = emit_mat('StageRing', (0.55, 0.7, 1.0), 1.5)
    o = add_obj('StageRing', ring, S['ring_mat'], (0, 0, 0.004))

    # the moon
    S['moon_pos'] = Vector((0, 120, 34))
    S['moon_mat'] = emit_mat('Moon', (1.0, 0.96, 0.86), 7.0)
    add_obj('Moon', prim_mesh('sphere', r=7.5, u=48, v=24), S['moon_mat'], S['moon_pos'])
    halo = emit_mat('MoonHalo', (0.35, 0.45, 0.8), 0.6)
    halo.surface_render_method = 'BLENDED'
    h = add_obj('MoonHalo', prim_mesh('circle', r=16, seg=64), halo, S['moon_pos'] + Vector((0, 1, 0)))
    h.rotation_euler = (math.radians(90), 0, 0)
    # make halo fade radially
    nt = halo.node_tree
    em = nt.nodes['Emission']
    tc = nt.nodes.new('ShaderNodeTexCoord')
    grad = nt.nodes.new('ShaderNodeTexGradient')
    grad.gradient_type = 'SPHERICAL'
    mp = nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (1 / 16, 1 / 16, 1 / 16)
    tr = nt.nodes.new('ShaderNodeBsdfTransparent')
    mx = nt.nodes.new('ShaderNodeMixShader')
    pw = nt.nodes.new('ShaderNodeMath')
    pw.operation = 'POWER'
    pw.inputs[1].default_value = 2.2
    nt.links.new(tc.outputs['Object'], mp.inputs['Vector'])
    nt.links.new(mp.outputs['Vector'], grad.inputs['Vector'])
    nt.links.new(grad.outputs['Fac'], pw.inputs[0])
    nt.links.new(pw.outputs[0], mx.inputs['Fac'])
    nt.links.new(tr.outputs[0], mx.inputs[1])
    nt.links.new(em.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], nt.nodes['Material Output'].inputs['Surface'])

    # stars (one mesh)
    bm = bmesh.new()
    for i in range(420):
        az = rng.uniform(0, 2 * math.pi)
        el = math.radians(rng.uniform(6, 80))
        d = 150
        c = Vector((math.cos(az) * math.cos(el) * d, math.sin(az) * math.cos(el) * d, math.sin(el) * d))
        bmesh.ops.create_icosphere(bm, subdivisions=0, radius=rng.uniform(0.08, 0.28), matrix=Matrix.Translation(c))
    me = bpy.data.meshes.new('stars')
    bm.to_mesh(me)
    bm.free()
    add_obj('Stars', me, emit_mat('Star', (0.8, 0.85, 1.0), 6.0))

    # distant town (人间灯火): houses + warm windows + a pagoda, toward (-25, 35)
    town_c = Vector((-25, 35, 0))
    S['town'] = town_c
    houses = bpy.data.materials.new('House')
    houses.use_nodes = True
    houses.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.02, 0.02, 0.035, 1)
    bm_h, bm_w = bmesh.new(), bmesh.new()
    for i in range(70):
        c = town_c + Vector((rng.gauss(0, 7), rng.gauss(0, 4), 0))
        w, d, hgt = rng.uniform(1, 2.5), rng.uniform(1, 2), rng.uniform(1.2, 3)
        bmesh.ops.create_cube(bm_h, size=1, matrix=Matrix.Translation(c + Vector((0, 0, hgt / 2))) @ Matrix.Diagonal((w, d, hgt, 1)))
        for k in range(rng.randint(1, 3)):
            wc = c + Vector((rng.uniform(-w / 3, w / 3), -d / 2 - 0.02, rng.uniform(0.4, hgt - 0.3)))
            bmesh.ops.create_cube(bm_w, size=1, matrix=Matrix.Translation(wc) @ Matrix.Diagonal((0.25, 0.04, 0.3, 1)))
    for lvl in range(5):   # pagoda
        s = 3.2 - lvl * 0.45
        z = lvl * 2.0
        bmesh.ops.create_cube(bm_h, size=1, matrix=Matrix.Translation(town_c + Vector((2, 6, z + 0.8))) @ Matrix.Diagonal((s * 0.7, s * 0.7, 1.6, 1)))
        bmesh.ops.create_cube(bm_h, size=1, matrix=Matrix.Translation(town_c + Vector((2, 6, z + 1.7))) @ Matrix.Diagonal((s * 1.15, s * 1.15, 0.18, 1)))
        bmesh.ops.create_cube(bm_w, size=1, matrix=Matrix.Translation(town_c + Vector((2, 6 - s * 0.36, z + 0.9))) @ Matrix.Diagonal((0.5, 0.05, 0.6, 1)))
    for b_, nm, m in ((bm_h, 'Houses', houses), (bm_w, 'Windows', None)):
        me = bpy.data.meshes.new(nm)
        b_.to_mesh(me)
        b_.free()
        S[nm] = add_obj(nm, me, m)
    S['window_mat'] = emit_mat('TownLight', (1.0, 0.62, 0.25), 8.0)
    S['Windows'].data.materials.append(S['window_mat'])
    # town glow points
    bm = bmesh.new()
    for i in range(160):
        c = town_c + Vector((rng.gauss(0, 9), rng.gauss(0, 5), rng.uniform(0.3, 4)))
        bmesh.ops.create_icosphere(bm, subdivisions=1, radius=rng.uniform(0.08, 0.2), matrix=Matrix.Translation(c))
    me = bpy.data.meshes.new('townglow')
    bm.to_mesh(me)
    bm.free()
    add_obj('TownGlow', me, S['window_mat'])

    # floating lanterns around the stage (rig empty scales them out / lifts them per act)
    rig = bpy.data.objects.new('LanternRig', None)
    scn.collection.objects.link(rig)
    S['lantern_rig'] = rig
    S['lantern_mat'] = emit_mat('Lantern', (1.0, 0.45, 0.16), 6.0)
    capm = cel_mat('LanternCap', (0.25, 0.05, 0.05))
    body_me = prim_mesh('sphere', r=1, u=16, v=10)
    cap_me = prim_mesh('cyl', r=0.07, d=0.03, seg=12)
    body_me.materials.append(S['lantern_mat'])
    cap_me.materials.append(capm)
    S['lanterns'] = []
    for i in range(44):
        a = i / 44 * 2 * math.pi + rng.uniform(-0.05, 0.05)
        r = rng.uniform(4.6, 10.0)
        z = rng.uniform(1.2, 4.8)
        ln = bpy.data.objects.new(f'Lantern.{i:02d}', body_me)
        ln.scale = (0.11, 0.11, 0.15)
        ln.location = (math.cos(a) * r, math.sin(a) * r, z)
        ln.parent = rig
        scn.collection.objects.link(ln)
        cap = bpy.data.objects.new(f'LanternCap.{i:02d}', cap_me)
        cap.parent = ln
        cap.location = (0, 0, 1.0)
        cap.scale = (1 / 0.11 * 0.11, 1 / 0.11 * 0.11, 1 / 0.15 * 0.15)
        scn.collection.objects.link(cap)
        # gentle bob – driver keeps file light
        fc = ln.driver_add('location', 2)
        fc.driver.type = 'SCRIPTED'
        ph = rng.uniform(0, 6.28)
        fc.driver.expression = f'{z:.3f} + 0.12*sin(frame/{rng.uniform(40, 70):.1f} + {ph:.2f})'
        S['lanterns'].append(ln)
    # a few lanterns on the ground circle (stage lights)
    for i in range(12):
        a = i / 12 * 2 * math.pi
        ln = bpy.data.objects.new(f'GroundLantern.{i:02d}', body_me)
        ln.scale = (0.09, 0.09, 0.12)
        ln.location = (math.cos(a) * 3.9, math.sin(a) * 3.9, 0.14)
        scn.collection.objects.link(ln)

    # lights
    sun_d = bpy.data.lights.new('MoonLight', 'SUN')
    sun_d.energy = 2.5
    sun_d.color = (0.72, 0.8, 1.0)
    sun_d.angle = math.radians(2)
    sun = add_obj('MoonLight', sun_d)
    sun.rotation_euler = Vector((0, -1, -0.45)).to_track_quat('-Z', 'Y').to_euler()
    fill_d = bpy.data.lights.new('LanternFill', 'AREA')
    fill_d.energy = 160
    fill_d.size = 4
    fill_d.color = (1.0, 0.62, 0.36)
    fill = add_obj('LanternFill', fill_d, loc=(-3.5, -5, 3.0))
    fill.rotation_euler = (Vector((0, 0, 1)) - fill.location).to_track_quat('-Z', 'Y').to_euler()
    rim_d = bpy.data.lights.new('CrownRim', 'SPOT')
    rim_d.energy = 0
    rim_d.color = (0.85, 0.25, 0.9)
    rim_d.spot_size = math.radians(50)
    rim = add_obj('CrownRim', rim_d, loc=(0, 4, 6))
    S.update(sun=sun_d, sun_obj=sun, fill=fill_d, rim=rim_d, rim_obj=rim)
    return S


def build_props(A, mats, rng):
    """Crown (bone-parented pivot), burning 情匣 box, crown shards."""
    scn = bpy.context.scene
    P = {}
    arm = A['arm']
    gold = mats['gold']
    # crown pivot sits on top of head bone tail, world-aligned in rest
    piv = bpy.data.objects.new('CrownPivot', None)
    scn.collection.objects.link(piv)
    piv.parent = arm
    piv.parent_type = 'BONE'
    piv.parent_bone = 'head'
    bpy.context.view_layer.update()
    piv.matrix_world = Matrix.Translation((0, 0.01, 1.60))
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=False, segments=24, radius1=0.085, radius2=0.095, depth=0.05,
                          matrix=Matrix.Translation((0, 0, 0)))
    for i in range(6):   # spikes + moon horns
        a = i / 6 * 2 * math.pi
        hgt = 0.11 if i % 3 == 0 else 0.07
        bmesh.ops.create_cone(bm, cap_ends=True, segments=4, radius1=0.022, radius2=0.0, depth=hgt,
                              matrix=Matrix.Translation((math.cos(a) * 0.09, math.sin(a) * 0.09, 0.025 + hgt / 2)))
    bmesh.ops.create_icosphere(bm, subdivisions=1, radius=0.018, matrix=Matrix.Translation((0, -0.095, 0.03)))
    me = bpy.data.meshes.new('crown')
    bm.to_mesh(me)
    bm.free()
    crown = add_obj('Crown', me, gold)
    crown.parent = piv
    crown.location = (0, 0, 3.0)
    crown_glow = emit_mat('CrownGem', (0.8, 0.3, 1.0), 6.0)
    me.materials.append(crown_glow)
    P['crown'], P['crown_pivot'] = crown, piv

    # 情匣 – burning box, follows hands via copy-location constraints
    box = add_obj('QingXia', prim_mesh('cube', s=(0.14, 0.14, 0.14), smooth=False))
    bm_ = emit_mat('QingXiaGlow', (1.0, 0.5, 0.15), 0.0)
    box.data.materials.append(bm_)
    edge = add_obj('QingXiaFrame', prim_mesh('cube', s=(0.155, 0.155, 0.155), smooth=False), gold)
    edge.parent = box
    wf = edge.modifiers.new('wf', 'WIREFRAME')
    wf.thickness = 0.012
    c1 = box.constraints.new('COPY_LOCATION')
    c1.target, c1.subtarget, c1.head_tail = arm, 'hand.L', 0.6
    c1.influence = 0
    c2 = box.constraints.new('COPY_LOCATION')
    c2.target, c2.subtarget, c2.head_tail = arm, 'hand.R', 0.6
    c2.influence = 0
    lamp_d = bpy.data.lights.new('BoxFire', 'POINT')
    lamp_d.energy = 0
    lamp_d.color = (1.0, 0.45, 0.12)
    lamp_d.shadow_soft_size = 0.2
    lamp = add_obj('BoxFire', lamp_d)
    lamp.parent = box
    P.update(box=box, box_mat=bm_, box_c1=c1, box_c2=c2, box_lamp=lamp_d)

    # shards (animated at the shatter)
    P['shards'] = []
    for i in range(16):
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, segments=3, radius1=rng.uniform(0.015, 0.03), radius2=0, depth=rng.uniform(0.04, 0.09))
        me = bpy.data.meshes.new('shard')
        bm.to_mesh(me)
        bm.free()
        s = add_obj(f'Shard.{i:02d}', me, gold)
        me.materials.append(crown_glow)
        s.scale = (0, 0, 0)
        P['shards'].append(s)
    return P


def particle_system(emitter, name, start, end, count, life, inst, vel_n=0.5, rnd=0.3, grav=0.0, drag=0.0,
                    size=1.0, size_rnd=0.5, align_z=0.0, emit_from='FACE'):
    mod = emitter.modifiers.new(name, 'PARTICLE_SYSTEM')
    ps = mod.particle_system
    st = ps.settings
    st.name = name
    st.count = count
    st.frame_start, st.frame_end = start, end
    st.lifetime = life
    st.lifetime_random = 0.4
    st.emit_from = emit_from
    st.normal_factor = vel_n
    st.factor_random = rnd
    st.object_align_factor = (0, 0, align_z)
    st.effector_weights.gravity = grav
    st.drag_factor = drag
    st.render_type = 'OBJECT'
    st.instance_object = inst
    st.particle_size = size
    st.size_random = size_rnd
    st.use_rotation_instance = False
    st.display_method = 'DOT'
    emitter.show_instancer_for_render = False
    return st
