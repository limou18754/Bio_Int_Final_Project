"""Analysis helpers for spike trains and beta-band power."""

from __future__ import annotations

import numpy as np
from scipy.signal import welch


BETA_LOW_HZ = 15.0
BETA_HIGH_HZ = 30.0


def population_rate(spike_times_ms: np.ndarray, population_size: int, duration_ms: float, bin_ms: float) -> tuple[np.ndarray, np.ndarray]:
    """Convert spike times to a population firing-rate trace."""

    bins = np.arange(0.0, duration_ms + bin_ms, bin_ms)
    counts, edges = np.histogram(spike_times_ms, bins=bins)
    rate_hz = counts / population_size / (bin_ms / 1000.0)
    time_ms = edges[:-1]
    return time_ms, rate_hz


def power_spectrum(rate_hz: np.ndarray, bin_ms: float) -> tuple[np.ndarray, np.ndarray]:
    """Compute the power spectrum of a rate trace."""

    fs_hz = 1000.0 / bin_ms
    segment = min(512, len(rate_hz))
    freqs_hz, power = welch(rate_hz, fs=fs_hz, nperseg=segment)
    return freqs_hz, power


def beta_band_power(freqs_hz: np.ndarray, power: np.ndarray) -> float:
    """Return integrated power in the beta band."""

    mask = (freqs_hz >= BETA_LOW_HZ) & (freqs_hz <= BETA_HIGH_HZ)
    if not np.any(mask):
        return 0.0
    return float(np.trapezoid(power[mask], freqs_hz[mask]))


def peak_frequency(freqs_hz: np.ndarray, power: np.ndarray) -> float:
    """Return the peak frequency of the spectrum."""

    if len(freqs_hz) == 0:
        return 0.0
    return float(freqs_hz[np.argmax(power)])


def summarize_trial(trial_result: dict, populations: tuple[str, ...] = ("STN", "GPe")) -> dict:
    """Compute rates and spectral summaries for selected populations."""

    summary = {
        "state": trial_result["state"],
        "seed": trial_result["seed"],
        "duration_ms": trial_result["duration_ms"],
        "bin_ms": trial_result["bin_ms"],
        "populations": {},
    }

    for name in populations:
        spike_info = trial_result["spikes"][name]
        time_ms, rate_hz = population_rate(
            spike_times_ms=spike_info["merged_spikes"],
            population_size=spike_info["population_size"],
            duration_ms=trial_result["duration_ms"],
            bin_ms=trial_result["bin_ms"],
        )
        freqs_hz, power = power_spectrum(rate_hz=rate_hz, bin_ms=trial_result["bin_ms"])
        summary["populations"][name] = {
            "time_ms": time_ms,
            "rate_hz": rate_hz,
            "freqs_hz": freqs_hz,
            "power": power,
            "beta_power": beta_band_power(freqs_hz, power),
            "peak_frequency_hz": peak_frequency(freqs_hz, power),
            "mean_rate_hz": float(np.mean(rate_hz)),
        }

    return summary


def aggregate_population_metric(trial_summaries: list[dict], population_name: str, field: str) -> np.ndarray:
    """Stack one metric from multiple trial summaries."""

    return np.vstack([summary["populations"][population_name][field] for summary in trial_summaries])
