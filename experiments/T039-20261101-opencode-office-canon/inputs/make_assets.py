"""Generate the two figures used by the T039 document fixture."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

OUT = Path(__file__).resolve().parent


def architecture() -> None:
    fig, ax = plt.subplots(figsize=(10, 4.8), dpi=240)
    ax.set_xlim(0, 10); ax.set_ylim(0, 4.8); ax.axis("off")
    boxes = [
        (0.4, 2.9, 2.2, 1.0, "#1F4E79", "Sources"),
        (3.0, 2.9, 2.2, 1.0, "#2E75B6", "Ingest"),
        (5.6, 2.9, 2.2, 1.0, "#2E75B6", "Validate"),
        (8.2, 2.9, 1.4, 1.0, "#1F4E79", "Store"),
        (3.0, 0.7, 2.2, 1.0, "#548235", "Report"),
        (5.6, 0.7, 2.2, 1.0, "#548235", "Review"),
    ]
    for x, y, w, h, color, label in boxes:
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.04,rounding_size=0.12",
                                    facecolor=color, edgecolor="none"))
        ax.text(x + w / 2, y + h / 2, label, color="white", ha="center", va="center",
                fontsize=13, fontweight="bold")
    arrows = [((2.6, 3.4), (3.0, 3.4)), ((5.2, 3.4), (5.6, 3.4)), ((7.8, 3.4), (8.2, 3.4)),
              ((4.1, 2.9), (4.1, 1.7)), ((5.2, 1.2), (5.6, 1.2)), ((7.8, 1.2), (8.2, 1.2))]
    for start, end in arrows:
        ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=18,
                                     color="#7F7F7F", linewidth=2))
    fig.tight_layout()
    fig.savefig(OUT / "architecture.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)


def trend() -> None:
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep"]
    baseline = np.array([120, 128, 135, 140, 150, 158, 166, 172, 180])
    target = np.array([130, 138, 148, 158, 170, 182, 195, 208, 220])
    fig, ax = plt.subplots(figsize=(10, 4.8), dpi=240)
    ax.plot(months, target, color="#ED7D31", marker="o", linewidth=2.4, label="Target")
    ax.plot(months, baseline, color="#1F4E79", marker="s", linewidth=2.4, label="Actual")
    ax.fill_between(months, baseline, target, color="#F4B183", alpha=0.25)
    ax.set_ylim(100, 240)
    ax.set_ylabel("Index (2025 = 100)")
    ax.grid(axis="y", color="#D9D9D9", linewidth=0.8)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, loc="upper left")
    fig.tight_layout()
    fig.savefig(OUT / "trend.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    architecture()
    trend()
    print("wrote architecture.png, trend.png")
