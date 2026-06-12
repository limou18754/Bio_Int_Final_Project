"""Run a targeted D2->GPe weight sweep as a mechanism experiment."""

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

    from src.analysis import BETA_HIGH_HZ, BETA_LOW_HZ, summarize_trial
    from src.config import STATE_MODIFIERS, make_state_config
    from src.model import BasalGangliaNetwork
else:
    from .analysis import BETA_HIGH_HZ, BETA_LOW_HZ, summarize_trial
    from .config import STATE_MODIFIERS, make_state_config
    from .model import BasalGangliaNetwork


def run_trials_for_scale(
    base_state: str,
    d2_gpe_scale: float,
    seeds: list[int],
    duration_ms: float,
    analysis_start_ms: float,
    bin_ms: float | None,
) -> list[dict]:
    """Run multiple trials for one D2->GPe scale value and return summaries."""

    config = make_state_config(
        base_state,
        duration_ms=duration_ms,
        bin_ms=bin_ms,
        connection_weight_scale_overrides={("D2", "GPe"): d2_gpe_scale},
    )

    summaries = []
    for seed in seeds:
        model = BasalGangliaNetwork(config=config, seed=seed)
        trial = model.run()
        summaries.append(summarize_trial(trial, analysis_start_ms=analysis_start_ms))
    return summaries


def summarize_scale(scale: float, trial_summaries: list[dict]) -> dict:
    """Aggregate trial-level metrics for one sweep point."""

    population_metrics = {}
    for population_name in ("STN", "GPe"):
        beta_power = np.array([summary["populations"][population_name]["beta_power"] for summary in trial_summaries])
        mean_rate = np.array([summary["populations"][population_name]["mean_rate_hz"] for summary in trial_summaries])
        beta_peak = np.array(
            [summary["populations"][population_name]["beta_peak_frequency_hz"] for summary in trial_summaries]
        )

        population_metrics[population_name] = {
            "beta_power_mean": float(np.mean(beta_power)),
            "beta_power_std": float(np.std(beta_power)),
            "mean_rate_hz_mean": float(np.mean(mean_rate)),
            "mean_rate_hz_std": float(np.std(mean_rate)),
            "beta_peak_frequency_hz_mean": float(np.mean(beta_peak)),
            "beta_peak_frequency_hz_std": float(np.std(beta_peak)),
            "trial_beta_power": beta_power.tolist(),
            "trial_mean_rate_hz": mean_rate.tolist(),
            "trial_beta_peak_frequency_hz": beta_peak.tolist(),
        }

    return {
        "d2_gpe_scale": scale,
        "populations": population_metrics,
    }


def save_sweep_plot(
    sweep_results: list[dict],
    output_path: Path,
    base_state: str,
    healthy_reference_scale: float,
    parkinsonian_reference_scale: float,
) -> None:
    """Save a compact two-panel plot for STN and GPe beta power across the sweep."""

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5), sharex=True)
    scales = np.array([result["d2_gpe_scale"] for result in sweep_results], dtype=float)

    for axis, population_name in zip(axes, ("STN", "GPe")):
        means = np.array([result["populations"][population_name]["beta_power_mean"] for result in sweep_results], dtype=float)
        stds = np.array([result["populations"][population_name]["beta_power_std"] for result in sweep_results], dtype=float)

        axis.plot(scales, means, color="tab:red", linewidth=2.0, marker="o")
        axis.fill_between(scales, means - stds, means + stds, color="tab:red", alpha=0.18)
        axis.axvline(healthy_reference_scale, color="tab:blue", linestyle="--", linewidth=1.2, label="Healthy reference")
        axis.axvline(
            parkinsonian_reference_scale,
            color="tab:red",
            linestyle=":",
            linewidth=1.4,
            label="Parkinsonian reference",
        )
        axis.set_title(f"{population_name} {BETA_LOW_HZ:.0f}-{BETA_HIGH_HZ:.0f} Hz Power")
        axis.set_xlabel("D2 -> GPe weight scale")
        axis.set_ylabel("Integrated power")
        axis.grid(alpha=0.2)

    axes[0].legend(loc="upper left")
    fig.suptitle(f"D2 -> GPe Sweep on {base_state.title()} Background", fontsize=13)
    fig.tight_layout()
    fig.savefig(output_path, dpi=200)
    plt.close(fig)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a D2->GPe parameter sweep.")
    parser.add_argument(
        "--base-state",
        choices=tuple(STATE_MODIFIERS.keys()),
        default="parkinsonian",
        help="State used for all parameters other than the swept D2->GPe weight.",
    )
    parser.add_argument(
        "--scales",
        type=float,
        nargs="+",
        default=[1.0, 1.2, 1.4, 1.62, 1.8, 2.0],
        help="Absolute D2->GPe weight scales to test.",
    )
    parser.add_argument("--trials", type=int, default=10, help="Number of seeds per sweep point.")
    parser.add_argument("--seed-start", type=int, default=1, help="First random seed.")
    parser.add_argument("--duration-ms", type=float, default=8000.0, help="Simulation duration in milliseconds.")
    parser.add_argument(
        "--analysis-start-ms",
        type=float,
        default=1000.0,
        help="Discard activity before this time when computing rates and spectra.",
    )
    parser.add_argument("--bin-ms", type=float, default=None, help="Optional analysis bin size override in milliseconds.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "outputs",
        help="Directory for generated sweep outputs.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.analysis_start_ms >= args.duration_ms:
        raise ValueError("--analysis-start-ms must be smaller than --duration-ms.")

    scales = sorted(dict.fromkeys(args.scales))
    seeds = list(range(args.seed_start, args.seed_start + args.trials))
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    healthy_reference_scale = STATE_MODIFIERS["healthy"]["connection_weight_scales"][("D2", "GPe")]
    parkinsonian_reference_scale = STATE_MODIFIERS["parkinsonian"]["connection_weight_scales"][("D2", "GPe")]

    sweep_results = []
    for scale in scales:
        trial_summaries = run_trials_for_scale(
            args.base_state,
            scale,
            seeds,
            duration_ms=args.duration_ms,
            analysis_start_ms=args.analysis_start_ms,
            bin_ms=args.bin_ms,
        )
        sweep_results.append(summarize_scale(scale, trial_summaries))

    save_sweep_plot(
        sweep_results=sweep_results,
        output_path=output_dir / "d2_gpe_beta_power_sweep.png",
        base_state=args.base_state,
        healthy_reference_scale=healthy_reference_scale,
        parkinsonian_reference_scale=parkinsonian_reference_scale,
    )

    summary_payload = {
        "experiment": {
            "type": "d2_gpe_weight_sweep",
            "base_state": args.base_state,
            "trials_per_scale": args.trials,
            "seed_start": args.seed_start,
            "seeds": seeds,
            "duration_ms": args.duration_ms,
            "analysis_start_ms": args.analysis_start_ms,
            "analysis_stop_ms": args.duration_ms,
            "bin_ms": make_state_config(args.base_state, bin_ms=args.bin_ms)["bin_ms"],
            "focus_band_low_hz": BETA_LOW_HZ,
            "focus_band_high_hz": BETA_HIGH_HZ,
            "healthy_reference_scale": healthy_reference_scale,
            "parkinsonian_reference_scale": parkinsonian_reference_scale,
        },
        "sweep_results": sweep_results,
    }

    with (output_dir / "d2_gpe_sweep_summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary_payload, handle, indent=2)

    print(f"Completed D2 -> GPe sweep on {args.base_state} background.")
    for result in sweep_results:
        stn = result["populations"]["STN"]["beta_power_mean"]
        gpe = result["populations"]["GPe"]["beta_power_mean"]
        print(f"scale={result['d2_gpe_scale']:.2f}: STN beta={stn:.3f}, GPe beta={gpe:.3f}")
    print(f"Saved outputs to: {output_dir.resolve()}")


if __name__ == "__main__":
    main()
