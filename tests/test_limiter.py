import numpy as np
import soundfile as sf

from audio_dsp.limiter import Limiter


def test_limiter_matches_reference():
    signal, sample_rate = sf.read("input.wav")

    expected, _ = sf.read("output_limiter.wav")

    limiter = Limiter()
    actual = limiter.process(signal, sample_rate)

    np.testing.assert_allclose(
        actual,
        expected,
        atol=1 / 32768,
        rtol=0,
    )


