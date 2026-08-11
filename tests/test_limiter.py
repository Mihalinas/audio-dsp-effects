import numpy as np

from audio_dsp.limiter import Limiter


def test_limiter_matches_reference():
    sample_rate = 44100

    # Deterministic stereo test signal.
    t = np.arange(44100) / sample_rate
    signal = np.column_stack(
        [
            1.2 * np.sin(2 * np.pi * 440 * t),
            0.9 * np.sin(2 * np.pi * 1000 * t),
        ]
    ).astype(np.float32)

    threshold_db = -1.0
    attack_ms = 0.5
    release_ms = 50.0

    threshold_lin = 10 ** (threshold_db / 20)

    attack_coeff = np.exp(
        -1.0 / (sample_rate * attack_ms / 1000)
    )

    release_coeff = np.exp(
        -1.0 / (sample_rate * release_ms / 1000)
    )

    expected = np.zeros_like(signal)

    for ch in range(signal.shape[1]):
        env = 0.0
        gain = np.ones_like(signal[:, ch])

        for i in range(len(signal)):
            level = abs(signal[i, ch])

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

        expected[:, ch] = signal[:, ch] * gain

    limiter = Limiter(
        threshold_db=threshold_db,
        attack_ms=attack_ms,
        release_ms=release_ms,
    )

    actual = limiter.process(signal, sample_rate)

    np.testing.assert_allclose(
        actual,
        expected,
        atol=1e-6,
        rtol=0,
    )
