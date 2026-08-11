import numpy as np
import soundfile as sf
from scipy.signal import iirpeak, lfilter
import matplotlib.pyplot as plt

# Učitavanje audio signala
x, sr = sf.read("input.wav")
x = x.astype(np.float32)

# Stereo kompatibilnost
if x.ndim == 1:
    x = x[:, np.newaxis]

# Definisanje 8-band ekvilajzera (EQ)
bands = [
    (60, 1.0, 3),
    (120, 1.0, -2),
    (250, 1.0, 4),
    (500, 1.0, 0),
    (1000, 1.0, -3),
    (2000, 1.0, 2),
    (4000, 1.0, -1),
    (8000, 1.0, 3),
]

y = x.copy()

# Primena EQ filtera za svaki pojas
for ch in range(x.shape[1]):
    for f0, Q, gain_db in bands:
        A = 10 ** (gain_db / 40)
        b, a = iirpeak(f0 / (sr / 2), Q)
        y[:, ch] = lfilter(b * A, a, y[:, ch])

# Mono rollback
if y.shape[1] == 1:
    y = y[:, 0]

# Snimanje obrađenog signala
sf.write("output_eq.wav", y, sr)

# Prikaz originalnog i obrađenog signala
factor = 100

plt.figure(figsize=(10, 4))
plt.plot(x[::factor, 0], label="Ulazni signal", alpha=0.6)

if x.shape[1] > 1:
    plt.plot(x[::factor, 1], alpha=0.6)

plt.plot(y[::factor, 0], label="Signal nakon EQ obrade", alpha=0.6)

if y.ndim > 1 and y.shape[1] > 1:
    plt.plot(y[::factor, 1], alpha=0.6)

plt.title("8-band ekvilajzer: Ulaz vs Izlaz")
plt.xlabel("Uzorci")
plt.ylabel("Amplituda")
plt.legend()
plt.tight_layout()
plt.show()
