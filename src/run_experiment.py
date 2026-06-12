"""Run the basal ganglia healthy vs Parkinsonian comparison."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if __package__ in (None, ""):
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))

    from src.analysis import BETA_HIGH_HZ, BETA_LOW_HZ, summarize_trial
    from src.config import make_state_config
    from src.model import BasalGangliaNetwork
    from src.plotting import save_power_spectrum_plot, save_raster_plot, save_rate_plot
else:
    from .analysis import BETA_HIGH_HZ, BETA_LOW_HZ, summarize_trial
    from .config import make_state_config
    from .model import BasalGangliaNetwork
    from .plotting import save_power_spectrum_plot, save_raster_plot, save_rate_plot


def run_trials(
    state_name: str,
    seeds: list[int],
    duration_ms: float,
    analysis_start_ms: float,
    bin_ms: float | None,
) -> tuple[list[dict], list[dict]]:
    """Run multiple trials and return raw trials plus analyzed summaries."""

    raw_trials = []
    summaries = []
    config = make_state_config(state_name, duration_ms=duration_ms, bin_ms=bin_ms)
    for seed in seeds:
        model = BasalGangliaNetwork(config=config, seed=seed)
        trial = model.run()
        summary = summarize_trial(trial, analysis_start_ms=analysis_start_ms)
        raw_trials.append(trial)
        summaries.append(summary)
    return raw_trials, summaries


def build_metrics(healthy_summaries: list[dict], pd_summaries: list[dict]) -> dict:
    """Create a compact metrics dictionary for JSON output."""

    metrics = {}
    for population_name in ("STN", "GPe"):
        healthy_beta = np.array([summary["populations"][population_name]["beta_power"] for summary in healthy_summaries])
        pd_beta = np.array([summary["populations"][population_name]["beta_power"] for summary in pd_summaries])
        healthy_global_peak = np.array(
            [summary["populations"][population_name]["global_peak_frequency_hz"] for summary in healthy_summaries]
        )
        pd_global_peak = np.array(
            [summary["populations"][population_name]["global_peak_frequency_hz"] for summary in pd_summaries]
        )
        healthy_beta_peak = np.array(
            [summary["populations"][population_name]["beta_peak_frequency_hz"] for summary in healthy_summaries]
        )
        pd_beta_peak = np.array(
            [summary["populations"][population_name]["beta_peak_frequency_hz"] for summary in pd_summaries]
        )

        metrics[population_name] = {
            "healthy_beta_power_mean": float(np.mean(healthy_beta)),
            "healthy_beta_power_std": float(np.std(healthy_beta)),
            "parkinsonian_beta_power_mean": float(np.mean(pd_beta)),
            "parkinsonian_beta_power_std": float(np.std(pd_beta)),
            "beta_power_ratio_pd_over_healthy": float(np.mean(pd_beta) / max(np.mean(healthy_beta), 1e-9)),
            "healthy_global_peak_frequency_mean_hz": float(np.mean(healthy_global_peak)),
            "healthy_global_peak_frequency_std_hz": float(np.std(healthy_global_peak)),
            "parkinsonian_global_peak_frequency_mean_hz": float(np.mean(pd_global_peak)),
            "parkinsonian_global_peak_frequency_std_hz": float(np.std(pd_global_peak)),
            "healthy_beta_peak_frequency_mean_hz": float(np.mean(healthy_beta_peak)),
            "healthy_beta_peak_frequency_std_hz": float(np.std(healthy_beta_peak)),
            "parkinsonian_beta_peak_frequency_mean_hz": float(np.mean(pd_beta_peak)),
            "parkinsonian_beta_peak_frequency_std_hz": float(np.std(pd_beta_peak)),
        }
    return metrics


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the basal ganglia beta-oscillation experiment.")
    parser.add_argument("--trials", type=int, default=10, help="Number of seeds per condition.")
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
        help="Directory for generated results.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.analysis_start_ms >= args.duration_ms:
        raise ValueError("--analysis-start-ms must be smaller than --duration-ms.")

    seeds = list(range(args.seed_start, args.seed_start + args.trials))
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    healthy_trials, healthy_summaries = run_trials(
        "healthy",
        seeds,
        duration_ms=args.duration_ms,
        analysis_start_ms=args.analysis_start_ms,
        bin_ms=args.bin_ms,
    )
    pd_trials, pd_summaries = run_trials(
        "parkinsonian",
        seeds,
        duration_ms=args.duration_ms,
        analysis_start_ms=args.analysis_start_ms,
        bin_ms=args.bin_ms,
    )

    metrics = build_metrics(healthy_summaries, pd_summaries)
    summary_payload = {
        "experiment": {
            "trials_per_condition": args.trials,
            "seed_start": args.seed_start,
            "duration_ms": args.duration_ms,
            "analysis_start_ms": args.analysis_start_ms,
            "analysis_stop_ms": args.duration_ms,
            "bin_ms": healthy_trials[0]["bin_ms"],
            "focus_band_low_hz": BETA_LOW_HZ,
            "focus_band_high_hz": BETA_HIGH_HZ,
        },
        "seeds": seeds,
        "metrics": metrics,
    }

    representative_healthy = healthy_summaries[0]
    representative_pd = pd_summaries[0]
    representative_healthy_trial = healthy_trials[0]
    representative_pd_trial = pd_trials[0]

    save_raster_plot(representative_healthy_trial, output_dir / "healthy_raster.png")
    save_raster_plot(representative_pd_trial, output_dir / "parkinsonian_raster.png")
    save_rate_plot(representative_healthy, representative_pd, output_dir / "population_rates.png")
    save_power_spectrum_plot(healthy_summaries, pd_summaries, output_dir / "power_spectra.png")

    with (output_dir / "summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary_payload, handle, indent=2)

    print("Completed healthy vs Parkinsonian comparison.")
    for population_name, values in metrics.items():
        print(
            f"{population_name}: {BETA_LOW_HZ:.0f}-{BETA_HIGH_HZ:.0f} Hz power {values['healthy_beta_power_mean']:.3f} -> "
            f"{values['parkinsonian_beta_power_mean']:.3f}, "
            f"ratio={values['beta_power_ratio_pd_over_healthy']:.2f}, "
            f"global peak={values['parkinsonian_global_peak_frequency_mean_hz']:.2f} Hz, "
            f"focus-band peak={values['parkinsonian_beta_peak_frequency_mean_hz']:.2f} Hz"
        )
    print(f"Saved outputs to: {output_dir.resolve()}")


if __name__ == "__main__":
    main()
