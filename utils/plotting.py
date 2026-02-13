import math
import matplotlib.pyplot as plt

def plot_risk_gauge(score: int, max_score: int = 100):
    """
    Semi-circular gauge (0..max_score).
    No custom colors -> stable and simple.
    """
    score = max(0, min(int(score), max_score))

    fig = plt.figure(figsize=(5.6, 3.2))
    ax = fig.add_subplot(111, polar=True)

    ax.set_theta_offset(math.pi)     # start left
    ax.set_theta_direction(-1)       # clockwise
    ax.set_ylim(0, 1)
    ax.set_yticklabels([])
    ax.set_xticklabels([])
    ax.grid(False)

    # arc
    theta = [math.radians(x) for x in range(0, 181)]
    ax.plot(theta, [1] * len(theta), linewidth=10)

    # needle
    needle_angle = math.radians((score / max_score) * 180)
    ax.plot([needle_angle, needle_angle], [0, 0.95], linewidth=3)
    ax.scatter([needle_angle], [0.95], s=80)

    ax.text(0.5, -0.15, f"Risk Score: {score}/{max_score}",
            transform=ax.transAxes, ha="center", va="center", fontsize=12)

    ax.text(0.02, 0.05, "0", transform=ax.transAxes, ha="left", va="center", fontsize=10)
    ax.text(0.50, 0.12, f"{max_score//2}", transform=ax.transAxes, ha="center", va="center", fontsize=10)
    ax.text(0.98, 0.05, f"{max_score}", transform=ax.transAxes, ha="right", va="center", fontsize=10)

    return fig


def plot_risk_breakdown(components: dict):
    """
    Bar chart for component breakdown.
    """
    labels = list(components.keys())
    values = list(components.values())

    fig = plt.figure(figsize=(6.2, 3.6))
    ax = fig.add_subplot(111)

    ax.bar(labels, values)
    ax.set_ylabel("Risk Points")
    ax.set_title("Risk Breakdown")
    ax.set_xticklabels(labels, rotation=25, ha="right")
    ax.grid(axis="y", linestyle="--", linewidth=0.5, alpha=0.6)
    fig.tight_layout()
    return fig
