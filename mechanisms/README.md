# Mechanisms

This repository currently uses only built-in `NEURON` artificial cells:
`IntFire1`.

That means:

- no custom `.mod` files are required for the current implementation
- no local `nrnmech.dll` compilation step is needed
- the default expectation is that the project is launched from a conda
  environment whose interpreter already has `neuron`
- the project can run after installing `NEURON` plus the Python packages in
  `requirements.txt`

If the model is later upgraded to conductance-based neurons or custom
synapses, the required `.mod` files should be placed in this folder.
