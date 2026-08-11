import numpy as np
from scipy.signal import iirpeak


DEFAULT_BANDS = [
    (60, 1.0, 3.0),
    (120, 1.0, -2.0),
    (250, 1.0, 4.0),
    (500, 1.0, 0.0),
    (1000, 1.0, -3.0),
    (2000, 1.0, 2.0),
    (4000, 1.0, -1.0),
    (8000, 1.0, 3.0),
]


def apply_eq(
    signal: np.ndarray,
    sample_rate: int,
    bands: list[tuple[float, float, float]] = DEFAULT_BANDS,
) -> np.ndarray:
    """Apply the thesis 8-band EQ implementation to an audio signal.

    Parameters
    ----------
    signal:
        Audio signal as a NumPy array. Shape can be (samples,) for mono
        or (samples, channels) for multi-channel audio.

    sample_rate:
        Audio sample rate in Hz.

    bands:
        List of (center_frequency_hz, Q, gain_db) tuples.

    Returns
    -------
    np.ndarray
        Processed audio signal with the same channel structure as input.
    """
    x = np.asarray(signal, dtype=np.float32)

    was_mono = x.ndim == 1

    if was_mono:
        x = x[:, np.newaxis]

    y = x.copy()

    for ch in range(x.shape[1]):
        for f0, q, gain_db in bands:
            gain = 10 ** (gain_db / 40)
            b, a = iirpeak(f0 / (sample_rate / 2), q)
            y[:, ch] = _apply_filter(y[:, ch], b * gain, a)

    if was_mono:
        return y[:, 0]

    return y


def _apply_filter(
    signal: np.ndarray,
    b: np.ndarray,
    a: np.ndarray,
) -> np.ndarray:
    """Apply one IIR filter.

    Kept separate so the DSP operation is easy to test.
    """
    from scipy.signal import lfilter

    return lfilter(b, a, signal)
