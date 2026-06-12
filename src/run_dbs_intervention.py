"""Run a simplified DBS-like intervention experiment on the Parkinsonian network."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if __package__ in (None, ""):
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))

    from src.analysis import BETA_HIGH_HZ, BETA_LOW_HZ, aggregate_population_metric, summarize_trial
    from src.config import make_state_config
    from src.model import BasalGangliaNetwork
else:
    from .analysis import BETA_HIGH_HZ, BETA_LOW_HZ, aggregate_population_metric, summarize_trial
    from .config import make_state_config
    from .model import BasalGangliaNetwork


def build_intervention(target: str, frequency_hz: float, weight: float, start_ms: float, stop_ms: float) -> dict:
    """Create one deterministic high-frequency pulse train specification."""

    return {
        "target": target,
        "interval_ms": 1000.0 / frequency_hz,
        "weight": weight,
        "start_ms": start_ms,
        "stop_ms": stop_ms,
        "delay_ms": 0.1,
    }


def run_condition(
    condition_name: str,
    state_name: str,
    seeds: list[int],
    duration_ms: float,
    analysis_start_ms: float,
    bin_ms: float,
    intervention: dict | None = None,
) -> list[dict]:
    """Run one condition across seeds and return analyzed summaries."""

    config = make_state_config(
        state_name,
        duration_ms=duration_ms,
        bin_ms=bin_ms,
        intervention=intervention,
    )

    summaries = []
    for seed in seeds:
        model = BasalGangliaNetwork(config=config, seed=seed)
        trial = model.run()
        summary = summarize_trial(trial, populations=("STN", "GPe", "GPi"), analysis_start_ms=analysis_start_ms)
        summary["condition_name"] = condition_name
        summaries.append(summary)
    return summaries


def summarize_condition(condition_name: str, trial_summaries: list[dict]) -> dict:
    """Aggregate trial-level metrics for one condition."""

    populations = {}
    for population_name in ("STN", "GPe", "GPi"):
        beta_power = np.array([summary["populations"][population_name]["beta_power"] for summary in trial_summaries])
        beta_peak = np.array(
            [summary["populations"][population_name]["beta_peak_frequency_hz"] for summary in trial_summaries]
        )
        global_peak = np.array(
            [summary["populations"][population_name]["global_peak_frequency_hz"] for summary in trial_summaries]
        )
        mean_rate = np.array([summary["populations"][population_name]["mean_rate_hz"] for summary in trial_summaries])

        populations[population_name] = {
            "beta_power_mean": float(np.mean(beta_power)),
            "beta_power_std": float(np.std(beta_power)),
            "beta_peak_frequency_mean_hz": float(np.mean(beta_peak)),
            "beta_peak_frequency_std_hz": float(np.std(beta_peak)),
            "global_peak_frequency_mean_hz": float(np.mean(global_peak)),
            "global_peak_frequency_std_hz": float(np.std(global_peak)),
            "mean_rate_hz_mean": float(np.mean(mean_rate)),
            "mean_rate_hz_std": float(np.std(mean_rate)),
            "trial_beta_power": beta_power.tolist(),
        }

    return {"condition": condition_name, "populations": populations}


def save_intervention_spectrum_plot(condition_trials: dict[str, list[dict]], output_path: Path) -> None:
    """Save STN and GPe spectra for healthy, Parkinsonian, and DBS conditions."""

    colors = {
        "healthy": "tab:blue",
        "parkinsonian": "tab:red",
        "parkinsonian_stn_dbs": "tab:green",
        "parkinsonian_gpi_dbs": "tab:orange",
    }
    labels = {
        "healthy": "Healthy",
        "parkinsonian": "Parkinsonian",
        "parkinsonian_stn_dbs": "Parkinsonian + STN DBS",
        "parkinsonian_gpi_dbs": "Parkinsonian + GPi DBS",
    }
    line_styles = {
        "healthy": "-",
        "parkinsonian": "--",
        "parkinsonian_stn_dbs": "-",
        "parkinsonian_gpi_dbs": ":",
    }
    markers = {
        "healthy": None,
        "parkinsonian": None,
        "parkinsonian_stn_dbs": None,
        "parkinsonian_gpi_dbs": "o",
    }
    plot_order = ("healthy", "parkinsonian_gpi_dbs", "parkinsonian", "parkinsonian_stn_dbs")
    legend_order = ("healthy", "parkinsonian", "parkinsonian_stn_dbs", "parkinsonian_gpi_dbs")

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5), sharey=True)
    for axis, population_name in zip(axes, ("STN", "GPe")):
        mean_power_by_condition = {}
        handles = {}
        for condition_name in plot_order:
            trials = condition_trials[condition_name]
            freqs_hz = trials[0]["populations"][population_name]["freqs_hz"]
            power = aggregate_population_metric(trials, population_name, "power")
            mean_power = power.mean(axis=0)
            mean_power_by_condition[condition_name] = mean_power
            (handle,) = axis.plot(
                freqs_hz,
                mean_power,
                color=colors[condition_name],
                linewidth=2.2,
                linestyle=line_styles[condition_name],
                marker=markers[condition_name],
                markersize=4.2 if markers[condition_name] else 0,
                markevery=18 if markers[condition_name] else None,
                markerfacecolor="white" if markers[condition_name] else None,
                markeredgewidth=1.0 if markers[condition_name] else None,
                label=labels[condition_name],
            )
            handles[condition_name] = handle
            axis.fill_between(
                freqs_hz,
                mean_power - power.std(axis=0),
                mean_power + power.std(axis=0),
                color=colors[condition_name],
                alpha=0.1,
            )

        axis.axvspan(BETA_LOW_HZ, BETA_HIGH_HZ, color="gold", alpha=0.18)
        axis.set_xlim(0, 80)
        axis.set_xlabel("Frequency (Hz)")
        axis.set_title(f"{population_name} Power Spectrum")
        axis.grid(alpha=0.2)
        if np.allclose(
            mean_power_by_condition["parkinsonian"],
            mean_power_by_condition["parkinsonian_gpi_dbs"],
        ):
            axis.text(
                0.03,
                0.97,
                "GPi DBS overlaps Parkinsonian",
                transform=axis.transAxes,
                va="top",
                fontsize=8,
                bbox={"boxstyle": "round,pad=0.2", "facecolor": "white", "alpha": 0.8, "edgecolor": "0.8"},
            )

    axes[0].set_ylabel("Power")
    axes[1].legend([handles[name] for name in legend_order], [labels[name] for name in legend_order], loc="upper right", fontsize=8)
    fig.tight_layout()
    fig.savefig(output_path, dpi=200)
    plt.close(fig)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a simplified DBS-like intervention experiment.")
    parser.add_argument("--trials", type=int, default=10, help="Number of seeds per condition.")
    parser.add_argument("--seed-start", type=int, default=1, help="First random seed.")
    parser.add_argument("--duration-ms", type=float, default=8000.0, help="Simulation duration in milliseconds.")
    parser.add_argument(
        "--analysis-start-ms",
        type=float,
        default=1000.0,
        help="Discard activity before this time when computing rates and spectra.",
    )
    parser.add_argument(
        "--dbs-start-ms",
        type=float,
        default=1000.0,
        help="Onset time for DBS pulses.",
    )
    parser.add_argument(
        "--dbs-frequency-hz",
        type=float,
        default=130.0,
        help="DBS pulse frequency in Hz.",
    )
    parser.add_argument(
        "--dbs-weight",
        type=float,
        default=-0.25,
        help="Pulse weight delivered to each target cell. Negative values approximate suppressive/disruptive DBS in this reduced model.",
    )
    parser.add_argument(
        "--bin-ms",
        type=float,
        default=2.0,
        help="Rate bin size in milliseconds. A finer bin helps resolve high-frequency stimulation.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "outputs",
        help="Directory for generated intervention outputs.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.analysis_start_ms >= args.duration_ms:
        raise ValueError("--analysis-start-ms must be smaller than --duration-ms.")
    if args.dbs_start_ms >= args.duration_ms:
        raise ValueError("--dbs-start-ms must be smaller than --duration-ms.")

    seeds = list(range(args.seed_start, args.seed_start + args.trials))
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    stn_dbs = build_intervention("STN", args.dbs_frequency_hz, args.dbs_weight, args.dbs_start_ms, args.duration_ms)
    gpi_dbs = build_intervention("GPi", args.dbs_frequency_hz, args.dbs_weight, args.dbs_start_ms, args.duration_ms)

    condition_trials = {
        "healthy": run_condition(
            "healthy",
            "healthy",
            seeds,
            duration_ms=args.duration_ms,
            analysis_start_ms=args.analysis_start_ms,
            bin_ms=args.bin_ms,
        ),
        "parkinsonian": run_condition(
            "parkinsonian",
            "parkinsonian",
            seeds,
            duration_ms=args.duration_ms,
            analysis_start_ms=args.analysis_start_ms,
            bin_ms=args.bin_ms,
        ),
        "parkinsonian_stn_dbs": run_condition(
            "parkinsonian_stn_dbs",
            "parkinsonian",
            seeds,
            duration_ms=args.duration_ms,
            analysis_start_ms=args.analysis_start_ms,
            bin_ms=args.bin_ms,
            intervention=stn_dbs,
        ),
        "parkinsonian_gpi_dbs": run_condition(
            "parkinsonian_gpi_dbs",
            "parkinsonian",
            seeds,
            duration_ms=args.duration_ms,
            analysis_start_ms=args.analysis_start_ms,
            bin_ms=args.bin_ms,
            intervention=gpi_dbs,
        ),
    }

    save_intervention_spectrum_plot(condition_trials, output_dir / "dbs_intervention_spectra.png")

    condition_summaries = [
        summarize_condition(condition_name, condition_trials[condition_name])
        for condition_name in ("healthy", "parkinsonian", "parkinsonian_stn_dbs", "parkinsonian_gpi_dbs")
    ]

    metrics_by_condition = {entry["condition"]: entry["populations"] for entry in condition_summaries}
    summary_payload = {
        "experiment": {
            "type": "dbs_intervention",
            "trials_per_condition": args.trials,
            "seed_start": args.seed_start,
            "seeds": seeds,
            "duration_ms": args.duration_ms,
            "analysis_start_ms": args.analysis_start_ms,
            "analysis_stop_ms": args.duration_ms,
            "bin_ms": args.bin_ms,
            "focus_band_low_hz": BETA_LOW_HZ,
            "focus_band_high_hz": BETA_HIGH_HZ,
            "dbs_frequency_hz": args.dbs_frequency_hz,
            "dbs_weight": args.dbs_weight,
            "dbs_start_ms": args.dbs_start_ms,
        },
        "interventions": {
            "stn_dbs": stn_dbs,
            "gpi_dbs": gpi_dbs,
        },
        "conditions": condition_summaries,
    }

    with (output_dir / "dbs_intervention_summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary_payload, handle, indent=2)

    print("Completed DBS intervention comparison.")
    for condition_name in ("healthy", "parkinsonian", "parkinsonian_stn_dbs", "parkinsonian_gpi_dbs"):
        stn_beta = metrics_by_condition[condition_name]["STN"]["beta_power_mean"]
        gpe_beta = metrics_by_condition[condition_name]["GPe"]["beta_power_mean"]
        print(f"{condition_name}: STN beta={stn_beta:.3f}, GPe beta={gpe_beta:.3f}")
    print(f"Saved outputs to: {output_dir.resolve()}")


if __name__ == "__main__":
    main()
