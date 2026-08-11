import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt

# Podešavanja kompresora
threshold_db = -20
ratio = 3.0
attack_ms = 10
release_ms = 100
makeup_gain_db = 3

# Učitavanje audio signala
x, sr = sf.read("input.wav")
x = x.astype(np.float32)

# Stereo kompatibilnost
if x.ndim == 1:
    x = x[:, np.newaxis]

# Pretvaranje parametara iz dB u linearni domen
threshold_lin = 10 ** (threshold_db / 20)

attack_coeff = np.exp(
    -1.0 / (sr * attack_ms / 1000)
)

release_coeff = np.exp(
    -1.0 / (sr * release_ms / 1000)
)

makeup_gain = 10 ** (makeup_gain_db / 20)

y = np.zeros_like(x)

# Glavna petlja kompresora
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
            gain_db = (
                threshold_db
                + (20 * np.log10(env) - threshold_db) / ratio
            )

            gain[i] = 10 ** (
                (gain_db - 20 * np.log10(env)) / 20
            )
        else:
            gain[i] = 1.0

    y[:, ch] = x[:, ch] * gain * makeup_gain

# Mono rollback
if y.shape[1] == 1:
    y = y[:, 0]

# Snimanje rezultujućeg signala
sf.write("output_compressor.wav", y, sr)

# Prikaz ulaznog i izlaznog signala
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
    label="Signal posle kompresije",
    alpha=0.6
)

if y.ndim > 1 and y.shape[1] > 1:
    plt.plot(y[::factor, 1], alpha=0.6)

plt.title("Kompresor: Ulaz naspram Izlaza")
plt.xlabel("Uzorci")
plt.ylabel("Amplituda")
plt.legend()
plt.tight_layout()
plt.show()
