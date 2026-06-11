"""NEURON model construction for the basal ganglia project."""

from __future__ import annotations

import random
from dataclasses import dataclass

import numpy as np

from .neuron_env import ensure_neuron

h = ensure_neuron()
h.load_file("stdrun.hoc")

POPULATION_STREAM_IDS = {
    "D1": 101,
    "D2": 102,
    "STN": 201,
    "GPe": 202,
    "GPi": 203,
}


@dataclass
class PopulationRecord:
    cells: list
    recorders: list
    spike_vectors: list


class BasalGangliaNetwork:
    """Simplified spiking network for basal ganglia beta oscillation studies."""

    def __init__(self, config: dict, seed: int) -> None:
        self.config = config
        self.seed = seed
        self.random = random.Random(seed)
        self.populations: dict[str, PopulationRecord] = {}
        self.external_stims: list = []
        self.connections: list = []
        self._build()

    def _build_population(self, name: str, spec: dict) -> PopulationRecord:
        cells = []
        recorders = []
        spike_vectors = []

        for _ in range(spec["size"]):
            cell = h.IntFire1()
            cell.tau = spec["tau"]
            cell.refrac = spec["refrac"]
            cells.append(cell)

            spike_vector = h.Vector()
            recorder = h.NetCon(cell, None)
            recorder.record(spike_vector)
            spike_vectors.append(spike_vector)
            recorders.append(recorder)

        return PopulationRecord(cells=cells, recorders=recorders, spike_vectors=spike_vectors)

    def _add_external_drive(self, population_name: str, spec: dict) -> None:
        for cell_index, cell in enumerate(self.populations[population_name].cells):
            stim = h.NetStim()
            stim.interval = spec["drive_interval"]
            stim.number = 1e9
            stim.start = 0.0
            stim.noise = 1.0
            stim.noiseFromRandom123(self.seed, POPULATION_STREAM_IDS[population_name], cell_index)

            netcon = h.NetCon(stim, cell)
            netcon.delay = 1.0
            netcon.weight[0] = spec["drive_weight"]

            self.external_stims.append(stim)
            self.connections.append(netcon)

    def _connect_populations(self, connection_spec: dict) -> None:
        pre_population = self.populations[connection_spec["pre"]].cells
        post_population = self.populations[connection_spec["post"]].cells

        for pre_cell in pre_population:
            for post_cell in post_population:
                if self.random.random() < connection_spec["p"]:
                    netcon = h.NetCon(pre_cell, post_cell)
                    netcon.delay = connection_spec["delay_ms"]
                    netcon.weight[0] = connection_spec["weight"]
                    self.connections.append(netcon)

    def _build(self) -> None:
        for name, spec in self.config["populations"].items():
            self.populations[name] = self._build_population(name, spec)

        for name, spec in self.config["populations"].items():
            self._add_external_drive(name, spec)

        for connection_spec in self.config["connections"]:
            self._connect_populations(connection_spec)

    @staticmethod
    def _vector_to_numpy(vector) -> np.ndarray:
        """Convert a NEURON Vector into a 1D numpy array reliably."""

        return np.asarray(vector.to_python(), dtype=float)

    def run(self) -> dict:
        """Run the network and return spike times per population."""

        h.dt = self.config["dt_ms"]
        h.tstop = self.config["duration_ms"]
        h.finitialize(-65.0)
        h.continuerun(h.tstop)

        spikes = {}
        for name, population in self.populations.items():
            spike_lists = [self._vector_to_numpy(vector) for vector in population.spike_vectors]
            if any(len(times) for times in spike_lists):
                merged = np.sort(np.concatenate([times for times in spike_lists if len(times)]))
            else:
                merged = np.array([])

            spikes[name] = {
                "cell_spikes": spike_lists,
                "merged_spikes": merged,
                "population_size": len(population.cells),
            }

        return {
            "state": self.config["state_name"],
            "seed": self.seed,
            "duration_ms": self.config["duration_ms"],
            "bin_ms": self.config["bin_ms"],
            "spikes": spikes,
        }
