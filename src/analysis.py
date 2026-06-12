"""Analysis helpers for spike trains and low-beta-focused spectral summaries."""

from __future__ import annotations

import numpy as np
from scipy.signal import welch


BETA_LOW_HZ = 10.0
BETA_HIGH_HZ = 25.0


def population_rate(
    spike_times_ms: np.ndarray,
    population_size: int,
    duration_ms: float,
    bin_ms: float,
    start_ms: float = 0.0,
    stop_ms: float | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Convert spike times to a population firing-rate trace."""

    stop_ms = duration_ms if stop_ms is None else min(stop_ms, duration_ms)
    if stop_ms <= start_ms:
        raise ValueError("Analysis window must satisfy stop_ms > start_ms.")

    trimmed_spikes = spike_times_ms[(spike_times_ms >= start_ms) & (spike_times_ms < stop_ms)]
    bins = np.arange(start_ms, stop_ms + bin_ms, bin_ms)
    if len(bins) < 2:
        bins = np.array([start_ms, stop_ms], dtype=float)
    if len(trimmed_spikes):
        counts, edges = np.histogram(trimmed_spikes, bins=bins)
    else:
        counts = np.zeros(len(bins) - 1, dtype=float)
        edges = bins
    rate_hz = counts / population_size / (bin_ms / 1000.0)
    time_ms = edges[:-1]
    return time_ms, rate_hz


def power_spectrum(rate_hz: np.ndarray, bin_ms: float, max_segment_bins: int = 1024) -> tuple[np.ndarray, np.ndarray]:
    """Compute the power spectrum of a rate trace."""

    if len(rate_hz) < 2:
        return np.array([]), np.array([])

    fs_hz = 1000.0 / bin_ms
    segment = min(max_segment_bins, len(rate_hz))
    freqs_hz, power = welch(rate_hz, fs=fs_hz, nperseg=segment)
    return freqs_hz, power


def beta_band_power(freqs_hz: np.ndarray, power: np.ndarray) -> float:
    """Return integrated power in the project-defined 10-25 Hz focus band."""

    mask = (freqs_hz >= BETA_LOW_HZ) & (freqs_hz <= BETA_HIGH_HZ)
    if not np.any(mask):
        return 0.0
    return float(np.trapezoid(power[mask], freqs_hz[mask]))


def peak_frequency(freqs_hz: np.ndarray, power: np.ndarray) -> float:
    """Return the peak frequency of the spectrum."""

    if len(freqs_hz) == 0:
        return 0.0
    return float(freqs_hz[np.argmax(power)])


def band_peak_frequency(freqs_hz: np.ndarray, power: np.ndarray, low_hz: float, high_hz: float) -> float:
    """Return the strongest spectral peak inside one frequency band."""

    mask = (freqs_hz >= low_hz) & (freqs_hz <= high_hz)
    if not np.any(mask):
        return 0.0
    band_freqs = freqs_hz[mask]
    band_power = power[mask]
    return float(band_freqs[np.argmax(band_power)])


def summarize_trial(
    trial_result: dict,
    populations: tuple[str, ...] = ("STN", "GPe"),
    analysis_start_ms: float = 0.0,
    analysis_stop_ms: float | None = None,
) -> dict:
    """Compute rates and spectral summaries for selected populations."""

    analysis_stop_ms = trial_result["duration_ms"] if analysis_stop_ms is None else min(analysis_stop_ms, trial_result["duration_ms"])
    summary = {
        "state": trial_result["state"],
        "seed": trial_result["seed"],
        "duration_ms": trial_result["duration_ms"],
        "bin_ms": trial_result["bin_ms"],
        "analysis_start_ms": analysis_start_ms,
        "analysis_stop_ms": analysis_stop_ms,
        "analysis_duration_ms": analysis_stop_ms - analysis_start_ms,
        "populations": {},
    }

    for name in populations:
        spike_info = trial_result["spikes"][name]
        time_ms, rate_hz = population_rate(
            spike_times_ms=spike_info["merged_spikes"],
            population_size=spike_info["population_size"],
            duration_ms=trial_result["duration_ms"],
            bin_ms=trial_result["bin_ms"],
            start_ms=analysis_start_ms,
            stop_ms=analysis_stop_ms,
        )
        freqs_hz, power = power_spectrum(rate_hz=rate_hz, bin_ms=trial_result["bin_ms"])
        summary["populations"][name] = {
            "time_ms": time_ms,
            "rate_hz": rate_hz,
            "freqs_hz": freqs_hz,
            "power": power,
            "beta_power": beta_band_power(freqs_hz, power),
            "global_peak_frequency_hz": peak_frequency(freqs_hz, power),
            "beta_peak_frequency_hz": band_peak_frequency(freqs_hz, power, BETA_LOW_HZ, BETA_HIGH_HZ),
            "mean_rate_hz": float(np.mean(rate_hz)),
        }

    return summary


def aggregate_population_metric(trial_summaries: list[dict], population_name: str, field: str) -> np.ndarray:
    """Stack one metric from multiple trial summaries."""

    return np.vstack([summary["populations"][population_name][field] for summary in trial_summaries])
