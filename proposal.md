# Final Project Proposal

## Title

Dopamine Depletion and the Emergence of Pathological Beta Oscillations in a Simplified Basal Ganglia Network

## Question

How does dopamine depletion, modeled as a shift in direct-pathway and
indirect-pathway balance, promote abnormal beta-band oscillations in the
STN-GPe loop of the basal ganglia?

## Model

The project uses a simplified spiking neural network implemented in
`NEURON` with built-in `IntFire1` cells.

Populations:

- `D1` striatal neurons
- `D2` striatal neurons
- `STN` neurons
- `GPe` neurons
- `GPi` readout neurons

Core circuit logic:

- `D2 -> GPe` inhibitory indirect pathway
- `GPe -> STN` inhibitory projection
- `STN -> GPe` excitatory feedback projection
- `D1 -> GPi` inhibitory direct pathway
- `STN -> GPi` excitatory output pathway

Healthy and Parkinsonian states are represented by different drive levels
and connection-weight scales, especially:

- reduced `D1` drive / direct-pathway effect
- enhanced `D2 -> GPe` inhibition
- stronger effective `STN <-> GPe` loop gain

## Experiment

For each condition:

1. run the network with noisy external drive
2. record spike times from `STN` and `GPe`
3. convert spikes into population firing-rate traces
4. compute power spectra with Welch's method
5. compare beta-band power between states

## Expected Result

The Parkinsonian condition should show:

- stronger rhythmic population activity in `STN` and `GPe`
- increased spectral power in the `15-30 Hz` beta band
- a clearer oscillatory peak than the healthy condition

## Interpretation

The mechanism hypothesis is that stronger indirect-pathway inhibition
changes the operating point of the `GPe-STN` excitatory-inhibitory loop.
With delays and stronger loop gain, the circuit becomes more resonant in
the beta range, which provides a simplified explanation for pathological
beta activity in Parkinsonian basal ganglia.

