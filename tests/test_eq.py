import numpy as np
import soundfile as sf

from audio_dsp.eq import apply_eq


def test_eq_matches_reference():
    signal, sample_rate = sf.read("input.wav")

    expected, _ = sf.read("output_eq.wav")

    actual = apply_eq(signal, sample_rate)

    np.testing.assert_allclose(
        actual,
        expected,
        atol=1 / 32768,
        rtol=0,
    )


