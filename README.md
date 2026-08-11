## Audio DSP Effects

[![Tests](https://github.com/Mihalinas/audio-dsp-effects/actions/workflows/tests.yml/badge.svg)](https://github.com/Mihalinas/audio-dsp-effects/actions/workflows/tests.yml)

A Python-based digital audio processing project containing implementations of common audio effects originally developed as part of a bachelor's thesis at the Faculty of Electrical Engineering, University of Belgrade (ETF).

The project started as a collection of standalone DSP scripts and was subsequently refactored into a modular, testable Python package while preserving the behavior of the original implementations.

## Features

The project currently includes four digital audio effects:

* **8-band Equalizer** — configurable IIR peak-filter based EQ
* **Dynamic Range Compressor** — threshold, ratio, attack, release and makeup gain
* **Peak Limiter** — attack/release envelope-based peak limiting
* **Multi-tap Delay Reverb** — multiple delayed feedback paths for artificial reverberation

The implementations support both **mono and stereo audio signals**.

## Project Structure

```text
audio-dsp-effects/
├── original/
│   ├── eq_original.py
│   ├── compressor_original.py
│   ├── limiter_original.py
│   └── reverb_original.py
│
├── src/
│   └── audio_dsp/
│       ├── __init__.py
│       ├── eq.py
│       ├── compressor.py
│       ├── limiter.py
│       └── reverb.py
│
├── tests/
│   ├── test_eq.py
│   ├── test_compressor.py
│   ├── test_limiter.py
│   └── test_reverb.py
│
├── examples/
├── docs/
├── .github/
│   └── workflows/
│       └── tests.yml
├── pyproject.toml
├── requirements.txt
├── README.md
└── .gitignore
```

## Original Implementations

The `original/` directory contains the DSP implementations as they were developed for the bachelor's thesis.

These implementations are preserved as a reference point for the refactoring process.

The original scripts operate directly on audio files and combine DSP processing, file I/O and visualization in a single script.

## Refactored Implementations

The `src/audio_dsp/` package separates the DSP algorithms from file handling and visualization.

Each effect exposes a reusable Python interface that can be imported by other applications or tested independently.

For example:

```python
import soundfile as sf

from audio_dsp.eq import apply_eq

signal, sample_rate = sf.read("input.wav")

processed = apply_eq(signal, sample_rate)

sf.write("output.wav", processed, sample_rate)
```

The same approach is used for the compressor, limiter and reverb implementations.

## Testing

The refactored implementations are covered by automated tests using `pytest`.

The tests verify the behavior of each DSP component and provide regression protection during the refactoring process.

Run the complete test suite with:

```bash
pytest -q
```

Current test coverage includes:

* Equalizer
* Compressor
* Limiter
* Reverb

During the refactoring process, the refactored implementations were validated against the original scripts using identical input signals.

The automated test suite now uses deterministic test signals and independent reference calculations so that the tests can run reproducibly in CI without requiring external audio files.

GitHub Actions automatically runs the test suite on pushes and pull requests.

## Audio Processing

The project uses standard Python scientific-computing and audio-processing libraries:

* **NumPy** — numerical signal processing
* **SciPy** — digital filter design and filtering
* **SoundFile** — WAV/audio file I/O
* **Matplotlib** — signal visualization
* **pytest** — automated testing

## Installation

Clone the repository:

```bash
git clone https://github.com/Mihalinas/audio-dsp-effects.git
cd audio-dsp-effects
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the project in editable mode together with development dependencies:

```bash
pip install -e ".[dev]"
```

Run the tests:

```bash
pytest -q
```

## Example Workflow

A typical processing workflow consists of:

```text
Input WAV
    │
    ▼
Audio loading
    │
    ▼
DSP effect
    │
    ▼
Processed signal
    │
    ▼
Output WAV
```

Individual effects can be combined to create a larger processing chain, for example:

```text
Input
  │
  ▼
EQ
  │
  ▼
Compressor
  │
  ▼
Limiter
  │
  ▼
Reverb
  │
  ▼
Output
```

## Technical Background

The project demonstrates several fundamental concepts from digital signal processing and digital audio production, including:

* IIR filter design
* Peak-filter based EQ processing
* Amplitude envelope detection
* Attack and release smoothing
* Dynamic range compression
* Peak limiting
* Delay lines
* Feedback processing
* Multi-tap delay structures
* Mono/stereo signal handling
* WAV audio processing
* Numerical signal comparison
* Regression testing

## Thesis Context

The original implementations were developed as part of a bachelor's thesis in the field of digital audio processing at the Faculty of Electrical Engineering, University of Belgrade (ETF).

The goal of this repository is not only to preserve the original implementations, but also to demonstrate how an academic DSP prototype can be transformed into a more maintainable software project with:

* modular architecture
* reusable components
* automated tests
* dependency management
* reproducible setup
* version control
* clear separation between original and refactored implementations

## Development Approach

The refactoring follows a gradual process:

1. Preserve the original DSP implementations.
2. Extract individual DSP algorithms into reusable modules.
3. Add automated tests for each component.
4. Compare refactored output against the original implementation.
5. Keep the original implementation available as a reference.
6. Document the project and its usage.

This approach makes it possible to improve the software structure without losing the original DSP behavior.

## Status

The four core DSP effects have been refactored into the `audio_dsp` package and are covered by automated tests.

The project currently focuses on correctness, reproducibility and clean software structure. Further development can extend the package with additional effects, improved parameter validation, processing pipelines and performance optimizations.

## License

This project is intended primarily as an academic and portfolio project based on work originally developed during bachelor's studies at the Faculty of Electrical Engineering, University of Belgrade.
