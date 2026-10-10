"""Beat-grid choreography engine: per-channel key tracks, foot-plant solver, baker, camera shots."""
import bpy, math, bisect, random
from collections import defaultdict
from mathutils import Vector, Quaternion, Euler, Matrix
from bpy_extras import anim_utils
import hsin_rig as R

# ------------------------------------------------------------------ musical time
BPM = 115.96          # fitted to onset envelope of the track
PHASE = 0.335         # time (s) of beat 0
SPB = 60.0 / BPM
FPS = 24
SONG_LEN = 216.6


def T(b):
    return PHASE + b * SPB


def FR(b):
    return T(b) * FPS + 1.0


def BEAT(frame):
    return ((frame - 1) / FPS - PHASE) / SPB


END_FRAME = int(SONG_LEN * FPS) + 1


# ------------------------------------------------------------------ easing
def ease(u, e):
    u = 0.0 if u < 0 else 1.0 if u > 1 else u
    if e == 'lin':
        return u
    if e == 'sm':
        return u * u * (3 - 2 * u)
    if e == 'smm':
        return u ** 3 * (u * (6 * u - 15) + 10)
    if e == 'in':
        return u ** 3
    if e == 'out':
        return 1 - (1 - u) ** 3
    if e == 'hit':
        return 1 - (1 - u) ** 5
    if e == 'snap':          # back-out: hits then settles (overshoot ~8%)
        c = 1.3
        v = u - 1
        return 1 + (c + 1) * v ** 3 + c * v ** 2
    if e == 'step':
        return 1.0 if u >= 1 else 0.0
    raise ValueError(e)


def lerp(a, b, w):
    if isinstance(a, tuple):
        return tuple(x + (y - x) * w for x, y in zip(a, b))
    return a + (b - a) * w


# ------------------------------------------------------------------ channels
ARM_DOWN = (0.06, 0.05, -0.47)
DEFAULTS = dict(
    x=0.0, y=0.0, h=0.0,
    hip=(0.0, 0.0, -0.04), hipr=(0.0, 0.0, 0.0),
    spine=(0.0, 0.0, 0.0), chest=(0.0, 0.0, 0.0), neck=(0.0, 0.0, 0.0), head=(0.0, 0.0, 0.0),
    armL=ARM_DOWN, armR=ARM_DOWN, poleL=(0.35, -0.35, -0.3), poleR=(0.35, -0.35, -0.3),
    wrL=(0.0, 10.0, 0.0), wrR=(0.0, 10.0, 0.0),
    earL=0.0, earR=0.0, tail=(0.0, 0.0, 0.0), wag=0.0,
    groove=0.0, sway=0.0, tremble=0.0,
    # mirror-double only
    gh_yaw=0.0,
)
BOTH = {'arms': ('armL', 'armR'), 'poles': ('poleL', 'poleR'), 'wr': ('wrL', 'wrR'), 'ears': ('earL', 'earR')}


def A(out, fwd, up, ext=0.97):
    """Straight-ish arm direction -> hand offset from shoulder (out, fwd, up)."""
    v = Vector((out, fwd, up)).normalized() * 0.495 * ext
    return (v.x, v.y, v.z)


class Choreo:
    def __init__(self):
        self.tr = defaultdict(list)
        self.feet = {'L': [], 'R': []}
        self.markers = []
        self.flicks = []
        self.cur = dict(x=0.0, y=0.0, h=0.0)

    # ---- pose keys
    def k(self, b, t=None, e='sm', **kw):
        for name, v in kw.items():
            for ch in BOTH.get(name, (name,)):
                assert ch in DEFAULTS, ch
                if isinstance(v, list):
                    v = tuple(v)
                self.tr[ch].append((b, v, e, t))
                if ch in self.cur:
                    self.cur[ch] = v

    def go(self, b, x=None, y=None, h=None, t=None, e='sm'):
        kw = {}
        if x is not None: kw['x'] = x
        if y is not None: kw['y'] = y
        if h is not None: kw['h'] = h
        self.k(b, t=t, e=e, **kw)

    def hold(self, b, *chs):
        """Re-key channels with their current authored value (= hold until b)."""
        for ch in chs:
            for c in BOTH.get(ch, (ch,)):
                v = self.value_at(c, b)
                self.tr[c].append((b, v, 'sm', None))

    def value_at(self, ch, b):
        keys = sorted(self.tr[ch], key=lambda k: k[0])
        v = DEFAULTS[ch]
        for kb, kv, _, _ in keys:
            if kb <= b:
                v = kv
        return v

    def heading_to(self, fx, fy, near=None):
        near = self.cur['h'] if near is None else near
        h = math.degrees(math.atan2(fx, -fy))
        while h - near > 180: h -= 360
        while h - near < -180: h += 360
        return h

    def face_point(self, px, py, near=None, frm=None):
        x, y = frm if frm else (self.cur['x'], self.cur['y'])
        return self.heading_to(px - x, py - y, near)

    # ---- feet
    def plant(self, b, f, x=None, y=0.0, hd=None, dur=0.45, lift=0.07, rel=0.0, att=False, auto=False):
        if x is None:
            x = 0.1 if f == 'L' else -0.1
        if hd is None:
            hd = 8.0 if f == 'L' else -8.0
        self.feet[f].append(dict(k='plant', b=b, x=x, y=y, z=0.0, hd=hd, dur=dur, lift=lift, p=rel, att=att, auto=auto))

    def air(self, b, f, x, y, z, hd=0.0, p=45.0, dur=0.4, att=True):
        self.feet[f].append(dict(k='air', b=b, x=x, y=y, z=z, hd=hd, dur=dur, lift=0.0, p=p, att=att, auto=False))

    def stance(self, b, w=0.11, y=0.0, dur=0.4, lift=0.05, rel=0.0, att=False, stagger=0.0):
        self.plant(b, 'L', w, y, dur=dur, lift=lift, rel=rel, att=att)
        self.plant(b + stagger, 'R', -w, y, dur=dur, lift=lift, rel=rel, att=att)

    def steps(self, b0, n, every=1.0, first='L', w=0.1, lift=0.07, rel=0.0, dur=None):
        f = first
        for i in range(n):
            self.plant(b0 + i * every, f, (w if f == 'L' else -w), 0.0, dur=dur or min(0.55, every * 0.85),
                       lift=lift, rel=rel, auto=True)
            f = 'R' if f == 'L' else 'L'
        return f

    def flick(self, b, side='B', amp=1.0):
        self.flicks.append((b, side, amp))

    def mark(self, b, name):
        self.markers.append((b, name))


# ------------------------------------------------------------------ evaluation
class Evaluator:
    def __init__(self, ch):
        self.ch = ch
        self.tracks = {}
        for name, d in DEFAULTS.items():
            keys = sorted(ch.tr.get(name, []), key=lambda k: k[0])
            # stable de-dup: same beat -> last wins
            dd = []
            for k in keys:
                if dd and abs(dd[-1][0] - k[0]) < 1e-6:
                    dd[-1] = k
                else:
                    dd.append(k)
            first = dd[0][1] if dd else d
            dd.insert(0, (-1e6, first if name in ('x', 'y', 'h') else d, 'sm', None))
            self.tracks[name] = (dd, [k[0] for k in dd])

    def get(self, name, b):
        keys, beats = self.tracks[name]
        i = bisect.bisect_right(beats, b) - 1
        k0 = keys[i]
        if i + 1 >= len(keys):
            return k0[1]
        k1 = keys[i + 1]
        start = k0[0] if k1[3] is None else max(k0[0], k1[0] - k1[3])
        if b <= start:
            return k0[1]
        w = ease((b - start) / (k1[0] - start), k1[2])
        return lerp(k0[1], k1[1], w)

    def frame(self, b):
        return self.get('x', b), self.get('y', b), math.radians(self.get('h', b))


def l2w(fr, lx, ly, lz=0.0):
    x, y, h = fr
    c, s = math.cos(h), math.sin(h)
    return Vector((x + c * lx - s * ly, y + s * lx + c * ly, lz))


def w2l_dir(fr, v):
    c, s = math.cos(fr[2]), math.sin(fr[2])
    return Vector((c * v.x + s * v.y, -s * v.x + c * v.y, 0))


ANKLE_Z = 0.075


def ankle_z(p_deg):
    return ANKLE_Z + 0.11 * math.sin(math.radians(max(0.0, p_deg)))


class FeetSolver:
    def __init__(self, ch, ev):
        self.ev = ev
        self.events = {}
        for f, sx in (('L', 1), ('R', -1)):
            evs = sorted(ch.feet[f], key=lambda e: e['b'])
            start = dict(k='plant', b=-1e6, x=0.1 * sx, y=0.0, z=0.0, hd=8.0 * sx, dur=0.4, lift=0.0, p=0.0, att=False,
                         auto=False, rb=0.0)
            evs.insert(0, start)
            for i in range(1, len(evs)):
                gap = evs[i]['b'] - evs[i - 1]['b']
                evs[i]['dur'] = max(0.05, min(evs[i]['dur'], gap * 0.98))
            for e in evs:
                if e['auto']:      # land slightly ahead along travel direction
                    lead = e['dur'] * SPB * 0.55
                    f0 = ev.frame(e['b'] - 0.12)
                    f1 = ev.frame(e['b'] + 0.12)
                    vel = Vector((f1[0] - f0[0], f1[1] - f0[1], 0)) / (0.24 * SPB)
                    lv = w2l_dir(ev.frame(e['b']), vel) * lead
                    e['x'] += lv.x
                    e['y'] += lv.y
            self.events[f] = (evs, [e['b'] for e in evs])

    def state(self, e, b):
        fr = self.ev.frame(e['b'] if (e['k'] == 'plant' and not e['att']) or e['b'] < -1e5 else b)
        if e['b'] < -1e5:
            fr = self.ev.frame(0.0)
        z = e['z'] if e['k'] == 'air' else ankle_z(e['p'])
        pos = l2w(fr, e['x'], e['y'], z)
        return pos, fr[2] + math.radians(e['hd']), e['p']

    def solve(self, f, b):
        evs, beats = self.events[f]
        i = bisect.bisect_right(beats, b) - 1
        e0 = evs[i]
        if i + 1 < len(evs):
            e1 = evs[i + 1]
            ts = e1['b'] - e1['dur']
            if b > ts:
                u = (b - ts) / e1['dur']
                p0, h0, q0 = self.state(e0, ts)
                p1, h1, q1 = self.state(e1, b)
                w = ease(u, 'sm')
                pos = p0.lerp(p1, w)
                dist = (p1 - p0).length
                if e1['k'] == 'plant':
                    pos.z += e1['lift'] * min(1.0, dist / 0.12 + 0.15) * math.sin(math.pi * u)
                    q = q0 + (q1 - q0) * w + 28 * math.sin(math.pi * u) * min(1.0, dist / 0.1)
                else:
                    q = q0 + (q1 - q0) * w
                dh = (h1 - h0 + math.pi) % (2 * math.pi) - math.pi
                return pos, h0 + dh * w, q, False
        pos, h, q = self.state(e0, b)
        return pos, h, q, e0['k'] == 'plant'


# ------------------------------------------------------------------ fcurve writing
def fcurve(id_, path, index, group=''):
    ad = id_.animation_data or id_.animation_data_create()
    if ad.action is None:
        ad.action = bpy.data.actions.new(id_.name + '_act')
    if ad.action_slot is None:
        ad.action_slot = ad.action.slots.new(id_type=id_.id_type, name=id_.name)
    cb = anim_utils.action_ensure_channelbag_for_slot(ad.action, ad.action_slot)
    fc = cb.fcurves.find(path, index=index)
    if fc is None:
        fc = cb.fcurves.new(path, index=index, group_name=group)
    return fc


def write_dense(id_, path, frames, cols, group=''):
    """cols: list (per index) of value lists."""
    for idx, vals in enumerate(cols):
        fc = fcurve(id_, path, idx, group)
        kp = fc.keyframe_points
        kp.clear()
        kp.add(len(frames))
        co = [0.0] * (2 * len(frames))
        co[0::2] = frames
        co[1::2] = vals
        kp.foreach_set('co', co)
        kp.foreach_set('interpolation', [1] * len(frames))   # LINEAR
        fc.update()


def key(obj, path, frame, value, index=-1, interp=None):
    """Sparse key helper (for lights / materials / props)."""
    owner, prop = obj, path
    if index >= 0:
        getattr(owner, prop)[index] = value
    else:
        setattr(owner, prop, value)
    owner.keyframe_insert(prop, index=index, frame=frame)


# ------------------------------------------------------------------ pose conversion
class RestInfo:
    def __init__(self, arm):
        self.q = {b.name: b.matrix_local.to_quaternion() for b in arm.data.bones}
        self.head = {b.name: b.head_local.copy() for b in arm.data.bones}

    def conj(self, bone, eul_deg):
        r = Euler([math.radians(a) for a in eul_deg], 'XYZ').to_quaternion()
        q = self.q[bone]
        return q.inverted() @ r @ q

    def loc(self, bone, v):
        return self.q[bone].inverted() @ Vector(v)


def mirror_rot(v):
    return (v[0], -v[1], -v[2])


def arm_vec(side, v):
    sx = 1 if side == 'L' else -1
    return Vector((v[0] * sx, -v[1], v[2]))


def sample_pose(ev, b, ch_over=None):
    P = {n: ev.get(n, b) for n in DEFAULTS}
    return P


def mirror_pose(P):
    Q = dict(P)
    Q['hip'] = (-P['hip'][0], P['hip'][1], P['hip'][2])
    for n in ('hipr', 'spine', 'chest', 'neck', 'head'):
        Q[n] = mirror_rot(P[n])
    Q['armL'], Q['armR'] = P['armR'], P['armL']
    Q['poleL'], Q['poleR'] = P['poleR'], P['poleL']
    Q['wrL'], Q['wrR'] = P['wrR'], P['wrL']
    Q['earL'], Q['earR'] = P['earR'], P['earL']
    Q['tail'] = (P['tail'][0], -P['tail'][1], P['tail'][2])
    Q['sway'] = -P['sway']
    return Q


# ------------------------------------------------------------------ the actor bake
class ActorBake:
    """Evaluates the choreography at every frame and writes dense f-curves."""

    def __init__(self, ch, A, seed=3):
        self.ch, self.A = ch, A
        self.ev = Evaluator(ch)
        self.feet = FeetSolver(ch, self.ev)
        self.rest = RestInfo(A['arm'])
        self.rng = random.Random(seed)

    def compute(self):
        frames = list(range(1, END_FRAME + 1))
        ev = self.ev
        out = []
        # spring state for tail
        sw, swv, lf, lfv = 0.0, 0.0, 0.0, 0.0
        prev_hip = None
        prev_h = None
        hist = []
        noise = [(self.rng.uniform(0, 6.28), self.rng.uniform(0.7, 1.3)) for _ in range(12)]
        for f in frames:
            b = BEAT(f)
            t = (f - 1) / FPS
            P = sample_pose(ev, b)
            fr = ev.frame(b)
            hip = list(P['hip'])
            # groove: dip on every beat; sway: side-to-side every two beats
            hip[2] -= P['groove'] * (0.5 + 0.5 * math.cos(2 * math.pi * b))
            hip[0] += P['sway'] * math.sin(math.pi * b)
            # feet
            feet = {s: self.feet.solve(s, b) for s in 'LR'}
            # auto-lower hips so planted feet stay reachable
            hip_w = l2w(fr, hip[0], hip[1]) + Vector((0, 0, 0.92 + hip[2]))
            for s, sx in (('L', 1), ('R', -1)):
                joint = hip_w + (l2w((0, 0, fr[2]), 0.09 * sx, 0.0) - Vector((0, 0, 0)))
                fp = feet[s][0]
                dh = (Vector((joint.x, joint.y, 0)) - Vector((fp.x, fp.y, 0))).length
                Lmax = 0.832
                if dh < Lmax:
                    zmax = fp.z + math.sqrt(Lmax * Lmax - dh * dh)
                    if joint.z > zmax:
                        hip[2] -= joint.z - zmax
                        hip_w.z -= joint.z - zmax
            P['hip'] = tuple(hip)
            # breathing
            br = math.sin(2 * math.pi * t / 3.6)
            P['chest'] = (P['chest'][0] + 1.6 * br, P['chest'][1], P['chest'][2])
            # tremble (arms shaking under effort)
            if P['tremble'] > 1e-3:
                tr = P['tremble']
                for side, k0 in (('armL', 0), ('armR', 3)):
                    v = P[side]
                    P[side] = tuple(v[i] + tr * 0.012 * math.sin(t * 31 * noise[k0 + i][1] + noise[k0 + i][0]) for i in range(3))
                P['head'] = tuple(P['head'][i] + tr * 1.5 * math.sin(t * 23 * noise[6 + i][1] + noise[6 + i][0]) for i in range(3))
            # tail spring driven by root motion
            if prev_hip is None:
                prev_hip, prev_h = hip_w.copy(), fr[2]
            vel = (hip_w - prev_hip) * FPS
            lv = w2l_dir(fr, vel)
            dh = (fr[2] - prev_h) * FPS
            prev_hip, prev_h = hip_w.copy(), fr[2]
            target_sw = P['tail'][1] + math.degrees(-lv.x * 0.22) + math.degrees(-dh * 0.10)
            target_sw += P['wag'] * 18 * math.sin(math.pi * b)
            target_lf = P['tail'][0] + max(-25, min(35, -vel.z * 14 + math.degrees(lv.y * 0.12)))
            k, c = 120.0, 14.0
            dt = 1.0 / FPS
            swv += (k * (target_sw - sw) - c * swv) * dt
            sw += swv * dt
            lfv += (k * (target_lf - lf) - c * lfv) * dt
            lf += lfv * dt
            hist.append((sw, lf))
            tail = []
            for i in range(7):
                hs, hl = hist[max(0, len(hist) - 1 - 2 * i)]
                wave = 4.0 * math.sin(2 * math.pi * (t * 0.6) - i * 0.7)
                tail.append(((hl * 0.16 + P['tail'][2] * i / 6.0 * 0.4), 0.0, hs * 0.16 + wave * (0.3 + i * 0.12)))
            # ear flicks
            ears = [P['earL'], P['earR']]
            for fb, side, amp in self.ch.flicks:
                d = b - fb
                if 0 <= d < 1.0:
                    v = amp * 0.9 * math.sin(math.pi * min(1, d / 0.35)) * math.exp(-3 * d)
                    if side in ('B', 'L'): ears[0] += v
                    if side in ('B', 'R'): ears[1] += v
            out.append(dict(b=b, fr=fr, P=P, feet=feet, tail=tail, ears=ears, hip_w=hip_w))
        self.frames, self.data = frames, out
        return out

    # ---------------------------------------------------------------
    def write(self, A, data, frames):
        arm = A['arm']
        rest = self.rest
        cols = defaultdict(lambda: None)
        series = defaultdict(list)
        prevq = {}

        def addq(bone, q):
            p = prevq.get(bone)
            if p is not None and p.dot(q) < 0:
                q = -q
            prevq[bone] = q
            series[('q', bone)].append(q)

        for d in data:
            P = d['P']
            series[('obj', 'loc')].append((d['fr'][0], d['fr'][1]))
            series[('obj', 'rot')].append(d['fr'][2])
            series[('l', 'hips')].append(rest.loc('hips', P['hip']))
            addq('hips', rest.conj('hips', P['hipr']))
            for n in ('spine', 'chest', 'neck'):
                addq(n, rest.conj(n, P[n]))
            hd = P['head']
            addq('head', rest.conj('head', (hd[0], hd[1], hd[2] + P.get('gh_yaw_eff', 0.0))))
            for s in 'LR':
                v = P['arm' + s]
                tgt = R.SHOULDER[s] + arm_vec(s, v)
                series[('l', f'ik_hand.{s}')].append(rest.loc(f'ik_hand.{s}', tgt - rest.head[f'ik_hand.{s}']))
                pv = R.SHOULDER[s] + arm_vec(s, P['pole' + s]) * 1.0
                series[('l', f'pole_arm.{s}')].append(rest.loc(f'pole_arm.{s}', pv - rest.head[f'pole_arm.{s}']))
                w = P['wr' + s]
                addq(f'hand.{s}', rest.conj(f'hand.{s}', w if s == 'L' else mirror_rot(w)))
                e = d['ears'][0 if s == 'L' else 1]
                sx = 1 if s == 'L' else -1
                addq(f'ear.{s}', rest.conj(f'ear.{s}', (-e * 25, e * 55 * sx, -e * 10 * sx)))
            for i, tr in enumerate(d['tail']):
                addq(f'tail.{i}', rest.conj(f'tail.{i}', tr))
            for s, sx in (('L', 1), ('R', -1)):
                pos, hh, pitch, planted = d['feet'][s]
                rq = (Quaternion((0, 0, 1), hh) @ Quaternion((1, 0, 0), math.radians(pitch)) @ rest.q[f'foot.{s}'])
                series[('fpos', s)].append(pos)
                p = prevq.get('ft' + s)
                if p is not None and p.dot(rq) < 0:
                    rq = -rq
                prevq['ft' + s] = rq
                series[('frot', s)].append(rq)
                # knee pole: in front of the knee along the foot heading
                fwd = Vector((math.sin(hh), -math.cos(hh), 0))
                joint = d['hip_w'] + l2w((0, 0, d['fr'][2]), 0.09 * sx, 0) - Vector((0, 0, 0))
                mid = (joint + pos) / 2
                series[('pole', s)].append(mid + fwd * 0.7 + Vector((0, 0, 0.05)))
        fl = [float(f) for f in frames]
        write_dense(arm, 'location', fl, [[v[0] for v in series[('obj', 'loc')]], [v[1] for v in series[('obj', 'loc')]],
                                          [0.0] * len(fl)], 'Root')
        write_dense(arm, 'rotation_euler', fl, [[0.0] * len(fl), [0.0] * len(fl), series[('obj', 'rot')]], 'Root')
        for key_, vals in series.items():
            kind, bone = key_
            if kind == 'q':
                write_dense(arm, f'pose.bones["{bone}"].rotation_quaternion', fl,
                            [[q[i] for q in vals] for i in range(4)], bone)
            elif kind == 'l':
                write_dense(arm, f'pose.bones["{bone}"].location', fl, [[v[i] for v in vals] for i in range(3)], bone)
            elif kind == 'fpos':
                write_dense(A['foot.' + bone], 'location', fl, [[v[i] for v in vals] for i in range(3)])
            elif kind == 'frot':
                write_dense(A['foot.' + bone], 'rotation_quaternion', fl, [[q[i] for q in vals] for i in range(4)])
            elif kind == 'pole':
                write_dense(A['pole.' + bone], 'location', fl, [[v[i] for v in vals] for i in range(3)])


# ------------------------------------------------------------------ mirror double
def reflect_point(p, plane_p, n):
    d = (p - plane_p).dot(n)
    return p - 2 * d * n


def reflect_heading(h, n):
    f = Vector((math.sin(h), -math.cos(h), 0))
    f2 = f - 2 * f.dot(n) * n
    return math.atan2(f2.x, -f2.y)


def double_data(data, plane_fn, delay_fn, ghyaw_fn):
    """Mirror image of the lead dancer across a moving vertical plane (with optional delay)."""
    out = []
    n_frames = len(data)
    for i, d in enumerate(data):
        b = d['b']
        dl = delay_fn(b)
        j = max(0, min(n_frames - 1, int(round(i - dl * SPB * FPS))))
        s = data[j]
        pp, n = plane_fn(b)
        fr = s['fr']
        pos = reflect_point(Vector((fr[0], fr[1], 0)), pp, n)
        h2 = reflect_heading(fr[2], n)
        # unwrap relative to previous
        if out:
            ph = out[-1]['fr'][2]
            while h2 - ph > math.pi: h2 -= 2 * math.pi
            while h2 - ph < -math.pi: h2 += 2 * math.pi
        P = mirror_pose(s['P'])
        P['gh_yaw_eff'] = ghyaw_fn(b)
        feet = {}
        for side, other in (('L', 'R'), ('R', 'L')):
            p, hh, q, pl = s['feet'][other]
            feet[side] = (reflect_point(p, pp, n), reflect_heading(hh, n), q, pl)
        hip_w = reflect_point(s['hip_w'], pp, n)
        tail = [(a, b_, -c) for a, b_, c in s['tail']]
        out.append(dict(b=b, fr=(pos.x, pos.y, h2), P=P, feet=feet, tail=tail, ears=[s['ears'][1], s['ears'][0]],
                        hip_w=hip_w))
    return out


# ------------------------------------------------------------------ camera
def smooth_series(vals, half_life_frames):
    a = 1 - 0.5 ** (1 / max(1e-3, half_life_frames))
    out, cur = [], None
    for v in vals:
        cur = v.copy() if cur is None else cur.lerp(v, a)
        out.append(cur.copy())
    return out


def bake_camera(cam, shots, data, ghost_data=None, moon=Vector((0, 120, 34)), seed=7):
    """shots: list of dicts with b0,b1 and parameters (see choreography)."""
    rng = random.Random(seed)
    her = smooth_series([Vector((d['hip_w'].x, d['hip_w'].y, 0)) for d in data], 5)
    mid = None
    if ghost_data:
        mid = smooth_series([(Vector((a['hip_w'].x, a['hip_w'].y, 0)) + Vector((g['hip_w'].x, g['hip_w'].y, 0))) / 2
                             for a, g in zip(data, ghost_data)], 6)
    heads = [d['fr'][2] for d in data]
    locs, rots, lens, fdist = [], [], [], []
    shots = sorted(shots, key=lambda s: s['b0'])
    ph = [(rng.uniform(0, 6.28), rng.uniform(0.6, 1.4)) for _ in range(6)]
    prevq = None
    for i, d in enumerate(data):
        b = d['b']
        sh = shots[0]
        for s in shots:
            if s['b0'] <= b:
                sh = s
        b0, b1 = sh['b0'], sh['b1']
        u = max(0.0, min(1.0, (b - b0) / (b1 - b0)))
        w = ease(u, sh.get('e', 'sm'))
        tgt_kind = sh.get('tgt', 'her')
        if tgt_kind == 'mid' and mid is not None:
            base = mid[i]
        elif isinstance(tgt_kind, tuple):
            base = Vector(tgt_kind)
        else:
            base = her[i]
        def g(key, dflt):
            v = sh.get(key, dflt)
            if isinstance(v, tuple) and len(v) == 2 and not isinstance(v[0], tuple):
                return lerp(v[0], v[1], w)
            return v
        lz = g('lz', 1.2)
        look = base + Vector((0, 0, lz))
        if sh.get('look_pt'):
            lw_ = sh.get('look_w', 0.3)
            lw_ = lerp(lw_[0], lw_[1], w) if isinstance(lw_, tuple) else lw_
            look = look.lerp(Vector(sh['look_pt']), lw_)
        if sh.get('look_moon'):
            mw = lerp(sh['look_moon'][0], sh['look_moon'][1], w)
            look = look.lerp(moon, mw)
        if sh['type'] == 'orbit':
            ref_h = heads[max(0, min(len(data) - 1, int(round(FR(b0))) - 1))] if sh.get('rel', True) else 0.0
            a = math.radians(g('a', 0.0)) + ref_h
            r = g('r', 4.0)
            z = g('z', 1.4)
            pos = base + Vector((math.sin(a) * r, -math.cos(a) * r, 0)) + Vector((0, 0, z))
        else:   # 'path' : world-space p0 -> p1
            p0, p1 = Vector(sh['p'][0]), Vector(sh['p'][1])
            pos = p0.lerp(p1, w)
            if sh.get('p_rel'):
                pos = pos + base
        lens_v = g('lens', 35.0)
        sk = sh.get('shake', 0.0)
        if sk:
            t = (i) / FPS
            pos = pos + Vector([sk * 0.04 * math.sin(t * 2.3 * ph[k][1] + ph[k][0]) +
                                sk * 0.015 * math.sin(t * 7.1 * ph[k][1] + ph[k][0] * 2) for k in range(3)])
        direction = look - pos
        q = direction.to_track_quat('-Z', 'Y')
        roll = g('roll', 0.0)
        if roll:
            q = q @ Quaternion((0, 0, 1), math.radians(roll))
        if prevq is not None and prevq.dot(q) < 0:
            q = -q
        prevq = q
        locs.append(pos)
        rots.append(q)
        lens.append(lens_v)
        fdist.append(direction.length)
    cam.rotation_mode = 'QUATERNION'
    fl = [float(d) for d in range(1, len(data) + 1)]
    write_dense(cam, 'location', fl, [[v[i] for v in locs] for i in range(3)])
    write_dense(cam, 'rotation_quaternion', fl, [[q[i] for q in rots] for i in range(4)])
    write_dense(cam.data, 'lens', fl, [lens])
    write_dense(cam.data, 'dof.focus_distance', fl, [fdist])
    # f-stop per shot (sparse, constant)
    for sh in shots:
        cam.data.dof.aperture_fstop = sh.get('fstop', 5.6)
        cam.data.dof.keyframe_insert('aperture_fstop', frame=FR(sh['b0']))
    return locs
