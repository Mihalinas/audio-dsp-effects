import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt

# Parametri reverba (odjeka)
delay_times = [0.0297, 0.0371, 0.0411, 0.0437]
gains = [0.7] * len(delay_times)

# Učitavanje audio signala
x, sr = sf.read("input.wav")
x = x.astype(np.float32)

# Stereo kompatibilnost
if x.ndim == 1:
    x = x[:, np.newaxis]

# Inicijalizacija bafera i indeksa po kanalima
buffers = [
    [np.zeros(int(sr * dt)) for dt in delay_times]
    for _ in range(x.shape[1])
]

indices = [
    [0] * len(delay_times)
    for _ in range(x.shape[1])
]

y = np.zeros_like(x)

# Glavna petlja obrade
for ch in range(x.shape[1]):
    for n in range(len(x)):
        sample = x[n, ch]
        acc = 0.0

        for i in range(len(buffers[ch])):
            buf = buffers[ch][i]
            idx = indices[ch][i]

            acc += buf[idx]
            buf[idx] = sample + buf[idx] * gains[i]
            indices[ch][i] = (idx + 1) % len(buf)

        y[n, ch] = 0.5 * sample + 0.5 * acc

# Mono rollback
if y.shape[1] == 1:
    y = y[:, 0]

# Snimanje izlaznog signala
sf.write("output_reverb.wav", y, sr)

# Vizuelni prikaz: ulaz vs. izlaz
factor = 100

plt.figure(figsize=(10, 4))
plt.plot(
    x[::factor, 0],
    label="Ulazni signal",
    alpha=0.6
)

if x.shape[1] > 1:
    plt.plot(x[::factor, 1], alpha=0.6)

plt.plot(
    y[::factor, 0],
    label="Signal sa odjekom",
    alpha=0.6
)

if y.ndim > 1 and y.shape[1] > 1:
    plt.plot(y[::factor, 1], alpha=0.6)

plt.title("Reverb: Ulaz naspram Izlaza")
plt.xlabel("Uzorci")
plt.ylabel("Amplituda")
plt.legend()
plt.tight_layout()
plt.show()


