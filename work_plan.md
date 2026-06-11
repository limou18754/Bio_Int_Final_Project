# Work Plan

This plan now assumes the selected project is:
`How does dopamine depletion promote beta-band oscillations in a simplified basal ganglia network?`

## Phase 1: Lock the Scientific Framing

Goal:
make the final research question precise and defensible.

Working hypothesis:
`Dopamine depletion shifts direct-pathway and indirect-pathway balance, increases effective GPe-STN loop gain, and thereby increases beta-band power in STN and GPe population activity.`

Deliverables:

- one final project title
- one hypothesis paragraph
- one short note clarifying that D1 is included as pathway context, while the beta mechanism is centered on the indirect pathway and the `GPe-STN` loop

## Phase 2: Build the Self-Contained Repository Model

Tasks:

- keep all runnable code inside `final_project/`
- use built-in `NEURON` `IntFire1` cells so the repo does not depend on custom `.mod` compilation
- define `D1`, `D2`, `STN`, `GPe`, and `GPi` populations
- implement noisy external drive, sparse connectivity, and connection delays
- define healthy and Parkinsonian parameter sets

Outputs:

- `src/model.py`
- `src/run_experiment.py`
- a reproducible run command from the repo root

## Phase 3: Run the Core Healthy-vs-PD Experiment

Primary manipulations:

- reduce `D1` drive / direct-pathway impact
- increase `D2 -> GPe` inhibition
- strengthen effective `STN <-> GPe` loop interactions

Measurements:

- `STN` population firing rate
- `GPe` population firing rate
- power spectrum of `STN` and `GPe`
- beta-band power in `15-30 Hz`
- peak spectral frequency

Plots to produce:

- raster plot for a representative healthy trial
- raster plot for a representative Parkinsonian trial
- population-rate comparison
- healthy vs Parkinsonian power spectra

## Phase 4: Add One Strong Extension

Choose one:

1. sweep `D2 -> GPe` inhibitory weight
2. sweep `GPe -> STN` and `STN -> GPe` delays
3. sweep background cortical-like drive to `STN`

Recommendation:
start with `1`, because it connects most directly to the dopamine-depletion story.

## Phase 5: Interpret the Circuit Mechanism

Questions to answer in writing:

- Why does stronger indirect-pathway inhibition shift the operating point of the loop?
- Why can an excitatory-inhibitory delayed feedback loop resonate in the beta range?
- Why does the healthy condition remain weaker or less organized in beta?
- What biological details are missing from this simplified model?

## Phase 6: Write the Mini Paper

Suggested structure:

1. Introduction
2. Model and Methods
3. Results
4. Discussion
5. Conclusion

Minimum figure set:

1. circuit schematic
2. representative raster or rate traces
3. power spectrum comparison
4. beta-power summary figure

## Concrete Timeline

Given today is `2026-06-11`, a practical schedule is:

1. `2026-06-11` to `2026-06-13`: finalize the circuit, run the first healthy/PD comparison
2. `2026-06-14` to `2026-06-16`: add one parameter sweep and clean the figures
3. `2026-06-17` to `2026-06-19`: draft methods, results, and discussion
4. `2026-06-20` to `2026-06-22`: revise the mini paper and polish the repo

Note:
the course PDF says the main deadline is between `2026-06-20` and `2026-06-28`,
while fourth-year students must submit before `2026-06-18`.

## Next Best Step

The repo already contains the first runnable implementation.
The next most valuable step is:

1. run `python -m src.run_experiment`
2. inspect `outputs/summary.json` and the generated spectra
3. decide which single extension sweep to add first
