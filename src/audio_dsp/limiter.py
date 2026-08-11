import numpy as np


class Limiter:
    """Simple peak limiter with attack and release envelope."""

    def __init__(
        self,
        threshold_db: float = -1.0,
        attack_ms: float = 0.5,
        release_ms: float = 50.0,
    ):
        if attack_ms <= 0:
            raise ValueError("attack_ms must be > 0")

        if release_ms <= 0:
            raise ValueError("release_ms must be > 0")

        self.threshold_db = threshold_db
        self.attack_ms = attack_ms
        self.release_ms = release_ms

    def process(self, signal: np.ndarray, sample_rate: int) -> np.ndarray:
        """Process mono or multi-channel audio."""

        x = np.asarray(signal, dtype=np.float32)
        was_mono = x.ndim == 1

        if was_mono:
            x = x[:, np.newaxis]

        threshold_lin = 10 ** (self.threshold_db / 20)

        attack_coeff = np.exp(
            -1.0 / (sample_rate * self.attack_ms / 1000)
        )
        release_coeff = np.exp(
            -1.0 / (sample_rate * self.release_ms / 1000)
        )

        y = np.zeros_like(x)

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
                    gain[i] = threshold_lin / (env + 1e-9)
                else:
                    gain[i] = 1.0

            y[:, ch] = x[:, ch] * gain

        if was_mono:
            return y[:, 0]

        return y


