"""Generate a simple circuit schematic for the mini-paper."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Circle, FancyArrowPatch


PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PATH = PROJECT_ROOT / "figures" / "basal_ganglia_schematic.png"


NODE_STYLE = {
    "D1": {"xy": (0.12, 0.68), "color": "#d8ead3"},
    "D2": {"xy": (0.12, 0.32), "color": "#f4cccc"},
    "STN": {"xy": (0.48, 0.68), "color": "#fce5cd"},
    "GPe": {"xy": (0.48, 0.32), "color": "#cfe2f3"},
    "GPi": {"xy": (0.82, 0.50), "color": "#ead1dc"},
}


def draw_node(ax: plt.Axes, label: str, xy: tuple[float, float], color: str) -> None:
    node = Circle(xy, 0.085, facecolor=color, edgecolor="#333333", linewidth=1.8)
    ax.add_patch(node)
    ax.text(xy[0], xy[1], label, ha="center", va="center", fontsize=13, weight="bold", color="#222222")


def draw_connection(
    ax: plt.Axes,
    start: tuple[float, float],
    end: tuple[float, float],
    color: str,
    label: str,
    label_xy: tuple[float, float],
    style: str = "solid",
    curve: float = 0.0,
    line_width: float = 2.2,
) -> None:
    arrow = FancyArrowPatch(
        start,
        end,
        arrowstyle="-|>",
        mutation_scale=16,
        linewidth=line_width,
        color=color,
        linestyle=style,
        connectionstyle=f"arc3,rad={curve}",
        shrinkA=18,
        shrinkB=18,
    )
    ax.add_patch(arrow)
    ax.text(
        label_xy[0],
        label_xy[1],
        label,
        color=color,
        fontsize=10.5,
        ha="center",
        va="center",
        bbox={"boxstyle": "round,pad=0.2", "facecolor": "white", "edgecolor": "none", "alpha": 0.9},
    )


def main() -> None:
    fig, ax = plt.subplots(figsize=(10, 5.8))
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 1.0)
    ax.axis("off")

    for label, cfg in NODE_STYLE.items():
        draw_node(ax, label, cfg["xy"], cfg["color"])

    excit = "#2f6db3"
    inhib = "#b22222"
    pd = "#6a3d9a"

    draw_connection(ax, NODE_STYLE["D1"]["xy"], NODE_STYLE["GPi"]["xy"], inhib, "D1 -> GPi", (0.47, 0.83))
    draw_connection(ax, NODE_STYLE["D2"]["xy"], NODE_STYLE["GPe"]["xy"], inhib, "D2 -> GPe", (0.30, 0.24))
    draw_connection(ax, NODE_STYLE["STN"]["xy"], NODE_STYLE["GPe"]["xy"], excit, "STN -> GPe", (0.61, 0.50), curve=-0.18)
    draw_connection(ax, NODE_STYLE["GPe"]["xy"], NODE_STYLE["STN"]["xy"], inhib, "GPe -> STN", (0.35, 0.50), curve=-0.18)
    draw_connection(ax, NODE_STYLE["STN"]["xy"], NODE_STYLE["GPi"]["xy"], excit, "STN -> GPi", (0.67, 0.67))
    draw_connection(ax, NODE_STYLE["GPe"]["xy"], NODE_STYLE["GPi"]["xy"], inhib, "GPe -> GPi", (0.67, 0.33))

    ax.text(0.10, 0.84, "Healthy and Parkinsonian states\nshare the same circuit skeleton", fontsize=11, color="#333333")
    ax.text(
        0.86,
        0.84,
        "Parkinsonian changes\n"
        "- D1 drive down\n"
        "- D2 drive up\n"
        "- D2 -> GPe stronger\n"
        "- STN <-> GPe loop gain up\n"
        "- STN self-excitation up",
        fontsize=10,
        weight="bold",
        color=pd,
        ha="left",
        va="top",
        linespacing=1.35,
        bbox={"boxstyle": "round,pad=0.4", "facecolor": "#f3e8ff", "edgecolor": pd, "linewidth": 1.2},
    )

    ax.text(0.15, 0.56, "striatal pathways", fontsize=10.5, color="#444444", ha="center")
    ax.text(0.47, 0.14, "core beta-generating loop", fontsize=10.5, color="#444444", ha="center")
    ax.text(0.82, 0.20, "basal ganglia output", fontsize=10.5, color="#444444", ha="center")

    legend_handles = [
        Line2D([0], [0], color=excit, linewidth=2.2, label="Excitatory projection"),
        Line2D([0], [0], color=inhib, linewidth=2.2, label="Inhibitory projection"),
    ]
    ax.legend(handles=legend_handles, loc="lower left", frameon=False, fontsize=10)

    fig.tight_layout()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT_PATH, dpi=300, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
