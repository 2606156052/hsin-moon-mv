// Graphic design layer: everything is a pure function of song time t (deterministic, frame-accurate).
export const W = 1920, H = 1080;
const BPM = 115.96, PH = 0.335, SPB = 60 / BPM;
export const beatOf = t => (t - PH) / SPB;
export const tOf = b => PH + b * SPB;
export const mk = (w, h) => { const c = document.createElement('canvas'); c.width = w; c.height = h; return c; };
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const sm = x => { x = clamp(x); return x * x * (3 - 2 * x); };
const outC = x => 1 - Math.pow(1 - clamp(x), 3);
const outBack = x => { x = clamp(x); const c = 1.7; return 1 + (c + 1) * Math.pow(x - 1, 3) + c * Math.pow(x - 1, 2); };
function rng(seed) { let s = seed >>> 0 || 1; return () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296); }
const noise1 = (x, s = 0) => { const i = Math.floor(x), f = x - i, h = n => { const v = Math.sin((n + s * 57.1) * 127.1) * 43758.5453; return v - Math.floor(v); }; return h(i) + (h(i + 1) - h(i)) * f * f * (3 - 2 * f); };
// palette taken from the reference short
const C = { night: '#0d1030', indigo: '#1b1d4f', violet: '#3a2a6e', gold: '#f2c66d', goldDeep: '#c8913a', red: '#c8202f', paper: '#f4ead6', ink: '#1a1024', lantern: '#ffb35c', moon: '#fff4dc' };
export const FONT = { cn: '"Ma Shan Zheng"', cn2: '"Zhi Mang Xing"', en: '"Cormorant Garamond"', cap: '"Cinzel"', serif: '"Noto Serif SC"' };
let PAPER = null;
export function init() {
  // paper fibre texture used by panels
  PAPER = mk(512, 512); const g = PAPER.getContext('2d'); const r = rng(9);
  const id = g.createImageData(512, 512);
  for (let i = 0; i < id.data.length; i += 4) { const v = 200 + r() * 55; id.data[i] = v; id.data[i + 1] = v * 0.97; id.data[i + 2] = v * 0.9; id.data[i + 3] = 255; }
  g.putImageData(id, 0, 0);
  g.globalAlpha = 0.06; g.strokeStyle = '#6b5a3a';
  for (let i = 0; i < 400; i++) { g.beginPath(); const x = r() * 512, y = r() * 512, a = r() * 6.28, l = 10 + r() * 50; g.moveTo(x, y); g.lineTo(x + Math.cos(a) * l, y + Math.sin(a) * l); g.stroke(); }
}

// ------------------------------------------------------------------ shapes
function raggedBlob(g, cx, cy, rx, ry, rot, seed, rough = 0.16) {
  g.beginPath();
  for (let i = 0; i <= 64; i++) {
    const a = i / 64 * Math.PI * 2;
    const k = 1 + rough * (noise1(a * 3, seed) - 0.5) * 2 + rough * 0.5 * (noise1(a * 11, seed + 3) - 0.5);
    const x = Math.cos(a) * rx * k, y = Math.sin(a) * ry * k;
    g.lineTo(cx + x * Math.cos(rot) - y * Math.sin(rot), cy + x * Math.sin(rot) + y * Math.cos(rot));
  }
  g.closePath();
}
// 祥云 auspicious cloud scroll: a row of spirals joined by a tail, drawn with progress p (0..1)
function cloudScroll(g, x, y, s, p, color, lw, flip = 1) {
  g.save(); g.translate(x, y); g.scale(s * flip, s);
  g.lineCap = 'round'; g.lineJoin = 'round'; g.strokeStyle = color; g.lineWidth = lw / s;
  const path = new Path2D();
  const spiral = (cx, cy, r, turns, dir) => { for (let i = 0; i <= 60; i++) { const u = i / 60, a = dir * (u * turns * Math.PI * 2), rr = r * (1 - u * 0.82); path.lineTo(cx + Math.cos(a) * rr, cy + Math.sin(a) * rr); } };
  path.moveTo(-260, 40); path.bezierCurveTo(-180, 60, -120, 40, -90, 0);
  spiral(-40, 0, 52, 1.15, -1);
  path.moveTo(-40, -52); path.bezierCurveTo(10, -110, 90, -90, 100, -30);
  spiral(60, -30, 42, 1.1, 1);
  path.moveTo(100, -30); path.bezierCurveTo(140, 30, 120, 70, 60, 64); path.lineTo(-90, 64);
  g.setLineDash([2400 * p, 3000]); g.stroke(path);
  g.restore();
}
const CRES = mk(512, 512);
function crescent(g, cx, cy, r, phase, fill) {
  // phase 0..1: thickness of the lit crescent (drawn off-screen so the cut-out never punches the background)
  const c = CRES.getContext('2d'); c.setTransform(1, 0, 0, 1, 0, 0); c.clearRect(0, 0, 512, 512);
  const k = 240 / r; c.setTransform(k, 0, 0, k, 256, 256);
  c.globalCompositeOperation = 'source-over'; c.shadowColor = 'rgba(255,230,170,0.9)'; c.shadowBlur = 0;
  c.beginPath(); c.arc(0, 0, r, 0, Math.PI * 2); c.fillStyle = fill; c.fill();
  c.globalCompositeOperation = 'destination-out'; c.beginPath(); c.arc(r * (0.25 + 1.6 * (1 - phase)), -r * 0.15, r * 1.02, 0, Math.PI * 2); c.fill();
  c.globalCompositeOperation = 'source-over';
  g.drawImage(CRES, cx - 256 / k, cy - 256 / k, 512 / k, 512 / k);
}
function glowDot(g, x, y, r, col, a) {
  const gr = g.createRadialGradient(x, y, 0, x, y, r); gr.addColorStop(0, col); gr.addColorStop(1, 'rgba(0,0,0,0)');
  g.globalAlpha = a; g.fillStyle = gr; g.fillRect(x - r, y - r, r * 2, r * 2); g.globalAlpha = 1;
}

// ------------------------------------------------------------------ transitions
export const transitions = {
  // diagonal sumi-e brush stroke reveals B, with a dark wet edge and splatter
  ink(ctx, A, B, p, t, o) {
    ctx.drawImage(A, 0, 0);
    const m = mk(W, H), g = m.getContext('2d');
    const e = sm(p), seed = o.seed || 3;
    const dir = o.dir || 1;
    g.fillStyle = '#000';
    const N = 14;
    for (let i = 0; i < N; i++) {
      const s = i / (N - 1); const appear = clamp((e * 1.35 - s * 0.35) / 0.65);
      if (appear <= 0) continue;
      const x = dir > 0 ? -150 + s * (W + 300) : W + 150 - s * (W + 300);
      const y = H * 0.85 - s * H * 0.7 + Math.sin(s * 5 + seed) * 80;
      raggedBlob(g, x, y, 260 + 1100 * Math.pow(appear, 1.6), 140 + 700 * Math.pow(appear, 1.6), -0.5 * dir, seed + i, 0.22);
      g.fill();
    }
    const r = rng(seed * 7 + 1);
    for (let i = 0; i < 70; i++) { const s = r(); if (s > e * 1.2) { r(); r(); r(); continue; } const x = r() * W, y = r() * H, rr = 3 + r() * 22 * e; g.beginPath(); g.arc(x, y, rr, 0, 7); g.fill(); }
    // edge: ink rim = mask dilated minus mask
    const bm = mk(W, H), bg = bm.getContext('2d');
    bg.drawImage(B, 0, 0); bg.globalCompositeOperation = 'destination-in'; bg.drawImage(m, 0, 0);
    const rim = mk(W, H), rg = rim.getContext('2d');
    rg.filter = 'blur(10px)'; rg.drawImage(m, 0, 0); rg.filter = 'none';
    rg.globalCompositeOperation = 'source-in'; rg.fillStyle = C.ink; rg.fillRect(0, 0, W, H);
    ctx.globalAlpha = 0.85 * (1 - sm((p - 0.7) / 0.3)); ctx.drawImage(rim, 0, 0); ctx.globalAlpha = 1;
    ctx.drawImage(bm, 0, 0);
  },
  // iris from the moon: circular reveal with gold ring
  moon(ctx, A, B, p, t, o) {
    ctx.drawImage(A, 0, 0);
    const e = sm(p), cx = o.cx ?? W / 2, cy = o.cy ?? H / 2, R = e * 2300;
    ctx.save(); ctx.beginPath(); ctx.arc(cx, cy, R, 0, 7); ctx.clip(); ctx.drawImage(B, 0, 0); ctx.restore();
    ctx.strokeStyle = C.gold; ctx.globalAlpha = 1 - e; ctx.lineWidth = 6; ctx.beginPath(); ctx.arc(cx, cy, R, 0, 7); ctx.stroke(); ctx.globalAlpha = 1;
  },
  cut(ctx, A, B, p) { ctx.drawImage(p < 0.5 ? A : B, 0, 0); },
};

// ------------------------------------------------------------------ overlays (drawn on top of a layer or the whole frame)
export const overlays = {
  letterbox(g, t, o) {
    const h = (o.h ?? 0.115) * H;
    g.fillStyle = '#000'; g.fillRect(0, 0, W, h); g.fillRect(0, H - h, W, h);
  },
  // small poetic title inside the top bar, like the reference short
  topTitle(g, t, o) {
    const a = sm((t - o.t0) / 0.6) * (1 - sm((t - o.t1 + 0.5) / 0.5));
    if (a <= 0) return;
    g.save(); g.globalAlpha = a * 0.9; g.fillStyle = '#e9dcc0'; g.font = `34px ${FONT.cn2}`; g.textBaseline = 'middle';
    g.font = `500 22px ${FONT.cap}`; spacedText(g, o.text, 60, H * 0.038, 4, 'left'); g.restore();
  },
  // English lyric: letters rise out of a soft blur, gold underline brush
  lyricEN(g, t, o) {
    if (t < o.t0 - 0.1 || t > o.t1 + 0.6) return;
    const size = o.size || 58; g.save(); g.font = `italic 600 ${size}px ${FONT.en}`; g.textBaseline = 'alphabetic';
    const chars = [...o.text]; const widths = chars.map(c => g.measureText(c).width); const tw = widths.reduce((a, b) => a + b, 0) + (chars.length - 1) * 2;
    let x = (o.x ?? W / 2) - (o.align === 'left' ? 0 : tw / 2); const y = o.y ?? H * 0.935;
    const out = sm((t - o.t1) / 0.5);
    chars.forEach((ch, i) => {
      const ct = o.t0 + i * (o.stagger ?? 0.028); const a = sm((t - ct) / 0.35) * (1 - out);
      if (a > 0) {
        g.globalAlpha = a; g.filter = `blur(${(1 - a) * 6}px)`;
        g.shadowColor = 'rgba(255,190,110,0.8)'; g.shadowBlur = 18;
        g.fillStyle = '#fff6e6'; g.fillText(ch, x, y + (1 - outC((t - ct) / 0.45)) * 18 - out * 10);
      }
      x += widths[i] + 2;
    });
    g.filter = 'none'; g.shadowBlur = 0;
    const u = outC((t - o.t0 - 0.2) / 0.9) * (1 - out);
    if (u > 0) { g.globalAlpha = 0.8 * u; const lx = (o.x ?? W / 2) - tw / 2; g.strokeStyle = C.gold; g.lineWidth = 2; g.beginPath(); g.moveTo(lx, y + 14); g.lineTo(lx + tw * u, y + 14); g.stroke(); }
    g.restore();
  },
  // Chinese calligraphy, vertical, each character brushed in top-to-bottom with an ink bleed
  lyricCN(g, t, o) {
    if (t < o.t0 - 0.1 || t > o.t1 + 0.7) return;
    const size = o.size || 92; const chars = [...o.text];
    const out = sm((t - o.t1) / 0.6);
    g.save(); g.font = `${size}px ${FONT.cn}`; g.textAlign = 'center'; g.textBaseline = 'top';
    chars.forEach((ch, i) => {
      const ct = o.t0 + i * (o.stagger ?? 0.11); const p = clamp((t - ct) / 0.32);
      if (p <= 0) return;
      const x = o.x, y = o.y + i * size * 1.02;
      g.save(); g.beginPath(); g.rect(x - size, y - 10, size * 2, (size + 20) * outC(p)); g.clip();
      g.globalAlpha = 1 - out;
      g.shadowColor = o.glow || 'rgba(255,170,90,0.9)'; g.shadowBlur = 24 * (1 - p) + 10;
      g.fillStyle = o.color || '#fffaf0'; g.fillText(ch, x + out * 30, y);
      g.restore();
    });
    g.restore();
  },
  // red seal stamp 印 that slams on a beat
  seal(g, t, o) {
    if (t < o.t0 || t > o.t1) return;
    const p = (t - o.t0) / 0.25, s = 1.6 - 0.6 * outBack(p), a = clamp(p * 3) * (1 - sm((t - o.t1 + 0.4) / 0.4));
    g.save(); g.translate(o.x, o.y); g.scale(s, s); g.rotate(-0.06); g.globalAlpha = a * 0.92;
    g.fillStyle = C.red; raggedBlob(g, 0, 0, 44, 44, 0, 5, 0.04); g.fill();
    g.fillStyle = '#ffeede'; g.font = `62px ${FONT.cn}`; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText(o.text || '心', 0, 4);
    g.restore();
  },
  // embers carried by the wind (beat-pumped)
  embers(g, t, o) {
    const r = rng(o.seed || 11), N = o.n || 120, wind = o.wind || [-1, -0.35];
    const pump = 1 + 0.6 * Math.pow(1 - (beatOf(t) % 1), 6);
    g.save(); g.globalCompositeOperation = 'lighter';
    for (let i = 0; i < N; i++) {
      const life = 1.4 + r() * 2.2, off = r() * life, sp = 300 + r() * 700, x0 = r() * W * 1.4, y0 = r() * H * 1.2, sz = 2 + r() * 5, ph = r() * 6.28;
      const u = ((t - (o.t0 || 0)) + off) % life / life; const tt = u * life;
      const x = (x0 + wind[0] * sp * tt + Math.sin(tt * 3 + ph) * 30) % (W * 1.4), y = y0 + wind[1] * sp * tt + Math.cos(tt * 2 + ph) * 20;
      const xx = x < 0 ? x + W * 1.4 : x; const a = Math.sin(Math.PI * u) * (o.alpha ?? 0.9);
      glowDot(g, xx, y, sz * 5 * pump, 'rgba(255,150,60,1)', a * 0.35); glowDot(g, xx, y, sz * 1.4, 'rgba(255,230,170,1)', a);
    }
    g.restore();
  },
  // wind streaks: long thin light lines
  wind(g, t, o) {
    const r = rng(o.seed || 21); g.save(); g.globalCompositeOperation = 'lighter'; g.lineCap = 'round';
    for (let i = 0; i < (o.n || 26); i++) {
      const per = 0.7 + r() * 0.9, off = r() * per, y = r() * H, len = 200 + r() * 500, w = 1 + r() * 2.5;
      const u = ((t + off) % per) / per; const x = W * 1.2 - u * (W * 1.6);
      const gr = g.createLinearGradient(x, 0, x + len, 0); gr.addColorStop(0, 'rgba(255,240,220,0)'); gr.addColorStop(0.3, `rgba(255,236,210,${0.35 * (o.alpha ?? 1)})`); gr.addColorStop(1, 'rgba(255,240,220,0)');
      g.strokeStyle = gr; g.lineWidth = w; g.beginPath(); g.moveTo(x, y); g.quadraticCurveTo(x + len / 2, y - 20, x + len, y + 6); g.stroke();
    }
    g.restore();
  },
  // anime speed lines around a point (for the leap)
  speedLines(g, t, o) {
    if (t < o.t0 || t > o.t1) return;
    const a = Math.sin(Math.PI * clamp((t - o.t0) / (o.t1 - o.t0))); const r = rng(Math.floor(t * 24) + 3);
    g.save(); g.globalAlpha = a * 0.32; g.fillStyle = '#fffaf2';
    for (let i = 0; i < 60; i++) {
      const ang = r() * Math.PI * 2, r0 = 520 + r() * 300, r1 = 1300, w = 0.002 + r() * 0.007;
      g.beginPath(); g.moveTo(o.cx + Math.cos(ang) * r0, o.cy + Math.sin(ang) * r0);
      g.lineTo(o.cx + Math.cos(ang + w) * r1, o.cy + Math.sin(ang + w) * r1); g.lineTo(o.cx + Math.cos(ang - w) * r1, o.cy + Math.sin(ang - w) * r1); g.fill();
    }
    g.restore();
  },
  // warm light-leak flash on given beats
  leak(g, t, o) {
    let a = 0; for (const b of o.beats) { const d = t - tOf(b); if (d >= 0 && d < 0.6) a = Math.max(a, Math.exp(-d * 7)); }
    if (a <= 0.01) return;
    g.save(); g.globalCompositeOperation = 'screen';
    const gr = g.createRadialGradient(W * 0.05, H * 0.1, 0, W * 0.05, H * 0.1, W * 0.9);
    gr.addColorStop(0, `rgba(255,170,90,${0.55 * a})`); gr.addColorStop(0.5, `rgba(255,110,60,${0.18 * a})`); gr.addColorStop(1, 'rgba(0,0,0,0)');
    g.fillStyle = gr; g.fillRect(0, 0, W, H); g.restore();
  },
};


// gold cloud scrolls unrolling over footage
overlays.cloudsOver = function (g, t, o) {
  if (t < o.t0) return;
  const lt = t - o.t0, a = Math.min(1, lt / 0.3) * (o.alpha ?? 0.9);
  const S = [[0.12, 0.25, 0.9, 1], [0.86, 0.22, 0.8, -1], [0.1, 0.78, 1.0, 1], [0.9, 0.8, 0.9, -1]];
  g.save(); g.globalAlpha = a;
  S.forEach(([x, y, s, f], i) => {
    const p = outC((lt - i * 0.07) / 0.8), sw = Math.sin(lt * 1.6 + i) * 24;
    cloudScroll(g, W * x + sw * f, H * y, s, p, 'rgba(255,240,220,0.35)', 10, f);
    cloudScroll(g, W * x + sw * f, H * y, s, p, C.gold, 4, f);
  });
  g.restore();
};

// ------------------------------------------------------------------ JS graphic panels (full-screen designed interludes)
function paperBG(g, t, tint = C.indigo, dark = C.night) {
  const gr = g.createRadialGradient(W * 0.5, H * 0.45, 100, W * 0.5, H * 0.5, W * 0.75);
  gr.addColorStop(0, tint); gr.addColorStop(1, dark); g.fillStyle = gr; g.fillRect(0, 0, W, H);
  g.save(); g.globalAlpha = 0.07; g.globalCompositeOperation = 'overlay'; g.fillStyle = g.createPattern(PAPER, 'repeat'); g.fillRect(0, 0, W, H); g.restore();
}
function mist(g, t, y, alpha, speed, seed) {
  g.save(); g.globalAlpha = alpha; g.filter = 'blur(28px)'; g.fillStyle = '#c9c4ff';
  for (let i = 0; i < 9; i++) { const x = ((i * 260 + t * speed * 60 + seed * 97) % (W + 600)) - 300; raggedBlob(g, x, y + Math.sin(i + t * 0.5) * 20, 220, 50, 0, seed + i, 0.3); g.fill(); }
  g.restore();
}
export const panels = {
  // cloud scrolls unroll and swirl around a crescent moon
  clouds(g, t, lt, seg) {
    paperBG(g, t, '#2c2a6b', '#0b0c26');
    const b = beatOf(t), pulse = Math.pow(1 - (b % 1), 4);
    // moon + rotating gold rings
    const cx = W * 0.5, cy = H * 0.46;
    glowDot(g, cx, cy, 520, 'rgba(255,230,180,0.55)', 0.55 + 0.2 * pulse);
    crescent(g, cx, cy, 170, 0.55 + 0.1 * Math.sin(lt), C.moon);
    g.save(); g.translate(cx, cy); g.strokeStyle = C.gold; g.globalAlpha = 0.7;
    for (let k = 0; k < 3; k++) { g.lineWidth = 1.5; g.beginPath(); g.setLineDash(k === 1 ? [4, 14] : []); g.arc(0, 0, 250 + k * 46 + pulse * 6, -Math.PI / 2, -Math.PI / 2 + Math.PI * 2 * outC(lt / 0.9 - k * 0.1)); g.stroke(); }
    g.rotate(lt * 0.4); for (let i = 0; i < 24; i++) { g.rotate(Math.PI / 12); g.fillStyle = C.gold; g.fillRect(292, -1, 14 + (i % 3 === 0 ? 10 : 0), 2); }
    g.restore();
    // swirling cloud scrolls (stirred)
    const S = [[0.18, 0.3, 1.1, 1], [0.8, 0.26, 0.9, -1], [0.25, 0.7, 1.0, 1], [0.78, 0.72, 1.2, -1], [0.5, 0.86, 0.8, 1]];
    S.forEach(([x, y, s, f], i) => {
      const p = outC((lt - i * 0.08) / 0.9); const sw = Math.sin(lt * 1.3 + i) * 30;
      cloudScroll(g, W * x + sw * f + lt * 40 * f, H * y, s * (1 + 0.04 * pulse), p, C.gold, 5, f);
      cloudScroll(g, W * x + sw * f + lt * 40 * f + 6, H * y + 6, s, p, 'rgba(255,240,220,0.25)', 9, f);
    });
    mist(g, lt, H * 0.62, 0.35, 1.2, 4); mist(g, lt, H * 0.3, 0.25, -0.8, 9);
    // headline typography
    const a = sm(lt / 0.4);
    g.save(); g.globalAlpha = a; g.textAlign = 'center';
    g.font = `140px ${FONT.cn}`; g.fillStyle = '#fff8ea'; g.shadowColor = 'rgba(40,20,90,0.95)'; g.shadowBlur = 26;
    const cn = [...(seg.cn || '拨云弄雾')]; cn.forEach((ch, i) => { const p = outBack((lt - 0.1 - i * 0.09) / 0.35); if (p > 0) { g.save(); g.translate(W * 0.5 + (i - (cn.length - 1) / 2) * 150, H * 0.5 + 50); g.scale(p, p); g.globalAlpha = clamp(p) * a; g.fillText(ch, 0, 0); g.restore(); } });
    g.restore();
    // drifting gold motes
    overlays.embers(g, t, { seed: 44, n: 60, wind: [0.25, -0.2], alpha: 0.6 });
  },
  // pre-roll / act card: moon phases orbit
  mandala(g, t, lt, seg) {
    paperBG(g, t, '#23215a', '#07071c');
    const cx = W / 2, cy = H / 2, b = beatOf(t);
    glowDot(g, cx, cy, 380, 'rgba(255,225,170,0.6)', 0.6);
    for (let i = 0; i < 8; i++) { const a = i / 8 * Math.PI * 2 + lt * 0.3; crescent(g, cx + Math.cos(a) * 300, cy + Math.sin(a) * 300, 34, (i + 1) / 9, C.moon); }
    g.save(); g.translate(cx, cy); g.rotate(-lt * 0.2); g.strokeStyle = C.gold; g.lineWidth = 2;
    for (let r = 120; r <= 220; r += 50) { g.beginPath(); g.arc(0, 0, r, 0, 7); g.stroke(); }
    g.restore();
    g.font = `120px ${FONT.cn}`; g.fillStyle = C.moon; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText(seg.text || '心', cx, cy);
  },
};

// ================================================================== v2: English-only design system for the full MV
let ONSET = null;
export async function loadOnsets() { try { ONSET = await (await fetch('onset.json')).json(); } catch (e) { ONSET = null; } }
const onsetAt = t => { if (!ONSET) return 0; const i = Math.floor(t * ONSET.fps); let m = 0; for (let k = -2; k <= 1; k++) m = Math.max(m, ONSET.env[i + k] || 0); return m; };
function spacedText(g, text, x, y, spacing, align = 'center') {
  const chars = [...text]; const ws = chars.map(c => g.measureText(c).width); const tw = ws.reduce((a, b) => a + b, 0) + spacing * (chars.length - 1);
  let cx = align === 'center' ? x - tw / 2 : align === 'right' ? x - tw : x;
  const saved = g.textAlign; g.textAlign = 'left';
  chars.forEach((c, i) => { g.fillText(c, cx, y); cx += ws[i] + spacing; }); g.textAlign = saved; return tw;
}
// a moon glyph seal (replaces the Chinese seal)
overlays.seal = function (g, t, o) {
  if (t < o.t0 || t > o.t1) return;
  const p = (t - o.t0) / 0.25, s = 1.6 - 0.6 * outBack(p), a = clamp(p * 3) * (1 - sm((t - o.t1 + 0.4) / 0.4));
  g.save(); g.translate(o.x, o.y); g.scale(s, s); g.rotate(-0.06); g.globalAlpha = a * 0.92;
  g.fillStyle = C.red; raggedBlob(g, 0, 0, 40, 40, 0, 5, 0.04); g.fill();
  crescent(g, 0, 0, 22, 0.45, '#ffeede');
  g.restore();
};
// large display lyric in serif caps, revealed letter by letter with a gold light sweep (replaces vertical calligraphy)
overlays.display = function (g, t, o) {
  if (t < o.t0 - 0.1 || t > o.t1 + 0.7) return;
  const out = sm((t - o.t1) / 0.6), size = o.size || 64;
  g.save(); g.font = `500 ${size}px ${FONT.cap}`; g.textBaseline = 'middle';
  const lines = o.text.split('|');
  lines.forEach((ln, li) => {
    const chars = [...ln]; const ws = chars.map(c => g.measureText(c).width); const sp = size * 0.12;
    const tw = ws.reduce((a, b) => a + b, 0) + sp * (chars.length - 1);
    let x = o.align === 'right' ? o.x - tw : o.align === 'left' ? o.x : o.x - tw / 2; const y = o.y + li * size * 1.25;
    chars.forEach((c, i) => {
      const ct = o.t0 + (li * chars.length + i) * (o.stagger ?? 0.035); const a = sm((t - ct) / 0.3) * (1 - out);
      if (a > 0) { const yy = y + (1 - outC((t - ct) / 0.4)) * 14;
        g.globalAlpha = a * 0.75; g.shadowBlur = 0; g.lineWidth = 6; g.lineJoin = 'round'; g.strokeStyle = 'rgba(18,10,40,0.85)'; g.strokeText(c, x + out * 20, yy);
        g.globalAlpha = a; g.shadowColor = 'rgba(255,190,110,0.85)'; g.shadowBlur = 22 * (1.4 - a);
        g.fillStyle = '#fff7e8'; g.fillText(c, x + out * 20, yy); }
      x += ws[i] + sp;
    });
  });
  g.restore();
};
// white flash on accent beats
overlays.flash = function (g, t, o) {
  let a = 0; for (const b of o.beats) { const d = t - tOf(b); if (d >= 0 && d < 0.25) a = Math.max(a, 1 - d / 0.25); }
  if (a > 0.01) { g.save(); g.globalCompositeOperation = 'screen'; g.fillStyle = `rgba(255,248,235,${0.7 * a})`; g.fillRect(0, 0, W, H); g.restore(); }
};
// slow falling moon motes over footage
overlays.motes = function (g, t, o) {
  const r = rng(o.seed || 77); g.save(); g.globalCompositeOperation = 'lighter';
  for (let i = 0; i < (o.n || 70); i++) { const x0 = r() * W, sp = 30 + r() * 70, ph = r() * 50, sz = 1.5 + r() * 3;
    const y = ((t * sp + ph * 40) % (H + 100)) - 50, x = x0 + Math.sin(t * 0.7 + ph) * 30;
    glowDot(g, x, y, sz * 6, 'rgba(190,210,255,1)', 0.25 * (o.alpha ?? 1)); glowDot(g, x, y, sz, 'rgba(240,245,255,1)', 0.9 * (o.alpha ?? 1)); }
  g.restore();
};
// color wash (act grading on top of footage)
overlays.wash = function (g, t, o) { g.save(); g.globalCompositeOperation = o.op || 'soft-light'; g.globalAlpha = o.a ?? 0.35; g.fillStyle = o.color; g.fillRect(0, 0, W, H); g.restore(); };

transitions.flash = function (ctx, A, B, p) { ctx.drawImage(p < 0.5 ? A : B, 0, 0); const a = 1 - Math.abs(p - 0.5) * 2; ctx.save(); ctx.globalCompositeOperation = 'screen'; ctx.fillStyle = `rgba(255,250,240,${a})`; ctx.fillRect(0, 0, W, H); ctx.restore(); };
transitions.dissolve = function (ctx, A, B, p) { ctx.drawImage(A, 0, 0); ctx.globalAlpha = sm(p); ctx.drawImage(B, 0, 0); ctx.globalAlpha = 1; };
transitions.black = function (ctx, A, B, p) { ctx.drawImage(p < 0.5 ? A : B, 0, 0); ctx.fillStyle = `rgba(0,0,0,${1 - Math.abs(p - 0.5) * 2})`; ctx.fillRect(0, 0, W, H); };
transitions.shatter = function (ctx, A, B, p, t, o) {
  ctx.drawImage(B, 0, 0); if (p >= 1) return;
  const r = rng(31); const N = 26; ctx.save();
  for (let i = 0; i < N; i++) { const cx = r() * W, cy = r() * H, ang = r() * 6.28, dist = sm(p) * (300 + r() * 900), rot = (r() - 0.5) * 2 * p;
    ctx.save(); ctx.translate(cx + Math.cos(ang) * dist, cy + Math.sin(ang) * dist); ctx.rotate(rot); ctx.globalAlpha = 1 - sm(p);
    ctx.beginPath(); const rr = 160 + r() * 200; for (let k = 0; k < 5; k++) { const a2 = k / 5 * 6.28 + r(); ctx.lineTo(Math.cos(a2) * rr, Math.sin(a2) * rr); } ctx.closePath(); ctx.clip();
    ctx.drawImage(A, -cx, -cy); ctx.strokeStyle = 'rgba(255,240,210,0.9)'; ctx.lineWidth = 3; ctx.stroke(); ctx.restore(); }
  ctx.restore();
  ctx.fillStyle = `rgba(255,255,255,${(1 - p) * 0.5})`; ctx.fillRect(0, 0, W, H);
};

// --------------------------------------------------------- panels
panels.title = function (g, t, lt, seg) {
  paperBG(g, t, '#23215a', '#05051a');
  const cx = W / 2, cy = H * 0.42;
  glowDot(g, cx, cy, 460 * outC(lt / 2), 'rgba(255,225,170,0.6)', 0.7);
  g.save(); g.translate(cx, cy); g.strokeStyle = C.gold; g.lineWidth = 2;
  g.beginPath(); g.arc(0, 0, 230, -Math.PI / 2, -Math.PI / 2 + Math.PI * 2 * outC(lt / 1.6)); g.stroke();
  g.setLineDash([3, 12]); g.beginPath(); g.arc(0, 0, 270, 0, Math.PI * 2 * outC((lt - 0.3) / 1.6)); g.stroke(); g.setLineDash([]);
  g.restore();
  for (let i = 0; i < 8; i++) { const a = i / 8 * Math.PI * 2 - Math.PI / 2 + lt * 0.12, p = outBack((lt - 0.4 - i * 0.08) / 0.5); if (p > 0) { g.globalAlpha = clamp(p); crescent(g, cx + Math.cos(a) * 300, cy + Math.sin(a) * 260, 24 * p, (i + 1) / 9, C.moon); g.globalAlpha = 1; } }
  crescent(g, cx, cy, 120 * outC((lt - 0.2) / 1.2), 0.55, C.moon);
  g.save(); g.textAlign = 'center'; g.fillStyle = '#fff6e4'; g.shadowColor = 'rgba(255,200,120,0.9)'; g.shadowBlur = 20;
  g.globalAlpha = sm((lt - 1.2) / 0.8); g.font = `500 76px ${FONT.cap}`; spacedText(g, 'ODE TO HSIN AND MOON', cx, H * 0.83, 14);
  g.globalAlpha = sm((lt - 1.8) / 0.8); g.font = `italic 500 40px ${FONT.en}`; spacedText(g, 'Endless Yearning', cx, H * 0.885, 4);
  g.restore();
};
panels.actcard = function (g, t, lt, seg) {
  const a = ACTS_UI[seg.act];
  paperBG(g, t, a.tint, '#06061a');
  // ink stroke
  g.save(); g.fillStyle = 'rgba(10,6,20,0.75)'; const p = outC(lt / 0.6);
  for (let i = 0; i < 9; i++) { raggedBlob(g, W * (0.1 + 0.8 * p * i / 8), H * 0.5 + Math.sin(i) * 20, 180 + 40 * Math.sin(i * 2), 70, 0.05, 50 + i, 0.25); g.fill(); }
  g.restore();
  g.save(); g.textAlign = 'center'; g.shadowColor = 'rgba(255,190,110,0.8)'; g.shadowBlur = 18;
  g.globalAlpha = sm((lt - 0.2) / 0.4); g.fillStyle = C.gold; g.font = `500 34px ${FONT.cap}`; spacedText(g, a.num, W / 2, H * 0.40, 18);
  g.globalAlpha = sm((lt - 0.35) / 0.5); g.fillStyle = '#fff6e4'; g.font = `500 92px ${FONT.cap}`; spacedText(g, a.title.toUpperCase(), W / 2, H * 0.53, 10);
  g.globalAlpha = sm((lt - 0.6) / 0.5); g.font = `italic 500 40px ${FONT.en}`; g.fillText(a.sub, W / 2, H * 0.62);
  g.restore();
  g.strokeStyle = C.gold; g.lineWidth = 2; const u = outC((lt - 0.4) / 0.8); g.beginPath(); g.moveTo(W / 2 - 360 * u, H * 0.575); g.lineTo(W / 2 + 360 * u, H * 0.575); g.stroke();
  overlays.embers(g, t, { seed: 61 + seg.act, n: 40, wind: [0.3, -0.25], alpha: 0.6 });
};
const ACTS_UI = {
  1: { num: 'ACT I', title: 'Moon-Born', sub: 'Playing among mortals', tint: '#2a2a6e' },
  2: { num: 'ACT II', title: 'A Mantle Not Her Own', sub: 'Power she never asked to bear', tint: '#3a1f55' },
  3: { num: 'ACT III', title: 'Burning Devotion', sub: "A mortal's last flame", tint: '#5a1e1e' },
  4: { num: 'ACT IV', title: 'Return to the Heart', sub: 'You have walked this far alone', tint: '#1f3a6e' },
  5: { num: 'ACT V', title: 'Where the Heart Belongs', sub: 'May the lanterns burn forever bright', tint: '#5a3a1e' },
};
panels.strings = function (g, t, lt, seg) {
  paperBG(g, t, '#2b2560', '#08081e');
  const n = 21, x0 = W * 0.08, x1 = W * 0.92;
  const e = onsetAt(t);
  for (let i = 0; i < n; i++) {
    const y = H * 0.2 + i * (H * 0.6 / (n - 1));
    const pluck = Math.max(0, e - 0.25) * ((i * 7 + Math.floor(t * 8)) % 5 === 0 ? 1.6 : 0.5);
    const amp = 18 * pluck, k = 3 + (i % 4);
    g.beginPath();
    for (let s = 0; s <= 120; s++) { const u = s / 120; const x = x0 + (x1 - x0) * u; g.lineTo(x, y + Math.sin(u * Math.PI) * Math.sin(u * Math.PI * k + t * 60) * amp); }
    g.strokeStyle = `rgba(242,198,109,${0.45 + pluck * 0.5})`; g.lineWidth = 1.5 + pluck * 2; g.shadowColor = 'rgba(255,200,120,0.9)'; g.shadowBlur = 8 + pluck * 20; g.stroke(); g.shadowBlur = 0;
  }
  // bridges
  g.fillStyle = C.goldDeep; for (let i = 0; i < n; i++) { const y = H * 0.2 + i * (H * 0.6 / (n - 1)); g.fillRect(W * 0.3 + Math.sin(i * 1.7) * 120, y - 6, 10, 12); }
  overlays.display(g, t, { text: seg.text || '', x: W / 2, y: H * 0.5, t0: seg.t0 + 0.2, t1: seg.t0 + 3.6, size: 70 });
};
panels.sorrowjoy = function (g, t, lt, seg) {
  const b = beatOf(t), swap = Math.floor((b - beatOf(seg.t0)) / 4) % 2;
  const half = (side, cool) => { g.save(); g.beginPath(); g.rect(side ? W / 2 : 0, 0, W / 2, H); g.clip();
    const gr = g.createLinearGradient(0, 0, 0, H); gr.addColorStop(0, cool ? '#1a2a60' : '#5a2a2a'); gr.addColorStop(1, cool ? '#05081c' : '#1c0806'); g.fillStyle = gr; g.fillRect(0, 0, W, H);
    const cx = side ? W * 0.75 : W * 0.25; glowDot(g, cx, H * 0.45, 360, cool ? 'rgba(170,200,255,0.5)' : 'rgba(255,190,120,0.6)', 0.8);
    crescent(g, cx, H * 0.45, 150, cool ? 0.3 : 0.8, cool ? '#dde8ff' : C.moon); g.restore(); };
  const sx = sm(((b - beatOf(seg.t0)) % 4) / 4 * 0.6);
  half(0, swap === 0); half(1, swap === 1);
  g.fillStyle = C.gold; g.fillRect(W / 2 - 1, H * 0.15, 2, H * 0.7);
  overlays.display(g, t, { text: 'SORROW', x: W * 0.25, y: H * 0.78, t0: seg.t0 + 0.1, t1: seg.t1 - 0.3, size: 60 });
  overlays.display(g, t, { text: 'JOY', x: W * 0.75, y: H * 0.78, t0: seg.t0 + 0.5, t1: seg.t1 - 0.3, size: 60 });
};
panels.phases = function (g, t, lt, seg) {
  paperBG(g, t, '#22306a', '#050a1e');
  const cx = W / 2, cy = H * 0.47, b = beatOf(t) - beatOf(seg.t0);
  for (let k = 0; k < 4; k++) { const rr = (((lt * 120 + k * 180) % 720) + 720) % 720; g.strokeStyle = `rgba(200,220,255,${0.25 * (1 - rr / 720)})`; g.lineWidth = 2; g.beginPath(); g.ellipse(cx, cy + 260, rr * 1.4, rr * 0.25, 0, 0, 7); g.stroke(); }
  glowDot(g, cx, cy, 420, 'rgba(230,235,255,0.5)', 0.6);
  for (let i = 0; i < 8; i++) { const a = (i - Math.floor(b)) / 8 * Math.PI * 2 - Math.PI / 2; const r0 = 300; crescent(g, cx + Math.cos(a) * r0, cy + Math.sin(a) * r0 * 0.75, 30, (i + 1) / 9, C.moon); }
  crescent(g, cx, cy, 140, 0.5 + 0.45 * Math.sin(b * Math.PI / 4), '#eef2ff');
  overlays.display(g, t, { text: seg.text || '', x: W / 2, y: H * 0.82, t0: seg.t0 + 0.0, t1: seg.t1 - 0.3, size: 52 });
};
panels.shards = function (g, t, lt, seg) {
  g.fillStyle = '#07040f'; g.fillRect(0, 0, W, H);
  const r = rng(91); const p = sm(lt / 3.5);
  for (let i = 0; i < 18; i++) { const cx = W / 2 + (r() - 0.5) * W * 0.9, cy = H / 2 + (r() - 0.5) * H * 0.8, rr = 90 + r() * 140, rot = (r() - 0.5) * 0.6 + lt * (r() - 0.5) * 0.2;
    g.save(); g.translate(cx + (cx - W / 2) * p * 0.3, cy + (cy - H / 2) * p * 0.3); g.rotate(rot);
    g.beginPath(); for (let k = 0; k < 4; k++) { const a = k / 4 * 6.28 + r(); g.lineTo(Math.cos(a) * rr, Math.sin(a) * rr * 0.8); } g.closePath();
    const gr = g.createLinearGradient(-rr, -rr, rr, rr); gr.addColorStop(0, '#3a2a6a'); gr.addColorStop(0.5, '#c8a8ff'); gr.addColorStop(1, '#2a1a40');
    g.globalAlpha = 0.35 + 0.25 * Math.sin(lt * 2 + i); g.fillStyle = gr; g.fill(); g.globalAlpha = 0.9; g.strokeStyle = 'rgba(240,220,255,0.8)'; g.lineWidth = 1.5; g.stroke();
    if (i % 4 === 0) { g.globalAlpha = 0.7; crescent(g, 0, 0, rr * 0.35, 0.5, '#f4e8ff'); }
    g.restore(); }
  overlays.display(g, t, { text: 'WHOSE FACE IS THIS?', x: W / 2, y: H * 0.5, t0: seg.t0 + 0.6, t1: seg.t1 - 0.3, size: 72 });
};
panels.moonrain = function (g, t, lt, seg) {
  paperBG(g, t, '#1e2a62', '#04061a');
  glowDot(g, W / 2, H * 0.35, 520, 'rgba(220,230,255,0.45)', 0.7);
  crescent(g, W / 2, H * 0.35, 150, 0.9, '#f2f5ff');
  overlays.motes(g, t, { n: 140, seed: 5 });
  overlays.display(g, t, { text: seg.text || '', x: W / 2, y: H * 0.7, t0: seg.t0 + 0.2, t1: seg.t1 - 1.6, size: 62 });
};
panels.endcard = function (g, t, lt, seg) {
  paperBG(g, t, '#23215a', '#020210');
  const cx = W / 2, cy = H * 0.42, close = sm((lt - 6.5) / 3);
  glowDot(g, cx, cy, 460 * (1 - close * 0.9), 'rgba(255,225,170,0.6)', 0.7);
  crescent(g, cx, cy, 120 * (1 - close * 0.95), 0.55, C.moon);
  g.save(); g.textAlign = 'center'; g.fillStyle = '#fff6e4'; g.shadowColor = 'rgba(255,200,120,0.9)'; g.shadowBlur = 16;
  const a = sm(lt / 1.2) * (1 - sm((lt - 8.5) / 1.5));
  g.globalAlpha = a; g.font = `500 64px ${FONT.cap}`; spacedText(g, 'ODE TO HSIN AND MOON', cx, H * 0.74, 12);
  g.font = `italic 500 32px ${FONT.en}`; g.fillText('Endless Yearning  ·  Vocals: Jaime Arin', cx, H * 0.80);
  g.font = `500 22px ${FONT.cap}`; g.globalAlpha = a * 0.75; spacedText(g, 'A FAN-MADE MUSIC VIDEO', cx, H * 0.86, 6);
  g.restore();
};
