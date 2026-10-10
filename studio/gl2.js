// "Vector" repaint (v2): multi-pass video abstraction at full output resolution, all in code.
//   P0  Catmull-Rom upscale 480p -> 1080p
//   P1  iterated edge-preserving bilateral (flat, noise-free colour areas)
//   P2  shock filter (re-sharpens soft upscaled edges into crisp steps, like vector shapes)
//   P3  thin anti-aliased line art (XDoG) + soft cel banding + grade, no grain
const VS = `#version 300 es
in vec2 p; out vec2 uv; void main(){ uv = p*0.5+0.5; gl_Position = vec4(p,0,1); }`;
const HEAD = `#version 300 es
precision highp float; in vec2 uv; out vec4 o; uniform sampler2D T; uniform vec2 res; uniform vec2 src;
float luma(vec3 c){ return dot(c, vec3(0.299,0.587,0.114)); }
`;
const UPSCALE = HEAD + `
vec3 tx(vec2 u){ return texture(T, vec2(u.x, 1.0-u.y)).rgb; }
void main(){
  vec2 sp = uv*src - 0.5; vec2 f = fract(sp); vec2 i0 = floor(sp);
  vec2 w0 = f*(-0.5 + f*(1.0 - 0.5*f)), w1 = 1.0 + f*f*(-2.5 + 1.5*f), w2 = f*(0.5 + f*(2.0 - 1.5*f)), w3 = f*f*(-0.5 + 0.5*f);
  vec2 w12 = w1 + w2, t12 = (i0 + 1.0 + w2 / w12 + 0.5) / src, t0 = (i0 - 0.5)/src, t3 = (i0 + 2.5)/src;
  vec3 r = (tx(vec2(t0.x,t0.y))*w0.x + tx(vec2(t12.x,t0.y))*w12.x + tx(vec2(t3.x,t0.y))*w3.x)*w0.y
         + (tx(vec2(t0.x,t12.y))*w0.x + tx(vec2(t12.x,t12.y))*w12.x + tx(vec2(t3.x,t12.y))*w3.x)*w12.y
         + (tx(vec2(t0.x,t3.y))*w0.x + tx(vec2(t12.x,t3.y))*w12.x + tx(vec2(t3.x,t3.y))*w3.x)*w3.y;
  o = vec4(clamp(r,0.0,1.0),1.0);
}`;
// separable-ish bilateral, 7x7 sparse kernel, colour sigma tuned for anime fills
const BILATERAL = HEAD + `
uniform vec2 dir; uniform float sr;
void main(){
  vec2 px = 1.0/res; vec3 c = texture(T, uv).rgb; vec3 acc = vec3(0); float ws = 0.0;
  for (int i=-4;i<=4;i++){ vec2 off = dir*float(i)*px*1.5; vec3 s = texture(T, uv+off).rgb;
    float w = exp(-float(i*i)/8.0) * exp(-dot(s-c,s-c)/(2.0*sr*sr)); acc += s*w; ws += w; }
  o = vec4(acc/ws, 1.0);
}`;
// shock filter: dilate where the Laplacian of the blurred luma is negative, erode where positive
const SHOCK = HEAD + `
uniform float strength;
void main(){
  vec2 px = 1.0/res; vec3 c = texture(T, uv).rgb;
  float l = luma(c);
  float lap = 0.0; float wsum = 0.0;
  for (int y=-2;y<=2;y++) for (int x=-2;x<=2;x++){ float w = exp(-float(x*x+y*y)/2.5); lap += luma(texture(T, uv+vec2(x,y)*px).rgb)*w; wsum += w; }
  lap = lap/wsum - l;     // >0: pixel darker than surroundings
  vec3 mx = c, mn = c; float lmx = l, lmn = l;
  for (int y=-1;y<=1;y++) for (int x=-1;x<=1;x++){ vec3 s = texture(T, uv+vec2(x,y)*px).rgb; float ls = luma(s);
    if (ls > lmx){ lmx = ls; mx = s; } if (ls < lmn){ lmn = ls; mn = s; } }
  // gradient magnitude gates the effect so flat areas stay untouched
  float gx = luma(texture(T, uv+vec2(px.x,0)).rgb) - luma(texture(T, uv-vec2(px.x,0)).rgb);
  float gy = luma(texture(T, uv+vec2(0,px.y)).rgb) - luma(texture(T, uv-vec2(0,px.y)).rgb);
  float g = smoothstep(0.015, 0.08, length(vec2(gx,gy)));
  vec3 target = lap > 0.0 ? mn : mx;
  o = vec4(mix(c, target, g*strength*smoothstep(0.0, 0.01, abs(lap))), 1.0);
}`;
const FXAA = HEAD + `
void main(){
  vec2 px = 1.0/res;
  vec3 rgbNW = texture(T, uv+vec2(-1,-1)*px).rgb, rgbNE = texture(T, uv+vec2(1,-1)*px).rgb;
  vec3 rgbSW = texture(T, uv+vec2(-1,1)*px).rgb, rgbSE = texture(T, uv+vec2(1,1)*px).rgb, rgbM = texture(T, uv).rgb;
  float lNW = luma(rgbNW), lNE = luma(rgbNE), lSW = luma(rgbSW), lSE = luma(rgbSE), lM = luma(rgbM);
  float lMin = min(lM, min(min(lNW,lNE), min(lSW,lSE))), lMax = max(lM, max(max(lNW,lNE), max(lSW,lSE)));
  vec2 dir = vec2(-((lNW+lNE)-(lSW+lSE)), ((lNW+lSW)-(lNE+lSE)));
  float red = max((lNW+lNE+lSW+lSE)*0.25*0.125, 1.0/128.0);
  float rcp = 1.0/(min(abs(dir.x), abs(dir.y)) + red);
  dir = clamp(dir*rcp, -8.0, 8.0) * px;
  vec3 a = 0.5*(texture(T, uv+dir*(1.0/3.0-0.5)).rgb + texture(T, uv+dir*(2.0/3.0-0.5)).rgb);
  vec3 b = a*0.5 + 0.25*(texture(T, uv-dir*0.5).rgb + texture(T, uv+dir*0.5).rgb);
  float lb = luma(b);
  o = vec4((lb < lMin || lb > lMax) ? a : b, 1.0);
}`;
const FINAL = HEAD + `
uniform sampler2D S;   // smoothed (pre-shock) image for line extraction
uniform sampler2D U;   // raw upscale for bloom source
uniform float time, expo, sat, ink, bloomAmt, warm, bands;
vec3 tx(sampler2D t, vec2 u){ return texture(t, u).rgb; }
void main(){
  vec2 px = 1.0/res;
  vec3 c = texture(T, uv).rgb;
  // XDoG line art at output resolution (thin, anti-aliased)
  float g1 = 0.0, g2 = 0.0, w1 = 0.0, w2 = 0.0;
  for (int y=-3;y<=3;y++) for (int x=-3;x<=3;x++){ float d = float(x*x+y*y); float l = luma(tx(S, uv+vec2(x,y)*px));
    float a = exp(-d/(2.0*0.7*0.7)), b = exp(-d/(2.0*1.25*1.25)); g1 += l*a; w1 += a; g2 += l*b; w2 += b; }
  float dog = g1/w1 - 0.985*(g2/w2);
  float line = 1.0 - smoothstep(-0.022, -0.002, dog);           // 1 on dark edges
  float L = luma(c);
  line *= 1.0 - smoothstep(0.62, 0.9, L);                       // no outlines on glowing lights
  // soft cel banding: snap luminance to bands with smooth transitions (clean flat fills)
  float q = L*bands; float lq = (floor(q) + smoothstep(0.42, 0.58, fract(q)))/bands;
  c *= mix(1.0, lq/max(L,1e-3), 0.45);
  c = mix(c, c*vec3(0.22,0.16,0.30), line*ink);
  // bloom
  vec3 big = textureLod(U, uv, 4.0).rgb + textureLod(U, uv, 2.5).rgb*0.6;
  c += max(big/1.6 - 0.55, 0.0) * bloomAmt * vec3(1.0,0.86,0.72);
  c *= expo; float Y = luma(c); c = mix(vec3(Y), c, sat);
  c += (1.0-smoothstep(0.0,0.45,Y)) * vec3(0.015,0.008,0.04);
  c *= mix(vec3(1.0), vec3(1.05,0.98,0.90), smoothstep(0.5,1.0,Y)*warm);
  vec2 qv = uv-0.5; c *= 1.0 - dot(qv,qv)*0.45;
  o = vec4(clamp(c,0.0,1.0),1.0);
}`;
export class VectorGL {
  constructor(canvas) {
    const gl = this.gl = canvas.getContext('webgl2', { preserveDrawingBuffer: true, premultipliedAlpha: false });
    this.W = canvas.width; this.H = canvas.height;
    const sh = (t, s) => { const x = gl.createShader(t); gl.shaderSource(x, s); gl.compileShader(x); if (!gl.getShaderParameter(x, gl.COMPILE_STATUS)) throw gl.getShaderInfoLog(x); return x; };
    const prog = fs => { const p = gl.createProgram(); gl.attachShader(p, sh(gl.VERTEX_SHADER, VS)); gl.attachShader(p, sh(gl.FRAGMENT_SHADER, fs)); gl.linkProgram(p); if (!gl.getProgramParameter(p, gl.LINK_STATUS)) throw gl.getProgramInfoLog(p); return p; };
    this.P = { up: prog(UPSCALE), bi: prog(BILATERAL), sh: prog(SHOCK), aa: prog(FXAA), fin: prog(FINAL) };
    const b = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, b); gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1,-1,1,-1,-1,1,1,1]), gl.STATIC_DRAW);
    for (const p of Object.values(this.P)) { const l = gl.getAttribLocation(p, 'p'); gl.enableVertexAttribArray(l); gl.vertexAttribPointer(l, 2, gl.FLOAT, false, 0, 0); }
    const mkTex = (w, h, mip) => { const t = gl.createTexture(); gl.bindTexture(gl.TEXTURE_2D, t);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, mip ? gl.LINEAR_MIPMAP_LINEAR : gl.LINEAR); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
      if (w) gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA8, w, h, 0, gl.RGBA, gl.UNSIGNED_BYTE, null); return t; };
    this.src = mkTex(0, 0, false);
    this.rt = [0, 1, 2, 3].map(() => { const t = mkTex(this.W, this.H, false); const f = gl.createFramebuffer(); gl.bindFramebuffer(gl.FRAMEBUFFER, f); gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, t, 0); return { t, f }; });
    this.upMip = mkTex(this.W, this.H, true);
  }
  pass(prog, inTex, out, uni = {}) {
    const gl = this.gl; gl.useProgram(prog);
    gl.bindFramebuffer(gl.FRAMEBUFFER, out ? out.f : null); gl.viewport(0, 0, this.W, this.H);
    gl.activeTexture(gl.TEXTURE0); gl.bindTexture(gl.TEXTURE_2D, inTex); gl.uniform1i(gl.getUniformLocation(prog, 'T'), 0);
    gl.uniform2f(gl.getUniformLocation(prog, 'res'), this.W, this.H);
    let unit = 1;
    for (const [k, v] of Object.entries(uni)) {
      const loc = gl.getUniformLocation(prog, k);
      if (v && v.tex) { gl.activeTexture(gl.TEXTURE0 + unit); gl.bindTexture(gl.TEXTURE_2D, v.tex); gl.uniform1i(loc, unit++); }
      else if (Array.isArray(v)) gl.uniform2f(loc, v[0], v[1]); else gl.uniform1f(loc, v);
    }
    gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
  }
  draw(img, mode, time, g) {
    const gl = this.gl, R = this.rt;
    gl.bindTexture(gl.TEXTURE_2D, this.src);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, img);
    this.pass(this.P.up, this.src, R[0], { src: [img.naturalWidth, img.naturalHeight] });
    // copy upscale into a mipmapped texture for bloom
    gl.bindFramebuffer(gl.READ_FRAMEBUFFER, R[0].f); gl.bindTexture(gl.TEXTURE_2D, this.upMip);
    gl.copyTexSubImage2D(gl.TEXTURE_2D, 0, 0, 0, 0, 0, this.W, this.H); gl.generateMipmap(gl.TEXTURE_2D);
    const sr = g.sr ?? 0.09;
    let a = R[0], b = R[1];
    for (let i = 0; i < (g.iters ?? 3); i++) {
      this.pass(this.P.bi, a.t, b, { dir: [1, 0], sr }); [a, b] = [b, a];
      this.pass(this.P.bi, a.t, b, { dir: [0, 1], sr }); [a, b] = [b, a];
    }
    const smoothed = a === R[0] ? R[0] : R[1];
    // keep smoothed in R[2] for line extraction
    this.pass(this.P.bi, smoothed.t, R[2], { dir: [1, 0], sr: 0.03 });
    let s1 = smoothed, s2 = smoothed === R[0] ? R[3] : R[3];
    let x = smoothed, y = R[3];
    for (let i = 0; i < (g.shock ?? 3); i++) { this.pass(this.P.sh, x.t, y, { strength: g.shockStr ?? 0.85 }); const tmp = x; x = y; y = (tmp === R[2]) ? R[3] : tmp; }
    this.pass(this.P.aa, x.t, y);  x = y;
    this.pass(this.P.fin, x.t, null, { S: { tex: R[2].t }, U: { tex: this.upMip }, time, expo: g.expo ?? 1.04, sat: g.sat ?? 1.1,
      ink: g.ink ?? 0.75, bloomAmt: g.bloom ?? 0.8, warm: g.warm ?? 1.0, bands: g.bands ?? 6.0 });
  }
}
