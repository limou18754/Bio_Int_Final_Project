# Code Availability

This repository contains the code, generated outputs, and manuscript source for the study:

`Dopamine Depletion and the Emergence of Pathological Beta Oscillations in a Simplified Basal Ganglia Network`

The project implements a reduced basal ganglia network in `NEURON` using built-in `IntFire1` cells. The model includes five populations: `D1`, `D2`, `STN`, `GPe`, and `GPi`. Its purpose is to test whether dopamine depletion, represented as a change in pathway balance and STN-GPe loop gain, is sufficient to produce stronger low-beta oscillations.

## Repository Contents

- `paper/`: LaTeX manuscript, bibliography, and compiled PDF
- `src/`: simulation, analysis, and plotting scripts
- `outputs/`: generated figures and summary files used in the manuscript
- `figures/`: static schematic assets
- `mechanisms/`: note on NEURON mechanism requirements
- `requirements.txt`: Python dependencies other than `neuron`

## Software Requirements

This repository assumes a Python environment in which `NEURON` is already installed.

Install the remaining packages with:

```powershell
python -m pip install -r requirements.txt
```

## Reproducing the Main Results

Run the healthy-versus-parkinsonian comparison from the repository root:

```powershell
python -m src.run_experiment --output-dir outputs
```

This command writes the main manuscript outputs to `outputs/`, including:

- `healthy_raster.png`
- `parkinsonian_raster.png`
- `population_rates.png`
- `power_spectra.png`
- `summary.json`

## Reproducing the Extension Analyses

Run the D2-to-GPe sweep:

```powershell
python -m src.run_d2_gpe_sweep --base-state parkinsonian
```

Run the simplified DBS-like intervention analysis:

```powershell
python -m src.run_dbs_intervention
```

These scripts generate the additional manuscript outputs:

- `d2_gpe_beta_power_sweep.png`
- `d2_gpe_sweep_summary.json`
- `dbs_intervention_spectra.png`
- `dbs_intervention_summary.json`

## Notes

- No custom `.mod` files are required for the current implementation.
- The DBS-like input is a phenomenological high-frequency suppressive or disruptive drive, not a biophysical extracellular stimulation model.
- The manuscript source is in [main.tex](/c:/Users/86180/Desktop/undergraduate/2025-Spring/Bio-Int/lab/final_project/paper/main.tex), and the compiled paper is [main.pdf](/c:/Users/86180/Desktop/undergraduate/2025-Spring/Bio-Int/lab/final_project/paper/main.pdf).
