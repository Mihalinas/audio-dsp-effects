import numpy as np
import soundfile as sf

from audio_dsp.compressor import Compressor


def test_compressor_matches_reference():
    signal, sample_rate = sf.read("input.wav")

    expected, _ = sf.read("output_compressor.wav")

    compressor = Compressor()
    actual = compressor.process(signal, sample_rate)

    np.testing.assert_allclose(
        actual,
        expected,
        atol=1 / 32768,
        rtol=0,
    )

