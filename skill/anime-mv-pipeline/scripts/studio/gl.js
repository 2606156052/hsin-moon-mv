// Base picture pass at 1080p.
// mode 'redraw' (Option 1): the low-res video is re-drawn by code — edge-aware smoothing into flat cel
//   paint, luminance banding, ink line extraction, sharpening — then graded.
// mode 'grade'  (Option 2): the frame is already AI-upscaled; only grade / bloom / grain.
const VS = `#version 300 es
in vec2 p; out vec2 uv; void main(){ uv = p*0.5+0.5; uv.y = 1.0-uv.y; gl_Position = vec4(p,0,1); }`;
const FS = `#version 300 es
precision highp float;
in vec2 uv; out vec4 o;
uniform sampler2D T; uniform vec2 src; uniform int mode; uniform float time;
uniform float expo, sat, ink, bloomAmt, warm;
float luma(vec3 c){ return dot(c, vec3(0.299,0.587,0.114)); }
vec3 tx(vec2 u){ return texture(T, u).rgb; }
vec3 txs(vec2 u){ return textureLod(T, u, 0.8).rgb; }
// Catmull-Rom bicubic (sharper than bilinear for the upscale)
vec3 bicubic(vec2 u){
  vec2 sp = u*src - 0.5; vec2 f = fract(sp); vec2 i0 = floor(sp);
  vec2 w0 = f*(-0.5 + f*(1.0 - 0.5*f)), w1 = 1.0 + f*f*(-2.5 + 1.5*f), w2 = f*(0.5 + f*(2.0 - 1.5*f)), w3 = f*f*(-0.5 + 0.5*f);
  vec2 w12 = w1 + w2, t12 = (i0 + 1.0 + w2 / w12 + 0.5) / src, t0 = (i0 - 1.0 + 0.5)/src, t3 = (i0 + 2.0 + 0.5)/src;
  vec3 r = (tx(vec2(t0.x,t0.y))*w0.x + tx(vec2(t12.x,t0.y))*w12.x + tx(vec2(t3.x,t0.y))*w3.x)*w0.y
         + (tx(vec2(t0.x,t12.y))*w0.x + tx(vec2(t12.x,t12.y))*w12.x + tx(vec2(t3.x,t12.y))*w3.x)*w12.y
         + (tx(vec2(t0.x,t3.y))*w0.x + tx(vec2(t12.x,t3.y))*w12.x + tx(vec2(t3.x,t3.y))*w3.x)*w3.y;
  return r;
}
float hash(vec2 p){ return fract(sin(dot(p, vec2(12.9898,78.233)))*43758.5453); }
void main(){
  vec2 px = 1.0/src;
  vec3 c = bicubic(uv);
  if (mode == 0) {
    // contrast-adaptive sharpening at output resolution (restores crisp detail after the upscale)
    vec2 op = 1.0/vec2(1920.0,1080.0);
    vec3 n = bicubic(uv+vec2(0,-op.y)), s2 = bicubic(uv+vec2(0,op.y)), w2 = bicubic(uv+vec2(-op.x,0)), e2 = bicubic(uv+vec2(op.x,0));
    vec3 mn = min(c, min(min(n,s2), min(w2,e2))), mx = max(c, max(max(n,s2), max(w2,e2)));
    vec3 amp = sqrt(clamp(min(mn, 2.0-mx)/max(mx,1e-4), 0.0, 1.0));
    vec3 wgt = -amp/mix(8.0, 5.0, 0.8);
    c = clamp((c + (n+s2+w2+e2)*wgt)/(1.0+4.0*wgt), 0.0, 1.0);
    // edge-preserving smoothing (bilateral, 5x5 in source pixels) -> flat painted cel areas
    vec3 acc = vec3(0); float wsum = 0.0;
    for (int y=-2; y<=2; y++) for (int x=-2; x<=2; x++) {
      vec2 o2 = vec2(x,y)*px*0.75; vec3 s = tx(uv+o2);
      float w = exp(-dot(vec2(x,y),vec2(x,y))/4.5) * exp(-dot(s-c,s-c)*38.0);
      acc += s*w; wsum += w; }
    vec3 sm = acc/wsum;
    // soft luminance banding: cel steps without posterising gradients flat
    float l = luma(sm); float lq = (floor(l*7.0)+smoothstep(0.35,0.65,fract(l*7.0)))/7.0;
    sm *= mix(1.0, lq/max(l,1e-3), 0.35);
    // ink lines from luminance edges (Sobel on the source grid)
    vec2 hp = px*0.6;
    float tl=luma(txs(uv+hp*vec2(-1,-1))), t=luma(txs(uv+hp*vec2(0,-1))), tr=luma(txs(uv+hp*vec2(1,-1)));
    float ml=luma(txs(uv+hp*vec2(-1,0))),                                 mr=luma(txs(uv+hp*vec2(1,0)));
    float bl=luma(txs(uv+hp*vec2(-1,1))),  b=luma(txs(uv+hp*vec2(0,1))),   br=luma(txs(uv+hp*vec2(1,1)));
    float gx = -tl-2.0*ml-bl+tr+2.0*mr+br, gy = -tl-2.0*t-tr+bl+2.0*b+br;
    float e = smoothstep(0.24, 0.55, length(vec2(gx,gy)));
    e *= 1.0 - smoothstep(0.55, 0.85, max(luma(c), luma(sm)));   // no ink halos around lights
    vec3 inkc = sm*vec3(0.25,0.18,0.32);
    c = mix(sm, inkc, e*ink);
    // unsharp against the smoothed field
    c += (c - sm)*0.45;
  } else {
    vec3 bl = (tx(uv+px*vec2(1,0))+tx(uv-px*vec2(1,0))+tx(uv+px*vec2(0,1))+tx(uv-px*vec2(0,1)))*0.25;
    c += (c-bl)*0.25;
  }
  // bloom from a blurred mip
  vec3 big = textureLod(T, uv, 4.5).rgb + textureLod(T, uv, 3.0).rgb*0.6;
  c += max(big/1.6 - 0.55, 0.0) * bloomAmt * vec3(1.0,0.86,0.72);
  // grade: violet shadows, warm lantern highlights
  c *= expo;
  float L = luma(c);
  c = mix(vec3(L), c, sat);
  c += (1.0-smoothstep(0.0,0.45,L)) * vec3(0.018,0.010,0.045);
  c *= mix(vec3(1.0), vec3(1.05,0.98,0.90), smoothstep(0.5,1.0,L)*warm);
  // vignette + grain
  vec2 q = uv-0.5; c *= 1.0 - dot(q,q)*0.55;
  c += (hash(uv*vec2(1920.,1080.)+time)-0.5)*0.018;
  o = vec4(clamp(c,0.0,1.0),1.0);
}`;
export class BaseGL {
  constructor(canvas) {
    const gl = this.gl = canvas.getContext('webgl2', { preserveDrawingBuffer: true, premultipliedAlpha: false });
    const sh = (t, s) => { const x = gl.createShader(t); gl.shaderSource(x, s); gl.compileShader(x); if (!gl.getShaderParameter(x, gl.COMPILE_STATUS)) throw gl.getShaderInfoLog(x); return x; };
    const pr = this.pr = gl.createProgram(); gl.attachShader(pr, sh(gl.VERTEX_SHADER, VS)); gl.attachShader(pr, sh(gl.FRAGMENT_SHADER, FS)); gl.linkProgram(pr);
    gl.useProgram(pr);
    const b = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, b); gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1,-1,1,-1,-1,1,1,1]), gl.STATIC_DRAW);
    const loc = gl.getAttribLocation(pr, 'p'); gl.enableVertexAttribArray(loc); gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
    this.tex = gl.createTexture(); gl.bindTexture(gl.TEXTURE_2D, this.tex);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR_MIPMAP_LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    this.u = n => gl.getUniformLocation(pr, n);
  }
  draw(img, mode, time, g) {
    const gl = this.gl;
    gl.bindTexture(gl.TEXTURE_2D, this.tex);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, img); gl.generateMipmap(gl.TEXTURE_2D);
    gl.viewport(0, 0, gl.canvas.width, gl.canvas.height);
    gl.uniform2f(this.u('src'), img.naturalWidth, img.naturalHeight);
    gl.uniform1i(this.u('mode'), mode === 'redraw' ? 0 : 1);
    gl.uniform1f(this.u('time'), time);
    gl.uniform1f(this.u('expo'), g.expo ?? 1.04); gl.uniform1f(this.u('sat'), g.sat ?? 1.08);
    gl.uniform1f(this.u('ink'), g.ink ?? 0.55); gl.uniform1f(this.u('bloomAmt'), g.bloom ?? 0.9); gl.uniform1f(this.u('warm'), g.warm ?? 1.0);
    gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
  }
}
