"""Static configuration for the basal ganglia project."""

from __future__ import annotations

from copy import deepcopy


BASE_CONFIG = {
    "duration_ms": 4000.0,
    "dt_ms": 0.1,
    "bin_ms": 5.0,
    "populations": {
        "D1": {"size": 40, "tau": 10.0, "refrac": 2.0, "drive_interval": 30.0, "drive_weight": 0.95},
        "D2": {"size": 40, "tau": 10.0, "refrac": 2.0, "drive_interval": 28.0, "drive_weight": 0.95},
        "STN": {"size": 20, "tau": 12.0, "refrac": 3.0, "drive_interval": 24.0, "drive_weight": 0.85},
        "GPe": {"size": 20, "tau": 14.0, "refrac": 4.0, "drive_interval": 22.0, "drive_weight": 1.05},
        "GPi": {"size": 20, "tau": 14.0, "refrac": 4.0, "drive_interval": 26.0, "drive_weight": 0.80},
    },
    "connections": [
        {"pre": "D1", "post": "GPi", "p": 0.25, "delay_ms": 7.0, "weight": -0.90},
        {"pre": "D2", "post": "GPe", "p": 0.25, "delay_ms": 7.0, "weight": -0.65},
        {"pre": "STN", "post": "GPe", "p": 0.25, "delay_ms": 5.0, "weight": 0.50},
        {"pre": "GPe", "post": "STN", "p": 0.28, "delay_ms": 8.0, "weight": -0.80},
        {"pre": "GPe", "post": "GPe", "p": 0.15, "delay_ms": 4.0, "weight": -0.15},
        {"pre": "STN", "post": "STN", "p": 0.08, "delay_ms": 3.0, "weight": 0.03},
        {"pre": "STN", "post": "GPi", "p": 0.25, "delay_ms": 6.0, "weight": 0.55},
        {"pre": "GPe", "post": "GPi", "p": 0.20, "delay_ms": 5.0, "weight": -0.45},
    ],
}


STATE_MODIFIERS = {
    "healthy": {
        "population_drive_scales": {
            "D1": 1.00,
            "D2": 1.00,
            "STN": 1.00,
            "GPe": 1.00,
            "GPi": 1.00,
        },
        "connection_weight_scales": {
            ("D1", "GPi"): 1.00,
            ("D2", "GPe"): 1.00,
            ("STN", "GPe"): 1.00,
            ("GPe", "STN"): 1.00,
            ("GPe", "GPe"): 1.00,
            ("STN", "STN"): 1.00,
            ("STN", "GPi"): 1.00,
            ("GPe", "GPi"): 1.00,
        },
    },
    "parkinsonian": {
        "population_drive_scales": {
            "D1": 0.85,
            "D2": 1.15,
            "STN": 1.18,
            "GPe": 1.05,
            "GPi": 1.05,
        },
        "connection_weight_scales": {
            ("D1", "GPi"): 0.72,
            ("D2", "GPe"): 1.62,
            ("STN", "GPe"): 2.10,
            ("GPe", "STN"): 1.38,
            ("GPe", "GPe"): 1.67,
            ("STN", "STN"): 3.33,
            ("STN", "GPi"): 1.45,
            ("GPe", "GPi"): 1.10,
        },
    },
}


def make_state_config(state_name: str) -> dict:
    """Return a concrete configuration dictionary for one state."""

    if state_name not in STATE_MODIFIERS:
        raise ValueError(f"Unknown state: {state_name}")

    config = deepcopy(BASE_CONFIG)
    modifier = STATE_MODIFIERS[state_name]

    for pop_name, scale in modifier["population_drive_scales"].items():
        config["populations"][pop_name]["drive_weight"] *= scale

    scale_map = modifier["connection_weight_scales"]
    for connection in config["connections"]:
        key = (connection["pre"], connection["post"])
        connection["weight"] *= scale_map.get(key, 1.0)

    config["state_name"] = state_name
    return config
