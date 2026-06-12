"""Plotting utilities for the basal ganglia experiment."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from .analysis import BETA_HIGH_HZ, BETA_LOW_HZ, aggregate_population_metric


def save_raster_plot(trial_result: dict, output_path: Path, populations: tuple[str, ...] = ("STN", "GPe")) -> None:
    """Save a raster plot for selected populations."""

    fig, axes = plt.subplots(len(populations), 1, figsize=(10, 5), sharex=True)
    if len(populations) == 1:
        axes = [axes]

    for axis, name in zip(axes, populations):
        cell_spikes = trial_result["spikes"][name]["cell_spikes"]
        axis.eventplot(cell_spikes, colors="black", lineoffsets=np.arange(len(cell_spikes)), linelengths=0.8)
        axis.set_ylabel(name)
        axis.set_title(f"{trial_result['state'].title()} {name} Raster")

    axes[-1].set_xlabel("Time (ms)")
    fig.tight_layout()
    fig.savefig(output_path, dpi=200)
    plt.close(fig)


def save_rate_plot(healthy_summary: dict, pd_summary: dict, output_path: Path) -> None:
    """Save representative rate traces for STN and GPe."""

    fig, axes = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
    analysis_start_ms = max(healthy_summary.get("analysis_start_ms", 0.0), pd_summary.get("analysis_start_ms", 0.0))

    for axis, population_name in zip(axes, ("STN", "GPe")):
        axis.plot(
            healthy_summary["populations"][population_name]["time_ms"],
            healthy_summary["populations"][population_name]["rate_hz"],
            label="Healthy",
            color="tab:blue",
            alpha=0.8,
        )
        axis.plot(
            pd_summary["populations"][population_name]["time_ms"],
            pd_summary["populations"][population_name]["rate_hz"],
            label="Parkinsonian",
            color="tab:red",
            alpha=0.8,
        )
        if analysis_start_ms > 0.0:
            axis.axvline(analysis_start_ms, color="0.35", linestyle="--", linewidth=1.0, label="Analysis start")
        axis.set_ylabel("Rate (Hz)")
        axis.set_title(f"{population_name} Population Rate")
        axis.legend(loc="upper right")

    axes[-1].set_xlabel("Time (ms)")
    fig.tight_layout()
    fig.savefig(output_path, dpi=200)
    plt.close(fig)


def save_power_spectrum_plot(healthy_trials: list[dict], pd_trials: list[dict], output_path: Path) -> None:
    """Save mean power spectra with trial variability."""

    fig, axes = plt.subplots(1, 2, figsize=(12, 4), sharey=True)

    for axis, population_name in zip(axes, ("STN", "GPe")):
        healthy_freqs = healthy_trials[0]["populations"][population_name]["freqs_hz"]
        pd_freqs = pd_trials[0]["populations"][population_name]["freqs_hz"]
        healthy_power = aggregate_population_metric(healthy_trials, population_name, "power")
        pd_power = aggregate_population_metric(pd_trials, population_name, "power")

        axis.plot(healthy_freqs, healthy_power.mean(axis=0), color="tab:blue", label="Healthy")
        axis.fill_between(
            healthy_freqs,
            healthy_power.mean(axis=0) - healthy_power.std(axis=0),
            healthy_power.mean(axis=0) + healthy_power.std(axis=0),
            color="tab:blue",
            alpha=0.15,
        )

        axis.plot(pd_freqs, pd_power.mean(axis=0), color="tab:red", label="Parkinsonian")
        axis.fill_between(
            pd_freqs,
            pd_power.mean(axis=0) - pd_power.std(axis=0),
            pd_power.mean(axis=0) + pd_power.std(axis=0),
            color="tab:red",
            alpha=0.15,
        )

        axis.axvspan(BETA_LOW_HZ, BETA_HIGH_HZ, color="gold", alpha=0.2)
        axis.set_xlim(0, 60)
        axis.set_title(f"{population_name} Power Spectrum")
        axis.set_xlabel("Frequency (Hz)")
        axis.legend(loc="upper right")

    axes[0].set_ylabel("Power")
    fig.tight_layout()
    fig.savefig(output_path, dpi=200)
    plt.close(fig)
