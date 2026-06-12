# Mechanism Notes

The current model uses only built-in `NEURON` artificial cells (`IntFire1`).

For this repository version:

- no custom `.mod` mechanism files are needed
- no local `nrnmech.dll` compilation step is required
- the code should run once `NEURON` and the packages in `requirements.txt` are installed

If the model is extended in the future with conductance-based neurons or custom synapses, the corresponding `.mod` files should be placed in this directory.
