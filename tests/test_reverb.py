import numpy as np
import soundfile as sf

from audio_dsp.reverb import Reverb


def test_reverb_matches_reference():
    signal, sample_rate = sf.read("input.wav")

    expected, _ = sf.read("output_reverb.wav")

    reverb = Reverb()
    actual = reverb.process(signal, sample_rate)

    np.testing.assert_allclose(
        actual,
        expected,
        atol=1 / 32768,
        rtol=0,
    )


