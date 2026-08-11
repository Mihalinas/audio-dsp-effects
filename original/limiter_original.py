import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt

# Podešavanja limitera
threshold_db = -1.0
attack_ms = 0.5
release_ms = 50.0

# Učitavanje audio signala
x, sr = sf.read("input.wav")
x = x.astype(np.float32)

# Stereo kompatibilnost
if x.ndim == 1:
    x = x[:, np.newaxis]

# Pretvaranje parametara u linearni domen
threshold_lin = 10 ** (threshold_db / 20)

attack_coeff = np.exp(
    -1.0 / (sr * attack_ms / 1000)
)

release_coeff = np.exp(
    -1.0 / (sr * release_ms / 1000)
)

y = np.zeros_like(x)

# Glavna petlja limitera
for ch in range(x.shape[1]):
    env = 0.0
    gain = np.ones_like(x[:, ch])

    for i in range(len(x)):
        level = abs(x[i, ch])

        if level > env:
            env = (
                attack_coeff * env
                + (1 - attack_coeff) * level
            )
        else:
            env = (
                release_coeff * env
                + (1 - release_coeff) * level
            )

        if env > threshold_lin:
            gain[i] = threshold_lin / (env + 1e-9)
        else:
            gain[i] = 1.0

    y[:, ch] = x[:, ch] * gain

# Mono rollback
if y.shape[1] == 1:
    y = y[:, 0]

# Snimanje rezultata
sf.write("output_limiter.wav", y, sr)

# Vizuelizacija: ulaz vs. izlaz
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
    label="Signal nakon limitera",
    alpha=0.6
)

if y.ndim > 1 and y.shape[1] > 1:
    plt.plot(y[::factor, 1], alpha=0.6)

plt.title("Limiter: Ulaz naspram Izlaza")
plt.xlabel("Uzorci")
plt.ylabel("Amplituda")
plt.legend()
plt.tight_layout()
plt.show()

