# DSP Overview

This document connects the theoretical material from the thesis with the original implementations, the refactored project structure, and the automated tests.

The project implements four fundamental audio DSP building blocks:

- An eight-band equalizer.
- A dynamic range compressor.
- A limiter.
- An algorithmic reverb.

The goal of the refactoring is not to replace the original algorithms with unrelated implementations. Instead, the original code is reorganized into focused, reusable modules while preserving the main processing concepts and making the behaviour easier to inspect and test.

## Project Context

The original implementations were developed as standalone Python scripts accompanying the thesis *Signal Processing Tools in Digital Audio Production*.

The thesis presents the theoretical background of four common audio effects:

| Effect | Main DSP concept | Original implementation | Refactored implementation | Test |
|---|---|---|---|---|
| 8-band EQ | Cascaded IIR filters | [`eq_original.py`](../original/eq_original.py) | [`eq.py`](../src/audio_dsp/eq.py) | [`test_eq.py`](../tests/test_eq.py) |
| Compressor | Envelope detection and gain reduction | [`compressor_original.py`](../original/compressor_original.py) | [`compressor.py`](../src/audio_dsp/compressor.py) | [`test_compressor.py`](../tests/test_compressor.py) |
| Limiter | Envelope-based peak control | [`limiter_original.py`](../original/limiter_original.py) | [`limiter.py`](../src/audio_dsp/limiter.py) | [`test_limiter.py`](../tests/test_limiter.py) |
| Reverb | Multi-tap delay lines and feedback | [`reverb_original.py`](../original/reverb_original.py) | [`reverb.py`](../src/audio_dsp/reverb.py) | [`test_reverb.py`](../tests/test_reverb.py) |

The thesis describes the theoretical principles behind these effects, while this repository focuses on making the implementations modular, readable, reproducible, and testable.

## Processing Model

All four effects operate on a discrete-time audio signal.

For a mono signal, the input can be represented as

\[
x[n]
\]

where \(n\) is the sample index. For a stereo or multichannel signal, the same processing model is applied independently to each channel unless the effect explicitly introduces cross-channel interaction.

The sample rate \(f_s\) determines the relationship between time-based parameters and samples. For example, a delay of \(t\) seconds corresponds approximately to

\[
D = \lfloor t f_s \rfloor
\]

samples.

Audio parameters are often expressed in decibels, while signal processing is performed using linear amplitude values. The conversion from decibels to amplitude is

\[
A = 10^{G_{\mathrm{dB}}/20}
\]

and the reverse conversion is

\[
G_{\mathrm{dB}} = 20 \log_{10}(A).
\]

This distinction is especially important for equalizer gain, compressor thresholds, and limiter ceilings.

## 8-Band Equalizer

### Theory

An equalizer changes the frequency content of an audio signal by applying filters with different frequency responses.

For a digital filter, the output can be described in the frequency domain as

\[
Y(z) = H(z)X(z)
\]

where:

- \(X(z)\) is the input signal.
- \(H(z)\) is the filter transfer function.
- \(Y(z)\) is the output signal.

The thesis discusses the main parameters used in parametric equalization:

- Center or cutoff frequency.
- Gain.
- Quality factor \(Q\).
- Filter slope.

The quality factor is commonly expressed as

\[
Q = \frac{f_0}{\Delta f}
\]

where \(f_0\) is the center frequency and \(\Delta f\) is the bandwidth.

A higher \(Q\) produces a narrower and more selective filter. A lower \(Q\) produces a wider and more gradual tonal change.

The thesis also introduces several common filter types, including high-pass, low-pass, band-pass, notch, peak, low-shelf, and high-shelf filters.

### Original implementation

The original EQ implementation defines eight frequency bands and processes them sequentially.

The main processing steps are:

1. Load the audio signal.
2. Convert the signal to floating-point representation.
3. Normalize mono input into a channel-oriented representation.
4. Design a filter for each configured band.
5. Apply the filters successively to every channel.
6. Restore the mono shape when necessary.
7. Write the processed signal to an output file.

The original implementation uses `scipy.signal.iirpeak` to design band-pass-style IIR filters and `scipy.signal.lfilter` to process the signal. The gain value is converted from decibels into a linear multiplier before being applied to each filter.

This is best understood as a frequency-band equalizer approximation rather than a complete commercial-style parametric EQ. In particular, the implementation does not expose every filter type discussed in the thesis, such as dedicated shelf and notch modes.

### Refactored implementation

The refactored EQ implementation is exposed through the
[`apply_eq`](../src/audio_dsp/eq.py) function. The original reference
script is preserved in [`eq_original.py`](../original/eq_original.py), while
the numerical equivalence is checked by
[`test_eq_matches_reference`](../tests/test_eq.py).

This makes the effect easier to reuse in other contexts:

- A caller can provide an array directly.
- The processing function can be used without reading or writing WAV files.
- Configuration can be passed explicitly.
- The implementation can be tested with deterministic synthetic signals.
- The DSP code is no longer coupled to plotting.

The conceptual signal flow remains:

```text
input signal
    ↓
band 1 filter
    ↓
band 2 filter
    ↓
...
    ↓
band 8 filter
    ↓
output signal
```

Because the filters are cascaded, the response of the complete equalizer is the product of the individual filter responses:

\[
H_{\mathrm{EQ}}(z)
=
\prod_{k=1}^{8} H_k(z).
\]

This also means that the order of processing and the filter state are relevant implementation details.

### Test intent

The current EQ test uses a deterministic stereo signal and compares
[`apply_eq`](../src/audio_dsp/eq.py) with a reference calculation based
directly on the original thesis algorithm.

The test verifies that:

- The eight configured bands are processed in the same order.
- The same IIR filters are designed for each band.
- Gain is converted and applied consistently.
- Both stereo channels are processed.
- The refactored implementation matches the original numerical result
  within a defined tolerance.

This is a reference-equivalence test. It protects the refactoring from
accidental changes while preserving the behaviour of
[`eq_original.py`](../original/eq_original.py). It is not yet a complete
frequency-response or perceptual-audio test.

## Dynamic Range Compressor

### Theory

A compressor reduces the dynamic range of an audio signal. It attenuates signal levels above a threshold while leaving lower levels unchanged or less affected.

The main compressor parameters are:

- Threshold.
- Ratio.
- Attack time.
- Release time.
- Knee.
- Make-up gain.
- Optional lookahead.

The thesis describes the compressor as a combination of envelope detection, gain-reduction calculation, and time-dependent gain smoothing.

### Envelope detection

The original implementation uses the absolute value of the signal as an amplitude estimate:

\[
a[n] = |x[n]|.
\]

The envelope is then smoothed recursively using different coefficients for attack and release:

\[
e[n] =
\begin{cases}
\alpha_{\mathrm{attack}}e[n-1]
+
(1-\alpha_{\mathrm{attack}})a[n],
& a[n] > e[n-1] \\
\alpha_{\mathrm{release}}e[n-1]
+
(1-\alpha_{\mathrm{release}})a[n],
& a[n] \leq e[n-1].
\end{cases}
\]

The coefficients are derived from the selected time constants:

\[
\alpha = e^{-1/(\tau f_s)}
\]

where:

- \(\tau\) is the attack or release time in seconds.
- \(f_s\) is the sample rate.

This allows the compressor to react quickly to increasing signal levels and recover more slowly after the signal falls.

### Gain reduction

The envelope is compared with the threshold in the linear domain. If the envelope exceeds the threshold, the target output level is calculated according to the compression ratio.

In decibels, a hard-knee compressor can be described as

\[
y =
\begin{cases}
x, & x \leq T \\
T + \frac{x-T}{R}, & x > T
\end{cases}
\]

where:

- \(x\) is the input level in dB.
- \(y\) is the output level in dB.
- \(T\) is the threshold.
- \(R\) is the compression ratio.

The required gain is then obtained from the difference between the target output level and the detected input level.

### Original implementation

The original compressor processes each channel independently.

Its main steps are:

1. Convert the threshold from dB to linear amplitude.
2. Calculate attack and release coefficients.
3. Track the signal envelope.
4. Calculate gain reduction when the envelope exceeds the threshold.
5. Apply the time-varying gain to the input signal.
6. Apply make-up gain.
7. Save the result.

The implementation represents a clear feed-forward compressor structure:

```text
input
  ├── envelope detector
  │       ↓
  │   gain computer
  │       ↓
  │   gain smoothing
  │
  └──────────────→ gain application → output
```

### Refactored implementation

The refactored compressor is implemented by the
[`Compressor`](../src/audio_dsp/compressor.py) class and its
`.process(...)` method. The original script is preserved in
[`compressor_original.py`](../original/compressor_original.py), while
[`test_compressor_matches_reference`](../tests/test_compressor.py) compares
the refactored output with the reference calculation.

This improves the code in several ways:

- Compressor parameters can be passed directly to the processing function.
- The algorithm can be reused in batch processing or a future real-time pipeline.
- The envelope and gain behaviour can be tested independently through public behaviour.
- The code can support both mono and multichannel arrays without duplicating the complete processing logic.

The refactored version should be viewed as a compact broadband compressor. The thesis discusses additional features such as soft knee, RMS detection, and lookahead, but those features are not necessarily part of the current implementation. This distinction is intentional: the documentation separates the broader theory from the subset currently implemented in the repository.

### Test intent

The current compressor test uses a deterministic stereo signal and compares
[`Compressor.process(...)`](../src/audio_dsp/compressor.py) with a reference
calculation based directly on the original thesis implementation.

The test verifies that:

- The envelope calculation matches the original algorithm.
- Attack and release coefficients are calculated consistently.
- Threshold and ratio are applied consistently.
- Make-up gain is applied consistently.
- Both stereo channels are processed.
- The refactored implementation matches the original numerical result
  within a defined tolerance.

This is a reference-equivalence test. It protects the refactoring from
accidental changes while preserving the behaviour of
[`compressor_original.py`](../original/compressor_original.py). It is not yet
a complete perceptual test for attack, release, knee, or loudness behaviour.

## Limiter

### Theory

A limiter is a dynamic processor designed to prevent the signal from exceeding a specified maximum level.

Conceptually, it is a compressor with an extremely high ratio. For an ideal limiter, the static transfer function is

\[
y =
\begin{cases}
x, & x \leq T \\
T, & x > T
\end{cases}
\]

where \(T\) is the limiting threshold or ceiling.

Unlike a general-purpose compressor, a limiter is primarily used to protect the output from excessive peaks and to increase perceived loudness without allowing the signal to exceed a selected maximum.

The thesis discusses envelope following, gain reduction, lookahead, release time, input gain, and ceiling control as relevant limiter concepts.

### Original implementation

The original limiter uses the same general envelope-following idea as the compressor, but applies a direct gain correction when the envelope exceeds the threshold:

\[
g[n] =
\begin{cases}
1, & e[n] \leq T \\
\frac{T}{e[n]}, & e[n] > T.
\end{cases}
\]

The signal is then processed as

\[
y[n] = x[n]g[n].
\]

The original implementation includes:

- A threshold expressed in dB.
- Attack and release smoothing.
- Per-channel processing.
- A small numerical stabilizer in the denominator.
- WAV output and plotting.

### Refactored implementation

The refactored limiter is implemented by the
[`Limiter`](../src/audio_dsp/limiter.py) class and its
`.process(...)` method. The original script is preserved in
[`limiter_original.py`](../original/limiter_original.py), while
[`test_limiter_matches_reference`](../tests/test_limiter.py) compares the
refactored output with the reference calculation.

This implementation should not be described as a full mastering-grade brickwall limiter. The theoretical limiter model in the thesis includes features such as lookahead and oversampling, while the current implementation is a simpler sample-domain limiter based on envelope detection.

That difference is important for technical transparency:

- The current limiter reduces detected peaks.
- It does not provide a complete inter-sample peak guarantee.
- It does not currently implement a dedicated lookahead buffer.
- It is intended as a clear educational DSP implementation rather than a production mastering processor.

### Test intent

The current limiter test uses a deterministic stereo signal and compares
[`Limiter.process(...)`](../src/audio_dsp/limiter.py) with a reference
calculation based directly on the original thesis implementation.

The test verifies that:

- The envelope calculation matches the original algorithm.
- Attack and release coefficients are calculated consistently.
- Threshold-based gain reduction is applied consistently.
- Both stereo channels are processed.
- The refactored implementation matches the original numerical result
  within a defined tolerance.

This is a reference-equivalence test. It protects the refactoring from
accidental changes while preserving the behaviour of
[`limiter_original.py`](../original/limiter_original.py).

Because the implementation uses a smoothed envelope, it should not be
described as a complete true-peak or lookahead brickwall limiter. The thesis
discusses those more advanced techniques, but they are outside the scope of
the current implementation.

## Algorithmic Reverb

### Theory

Reverb simulates the reflections and energy decay of an acoustic space.

The general linear-system model is

\[
y[n] = x[n] * h[n]
\]

where:

- \(x[n]\) is the input signal.
- \(h[n]\) is the impulse response of the simulated space.
- \(y[n]\) is the reverberated output.
- \(*\) denotes convolution.

A convolution reverb uses a measured or designed impulse response directly. An algorithmic reverb instead synthesizes a similar response using delays, filters, and feedback structures.

The thesis distinguishes between:

- Early reflections, which represent the first discrete reflections from nearby surfaces.
- Late reflections, which create a dense and diffuse reverberation tail.
- Damping, which models the faster absorption of high frequencies.
- Pre-delay, which separates the direct sound from the onset of the reverberant field.
- Wet/dry mixing, which controls the balance between processed and unprocessed signal.

### Delay-line model

The original reverb uses several delay lines with feedback.

A simple feedback delay can be represented as

\[
y[n] = x[n] + g\,y[n-D]
\]

where:

- \(D\) is the delay in samples.
- \(g\) is the feedback gain.
- \(|g| < 1\) is required for a decaying response.

Several delay lines with different lengths produce a denser pattern of echoes. The delay times used by the original implementation are different non-uniform values, which helps prevent all echoes from arriving at the same periodic interval.

The thesis also discusses comb filters, all-pass filters, and feedback delay networks as more advanced algorithmic reverb structures. The current implementation uses the simpler parallel feedback-delay approach rather than a complete FDN or Schroeder network.

### Original implementation

The original reverb performs the following operations:

1. Define delay times and feedback gains.
2. Convert delay times from seconds to samples.
3. Allocate a circular buffer for every delay line and channel.
4. Read the delayed samples.
5. Feed the current sample back into each delay line.
6. Combine the delayed signal with the direct signal.
7. Restore mono shape when necessary.
8. Save the output.

Conceptually, the signal flow is:

```text
                 ┌── delay line 1 ──┐
input ───────────┼── delay line 2 ──┼── feedback sum ──┐
                 ├── delay line 3 ──┤                  │
                 └── delay line 4 ──┘                  │
                                                       ↓
                         dry signal + reverberated signal
```

### Refactored implementation

The refactored reverb is implemented by the
[`Reverb`](../src/audio_dsp/reverb.py) class and its
`.process(...)` method. The original script is preserved in
[`reverb_original.py`](../original/reverb_original.py), while
[`test_reverb_matches_reference`](../tests/test_reverb.py) compares the
refactored output with the reference calculation.

The refactoring clarifies several important implementation details:

- Delay times are converted using the supplied sample rate.
- Each delay line has its own circular buffer.
- Buffer indices advance modulo the buffer length.
- Feedback gains determine the decay rate.
- The direct and delayed signals are mixed explicitly.
- Mono and multichannel inputs are handled consistently.

This gives the repository a compact and understandable example of stateful DSP processing. Unlike a memoryless gain or filter operation, a reverb depends on state from previous samples.

### Test intent

The current reverb test uses a short deterministic stereo signal and compares
[`Reverb.process(...)`](../src/audio_dsp/reverb.py) with a reference
calculation based directly on the original thesis implementation.

The test verifies that:

- Delay buffers are created consistently.
- Delay-line indices are advanced consistently.
- Feedback gains are applied consistently.
- Dry and wet signals are mixed consistently.
- Both stereo channels are processed.
- The refactored implementation matches the original numerical result
  within a defined tolerance.

This is a reference-equivalence test. It protects the refactoring from
accidental changes while preserving the behaviour of
[`reverb_original.py`](../original/reverb_original.py).

The current implementation is a multi-tap feedback-delay reverb. It does not
yet implement a complete feedback delay network, all-pass diffusion stages,
frequency-dependent damping, or independent stereo cross-feed.

## Thesis-to-Repository Mapping

The relationship between the thesis and the repository can be summarized as follows:

| Layer | Role in the project |
|---|---|
| Thesis theory | Defines the DSP concepts, parameters, equations, and expected signal-processing behaviour |
| [`original/`](../original/) | Preserves the standalone implementations developed for the thesis |
| [`src/audio_dsp/`](../src/audio_dsp/) | Provides modular, reusable versions of the DSP effects |
| [`tests/`](../tests/) | Verifies observable behaviour and protects the refactored code from regressions |
| CI workflow | Runs the test suite automatically on repository changes |

The thesis provides a broader theoretical scope than the current codebase. For example, it discusses soft-knee compression, lookahead limiting, oversampling, and feedback delay networks, while the repository contains intentionally smaller implementations of these ideas.

This is not a contradiction. It shows the difference between:

- The full design space of an audio DSP effect.
- The specific algorithm selected for an educational implementation.
- The engineering work required to make that algorithm modular and testable.

## Design Decisions

### Separate DSP from I/O

The original scripts combine signal processing with:

- WAV file loading.
- WAV file writing.
- Plotting.
- Parameter configuration.
- Shape conversion.

The refactored modules focus on the DSP operation itself. File I/O and visualization can be handled by a separate application layer.

This separation makes the processing functions easier to:

- Reuse.
- Benchmark.
- Test.
- Integrate into another audio pipeline.
- Extend with additional input and output formats.

### Preserve channel shape

Audio arrays commonly use either:

- A one-dimensional shape for mono audio.
- A two-dimensional shape for multichannel audio.

The implementations normalize the internal representation where necessary and restore the expected external shape afterward. This keeps the processing logic consistent while preserving a convenient public API.

### Prefer explicit state

The compressor, limiter, and reverb all depend on state from previous samples:

- The compressor and limiter maintain an envelope.
- The reverb maintains delay-line buffers and indices.

Keeping this state visible in the implementation is useful for understanding the algorithms and for testing their time-dependent behaviour.

### Test behaviour, not implementation details

The tests are designed around signal-processing properties rather than private variables or exact internal loops.

For example, a compressor test should verify gain reduction above the threshold. It should not depend on the exact name of the envelope variable or on a specific loop structure.

This keeps the tests useful during future refactoring, provided that the externally observable DSP behaviour remains compatible.

## Current Scope and Future Work

The current repository provides compact reference implementations of four common audio DSP effects. It is intentionally focused on clarity and modularity rather than production-grade mastering performance.

Possible future improvements include:

- Parametric biquad filters for a more complete EQ implementation.
- Dedicated low-pass, high-pass, shelf, notch, and peak filter modes.
- RMS-based or weighted envelope detection.
- Soft-knee compression.
- Explicit lookahead buffers for the compressor and limiter.
- Oversampling and true-peak detection.
- Stereo-linked dynamics processing.
- Damping filters inside the reverb feedback paths.
- All-pass diffusion stages.
- Feedback delay networks.
- Performance benchmarking for longer audio signals.
- Frequency-response and impulse-response visualizations.

These extensions should be added only when they serve a clear technical purpose. The current structure provides a stable foundation for introducing them incrementally.

## References

The theoretical background for this overview is based on the thesis and the following references cited there:

- Zölzer, U. *Digital Audio Signal Processing*, 2nd edition, Wiley, 2011.
- Reiss, J. D., and McPherson, A. *Audio Effects: Theory, Implementation and Application*, CRC Press, 2014.
- Pohlmann, K. C. *Principles of Digital Audio*, 6th edition, McGraw-Hill, 2010.

The original thesis contains the detailed discussion of the four effects, their parameters, mathematical models, and standalone Python implementations.
