"""
Ode to Hsin and Moon — Endless Yearning : full choreography, camera and lighting.

Run:  Blender -b --factory-startup -P hsin_dance.py -- --out hsin_dance.blend [--audio song.mp3]

Everything is authored on the musical beat grid (115.96 BPM, beat 0 = 0.335 s; lyric
lines fall on 8-beat phrases).  c.k(beat, ...) keys pose channels, c.go() moves the
dancer's floor frame, c.plant()/c.air() place feet.  See hsin_engine.py for the meaning
of every channel.
"""
import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from mathutils import Vector, Matrix
import hsin_rig as R
import hsin_engine as E
from hsin_engine import A, ARM_DOWN, FR, Choreo

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
OUT = argv[argv.index('--out') + 1] if '--out' in argv else os.path.join(os.path.dirname(__file__), 'hsin_dance.blend')
AUDIO = argv[argv.index('--audio') + 1] if '--audio' in argv else None
QUICK = '--quick' in argv

MOON = (0.0, 120.0)
TOWN = (-25.0, 35.0)

# handy arm shapes (hand offset from shoulder: out, fwd, up)
HIP_HAND = (0.10, -0.02, -0.25)
PAW = (-0.02, 0.28, 0.0)
HEART = (-0.10, 0.20, -0.07)
ON_HEAD = (-0.04, 0.03, 0.30)
HOLD_BOX = (-0.075, 0.30, -0.06)
OVERHEAD = (-0.08, 0.06, 0.44)
CRESCENT = (-0.11, 0.10, 0.40)
HUG = (-0.22, 0.18, -0.05)
FIRST = (-0.07, 0.27, -0.06)
P_DEF = (0.35, -0.35, -0.3)
P_OUT = (0.6, 0.0, 0.05)
P_UP = (0.55, 0.0, 0.2)
P_LOW = (0.4, 0.0, -0.4)

c = Choreo()


# ======================================================================= motifs
def jump(b0, b1, hgt, kind='tuck', turn=0.0, land='L', prep=True):
    if prep:
        c.k(b0 - 0.5, t=0.5, hip=(0, 0.02, -0.16))
    c.k(b0, t=0.3, e='out', hip=(0, 0, 0.02))
    c.k((b0 + b1) / 2, t=(b1 - b0) / 2, e='out', hip=(0, 0, hgt))
    c.k(b1, t=(b1 - b0) / 2, e='in', hip=(0, 0, -0.01))
    c.k(b1 + 0.35, t=0.35, e='out', hip=(0, 0.02, -0.15))
    if turn:
        c.go(b0, h=c.cur['h'])
        c.go(b1, h=c.cur['h'] + turn, e='sm')
    mid = b0 + (b1 - b0) * 0.45
    sl = 1 if land == 'L' else -1
    if kind == 'tuck':
        c.air(mid, 'L', 0.1, 0.06, hgt * 0.7 + 0.22, p=55, dur=(b1 - b0) * 0.4)
        c.air(mid, 'R', -0.1, 0.06, hgt * 0.7 + 0.22, p=55, dur=(b1 - b0) * 0.4)
        c.plant(b1, 'L', 0.11, 0, dur=(b1 - b0) * 0.45, lift=0)
        c.plant(b1 + 0.05, 'R', -0.11, 0, dur=(b1 - b0) * 0.45, lift=0)
    else:  # split leap (grand jeté): front leg = landing leg
        fr_, bk = ('L', 'R') if land == 'L' else ('R', 'L')
        c.air(mid, fr_, 0.06 * sl, -0.44, hgt + 0.30, p=60, dur=(b1 - b0) * 0.45)
        c.air(mid, bk, -0.06 * sl, 0.48, hgt + 0.42, p=60, dur=(b1 - b0) * 0.45)
        c.plant(b1, fr_, 0.08 * sl, -0.12, dur=(b1 - b0) * 0.45, lift=0)
        c.plant(b1 + 0.45, bk, -0.1 * sl, 0.05, dur=0.4, lift=0.04)


def pirouette(b0, b1, turns, support='L', arms=True, prep=True):
    sx = 1 if support == 'L' else -1
    other = 'R' if support == 'L' else 'L'
    if prep:
        c.k(b0 - 0.3, t=0.5, hip=(0.03 * sx, 0, -0.14))
    c.k(b0, t=0.3, e='out', hip=(0.04 * sx, 0, 0.02))
    if arms:
        c.k(b0 + 0.1, t=0.4, e='out', arms=FIRST, poles=(0.45, 0, -0.15), wr=(0, 0, 0))
    c.plant(b0, support, 0.03 * sx, 0.0, hd=0, att=True, rel=55, dur=0.3, lift=0.0)
    c.air(b0 + 0.25, other, 0.04 * sx, -0.04, 0.42, p=60, dur=0.3)
    c.go(b0, h=c.cur['h'])
    c.go(b1, h=c.cur['h'] + 360 * turns * sx, e='sm')
    c.plant(b1 + 0.15, other, -0.11 * sx, 0.02, dur=0.3, lift=0.0)
    c.plant(b1 + 0.2, support, 0.1 * sx, 0.0, dur=0.2, lift=0.0)
    c.k(b1 + 0.45, t=0.45, hip=(0, 0, -0.10))


def path(pts, every=0.25, face=True, h_off=0.0):
    """Catmull-Rom floor path. pts = [(beat, x, y), ...]; heading follows the tangent."""
    n = len(pts)
    P = lambda i: Vector((pts[max(0, min(n - 1, i))][1], pts[max(0, min(n - 1, i))][2], 0))
    for i in range(n - 1):
        b0, b1 = pts[i][0], pts[i + 1][0]
        m = max(1, int(round((b1 - b0) / every)))
        for j in range(m + (1 if i == n - 2 else 0)):
            s = j / m
            p0, p1, p2, p3 = P(i - 1), P(i), P(i + 1), P(i + 2)
            pos = 0.5 * ((2 * p1) + (-p0 + p2) * s + (2 * p0 - 5 * p1 + 4 * p2 - p3) * s * s + (-p0 + 3 * p1 - 3 * p2 + p3) * s ** 3)
            tan = 0.5 * ((-p0 + p2) + 2 * (2 * p0 - 5 * p1 + 4 * p2 - p3) * s + 3 * (-p0 + 3 * p1 - 3 * p2 + p3) * s * s)
            kw = dict(x=pos.x, y=pos.y)
            if face and tan.length > 1e-4:
                kw['h'] = c.heading_to(tan.x, tan.y) + h_off
            c.go(b0 + (b1 - b0) * s, e='lin', **kw)


def turn_to(b0, b1, h, steps=True):
    c.go(b0, h=c.cur['h'])
    c.go(b1, h=h, e='sm')
    if steps:
        c.plant(b0 + (b1 - b0) * 0.45, 'L', 0.1, 0, dur=(b1 - b0) * 0.45, lift=0.05)
        c.plant(b1, 'R', -0.1, 0, dur=(b1 - b0) * 0.45, lift=0.05)


def travel(b0, b1, x, y, e='sm'):
    c.go(b0, x=c.cur['x'], y=c.cur['y'])
    c.go(b1, x=x, y=y, e=e)


def front():
    return c.heading_to(0, -1)


def body_wave(b, d):
    c.k(b, t=0.5, hip=(0, -0.05 * d, -0.11))
    c.k(b + 0.35, t=0.5, spine=(-10 * d, 0, 0))
    c.k(b + 0.7, t=0.5, chest=(14 * d, 0, 0))
    c.k(b + 1.05, t=0.5, head=(10 * d, 0, 0))
    c.k(b + 1.7, t=0.6, spine=(0, 0, 0), chest=(0, 0, 0), head=(0, 0, 0), hip=(0, 0, -0.06))


def lantern_sway(b0, warm=False):
    """'Lanterns sway' motif (Act 1, reprised warmer in Act 5)."""
    c.stance(b0, w=0.15, dur=0.6, lift=0.04)
    hi = A(0.55, 0.35, 0.62 if warm else 0.5)
    lo = A(0.6, 0.3, -0.15)
    for i in range(3):
        s = 1 if i % 2 == 0 else -1
        c.k(b0 + 2 * i + 1, t=1.6, hip=(0.05 * s, 0, -0.07), spine=(0, -7 * s, 0), chest=(0, -6 * s, 4 * s),
            head=(-4 if warm else 0, 9 * s, 6 * s), armL=hi if s > 0 else lo, armR=lo if s > 0 else hi,
            poles=(0.4, -0.1, -0.35), wr=(0, -10, 0), wag=0.8 if warm else 0.4)
    c.k(b0 + 6.5, t=0.8, arms=HUG, poles=(0.4, -0.1, -0.4), hip=(0, 0, -0.08), spine=(0, 0, 0), chest=(6, 0, 0),
        head=(6, 0, 0))
    c.k(b0 + 7.8, t=1.2, e='out', arms=A(0.8, 0.25, 0.45 if not warm else 0.6), chest=(-8, 0, 0), head=(-10, 0, 0),
        hip=(0, 0, -0.04))


# ======================================================================= ACT 1  月下化形，游戏人间
c.mark(0, 'ACT1 月下化形 | Moon up high – fox crouched under the moon')
c.go(0, x=0.0, y=0.6, h=180)
c.stance(0, w=0.13, dur=0.1)
c.k(0, hip=(0, 0.06, -0.43), spine=(42, 0, 0), chest=(28, 0, 0), neck=(12, 0, 0), head=(18, 0, 0),
    arms=(-0.05, 0.30, -0.27), poles=(0.3, 0.05, -0.35), wr=(0, 40, 0), ears=0.9, tail=(-25, 55, 45))
c.k(4.5, t=4.5, hip=(0, 0.03, -0.26), spine=(22, 0, 0), chest=(12, 0, 0), neck=(4, 0, 0), head=(0, 0, 0), ears=0.4,
    tail=(-5, 25, 20), arms=(0.0, 0.2, -0.40))
c.k(8, t=3.5, e='out', hip=(0, 0, -0.04), spine=(-4, 0, 0), chest=(-10, 0, 0), neck=(-8, 0, 0), head=(-22, 0, 0),
    arms=(0.16, 0.08, -0.44), wr=(0, 15, 0), ears=-0.25, tail=(12, 0, 0), poles=P_DEF)
c.flick(8)
c.mark(8, 'Who is peeking down today – peeking left/right, turns to the viewer')
c.k(9, t=0.6, e='snap', head=(-15, 6, 30), neck=(0, 0, 10), hip=(0.03, 0, -0.04))
c.k(10.5, t=0.6, e='snap', head=(-15, -6, -30), neck=(0, 0, -10), hip=(-0.03, 0, -0.04))
c.k(11.5, t=0.5, head=(-10, 0, 0), neck=(0, 0, 0), hip=(0, 0, -0.06))
c.go(12, h=180)
c.go(13.5, h=360, e='sm')
c.plant(12.6, 'R', -0.1, 0, dur=0.5, lift=0.05, rel=20)
c.plant(13.4, 'L', 0.1, 0, dur=0.5, lift=0.05)
c.plant(13.9, 'R', -0.1, 0, dur=0.4, lift=0.03)
c.k(14, t=1.2, e='snap', hip=(0.02, 0.05, -0.06), spine=(14, 0, 0), chest=(8, 6, 0), head=(-4, 14, -8),
    arms=(0.07, -0.20, -0.40), poles=(0.4, -0.3, -0.2), ears=-0.3, tail=(15, 0, 0), wag=1.0)
c.flick(14.5, 'R')
c.k(16, t=1, wag=0.4, spine=(0, 0, 0), chest=(0, 0, 0))

c.mark(16, '[L03] – lantern sway motif')
lantern_sway(16)

c.mark(24, "Who knows what's left untold – 'shh', tendu, finger wag")
c.k(25, t=0.8, e='snap', armR=(-0.10, 0.22, 0.12), poleR=(0.35, 0.1, -0.4), wrR=(0, -20, 0), armL=HIP_HAND,
    poleL=P_OUT, wrL=(0, -30, 0), hip=(0.06, 0, -0.05), head=(5, 12, -12), chest=(0, 6, -8), spine=(0, 4, 0), wag=0)
c.plant(25, 'R', -0.30, -0.06, dur=0.5, lift=0.04, rel=65)
c.flick(26, 'L')
for j, bb in enumerate([28, 28.5, 29, 29.5]):
    c.k(bb, t=0.3, e='snap', wrR=(0, -20, 25 if j % 2 == 0 else -25), head=(5, 12 if j % 2 == 0 else 6, -12))
c.k(30, t=0.6, armR=ARM_DOWN, poleR=P_DEF, wrR=(0, 10, 0), armL=ARM_DOWN, poleL=P_DEF, wrL=(0, 10, 0),
    hip=(0, 0, -0.05), head=(0, 0, 0), chest=(0, 0, 0), spine=(0, 0, 0))
turn_to(30, 31.6, c.heading_to(-1, 0))           # face screen-left for the sneak

# ---- instrumental: playful fox
c.mark(32, 'Instrumental – fox sneak (on toes, paws)')
travel(32, 40, -2.4, 0.3)
c.k(32.6, t=1, hip=(0, 0, -0.12), spine=(20, 0, 0), chest=(6, 0, 0), head=(-14, 0, 0), arms=PAW,
    poles=(0.25, 0.05, -0.45), wr=(0, 70, 0), ears=-0.3, tail=(25, 0, 10), groove=0.03)
c.steps(33, 8, every=1.0, first='L', w=0.07, lift=0.12, rel=25)
c.k(38, t=0.4, e='snap', head=(-5, 8, 45))
c.flick(38.2, 'L')
c.k(39.5, t=0.5, head=(-14, 0, 0))

c.mark(40, 'Pounce!')
c.stance(40.8, w=0.12, dur=0.5)
c.k(42, t=1.5, hip=(0, 0.04, -0.26), spine=(35, 0, 0), chest=(10, 0, 0), head=(-30, 0, 0), arms=(-0.02, 0.30, -0.18),
    tail=(35, 0, 0), wag=1.5, groove=0, ears=-0.4)
c.k(43.4, t=0.8, hip=(0, 0.06, -0.32), wag=0.5)
travel(44, 45, -3.1, 0.3, e='lin')
jump(44, 45, 0.30, prep=False)
c.k(44.5, t=0.4, e='out', arms=A(0.1, 0.85, 0.45), spine=(10, 0, 0), head=(-20, 0, 0))
c.k(45.3, t=0.3, e='out', spine=(38, 0, 0), arms=(-0.02, 0.32, -0.34), head=(-35, 0, 0))
c.k(46, t=0.4, e='snap', head=(-25, 0, 40))
c.k(47, t=0.4, e='snap', head=(-25, 0, -40))
c.flick(47)
c.k(47.7, t=0.4, head=(-20, 0, 0))

c.mark(48, 'Tail chase spin')
c.k(48.2, t=0.6, hip=(0, 0, -0.07), spine=(14, 12, 0), chest=(5, 10, 25), head=(-5, 10, 55), armL=A(0.4, -0.5, -0.3),
    armR=A(0.2, 0.6, -0.1), poles=P_DEF, wr=(0, 10, 0), ears=-0.2, tail=(10, -35, 20), wag=0)
c.go(48, h=c.cur['h'])
c.go(52, h=c.cur['h'] + 720, e='sm')
c.steps(48.5, 8, every=0.5, w=0.09, lift=0.05, rel=15)
c.k(52, t=0.5, spine=(0, 0, 0), chest=(0, 0, 0), head=(0, 0, 0), tail=(10, 0, 0))
turn_to(52.0, 52.8, front())

c.mark(52.5, 'Peek-a-boo')
c.k(53, t=0.4, e='snap', arms=(-0.10, 0.20, 0.17), poles=(0.4, 0.0, -0.35), wr=(0, -10, 0), head=(10, 0, 0))
c.k(54, t=0.35, e='snap', arms=A(0.7, 0.3, 0.5), poles=P_OUT, head=(-8, 14, 0), hip=(0, 0, 0.0), ears=-0.4, wag=1.5)
c.flick(54)
c.k(55.5, t=0.8, arms=HIP_HAND, poles=P_OUT, wr=(0, -30, 0), head=(-4, -10, 0), hip=(0, 0, -0.05), wag=0.6)

c.mark(56, 'Chaîné turns across the stage')
c.go(56, x=c.cur['x'], y=c.cur['y'])
hx = c.heading_to(1, 0)
c.go(56.5, h=hx, t=0.5)
c.go(60, x=0.8, y=0.4, e='sm')
c.go(60, h=hx + 1080, e='sm')
c.k(56.6, t=0.5, arms=FIRST, poles=(0.45, 0, -0.15), wr=(0, 0, 0), hip=(0, 0, 0.0), head=(-4, 0, 0))
c.steps(56.5, 8, every=0.5, w=0.06, lift=0.03, rel=45)
c.go(61, h=front(), t=0.8)
c.stance(60.8, w=0.16, dur=0.5)
for i, b in enumerate([61, 62, 63, 64]):
    s = 1 if i % 2 == 0 else -1
    c.k(b, t=1, armL=A(0.6, 0.15, 0.5 * s), armR=A(0.6, 0.15, -0.5 * s), poles=P_OUT, spine=(0, -8 * s, 0),
        hip=(0.05 * s, 0, -0.06), head=(0, 8 * s, 0), wr=(0, -15 * s, 0))
c.k(65, t=1, arms=(-0.09, 0.22, -0.30), poles=(0.4, 0, -0.3), hip=(0, 0, -0.08), spine=(8, 0, 0), head=(0, 0, 0))
c.k(66.5, t=1.5, hip=(0, 0.02, -0.18), spine=(22, 0, 0), head=(10, 0, 0), tail=(-10, 0, 0))
c.k(67.6, t=1.1, e='out', hip=(0, 0, -0.06), arms=A(0.3, -0.6, -0.5), spine=(10, 0, 0), head=(-5, 0, 0), ears=-0.3,
    tail=(15, 0, 0))
c.flick(67.5)
c.go(67, h=c.cur['h'])
c.go(68, h=c.heading_to(1.1, -1.0), e='sm')

# ---- verse 1
c.mark(68, '[L05] – wind run + grand jeté')
path([(68, 0.8, 0.4), (70, 1.9, -0.6), (72, 1.2, -2.0), (74, -0.4, -1.9), (76, -1.1, -1.0)])
c.k(68.5, t=0.5, e='out', spine=(14, 0, 0), chest=(4, 0, 0), head=(-6, 0, 0), arms=A(0.45, -0.55, -0.25),
    poles=(0.4, -0.1, -0.4), wr=(0, -25, 0), ears=-0.2, groove=0.0)
c.steps(68.5, 11, every=0.5, first='L', w=0.09, lift=0.13, rel=20)
c.k(74.4, t=0.5, e='out', armL=A(0.25, 0.8, 0.45), armR=A(0.5, -0.55, 0.2), spine=(-4, 0, 0), chest=(-10, 0, 0),
    head=(-20, 0, 0))
jump(74, 75, 0.36, kind='split', land='L', prep=False)
c.k(75.6, t=0.6, spine=(4, 0, 0), chest=(0, 0, 0), head=(0, 0, 0), arms=A(0.6, 0.3, -0.3))
c.stance(76.2, w=0.13, dur=0.5)
turn_to(76.0, 76.9, front(), steps=False)

c.mark(76, '[L06] – arm circles, step-touch')
cyc = [A(0.12, 0.15, 1), A(0.9, 0.15, 0.35), A(0.45, 0.45, -0.75), A(-0.25, 0.9, 0.15)]
for i in range(8):
    b = 77 + i
    roll = (-9, 0, 9, 0)[i % 4]
    c.k(b, t=1, armL=cyc[i % 4], armR=cyc[(i + 2) % 4], poles=P_LOW, chest=(0, roll, 0), spine=(0, roll * 0.5, 0),
        head=(0, -roll * 0.6, 0), groove=0.02, wr=(0, -10, 0))
for rep in (0, 4):
    b = 77 + rep
    c.plant(b, 'L', 0.22, 0, dur=0.5, lift=0.05)
    c.plant(b + 1, 'R', 0.06, 0, dur=0.5, lift=0.04, rel=30)
    c.plant(b + 2, 'R', -0.22, 0, dur=0.5, lift=0.05)
    c.plant(b + 3, 'L', -0.06, 0, dur=0.5, lift=0.04, rel=30)
    c.k(b, t=0.6, hip=(0.14, 0, -0.06))
    c.k(b + 1, t=0.6, hip=(0.15, 0, -0.04))
    c.k(b + 2, t=0.6, hip=(-0.14, 0, -0.06))
    c.k(b + 3, t=0.6, hip=(-0.15, 0, -0.04))

c.mark(84, 'Bathe me in tender moonbeams – open to the moon, piqué turn')
hm = c.heading_to(MOON[0] - c.cur['x'], MOON[1] - c.cur['y'])
c.go(84, h=c.cur['h'])
c.go(85, h=hm, e='sm')
c.plant(84.5, 'L', 0.1, 0, dur=0.5)
c.plant(85.0, 'R', -0.1, 0, dur=0.5)
c.k(86, t=2, arms=A(0.45, 0.15, 0.88), poles=P_OUT, wr=(0, -20, 0), chest=(-18, 0, 0), spine=(-6, 0, 0),
    neck=(-8, 0, 0), head=(-22, 0, 0), hip=(0, 0, 0.0), ears=-0.35, tail=(25, 0, 0), groove=0, sway=0)
c.stance(86, w=0.1, rel=35, dur=0.5)
c.k(87.2, t=1, hip=(0.03, 0, 0.0), chest=(-14, 5, 0))
pirouette(88, 90, 1.5, support='L')
c.k(90.4, t=0.5, e='out', arms=A(0.8, 0.3, 0.25), poles=P_OUT, chest=(0, 0, 0), spine=(0, 0, 0), neck=(0, 0, 0),
    head=(-6, 0, 0))

c.mark(92, 'how carefree – chassés, flicks')
x0 = c.cur['x']
c.go(92, x=x0)
c.go(93, x=x0 + 0.5)
c.go(94, x=x0 + 0.5)
c.go(95, x=x0)
c.plant(92.0, 'L', 0.1, 0, auto=True, dur=0.4)
c.plant(92.5, 'R', -0.06, 0, auto=True, dur=0.4)
c.plant(93.0, 'L', 0.1, 0, auto=True, dur=0.4)
c.plant(94.0, 'R', -0.1, 0, auto=True, dur=0.4)
c.plant(94.5, 'L', 0.06, 0, auto=True, dur=0.4)
c.plant(95.0, 'R', -0.1, 0, auto=True, dur=0.4)
for i, b in enumerate([92, 93, 94, 95]):
    s = 1 if i % 2 == 0 else -1
    c.k(b, t=0.5, e='snap', armL=A(0.8, 0.3, 0.3 * s), armR=A(0.8, 0.3, -0.3 * s), head=(0, -10 * s, 8 * s),
        chest=(0, -6 * s, 0), wag=1.2)
    c.k(b + 0.5, t=0.25, e='snap', wr=(0, 30 * s, 0))
c.flick(92)
c.flick(94)

c.mark(96, '[L08] – kneel, guzheng plucking')
c.k(97, t=1, hip=(0, 0.05, -0.40), spine=(12, 0, 0), chest=(4, 0, 0), head=(10, 0, 0), arms=(-0.04, 0.32, -0.27),
    poles=P_LOW, wr=(0, 25, 0), ears=0, wag=0, tail=(-10, 40, 30))
c.plant(96.6, 'L', 0.13, -0.26, dur=0.6, lift=0.04)
c.plant(97.2, 'R', -0.1, 0.42, rel=75, dur=0.6, lift=0.03)
for j, b in enumerate([98, 98.5, 99, 99.5]):
    s = 1 if j % 2 == 0 else -1
    c.k(b, t=0.25, e='hit', wrL=(0, 25 + 18 * s, 0), wrR=(0, 25 - 18 * s, 0),
        armL=(-0.04 + 0.03 * s, 0.32, -0.27), head=(10, 5 * s, 0))
for j in range(8):
    b = 100 + j * 0.25
    s = 1 if j % 2 == 0 else -1
    c.k(b, t=0.12, e='hit', wrL=(0, 25 + 20 * s, 0), wrR=(0, 25 - 20 * s, 0))
c.flick(100)
c.k(101.6, t=0.5, head=(4, 0, 0), wr=(0, 20, 0))
c.k(103.5, t=1.5, hip=(0, 0, -0.05), spine=(0, 0, 0), chest=(0, 0, 0), head=(0, 0, 0), arms=ARM_DOWN, poles=P_DEF,
    wr=(0, 10, 0), tail=(10, 0, 0))
c.plant(102.8, 'R', -0.1, 0, dur=0.7, lift=0.06)
c.plant(103.4, 'L', 0.1, 0, dur=0.5)

c.mark(104, '[L09] – point L, point R, both up, double pirouette')
c.k(104.4, t=0.5, e='snap', armL=A(0.6, 0.5, 0.62), poleL=P_OUT, armR=HIP_HAND, poleR=P_OUT, head=(-15, 0, 30),
    chest=(0, 4, 10), hip=(0.05, 0, -0.05), wrL=(0, -15, 0))
c.k(106.4, t=0.5, e='snap', armR=A(0.6, 0.5, 0.62), poleR=P_OUT, armL=HIP_HAND, poleL=P_OUT, head=(-15, 0, -30),
    chest=(0, -4, -10), hip=(-0.05, 0, -0.05), wrR=(0, -15, 0))
c.k(108.4, t=0.6, e='snap', arms=A(0.4, 0.2, 0.9), poles=P_OUT, head=(-25, 0, 0), chest=(-10, 0, 0), hip=(0, 0, 0))
c.stance(108.4, w=0.09, rel=30)
c.k(109.5, t=0.8, arms=A(0.8, 0.4, 0.0), head=(0, 0, 0), chest=(0, 0, 0))
pirouette(110, 111.5, 2, support='L')
c.k(112, t=0.5, e='out', arms=A(0.7, 0.4, -0.3), poles=P_DEF, wr=(0, 0, 0))

c.mark(112, '[L10] – walk to the viewer, gather the lights')
travel(112, 116, c.cur['x'] + 0.1, c.cur['y'] - 0.9)
c.steps(112.7, 4, every=1, first='R', lift=0.05)
c.stance(116.5)
c.k(114, t=2, arms=A(0.9, 0.3, -0.2), poles=(0.4, -0.2, -0.4), chest=(-6, 0, 0), head=(-6, 0, 0), wr=(0, -20, 0))
c.k(116, t=2, arms=A(0.8, 0.35, 0.35), head=(-12, 0, 0))
c.k(119, t=3, arms=HEART, poles=(0.4, -0.1, -0.35), wr=(0, 10, 0), head=(8, 0, 0), chest=(6, 0, 0), sway=0.02,
    ears=0.2)
c.mark(120, '[L11] – hold to heart, release upward')
c.k(121, t=1, sway=0, chest=(4, 0, 20), head=(5, 0, 15))
c.k(124, t=1.2, e='out', arms=A(0.5, 0.75, 0.45), wr=(0, -25, 0), chest=(-12, 0, 0), head=(-18, 0, 0),
    hip=(0, 0, -0.02), ears=-0.3)
c.stance(124, rel=30, w=0.1)
c.k(126, t=1.5, arms=A(0.85, 0.3, 0.4), chest=(-8, 0, 0))
c.k(127.6, t=1.2, arms=(-0.08, 0.2, -0.32), hip=(0, 0.02, -0.14), spine=(15, 0, 0), head=(5, 0, 0), chest=(0, 0, 0))
c.stance(127.0, rel=0)

# ---- chorus 1
c.mark(128, '[L12] – reach to the moon, arabesque')
hm = c.heading_to(MOON[0] - c.cur['x'], MOON[1] - c.cur['y'])
turn_to(127.6, 128.6, hm + 30)
c.k(129, t=1.2, e='out', armL=A(0.25, 0.55, 0.8), armR=A(0.9, -0.3, 0.1), poles=P_OUT, chest=(-15, 8, 0),
    head=(-30, 6, 0), spine=(-4, 0, 0), hip=(0, 0, 0.0), ears=-0.35, tail=(25, 0, 0))
c.stance(129, rel=40, w=0.08)
fx, fy = math.sin(math.radians(c.cur['h'])), -math.cos(math.radians(c.cur['h']))
travel(130, 131.6, c.cur['x'] + fx * 0.6, c.cur['y'] + fy * 0.6)
c.steps(130.6, 2, every=0.7, first='L')
c.plant(132, 'L', 0.03, 0, dur=0.4)
c.air(132.5, 'R', -0.04, 0.55, 0.42, p=60, dur=0.5)
c.k(132.6, t=1, spine=(22, 0, 0), chest=(10, 0, 0), head=(-15, 0, 0), armL=A(0.1, 0.85, 0.4), armR=A(0.9, -0.1, 0.1),
    hip=(0.04, 0.04, -0.03))
c.k(134, t=0.6, spine=(0, 0, 0), chest=(0, 0, 0), head=(0, 0, 0), hip=(0, 0, -0.08))
c.plant(134.1, 'R', -0.1, 0.0, dur=0.5)

c.mark(134, '[L13] – run, high grand jeté, self-embrace')
turn_to(134.0, 134.8, c.heading_to(1, 0), steps=False)
travel(134.5, 137.6, c.cur['x'] + 2.6, c.cur['y'], e='lin')
c.steps(134.8, 3, every=0.5, first='L', lift=0.12, rel=20)
c.k(135, t=0.5, arms=A(0.45, -0.55, -0.25), spine=(12, 0, 0), poles=(0.4, -0.1, -0.4))
c.k(136.5, t=0.5, e='out', armL=A(0.25, 0.8, 0.5), armR=A(0.5, -0.55, 0.25), spine=(-4, 0, 0), chest=(-10, 0, 0),
    head=(-22, 0, 0))
jump(136.2, 137.6, 0.42, kind='split', land='L', prep=False)
c.k(138.5, t=1, arms=HUG, poles=(0.4, -0.1, -0.4), chest=(8, 0, 0), head=(12, 10, 0), hip=(0, 0, -0.08), wr=(0, 15, 0),
    spine=(0, 0, 0))
turn_to(138.0, 139.0, front(), steps=False)
c.stance(138.4)
c.k(140.5, t=1, sway=0.02)
c.k(143.5, t=2, sway=0, arms=A(0.5, 0.4, -0.5), head=(0, 0, 0), chest=(0, 0, 0))

c.mark(144, '[L14] – curl down, bloom up, soutenu')
c.k(146, t=2, hip=(0.05, 0, -0.10), spine=(22, 10, 0), chest=(12, 6, 0), head=(25, 15, 0), armL=(0.02, 0.18, -0.42),
    armR=(-0.06, 0.2, -0.40), poles=(0.3, -0.2, -0.4), wr=(0, 30, 0), ears=0.7, tail=(-20, 0, 0))
c.k(150, t=2.5, hip=(-0.04, 0, 0.0), spine=(-6, -6, 0), chest=(-16, -6, 0), head=(-28, -10, 0), arms=A(0.55, 0.25, 0.8),
    poles=P_OUT, wr=(0, -20, 0), ears=-0.4, tail=(30, 0, 0), wag=1.0)
c.stance(149, rel=35, w=0.1)
c.flick(150)
c.plant(150.5, 'L', 0.03, 0, att=True, rel=50, dur=0.3)
c.plant(150.5, 'R', -0.03, 0, att=True, rel=50, dur=0.3)
c.go(150.5, h=c.cur['h'])
c.go(151.8, h=c.cur['h'] + 360, e='sm')
c.stance(152.0, w=0.05, rel=55)

c.mark(152, '[L15] – bourrée glide, reaching for a companion')
travel(152.2, 160, c.cur['x'] - 2.4, c.cur['y'])
c.steps(152.5, 15, every=0.5, w=0.045, lift=0.02, rel=55)
c.k(152.5, t=0.5, hip=(0, 0, 0.02), head=(-5, 0, 0), chest=(-4, 0, 0), spine=(0, 0, 0))
for i in range(4):
    b = 153 + 2 * i
    s = 1 if i % 2 == 0 else -1
    c.k(b, t=2, armL=A(0.8, 0.2, 0.4 * s), armR=A(0.8, 0.2, -0.4 * s), wr=(0, -20 * s, 0), wag=0.6)
c.k(156.5, t=1.2, head=(-5, -6, -35), armR=A(0.9, 0.4, 0.1), armL=A(0.5, 0.2, -0.3))

c.mark(160, '[L16] – vertical line, slow promenade')
c.stance(160.2, w=0.1)
c.k(160.8, t=0.8, e='out', armL=A(0.05, 0.05, 1), armR=A(0.12, 0.1, -1), poles=P_OUT, head=(-12, 0, 0), chest=(-4, 0, 0),
    hip=(0, 0, -0.04), sway=0, wag=0.3)
c.go(161, h=c.cur['h'])
c.go(167, h=c.cur['h'] + 360, e='sm')
c.steps(161.6, 6, every=1, w=0.1, lift=0.03)
c.k(164.5, t=2.5, armL=A(0.12, 0.1, -1), armR=A(0.05, 0.05, 1), head=(10, 0, 0))
c.k(167.5, t=1, head=(0, 0, 0))

c.mark(168, "[L17] – crescent arms, side bends")
c.k(168.6, t=0.8, e='out', arms=CRESCENT, poles=(0.6, 0.0, 0.3), wr=(0, -20, 0), head=(-10, 0, 0), chest=(-6, 0, 0),
    hip=(0, 0, 0.0))
c.stance(168.5, rel=35, w=0.08)
c.k(172.5, t=2, spine=(0, 14, 0), chest=(0, 12, 0), head=(0, 10, 0), hip=(-0.06, 0, -0.02))
c.k(174.5, t=1, spine=(0, 0, 0), chest=(0, 0, 0), head=(-10, 0, 0), hip=(0, 0, 0))
c.k(176.5, t=2, spine=(0, -14, 0), chest=(0, -12, 0), head=(0, -10, 0), hip=(0.06, 0, -0.02))
c.k(178.5, t=1.2, spine=(0, 0, 0), chest=(0, 0, 0), head=(-6, 0, 0), hip=(0, 0, 0))
c.k(179.6, t=0.8, e='out', arms=A(0.5, 0.6, -0.3), poles=P_LOW, hip=(0, 0, -0.14), spine=(10, 0, 0), head=(5, 0, 0))
c.stance(179.3, rel=0, w=0.12)

c.mark(180, "[L18] – body waves forward/back")
for i, b in enumerate([180, 182, 184, 186]):
    d = 1 if i % 2 == 0 else -1
    fx, fy = math.sin(math.radians(c.cur['h'])), -math.cos(math.radians(c.cur['h']))
    travel(b, b + 1.3, c.cur['x'] + fx * 0.35 * d, c.cur['y'] + fy * 0.35 * d)
    c.plant(b + 0.6, 'L', 0.1, 0, auto=True, dur=0.5)
    c.plant(b + 1.2, 'R', -0.1, 0, auto=True, dur=0.5)
    body_wave(b, d)
    if d > 0:
        c.k(b + 0.4, t=0.5, arms=A(0.3, 0.9, -0.4), wr=(0, 20, 0))
        c.k(b + 1.4, t=1.0, arms=A(0.35, 0.9, 0.3), wr=(0, -30, 0))
    else:
        c.k(b + 1.4, t=1.2, arms=A(0.5, -0.3, -0.6), wr=(0, 30, 0))
c.k(187.6, t=1.2, head=(-30, 0, 0), neck=(-10, 0, 0), arms=A(0.6, 0.4, -0.1), ears=-0.4)
c.flick(186.6)

# ======================================================================= ACT 2  戴上不属于自己的冠
c.mark(188, 'ACT2 戴上不属于自己的冠 | Crown descends')
c.k(188.8, t=0.8, head=(-38, 0, 0), neck=(-12, 0, 0), arms=A(0.4, 0.5, 0.4), wr=(0, -30, 0), ears=0.5, tail=(5, 0, 0))
c.k(192, t=0.25, e='hit', hip=(0, 0.04, -0.24), spine=(26, 0, 0), chest=(16, 0, 0), neck=(10, 0, 0), head=(18, 0, 0),
    arms=A(0.6, 0.3, -0.55), ears=1.0, tail=(-28, 0, 0), groove=0)
c.stance(192, w=0.15, dur=0.3)
c.mark(192, 'Struggle against the crown')
c.k(193, t=0.5, e='snap', arms=ON_HEAD, poles=(0.55, 0.0, 0.15), wr=(0, -40, 0), hip=(0, 0, -0.12), spine=(10, 0, 0),
    chest=(0, 0, 0), head=(0, 0, 0), neck=(0, 0, 0))
c.k(194, t=0.4, e='snap', chest=(-12, 0, 0), head=(-22, 0, 0), hip=(0, 0, -0.03))
c.k(195, t=0.3, e='hit', head=(20, 0, 0), chest=(14, 0, 0), hip=(0, 0.03, -0.2), spine=(14, 0, 0))
c.k(196, t=0.3, e='snap', neck=(0, 0, 28), head=(10, 8, 10))
c.k(196.5, t=0.3, e='snap', neck=(0, 0, -28), head=(10, -8, -10))
c.k(197, t=0.3, e='snap', neck=(0, 0, 24))
c.k(197.5, t=0.3, e='snap', neck=(0, 0, 0), head=(5, 0, 0))
offs = [(0.25, 0.3), (-0.3, 0.3), (0.35, 0.1), (-0.3, 0.35), (0.3, 0.2), (-0.2, 0.15)]
for i, b in enumerate([198, 199, 200, 201, 202, 203]):
    s = 1 if i % 2 == 0 else -1
    nx, ny = c.cur['x'] + offs[i][0], c.cur['y'] + offs[i][1]
    c.go(b - 0.4, x=c.cur['x'], y=c.cur['y'], h=c.cur['h'])
    c.go(b, x=nx, y=ny, h=c.cur['h'] + 25 * s, e='out')
    c.plant(b, 'L' if s > 0 else 'R', 0.12 * s, 0, auto=True, dur=0.4, lift=0.05)
    c.k(b, t=0.35, e='hit', chest=(8, 10 * s, 30 * s), spine=(10, 0, 12 * s), head=(10, 15 * s, -20 * s),
        armL=A(0.9, 0.2, 0.3) if s > 0 else (-0.12, 0.25, 0.05), armR=(-0.12, 0.25, 0.05) if s > 0 else A(0.9, 0.2, 0.3),
        poles=P_OUT, hip=(0.05 * s, 0, -0.12), wr=(0, -20, 0))
c.stance(203.6, w=0.12, dur=0.4)
c.k(204, t=0.4, e='out', armL=A(0.1, 1, 0.25), armR=A(0.4, 0.2, -0.6), poles=P_LOW, chest=(-4, 0, 0), head=(-10, 0, 0),
    spine=(0, 0, 0), hip=(0, 0, -0.06), neck=(0, 0, 0))
c.k(205, t=0.3, e='hit', armL=(-0.12, 0.20, -0.04), chest=(12, 0, 0), head=(15, 0, 0))
turn_to(205.2, 206.4, c.heading_to(1, 0))
c.k(207.6, t=1.8, e='in', hip=(0, 0.05, -0.40), spine=(34, 0, 0), chest=(12, 0, 0), head=(28, 0, 0),
    arms=(0.10, 0.12, -0.44), poles=(0.3, -0.2, -0.4), wr=(0, 30, 0), ears=1.0, tail=(-30, 25, 20))
c.plant(206.8, 'L', 0.13, -0.26, dur=0.6)
c.plant(207.5, 'R', -0.1, 0.42, rel=75, dur=0.6)
MIRROR2 = (c.cur['x'] + 0.95, c.cur['y'])          # mirror plane (normal +X) in front of her

c.mark(208, '镜中不是自己的脸 | The mirror: a reflection one beat late')
c.k(210.5, t=2.5, head=(0, 0, 0), spine=(20, 0, 0), chest=(4, 0, 0), ears=0.7)
c.k(215, t=3, hip=(0, 0, -0.06), spine=(4, 0, 0), chest=(0, 0, 0), head=(0, 0, 0), arms=ARM_DOWN, poles=P_DEF,
    tail=(-15, 0, 0), wr=(0, 10, 0))
c.plant(214, 'R', -0.1, 0.0, dur=0.8, lift=0.05)
c.plant(214.8, 'L', 0.1, 0, dur=0.6)
travel(216, 217.5, c.cur['x'] + 0.25, c.cur['y'])
c.plant(216.6, 'L', 0.1, 0, auto=True)
c.plant(217.4, 'R', -0.1, 0, auto=True)
c.k(218, t=2, armL=A(0.05, 1, 0.2, ext=1.0), poleL=P_LOW, wrL=(0, -50, 0), head=(-4, 0, 0), chest=(-4, 0, 0))
c.k(220.3, t=0.35, e='hit', armL=(-0.12, 0.22, 0.16), poleL=(0.4, 0.1, -0.35), wrL=(0, -10, 0), head=(10, 0, -40),
    neck=(0, 0, -15), chest=(8, 0, -10), hip=(0, 0.04, -0.10))
travel(220, 220.8, c.cur['x'] - 0.3, c.cur['y'], e='out')
c.plant(220.4, 'R', -0.1, 0, auto=True, dur=0.4)
c.plant(220.9, 'L', 0.1, 0, auto=True, dur=0.4)
c.k(220.5, t=0.8, gh_yaw=30)
c.k(228, t=2, gh_yaw=0)
c.k(224.5, t=1.5, arms=ON_HEAD, poles=(0.55, 0.0, 0.15), wr=(0, -40, 0), head=(12, 0, 0), neck=(0, 0, 0),
    chest=(12, 0, 0), spine=(8, 0, 0), hip=(0, 0, -0.12))
c.k(225.5, t=1, spine=(8, 8, 0))
c.k(226.5, t=1, spine=(8, -8, 0))
c.k(227.5, t=1, spine=(8, 6, 0))
c.mark(228, 'Tries the old playful fox steps – the crown drags her down')
c.k(228.6, t=0.5, e='snap', arms=PAW, poles=(0.25, 0.05, -0.45), wr=(0, 70, 0), spine=(16, 0, 0), head=(-10, 0, 0),
    hip=(0, 0, -0.08), ears=0.1, tail=(10, 0, 0))
jump(229.2, 229.8, 0.08, prep=False)
jump(230.1, 230.6, 0.06, prep=False)
c.k(231, t=0.3, e='hit', hip=(0, 0.05, -0.24), spine=(30, 0, 0), head=(25, 0, 0), arms=A(0.4, 0.4, -0.6), poles=P_DEF,
    wr=(0, 20, 0), ears=1.0, tail=(-25, 0, 0))
c.stance(231.2, w=0.14, dur=0.3)
c.k(233, t=1.5, hip=(0, 0, -0.07), spine=(6, 0, 0), chest=(4, 0, 0), head=(5, 0, 0), arms=(0.08, 0.06, -0.47),
    wr=(0, 15, 0), ears=0.8, tail=(-20, 0, 0))
ty = c.heading_to(TOWN[0] - c.cur['x'], TOWN[1] - c.cur['y']) - c.cur['h']
c.k(235, t=1.5, head=(-4, 0, max(-60, min(60, ty))))

# ---- verse 2
c.mark(236, '[L19] – facing the town, walking toward it')
ht = c.heading_to(TOWN[0] - c.cur['x'], TOWN[1] - c.cur['y'])
turn_to(236, 237.2, ht)
c.k(237.5, t=1, armR=(-0.08, 0.25, 0.18), poleR=(0.45, 0.0, -0.25), wrR=(0, 40, 0), head=(-6, 0, 0), neck=(0, 0, 0),
    ears=0.3)
d = Vector((TOWN[0] - c.cur['x'], TOWN[1] - c.cur['y'])).normalized()
travel(239.5, 243.8, c.cur['x'] + d.x * 1.2, c.cur['y'] + d.y * 1.2)
c.steps(240, 4, every=1, first='L', lift=0.05)
c.k(242, t=2, armL=A(0.1, 0.85, 0.3), poleL=P_LOW, wrL=(0, -25, 0), armR=A(0.2, 0.3, -0.9), poleR=P_DEF)
c.mark(244, '[L21] – eager, then pulled back')
travel(244, 247.8, c.cur['x'] + d.x * 1.0, c.cur['y'] + d.y * 1.0)
c.steps(244.2, 7, every=0.5, lift=0.06)
c.k(246, t=1.5, arms=A(0.15, 0.9, 0.35), poles=P_LOW, wr=(0, -30, 0), chest=(-6, 0, 0), head=(-10, 0, 0), ears=-0.2,
    tail=(10, 0, 0))
travel(248, 249.6, c.cur['x'] - d.x * 0.6, c.cur['y'] - d.y * 0.6, e='out')
c.steps(248.2, 4, every=0.4, lift=0.04)
c.k(248.3, t=0.3, e='hit', chest=(-18, 0, 0), spine=(-8, 0, 0), head=(-5, 0, 0), hip=(0, 0.08, -0.10),
    arms=A(0.15, 0.9, 0.2))
c.k(250, t=1, arms=ARM_DOWN, poles=P_DEF, chest=(4, 0, 0), spine=(4, 0, 0), head=(10, 0, 0), wr=(0, 10, 0))
c.stance(250.2)
c.k(252.4, t=1.4, arms=HUG, poles=(0.4, -0.1, -0.4), head=(20, 10, 0), ears=0.9, tail=(-15, 45, 30), hip=(0, 0, -0.10))
turn_to(254, 256, front())
c.mark(256, 'A glow appears – the 情匣')
BOX_POS = Vector((c.cur['x'], c.cur['y'] - 0.95, 1.15))
c.k(258, t=0.35, e='snap', head=(-6, 0, 0), hip=(0, 0, -0.06), chest=(-4, 0, 0), arms=A(0.3, 0.2, -0.8), ears=-0.3,
    tail=(15, 0, 0))
c.flick(258)
travel(259, 262, c.cur['x'], c.cur['y'] - 0.55)
c.steps(259.4, 3, every=1)
c.k(262.5, t=1.5, arms=(-0.075, 0.30, -0.02), poles=P_LOW, wr=(0, -10, 0), head=(10, 0, 0))
c.stance(262.6)

# ======================================================================= ACT 3  璇情燃尽
c.mark(264, 'ACT3 璇情燃尽 | Shimmering fire – receiving the burning box')
c.k(266, t=1, arms=HOLD_BOX, hip=(0, 0, -0.18), spine=(4, 0, 0), chest=(0, 0, 0), head=(-5, 0, 0), ears=-0.1,
    tail=(10, 0, 0))
c.stance(265.5, w=0.21, dur=0.6, lift=0.06)
c.mark(268, 'a speaking heart – box to the chest, sharp twist')
c.k(268, t=1.2, arms=(-0.09, 0.17, -0.06), poles=(0.4, -0.1, -0.4), hip=(0, 0, -0.10), chest=(6, 0, 0))
c.k(270, t=0.35, e='hit', chest=(0, 0, 35), spine=(0, 0, 10), head=(-5, 0, 25), hip=(0.06, 0, -0.14))
c.k(271.2, t=0.6, chest=(0, 0, 0), spine=(0, 0, 0), head=(0, 0, 0), hip=(0, 0, -0.1))
c.mark(272, '[L23] – whip turns with the box overhead')
c.stance(271.8, w=0.1)
c.k(272.5, t=0.6, arms=OVERHEAD, poles=P_UP, wr=(0, -25, 0), hip=(0, 0, -0.12))
pirouette(273, 274, 1, support='L', arms=False)
c.air(274.3, 'R', -0.45, -0.05, 0.50, p=60, dur=0.25)
c.k(274.4, t=0.3, e='snap', hip=(0.04, 0, -0.02), chest=(0, -10, 0))
pirouette(275, 276, 1, support='L', arms=False, prep=False)
c.stance(276.3, w=0.2, dur=0.3)
c.k(276.5, t=0.3, e='hit', hip=(0, 0, -0.2), chest=(0, 0, 0))
c.k(277, t=0.3, e='snap', arms=(-0.075, 0.42, 0.02), poles=P_LOW, chest=(10, 0, 0), head=(-8, 0, 0))
c.k(278.2, t=0.6, chest=(0, 0, -30), head=(0, 0, -20), arms=HOLD_BOX)
c.k(279.5, t=0.8, chest=(0, 0, 0), head=(0, 0, 0))
c.mark(280, '[L24] – box lifted overhead, it flares')
c.k(283, t=3, arms=(-0.075, 0.08, 0.47), poles=P_UP, wr=(0, -30, 0), chest=(-16, 0, 0), spine=(-6, 0, 0),
    head=(-30, 0, 0), hip=(0, 0, 0.02), ears=-0.4, tail=(30, 0, 10))
c.stance(281, w=0.1, rel=45, dur=0.6)
c.k(284, tremble=0)
c.k(285, t=1, tremble=1.0)
c.k(287.5, t=1.5, arms=(-0.075, 0.15, 0.40), tremble=1.4, chest=(-8, 0, 0), head=(-20, 0, 0))
c.mark(288, '[L25] – she kneels, the box burns away in her hands')
c.k(290, t=2, hip=(0, 0.05, -0.40), spine=(20, 0, 0), chest=(8, 0, 0), head=(15, 0, 0), arms=(-0.08, 0.24, -0.12),
    poles=(0.4, -0.1, -0.4), wr=(0, 0, 0), tremble=0.6, tail=(-20, 40, 30), ears=0.6)
c.plant(288.6, 'L', 0.13, -0.26, dur=0.6)
c.plant(289.4, 'R', -0.1, 0.42, rel=75, dur=0.6)
c.k(294.3, t=0.8, arms=(0.06, 0.30, -0.14), poles=P_LOW, wr=(70, 0, 0), head=(30, 0, 0), tremble=0, ears=1.0,
    tail=(-25, 50, 40))
c.k(295.6, t=1.2, chest=(-4, 0, 0), head=(18, 0, 0))

# ======================================================================= ACT 4  溯心
c.mark(296, 'ACT4 溯心 | Crown shatters – rebirth')
c.k(296.5, t=0.5, e='out', hip=(0, 0, 0.03), spine=(-6, 0, 0), chest=(-14, 0, 0), head=(-26, 0, 0), neck=(-5, 0, 0),
    arms=A(0.75, 0.2, 0.65), poles=P_OUT, wr=(0, -30, 0), ears=-0.5, tail=(40, 0, 0), wag=0.0)
c.stance(296.4, w=0.11, rel=40, dur=0.4, lift=0.04)
c.flick(296.5)
c.mark(297, '[L26]')
hm = c.heading_to(MOON[0] - c.cur['x'], MOON[1] - c.cur['y'])
turn_to(297, 298.5, hm)
c.k(298.6, t=1.5, arms=A(0.45, 0.15, 0.9), chest=(-18, 0, 0), head=(-28, 0, 0), neck=(0, 0, 0))
turn_to(299.8, 300.8, front())
c.k(301.2, t=0.8, e='snap', arms=(-0.07, 0.21, 0.19), poles=P_OUT, wr=(0, -15, 0), head=(-6, 12, 0), chest=(0, 0, 0),
    hip=(0.04, 0, -0.05), ears=-0.3)
c.flick(302, 'L')
turn_to(303, 304, c.heading_to(1, 0))
c.k(303.8, t=0.8, arms=A(0.5, 0.3, -0.6), poles=P_DEF, head=(0, 0, 0), hip=(0, 0, -0.05))
Q = (c.cur['x'], c.cur['y'])
MIRROR4 = (Q[0] + 1.0, Q[1])

c.mark(304, '[L27] – duet with her true self (本体)')
c.k(304.6, t=0.6, e='out', arms=A(0.6, 0.15, 0.8), poles=P_OUT, hip=(0, 0, 0.0), chest=(-8, 0, 0))
c.stance(304.5, rel=35, w=0.09)
c.go(305.6, x=Q[0])
c.go(306.6, x=Q[0] + 0.3, e='out')
c.plant(306.4, 'L', 0.11, -0.32, dur=0.6)
c.k(306.8, t=1, arms=A(0.5, 0.75, -0.5), wr=(0, 30, 0), spine=(14, 0, 0), head=(18, 0, 0), hip=(0, -0.08, -0.2),
    chest=(0, 0, 0))
c.go(307.8, x=Q[0] + 0.3)
c.go(308.8, x=Q[0], e='sm')
c.stance(308.6)
c.k(309, t=1, arms=A(0.85, 0.0, 0.3), hip=(0, 0, -0.04), spine=(0, 0, 0), head=(-8, 0, 0), wr=(0, -10, 0))
c.go(309.6, x=Q[0])
c.go(310.6, x=Q[0] + 0.3, e='out')
c.plant(310.4, 'R', -0.11, -0.32, dur=0.6)
c.k(310.8, t=1, arms=A(0.9, 0.35, -0.4), wr=(0, -30, 0), hip=(0, -0.08, -0.2), spine=(8, 0, 0), head=(15, 0, 0))
c.mark(312, '[L28] – mirrored circling')
c.k(311.8, t=0.6, hip=(0, 0, -0.06), spine=(0, 0, 0), head=(0, 0, 0))
path([(312, Q[0] + 0.3, Q[1]), (314, Q[0] - 0.3, Q[1] - 0.9), (316, Q[0] - 0.7, Q[1]), (318, Q[0] - 0.3, Q[1] + 0.9),
      (320, Q[0] + 0.1, Q[1])])
c.steps(312.4, 15, every=0.5, lift=0.05, rel=20)
c.k(313, t=1, arms=A(0.8, 0.2, 0.4))
c.k(315, t=2, armL=A(0.8, 0.2, 0.6), armR=A(0.8, 0.2, -0.2))
c.k(317, t=2, armL=A(0.8, 0.2, -0.2), armR=A(0.8, 0.2, 0.6))
c.k(319, t=2, arms=A(0.8, 0.3, 0.2))
c.mark(320, '[L29] – tour en l\'air together')
turn_to(320.0, 320.6, c.heading_to(1, 0), steps=False)
c.k(321, t=1, arms=A(0.4, 0.2, 0.9), head=(-15, 0, 0))
c.stance(320.6, rel=35)
hm = c.heading_to(MOON[0] - c.cur['x'], MOON[1] - c.cur['y'])
turn_to(321.8, 322.8, hm)
c.k(323.8, t=0.6, arms=OVERHEAD, poles=P_UP)
jump(324, 325.2, 0.32, kind='tuck', turn=360)
c.k(326, t=1, arms=A(0.55, 0.15, 0.85), poles=P_OUT, chest=(-14, 0, 0), head=(-28, 0, 0))
c.stance(325.4)
c.mark(328, '[L30] – palms meet, she merges with her true self')
turn_to(327.8, 328.8, c.heading_to(1, 0))
c.k(328.5, t=1, chest=(0, 0, 0), head=(0, 0, 0), arms=ARM_DOWN, poles=P_DEF)
travel(329, 330.5, Q[0] + 0.45, Q[1])
c.steps(329.3, 3, every=0.6)
c.k(331, t=1.2, armL=A(0.05, 1, 0.25, ext=1.0), poleL=P_LOW, wrL=(0, -55, 0), armR=A(0.3, 0.3, -0.8), head=(-5, 0, 0))
c.k(333.5, t=1.5, head=(12, 0, 0), chest=(4, 0, 0), armL=HEART, poleL=(0.4, -0.1, -0.35), wrL=(0, 10, 0))
c.k(335.6, t=1.2, e='out', arms=A(0.8, 0.3, 0.3), poles=P_OUT, head=(-15, 0, 0), chest=(-10, 0, 0))
c.mark(336, '[L31] – reborn: jump-turn, triple pirouette, jeté')
c.k(336.2, t=0.4, arms=OVERHEAD, poles=P_UP)
jump(336.4, 337.6, 0.40, kind='tuck', turn=360)
c.k(338, t=0.4, arms=A(0.8, 0.4, 0.1), poles=P_OUT)
pirouette(338.4, 340, 3, support='L')
hj = c.heading_to(0.7, -0.7)
turn_to(340.1, 340.5, hj, steps=False)
fx, fy = math.sin(math.radians(hj)), -math.cos(math.radians(hj))
travel(340.5, 341.8, c.cur['x'] + fx * 1.5, c.cur['y'] + fy * 1.5, e='lin')
c.k(340.6, t=0.4, e='out', armL=A(0.25, 0.8, 0.5), armR=A(0.5, -0.55, 0.25), chest=(-10, 0, 0), head=(-20, 0, 0))
jump(340.5, 341.8, 0.40, kind='split', land='L', prep=False)
c.k(342.2, t=0.6, e='out', armL=A(0.3, 0.6, 0.8), armR=A(0.9, -0.2, 0.0), hip=(0, -0.06, -0.18), chest=(-10, 0, 0),
    head=(-20, 0, 0))
c.plant(342.3, 'L', 0.12, -0.35, dur=0.4)
c.plant(342.5, 'R', -0.1, 0.3, dur=0.4, rel=30)
c.mark(344, 'Breath – moonlight rain, she walks toward us')
turn_to(344.6, 345.4, front(), steps=False)
travel(345.5, 352, c.cur['x'], c.cur['y'] - 1.6)
c.steps(346, 6, every=1, lift=0.05)
c.k(346, t=2, arms=A(0.5, 0.4, 0.6), hip=(0, 0, -0.05), chest=(-4, 0, 0), head=(-5, 0, 0), poles=P_OUT)
c.k(348, t=2, arms=A(0.8, 0.2, -0.2))
c.k(350, t=2, arms=A(0.5, 0.4, 0.5))
c.k(352, t=2, arms=A(0.4, 0.2, -0.6), head=(0, 10, 0), poles=P_DEF)
c.stance(352.6)
c.flick(352)
c.k(354, t=2, sway=0.025, wag=0.8)
c.k(356, t=1, sway=0)

# ======================================================================= ACT 5  心有所归
c.mark(356, 'ACT5 心有所归 | Moon up high (reprise) – lantern sway, warmer')
lantern_sway(356, warm=True)
c.k(362.5, t=0.5, e='snap', head=(-10, 6, 30))
c.k(363.5, t=0.5, e='snap', head=(-10, -6, -30))
c.flick(362.6)
c.mark(364, '[L33] – joyful run around the stage')
cx, cy = 0.0, 0.0
a0 = math.atan2(c.cur['y'] - cy, c.cur['x'] - cx)
pts = [(364 + i, cx + math.cos(a0 + i * 0.6) * 1.8, cy + math.sin(a0 + i * 0.6) * 1.8) for i in range(9)]
pts[0] = (364, c.cur['x'], c.cur['y'])
c.go(363.8, h=c.cur['h'])
path(pts)
c.k(364.3, t=0.5, e='out', armL=A(0.2, 0.8, 0.6), armR=A(0.5, -0.6, -0.2), poles=P_OUT, spine=(10, 0, 0), head=(-12, 0, 0),
    ears=-0.4, wag=0, chest=(-4, 0, 0), sway=0)
c.steps(364.5, 7, every=0.5, lift=0.13, rel=20)
jump(368, 369, 0.25, kind='split', land='L', prep=False)
c.steps(369.5, 5, every=0.5, lift=0.12, rel=20, first='R')
c.stance(372.4)
c.mark(372, '[L34] – slow promenade, hand on heart')
c.k(372.5, t=1, armL=A(0.3, 0.9, 0.5), armR=HEART, poleR=(0.4, -0.1, -0.35), spine=(0, 0, 0), head=(-10, 0, 0),
    chest=(-4, 0, 0))
c.go(372.5, h=c.cur['h'])
c.go(378, h=c.cur['h'] + 360, e='sm')
c.steps(373, 5, every=1, lift=0.03)
turn_to(378.4, 379.6, front())
c.mark(380, '[L35] – offering to the moon, a bow to the people')
c.k(380.8, t=1, armL=HEART, poleL=(0.4, -0.1, -0.35), armR=A(0.3, 0.5, 0.85), poleR=P_OUT, wrR=(0, -30, 0),
    head=(-12, -8, 0), chest=(-6, 0, 0), ears=-0.3, tail=(20, 0, 0), wag=0.8)
c.k(384.6, t=1.2, spine=(22, 0, 0), chest=(10, 0, 0), head=(18, 0, 0), armR=(-0.10, 0.20, -0.10), poleR=(0.4, -0.1, -0.35),
    hip=(0, 0.05, -0.08), ears=0.2)
c.k(386.6, t=1.2, spine=(0, 0, 0), chest=(0, 0, 0), head=(-4, 10, 0), hip=(0, 0, -0.04), arms=ARM_DOWN, poles=P_DEF,
    wag=1.2, wr=(0, 10, 0))
c.flick(386.5)
c.mark(388, 'Home – she sits facing the moon, tail wrapped around her')
hm = c.heading_to(MOON[0] - c.cur['x'], MOON[1] - c.cur['y'])
turn_to(388, 389.5, hm)
c.k(393.5, t=3.5, hip=(0, 0.10, -0.53), spine=(6, 0, 0), chest=(0, 0, 0), head=(-26, 0, 0), neck=(-8, 0, 0),
    arms=(-0.05, 0.24, -0.36), poles=(0.35, -0.2, -0.35), wr=(0, 15, 0), tail=(-20, 60, 45), ears=0.0, wag=0.0)
c.plant(391, 'L', 0.1, 0.36, rel=85, dur=1.0, lift=0.04)
c.plant(392, 'R', -0.1, 0.36, rel=85, dur=1.0, lift=0.04)
c.k(400, t=4, wag=0.5)
c.flick(404, 'L')
c.flick(410)
c.k(412, t=4, wag=0.0, head=(-30, -8, 0))
c.mark(417, 'END')


# ======================================================================= camera shots
def orbit(b0, b1, a, r, z, lz, lens, **kw):
    return dict(b0=b0, b1=b1, type='orbit', a=a, r=r, z=z, lz=lz, lens=lens, **kw)


def pathshot(b0, b1, p0, p1, lz, lens, **kw):
    return dict(b0=b0, b1=b1, type='path', p=(p0, p1), lz=lz, lens=lens, **kw)


SHOTS = [
    pathshot(0, 12, (0.0, -14, 10), (0.6, -4.6, 1.25), 1.1, (30.0, 35.0), look_moon=(1.0, 0.0), e='sm', fstop=8),
    orbit(12, 16, (5.0, 0.0), (4.4, 3.4), 1.3, 1.1, 35.0, rel=False, fstop=5.6),
    orbit(16, 24, (0.0, 15.0), (3.2, 2.6), 1.3, 1.15, 40.0, fstop=2.8),
    orbit(24, 32, (35.0, 25.0), (2.3, 2.0), 1.45, 1.3, 55.0, fstop=2.4),
    orbit(32, 44, 70.0, 3.2, 0.55, 0.85, 32.0, e='lin', fstop=4),
    orbit(44, 48, (30.0, 50.0), 2.4, 0.35, 0.6, 24.0, fstop=4),
    pathshot(48, 52, (0.0, 0.01, 6.0), (0.0, 0.01, 5.0), 0.5, 28.0, p_rel=True, roll=(0.0, 120.0), fstop=8),
    orbit(52, 56, (10.0, 0.0), (2.6, 2.3), 1.3, 1.2, 50.0, rel=False, fstop=2.8),
    orbit(56, 68, (-30.0, 30.0), 6.5, 2.2, 1.0, 24.0, rel=False, fstop=8),
    orbit(68, 76, (35.0, -40.0), 4.0, 0.45, 0.9, 22.0, rel=False, e='lin', fstop=8),
    orbit(76, 84, (-20.0, 20.0), 3.4, 1.1, 1.25, 35.0, fstop=4),
    orbit(84, 92, (205.0, 190.0), 3.2, 0.45, 1.3, 26.0, look_moon=(0.0, 0.03), fstop=8),
    orbit(92, 96, 0.0, 4.5, 1.2, 1.0, 30.0, rel=False, fstop=5.6),
    orbit(96, 104, (55.0, 35.0), 2.6, 0.8, 0.8, 40.0, fstop=2.4),
    orbit(104, 112, (-40.0, 140.0), 3.8, (0.6, 1.5), 1.3, 28.0, fstop=5.6),
    orbit(112, 128, (0.0, -8.0), (4.5, 1.9), 1.4, 1.3, (40.0, 60.0), fstop=2.8),
    orbit(128, 134, (150.0, 125.0), 3.6, 0.5, 1.2, 26.0, fstop=8),
    orbit(134, 140, 0.0, 5.0, 1.0, 1.0, 30.0, rel=False, e='lin', fstop=8),
    orbit(140, 152, (-30.0, 30.0), 3.4, 1.3, 1.1, 40.0, fstop=4),
    orbit(152, 160, 10.0, 4.8, 1.0, 1.0, 32.0, rel=False, fstop=5.6),
    pathshot(160, 168, (0.0, 0.01, 7.5), (0.0, 0.01, 6.0), 0.8, 35.0, p_rel=True, roll=(0.0, -120.0), fstop=8),
    orbit(168, 180, (0.0, 10.0), (2.6, 6.0), (1.5, 2.0), (1.3, 1.2), (50.0, 30.0), fstop=4),
    orbit(180, 188, (70.0, 50.0), 3.8, 1.0, 1.0, 35.0, fstop=5.6),
    # act 2
    pathshot(188, 192, (0.5, -1.6, 4.5), (0.4, -1.3, 3.8), 1.5, 28.0, p_rel=True, fstop=5.6),
    orbit(192, 196, 25.0, 2.6, 1.5, 1.2, 38.0, shake=1.0, roll=8.0, fstop=4),
    orbit(196, 200, -50.0, 2.4, 0.7, 1.2, 32.0, shake=1.2, roll=-12.0, fstop=4),
    orbit(200, 204, 30.0, 3.5, 1.8, 1.0, 28.0, rel=False, shake=1.2, roll=10.0, fstop=5.6),
    orbit(204, 208, 10.0, (2.5, 3.2), 1.2, 0.9, 35.0, shake=0.6, roll=-6.0, fstop=4),
    orbit(208, 220, 0.0, (4.2, 3.4), 1.0, 0.9, 35.0, rel=False, tgt='mid', roll=(0.0, -4.0), fstop=5.6),
    orbit(220, 228, -60.0, 2.5, 1.4, 1.25, 45.0, fstop=2.4),
    orbit(228, 237.5, 0.0, (3.6, 4.6), 1.4, 1.0, 30.0, rel=False, tgt='mid', fstop=5.6),
    orbit(237.5, 248, 160.0, 2.4, 1.7, 1.2, 35.0, look_pt=(TOWN[0], TOWN[1], 2.0), look_w=(0.05, 0.09), fstop=4),
    orbit(248, 256, 0.0, (3.2, 2.4), 1.3, 1.2, 40.0, fstop=2.8),
    orbit(256, 264, (40.0, 20.0), (3.0, 2.5), 1.25, 1.1, 40.0, fstop=2.4),
    # act 3
    orbit(264, 280, (-60.0, 120.0), 3.0, 0.5, 1.1, 26.0, shake=0.4, fstop=4),
    orbit(280, 288, 15.0, 2.6, 0.2, 1.7, 22.0, fstop=5.6),
    pathshot(288, 296, (0.3, -1.2, 3.8), (0.2, -0.8, 2.6), 0.7, 40.0, p_rel=True, fstop=2.8),
    # act 4
    orbit(296, 304, (0.0, 20.0), (1.4, 5.5), (1.2, 2.2), 1.3, (35.0, 24.0), e='out', fstop=5.6),
    orbit(304, 320, 0.0, (5.0, 4.4), 1.1, 1.0, 30.0, rel=False, tgt='mid', fstop=5.6),
    orbit(320, 328, (0.0, -80.0), 5.0, (1.5, 0.6), 1.2, 26.0, rel=False, tgt='mid', fstop=5.6),
    orbit(328, 336, 0.0, (2.6, 2.2), 1.4, 1.35, 45.0, rel=False, tgt='mid', fstop=2.4),
    orbit(336, 344, (-30.0, 60.0), 3.4, 0.35, 1.0, 22.0, fstop=5.6),
    orbit(344, 356, 0.0, (7.5, 6.0), 1.4, 1.3, 85.0, rel=False, fstop=2.0),
    # act 5
    orbit(356, 364, (0.0, 10.0), 3.0, 1.3, 1.2, 45.0, rel=False, fstop=2.8),
    orbit(364, 372, (0.0, 120.0), 7.5, 3.5, 0.8, 28.0, rel=False, tgt=(0.0, 0.0, 0.0), fstop=8),
    orbit(372, 380, (0.0, -40.0), 3.6, 1.2, 1.1, 38.0, fstop=2.8),
    orbit(380, 388, 0.0, 3.0, 0.8, 1.4, 45.0, rel=False, fstop=2.2),
    pathshot(388, 420, (0.0, -2.6, 1.0), (0.0, -14.0, 9.0), (1.0, 1.0), (35.0, 28.0), p_rel=True, look_moon=(0.0, 0.35),
             e='smm', fstop=8),
]


# ======================================================================= build
def build():
    rng = random.Random(11)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scn = bpy.context.scene
    scn.name = 'HsinDance'
    scn.render.fps = E.FPS
    scn.frame_start, scn.frame_end = 1, E.END_FRAME
    mats = R.make_materials()
    lead = R.build_actor('Hsin', mats=mats)
    ghost_m = R.ghost_mat()
    dbl = R.build_actor('TrueSelf', ghost=ghost_m)
    poles_lead = R.calibrate_poles(lead)
    poles_dbl = R.calibrate_poles(dbl)
    print('IK pole angles', poles_lead)
    S = R.build_stage(rng)
    P = R.build_props(lead, mats, rng)

    # ---------------------------------------------------- dance bake
    bake = E.ActorBake(c, lead)
    data = bake.compute()
    bake.write(lead, data, bake.frames)

    def plane_fn(b):
        if b < 270:
            return Vector((MIRROR2[0], MIRROR2[1], 0)), Vector((1, 0, 0))
        x = MIRROR4[0]
        if b > 332:
            u = E.ease((b - 332) / 3.5, 'sm')
            x = MIRROR4[0] + (Q[0] + 0.45 - MIRROR4[0]) * u
        return Vector((x, MIRROR4[1], 0)), Vector((1, 0, 0))

    ddata = E.double_data(data, plane_fn, lambda b: 1.0 if b < 270 else 0.0, lambda b: bake.ev.get('gh_yaw', b))
    E.ActorBake.write(bake, dbl, ddata, bake.frames)

    # ghost visibility + look per act
    nodes = ghost_m.node_tree.nodes
    al, gl, tint = nodes['alpha'].outputs[0], nodes['glow'].outputs[0], nodes['tint'].outputs[0]
    for b, a, g, col in [(-1, 0, 1.2, (0.45, 0.25, 0.75)), (207.5, 0, 1.2, (0.45, 0.25, 0.75)),
                         (212, 0.6, 1.2, (0.45, 0.25, 0.75)), (232, 0.6, 1.2, (0.45, 0.25, 0.75)),
                         (236, 0.0, 1.2, (0.45, 0.25, 0.75)), (300, 0.0, 2.5, (0.6, 0.9, 1.0)),
                         (304.5, 0.85, 2.5, (0.6, 0.9, 1.0)), (332, 0.85, 3.0, (0.6, 0.9, 1.0)),
                         (335.6, 0.9, 9.0, (0.9, 0.97, 1.0)), (336.6, 0.0, 2.0, (0.9, 0.97, 1.0))]:
        f = max(1, E.FR(b))
        al.default_value = a
        al.keyframe_insert('default_value', frame=f)
        gl.default_value = g
        gl.keyframe_insert('default_value', frame=f)
        tint.default_value = (*col, 1)
        tint.keyframe_insert('default_value', frame=f)
    for o in (dbl['body'],):
        for b, hide in [(-1, True), (207.5, False), (236.5, True), (300, False), (337, True)]:
            o.hide_render = hide
            o.hide_viewport = hide
            o.keyframe_insert('hide_render', frame=max(1, E.FR(b)))
            o.keyframe_insert('hide_viewport', frame=max(1, E.FR(b)))
    dbl['arm'].hide_render = True

    # ---------------------------------------------------- props
    crown = P['crown']
    for b, z, sc in [(-1, 3.0, 0.0), (186.8, 3.0, 0.0), (187.4, 3.0, 1.0), (188, 3.0, 1.0), (192, 0.0, 1.0),
                     (296, 0.0, 1.0), (296.15, 0.0, 0.0)]:
        crown.location = (0, 0, z)
        crown.scale = (sc, sc, sc)
        crown.keyframe_insert('location', index=2, frame=max(1, E.FR(b)))
        crown.keyframe_insert('scale', frame=max(1, E.FR(b)))
    # shards fly from the crown position at the shatter
    scn.frame_set(int(E.FR(296)))
    cpos = crown.matrix_world.translation.copy()
    f0 = int(E.FR(296))
    for i, sh in enumerate(P['shards']):
        v = Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(0.3, 1.2))).normalized() * rng.uniform(2.0, 4.0)
        spin = Vector((rng.uniform(-12, 12), rng.uniform(-12, 12), rng.uniform(-12, 12)))
        for k in range(0, 50, 2):
            t = k / E.FPS
            p = cpos + v * t + Vector((0, 0, -4.9 * t * t))
            p.z = max(0.02, p.z)
            sh.location = p
            sh.rotation_euler = spin * t
            s = 1.0 if k < 30 else max(0.0, 1 - (k - 30) / 20)
            sh.scale = (s, s, s)
            for prop in ('location', 'rotation_euler', 'scale'):
                sh.keyframe_insert(prop, frame=f0 + k)
        sh.scale = (0, 0, 0)
        sh.keyframe_insert('scale', frame=f0 - 1)
        sh.keyframe_insert('scale', frame=f0 + 52)

    box = P['box']
    box.location = BOX_POS
    for b, sc in [(-1, 0.0), (255.5, 0.0), (257, 1.0), (290, 1.0), (294, 0.0)]:
        box.scale = (sc, sc, sc)
        box.keyframe_insert('scale', frame=max(1, E.FR(b)))
    for b, inf in [(-1, 0.0), (264, 0.0), (266, 1.0)]:
        P['box_c1'].influence = inf
        P['box_c1'].keyframe_insert('influence', frame=max(1, E.FR(b)))
        P['box_c2'].influence = inf * 0.5
        P['box_c2'].keyframe_insert('influence', frame=max(1, E.FR(b)))
    em = P['box_mat'].node_tree.nodes['Emission'].inputs['Strength']
    lamp = P['box_lamp']
    for b, s, lw in [(-1, 0, 0), (256, 0, 0), (262, 6, 30), (266, 15, 120), (283.5, 20, 200), (284.3, 70, 700),
                     (288, 25, 220), (292, 10, 80), (294.5, 0, 0)]:
        em.default_value = s
        em.keyframe_insert('default_value', frame=max(1, E.FR(b)))
        lamp.energy = lw
        lamp.keyframe_insert('energy', frame=max(1, E.FR(b)))

    # ---------------------------------------------------- particles
    def instance(name, color, strength, r):
        o = R.add_obj(name, R.prim_mesh('ico', r=r, sub=1), R.emit_mat(name + 'Mat', color, strength), (0, 0, -50))
        return o
    ember = instance('Ember', (1.0, 0.45, 0.1), 12, 0.012)
    spark = instance('Spark', (0.75, 0.9, 1.0), 14, 0.014)
    mote = instance('Mote', (0.85, 0.9, 1.0), 10, 0.01)
    R.particle_system(box, 'Embers', int(E.FR(262)), int(E.FR(294)), 900, 40, ember, vel_n=0.25, rnd=0.3, grav=-0.12)
    R.particle_system(box, 'Flare', int(E.FR(284.2)), int(E.FR(285.2)), 500, 34, ember, vel_n=1.6, rnd=0.8, grav=-0.05,
                      drag=0.3)
    R.particle_system(box, 'Dissolve', int(E.FR(290)), int(E.FR(294)), 700, 60, ember, vel_n=0.4, rnd=0.6, grav=-0.25)
    hw = data[int(E.FR(296))]['hip_w']
    burst = R.add_obj('RebirthBurst', R.prim_mesh('ico', r=0.25, sub=2), None, hw + Vector((0, 0, 0.35)))
    R.particle_system(burst, 'Rebirth', int(E.FR(296)), int(E.FR(296.8)), 900, 50, spark, vel_n=3.0, rnd=1.0, drag=0.55)
    burst.hide_render = False
    rain = R.add_obj('MoonRain', R.prim_mesh('circle', r=6, seg=32), None, (0, -0.5, 7.5))
    R.particle_system(rain, 'MoonRain', int(E.FR(299)), E.END_FRAME, 2600, 140, mote, vel_n=-0.25, rnd=0.15, grav=0.03)

    # ---------------------------------------------------- lights & atmosphere by act
    bg_c, bg_s = S['bg'].inputs['Color'], S['bg'].inputs['Strength']
    lan = S['lantern_mat'].node_tree.nodes['Emission'].inputs['Strength']
    win = S['window_mat'].node_tree.nodes['Emission'].inputs['Strength']
    ring = S['ring_mat'].node_tree.nodes['Emission'].inputs['Strength']
    cues = [
        # beat, sun, sun_col, fill, fill_col, rim, bg, lantern, windows, ring
        (-1, 2.2, (0.72, 0.8, 1.0), 120, (1.0, 0.62, 0.36), 0, (0.012, 0.018, 0.045), 6, 8, 1.5),
        (186, 2.2, (0.72, 0.8, 1.0), 120, (1.0, 0.62, 0.36), 0, (0.012, 0.018, 0.045), 6, 8, 1.5),
        (192, 0.7, (0.55, 0.5, 0.8), 25, (0.5, 0.5, 0.9), 900, (0.006, 0.004, 0.014), 1.5, 8, 0.4),
        (236, 0.7, (0.55, 0.5, 0.8), 25, (0.5, 0.5, 0.9), 600, (0.006, 0.004, 0.014), 1.5, 16, 0.4),
        (262, 0.8, (0.6, 0.5, 0.7), 60, (1.0, 0.5, 0.25), 200, (0.02, 0.008, 0.006), 1.5, 10, 0.4),
        (295.8, 0.8, (0.6, 0.5, 0.7), 40, (1.0, 0.5, 0.25), 0, (0.01, 0.006, 0.006), 1.0, 8, 0.3),
        (296.2, 12.0, (0.95, 0.97, 1.0), 300, (0.85, 0.9, 1.0), 0, (0.03, 0.04, 0.1), 10, 8, 4.0),
        (300, 3.5, (0.8, 0.88, 1.0), 140, (0.85, 0.9, 1.0), 0, (0.02, 0.03, 0.08), 9, 8, 2.5),
        (354, 3.0, (0.8, 0.88, 1.0), 140, (0.9, 0.85, 0.9), 0, (0.02, 0.03, 0.07), 9, 8, 2.0),
        (360, 2.5, (0.8, 0.85, 1.0), 220, (1.0, 0.6, 0.35), 0, (0.015, 0.02, 0.05), 12, 12, 1.5),
        (417, 2.5, (0.8, 0.85, 1.0), 220, (1.0, 0.6, 0.35), 0, (0.015, 0.02, 0.05), 14, 14, 1.5),
    ]
    for b, sun, sc, fill, fc, rim, bg, ln, wn, rg in cues:
        f = max(1, E.FR(b))
        S['sun'].energy = sun
        S['sun'].color = sc
        S['fill'].energy = fill
        S['fill'].color = fc
        S['rim'].energy = rim
        for o, props in ((S['sun'], ('energy', 'color')), (S['fill'], ('energy', 'color')), (S['rim'], ('energy',))):
            for pr in props:
                o.keyframe_insert(pr, frame=f)
        bg_c.default_value = (*bg, 1)
        bg_c.keyframe_insert('default_value', frame=f)
        for sock, v in ((lan, ln), (win, wn), (ring, rg)):
            sock.default_value = v
            sock.keyframe_insert('default_value', frame=f)
    # lantern pulses on "[L09]"
    for b in (104.4, 106.4, 108.4):
        for db, v in ((-0.3, 6), (0.0, 16), (0.9, 6)):
            lan.default_value = v
            lan.keyframe_insert('default_value', frame=E.FR(b + db))
    rig = S['lantern_rig']
    for b, sc, z in [(-1, 1.0, 0.0), (188, 1.0, 0.0), (200, 1.7, -0.5), (296, 1.7, -0.5), (304, 1.15, 0.0),
                     (356, 1.15, 0.0), (417, 1.3, 3.2)]:
        rig.scale = (sc, sc, 1)
        rig.location = (0, 0, z)
        rig.keyframe_insert('scale', frame=max(1, E.FR(b)))
        rig.keyframe_insert('location', frame=max(1, E.FR(b)))
    # rim spotlight follows her head area
    rc = S['rim_obj'].constraints.new('TRACK_TO')
    rc.target, rc.subtarget = lead['arm'], 'head'

    # ---------------------------------------------------- camera
    cam_d = bpy.data.cameras.new('Cam')
    cam_d.dof.use_dof = True
    cam_d.sensor_width = 36
    cam = bpy.data.objects.new('Cam', cam_d)
    scn.collection.objects.link(cam)
    scn.camera = cam
    E.bake_camera(cam, SHOTS, data, ddata, moon=S['moon_pos'])

    # ---------------------------------------------------- render setup
    r = scn.render
    r.engine = 'BLENDER_EEVEE'
    r.resolution_x, r.resolution_y = 1920, 1080
    r.resolution_percentage = 100
    ee = scn.eevee
    ee.taa_render_samples = 24
    ee.use_raytracing = True
    ee.ray_tracing_method = 'SCREEN'
    ee.use_shadows = True
    scn.view_settings.view_transform = 'AgX'
    try:
        scn.view_settings.look = 'AgX - Medium High Contrast'
    except Exception:
        pass
    r.film_transparent = False
    try:   # bloom via compositor glare
        ng = bpy.data.node_groups.new('Bloom', 'CompositorNodeTree')
        rl = ng.nodes.new('CompositorNodeRLayers')
        gl_ = ng.nodes.new('CompositorNodeGlare')
        gl_.inputs['Type'].default_value = 'Bloom'
        for nm, val in (('Threshold', 0.9), ('Strength', 0.5), ('Size', 0.6)):
            if nm in gl_.inputs:
                gl_.inputs[nm].default_value = val
        go = ng.nodes.new('NodeGroupOutput')
        ng.interface.new_socket('Image', in_out='OUTPUT', socket_type='NodeSocketColor')
        ng.links.new(rl.outputs['Image'], gl_.inputs['Image'])
        ng.links.new(gl_.outputs['Image'], go.inputs[0])
        scn.compositing_node_group = ng
    except Exception as ex:
        print('bloom skipped:', ex)

    # ---------------------------------------------------- music + markers
    if AUDIO and os.path.exists(AUDIO):
        sed = scn.sequence_editor_create()
        sed.strips.new_sound('Ode to Hsin and Moon', AUDIO, 1, 1)
        scn.use_audio_scrub = True
        scn.sync_mode = 'AUDIO_SYNC'
    for b, name in c.markers:
        scn.timeline_markers.new(name[:60], frame=int(round(E.FR(b))))

    # tidy: collections
    def coll(name, objs):
        col = bpy.data.collections.new(name)
        scn.collection.children.link(col)
        for o in objs:
            for uc in o.users_collection:
                uc.objects.unlink(o)
            col.objects.link(o)
    coll('Hsin', [o for o in scn.objects if o.name.startswith('Hsin')])
    coll('TrueSelf', [o for o in scn.objects if o.name.startswith('TrueSelf')])
    coll('Props', [o for o in scn.objects if o.name.split('.')[0] in
                   ('Crown', 'CrownPivot', 'QingXia', 'QingXiaFrame', 'BoxFire', 'Shard', 'Ember', 'Spark', 'Mote',
                    'RebirthBurst', 'MoonRain')])
    coll('Stage', [o for o in scn.objects if o.users_collection and o.users_collection[0] == scn.collection
                   and o.type != 'CAMERA'])
    scn.frame_set(1)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(OUT))
    print('SAVED', OUT, 'frames', E.END_FRAME)
    return data


if __name__ == '__main__':
    build()
