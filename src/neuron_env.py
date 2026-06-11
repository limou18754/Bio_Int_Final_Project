"""Utilities for importing NEURON with conda-first behavior."""

from __future__ import annotations

import os
import sys
from pathlib import Path


SYSTEM_FALLBACK_FLAG = "NEURON_ALLOW_SYSTEM_FALLBACK"


def _allow_system_fallback() -> bool:
    """Return whether standalone NEURON fallback is explicitly allowed."""

    return os.environ.get(SYSTEM_FALLBACK_FLAG, "").strip().lower() in {"1", "true", "yes", "on"}


def _fallback_candidates() -> tuple[list[Path], list[Path]]:
    """Collect standalone NEURON candidate paths."""

    candidate_python_paths: list[Path] = []
    candidate_bin_paths: list[Path] = []

    env_python = os.environ.get("NRN_PYTHONPATH")
    env_home = os.environ.get("NEURONHOME")
    if env_python:
        candidate_python_paths.append(Path(env_python))
    if env_home:
        candidate_python_paths.append(Path(env_home) / "lib" / "python")
        candidate_bin_paths.append(Path(env_home) / "bin")

    candidate_python_paths.append(Path(r"C:\nrn\lib\python"))
    candidate_bin_paths.append(Path(r"C:\nrn\bin"))
    return candidate_python_paths, candidate_bin_paths


def _install_fallback_paths(candidate_python_paths: list[Path], candidate_bin_paths: list[Path]) -> None:
    """Add standalone NEURON paths to Python and process PATH."""

    for path in candidate_python_paths:
        if path.is_dir():
            sys.path.insert(0, str(path))
            break

    valid_bin_paths = [str(path) for path in candidate_bin_paths if path.is_dir()]
    if valid_bin_paths:
        os.environ["PATH"] = os.pathsep.join(valid_bin_paths + [os.environ.get("PATH", "")])


def ensure_neuron():
    """Import and return the NEURON hoc handle.

    The preferred path is the currently active Python environment, including
    an activated conda environment. This repository assumes that normal runs
    use the interpreter from that environment. Standalone Windows NEURON
    paths are used only when explicitly enabled via
    `NEURON_ALLOW_SYSTEM_FALLBACK=1`.
    """

    try:
        from neuron import h  # type: ignore

        return h
    except ModuleNotFoundError as exc:
        if not _allow_system_fallback():
            active_env = os.environ.get("CONDA_DEFAULT_ENV") or os.environ.get("VIRTUAL_ENV") or "current Python environment"
            raise ModuleNotFoundError(
                "Could not import 'neuron' from the active interpreter. "
                f"Active environment hint: {active_env}. "
                "This repository is expected to run with the Python interpreter "
                "from your NEURON-enabled conda environment. "
                "Please activate the conda environment that contains NEURON, "
                "or install it into the current environment with "
                "`python -m pip install neuron`. "
                f"If you intentionally want to use a standalone NEURON install such as C:\\nrn, "
                f"set {SYSTEM_FALLBACK_FLAG}=1 before running."
            ) from exc

    candidate_python_paths, candidate_bin_paths = _fallback_candidates()
    _install_fallback_paths(candidate_python_paths, candidate_bin_paths)

    from neuron import h  # type: ignore

    return h
