import numpy as np

from audio_dsp.reverb import Reverb


def test_reverb_matches_reference():
    sample_rate = 1000

    # Short deterministic stereo test signal.
    signal = np.array(
        [
            [1.0, 0.5],
            [0.0, 0.0],
            [0.0, 0.0],
            [0.0, 0.0],
            [0.0, 0.0],
            [0.0, 0.0],
            [0.0, 0.0],
            [0.0, 0.0],
        ],
        dtype=np.float32,
    )

    delay_times = [0.002, 0.003]
    gains = [0.7, 0.5]
    dry_mix = 0.5
    wet_mix = 0.5

    buffers = [
        [np.zeros(int(sample_rate * dt)) for dt in delay_times]
        for _ in range(signal.shape[1])
    ]

    indices = [
        [0] * len(delay_times)
        for _ in range(signal.shape[1])
    ]

    expected = np.zeros_like(signal)

    for ch in range(signal.shape[1]):
        for n in range(len(signal)):
            sample = signal[n, ch]
            acc = 0.0

            for i in range(len(buffers[ch])):
                buf = buffers[ch][i]
                idx = indices[ch][i]

                acc += buf[idx]
                buf[idx] = sample + buf[idx] * gains[i]

                indices[ch][i] = (idx + 1) % len(buf)

            expected[n, ch] = (
                dry_mix * sample
                + wet_mix * acc
            )

    reverb = Reverb(
        delay_times=delay_times,
        gains=gains,
        dry_mix=dry_mix,
        wet_mix=wet_mix,
    )

    actual = reverb.process(signal, sample_rate)

    np.testing.assert_allclose(
        actual,
        expected,
        atol=1e-6,
        rtol=0,
    )
