# Final Project Workspace

This folder is now a self-contained repository for the chosen final project:

`How does dopamine depletion promote pathological beta oscillations in a simplified basal ganglia network?`

## Project Structure

- `proposal.md`: compact project proposal in course format
- `work_plan.md`: concrete execution roadmap
- `src/`: runnable simulation and analysis code
- `mechanisms/`: notes about NEURON mechanism dependencies
- `outputs/`: generated figures and JSON summaries
- `paper/`: notes and future mini-paper drafts

## Model Choice

The current implementation uses a simplified spiking neural network in
`NEURON` with built-in `IntFire1` cells.

Populations:

- `D1`
- `D2`
- `STN`
- `GPe`
- `GPi`

This keeps the project:

- close to `Basal ganglia modeling`
- biologically interpretable at the circuit level
- lightweight enough to run quickly and be shared as a small git repo

## Dependency Policy

This repository is designed so that clone users do not need files from the
parent course directory.

- The current code does not require custom `.mod` files.
- It uses only built-in `NEURON` artificial cells.
- The default assumption is that you run this repository with the Python
  interpreter from a conda environment that already has `neuron` installed.
- The reasoning is documented in [mechanisms/README.md](/c:/Users/86180/Desktop/undergraduate/2025-Spring/Bio-Int/lab/final_project/mechanisms/README.md).

## How To Run

This repository should be run with the interpreter inside your
`NEURON`-enabled conda environment.

Recommended workflow from the `final_project` directory:

```powershell
conda activate <your-neuron-env>
python -m pip install -r requirements.txt
python -m src.run_experiment
```

For this project, `python` should mean the `python.exe` inside that conda
environment.

- If your activated environment contains `neuron`, that interpreter is used.
- If `neuron` is missing from the active interpreter, the code raises a clear
  error by default.
- Standalone Windows NEURON paths such as `C:\nrn` are used only if you
  explicitly opt in:

```powershell
$env:NEURON_ALLOW_SYSTEM_FALLBACK=1
python -m src.run_experiment
```

Direct script execution is also supported, but the same interpreter rule
still applies:

```powershell
conda activate <your-neuron-env>
python src/run_experiment.py
```

## Outputs

Running the experiment generates:

- `outputs/healthy_raster.png`
- `outputs/parkinsonian_raster.png`
- `outputs/population_rates.png`
- `outputs/power_spectra.png`
- `outputs/summary.json`

The main analysis compares healthy and Parkinsonian conditions and reports
how beta-band power changes in `STN` and `GPe`.
