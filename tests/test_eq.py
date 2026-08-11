import numpy as np
from scipy.signal import iirpeak, lfilter

from audio_dsp.eq import apply_eq


def test_eq_matches_reference():
    sample_rate = 44100

    # Deterministic stereo test signal.
    t = np.arange(44100) / sample_rate
    signal = np.column_stack(
        [
            0.5 * np.sin(2 * np.pi * 440 * t),
            0.5 * np.sin(2 * np.pi * 1000 * t),
        ]
    ).astype(np.float32)

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

    # Reference implementation based directly on the original thesis script.
    expected = signal.copy()

    for ch in range(signal.shape[1]):
        for f0, q, gain_db in bands:
            gain = 10 ** (gain_db / 40)
            b, a = iirpeak(f0 / (sample_rate / 2), q)
            expected[:, ch] = lfilter(
                b * gain,
                a,
                expected[:, ch],
            )

    actual = apply_eq(signal, sample_rate)

    np.testing.assert_allclose(
        actual,
        expected,
        atol=1e-7,
        rtol=0,
    )

