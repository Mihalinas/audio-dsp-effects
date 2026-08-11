import numpy as np


class Reverb:
    """Simple multi-tap delay reverb."""

    def __init__(
        self,
        delay_times: list[float] | None = None,
        gains: list[float] | None = None,
        dry_mix: float = 0.5,
        wet_mix: float = 0.5,
    ):
        if delay_times is None:
            delay_times = [0.0297, 0.0371, 0.0411, 0.0437]

        if gains is None:
            gains = [0.7] * len(delay_times)

        if len(delay_times) != len(gains):
            raise ValueError("delay_times and gains must have equal length")

        if not delay_times:
            raise ValueError("at least one delay time is required")

        if any(dt <= 0 for dt in delay_times):
            raise ValueError("delay times must be > 0")

        self.delay_times = delay_times
        self.gains = gains
        self.dry_mix = dry_mix
        self.wet_mix = wet_mix

    def process(self, signal: np.ndarray, sample_rate: int) -> np.ndarray:
        """Process mono or multi-channel audio."""

        x = np.asarray(signal, dtype=np.float32)
        was_mono = x.ndim == 1

        if was_mono:
            x = x[:, np.newaxis]

        buffers = [
            [np.zeros(int(sample_rate * dt)) for dt in self.delay_times]
            for _ in range(x.shape[1])
        ]

        indices = [
            [0] * len(self.delay_times)
            for _ in range(x.shape[1])
        ]

        y = np.zeros_like(x)

        for ch in range(x.shape[1]):
            for n in range(len(x)):
                sample = x[n, ch]
                acc = 0.0

                for i in range(len(buffers[ch])):
                    buf = buffers[ch][i]
                    idx = indices[ch][i]

                    acc += buf[idx]
                    buf[idx] = sample + buf[idx] * self.gains[i]

                    indices[ch][i] = (idx + 1) % len(buf)

                y[n, ch] = (
                    self.dry_mix * sample
                    + self.wet_mix * acc
                )

        if was_mono:
            return y[:, 0]

        return y


