import numpy as np, json, sys
sr = 22050
x = np.fromfile(sys.argv[1], dtype=np.int16).astype(np.float32) / 32768
hop, n = 512, 2048
frames = 1 + (len(x) - n) // hop
win = np.hanning(n).astype(np.float32)
idx = np.arange(n)[None, :] + hop * np.arange(frames)[:, None]
S = np.abs(np.fft.rfft(x[idx] * win, axis=1))
fps = sr / hop
# mel-ish log bands
freqs = np.fft.rfftfreq(n, 1 / sr)
edges = np.geomspace(40, 10000, 41)
B = np.stack([S[:, (freqs >= edges[i]) & (freqs < edges[i + 1])].sum(1) for i in range(40)], 1)
L = np.log1p(100 * B)
flux = np.maximum(0, np.diff(L, axis=0)).sum(1)
flux = np.concatenate([[0], flux])
flux -= np.convolve(flux, np.ones(31) / 31, 'same')
flux = np.maximum(flux, 0); flux /= flux.max()
rms = np.sqrt((x[idx] ** 2).mean(1))
low = B[:, :10].sum(1)
# tempo via autocorrelation, 60-180 bpm
def tempo(seg):
    ac = np.correlate(seg, seg, 'full')[len(seg) - 1:]
    lags = np.arange(len(ac)); bpm = 60 * fps / np.maximum(lags, 1)
    m = (bpm > 60) & (bpm < 180)
    w = np.exp(-0.5 * (np.log2(bpm / 100) / 0.9) ** 2)
    sc = ac * w
    l = lags[m][np.argmax(sc[m])]
    return 60 * fps / l, l
bpm, lag = tempo(flux)
# DP beat tracking
period = lag
score = flux.copy(); back = -np.ones(len(flux), int)
for t in range(len(flux)):
    lo, hi = int(t - 2 * period), int(t - period / 2)
    if hi <= 0: continue
    p = np.arange(max(lo, 0), hi)
    pen = -100 * (np.log((t - p) / period)) ** 2 * 0.01
    c = score[p] + pen
    k = np.argmax(c); score[t] += c[k]; back[t] = p[k]
t = np.argmax(score[-int(period * 2):]) + len(score) - int(period * 2)
beats = []
while t >= 0: beats.append(t); t = back[t]
beats = np.array(beats[::-1]) / fps
# per-2s energy profile
sec = int(len(x) / sr)
prof = []
for s in range(0, sec, 2):
    a, b = int(s * fps), int((s + 2) * fps)
    prof.append((s, float(rms[a:b].mean()), float(flux[a:b].mean()), float(low[a:b].mean())))
# local tempo per 20 s window
lt = []
for s in range(0, sec - 20, 10):
    a, b = int(s * fps), int((s + 20) * fps)
    lt.append((s, round(tempo(flux[a:b])[0], 1)))
json.dump({'bpm': bpm, 'beats': beats.round(3).tolist(), 'profile': prof, 'local_tempo': lt,
           'onset': {'fps': fps, 'env': flux.round(3).tolist()}}, open(sys.argv[2], 'w'))
print('bpm', bpm, 'nbeats', len(beats))
print('local', lt)
mx = max(p[1] for p in prof)
for s, r, f, l in prof:
    print(f"{s//60}:{s%60:02d} {'#' * int(40 * r / mx):40s} {f:.3f}")
ib = np.diff(beats); print('ibi median', np.median(ib), 'first beats', beats[:12])
