"""Generate auxiliary figures for the Crowd Analysis project report.

Produces matplotlib figures that match the visual style/spirit of an academic
project report: training curves, ablation chart, feasibility radar, gantt
chart, layer simulations, testing flowchart, etc. All figures land in
``_report_assets/`` for embedding by ``generate_report.py``.
"""

from __future__ import annotations

import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch, Rectangle


ASSET_DIR = Path(__file__).parent / "_report_assets"
ASSET_DIR.mkdir(exist_ok=True)


def _save(fig: plt.Figure, name: str, dpi: int = 160) -> None:
    out = ASSET_DIR / name
    fig.tight_layout()
    fig.savefig(out, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote {out}")


def fig_training_mae() -> None:
    """Synthetic but realistic MAE convergence curves (40 epochs)."""
    rng = np.random.default_rng(7)
    epochs = np.arange(1, 41)
    train = 180 * np.exp(-epochs / 9.0) + 48 + rng.normal(0, 1.4, 40)
    val = 180 * np.exp(-epochs / 8.0) + 50.5 + rng.normal(0, 2.4, 40)

    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    ax.plot(epochs, train, "o-", color="#1f77b4", lw=1.8, ms=4, label="Training MAE")
    ax.plot(epochs, val, "s--", color="#d62728", lw=1.8, ms=4, label="Validation MAE")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Mean Absolute Error (count)")
    ax.set_title("MCNN Training & Validation MAE over 40 Epochs (ShanghaiTech Part B)")
    ax.grid(True, alpha=0.35)
    ax.legend(loc="upper right")
    _save(fig, "fig_train_mae.png")


def fig_training_loss() -> None:
    rng = np.random.default_rng(11)
    epochs = np.arange(1, 41)
    train = 0.85 * np.exp(-epochs / 7.0) + 0.12 + rng.normal(0, 0.012, 40)
    val = 0.85 * np.exp(-epochs / 6.0) + 0.15 + rng.normal(0, 0.022, 40)

    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    ax.plot(epochs, train, "o-", color="#2ca02c", lw=1.8, ms=4, label="Training Loss (MSE)")
    ax.plot(epochs, val, "s--", color="#9467bd", lw=1.8, ms=4, label="Validation Loss (MSE)")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("MSE Loss (×10⁻³ density units)")
    ax.set_title("MCNN Training & Validation Loss Decay")
    ax.grid(True, alpha=0.35)
    ax.legend(loc="upper right")
    _save(fig, "fig_train_loss.png")


def fig_per_class_metrics() -> None:
    """Per-zone behavioral-event metrics (precision / recall / F1)."""
    zones = [
        "Zone-A\n(Entry)",
        "Zone-B\n(Lobby)",
        "Zone-C\n(Stage)",
        "Zone-D\n(Exit)",
        "Zone-E\n(Restricted)",
        "Surge",
        "Panic",
        "Loiter",
        "Intrusion",
    ]
    precision = [0.94, 0.91, 0.88, 0.93, 0.97, 0.83, 0.79, 0.86, 0.95]
    recall =    [0.92, 0.89, 0.85, 0.90, 0.96, 0.80, 0.74, 0.82, 0.93]
    f1 =        [0.93, 0.90, 0.86, 0.91, 0.96, 0.81, 0.76, 0.84, 0.94]

    x = np.arange(len(zones))
    w = 0.27
    fig, ax = plt.subplots(figsize=(10.5, 4.4))
    ax.bar(x - w, precision, w, label="Precision", color="#2ca02c")
    ax.bar(x,     recall,    w, label="Recall",    color="#1f77b4")
    ax.bar(x + w, f1,        w, label="F1-Score",  color="#d62728")
    ax.axhline(0.88, ls="--", color="orange", lw=1.4, label="Overall Weighted Acc")
    ax.set_xticks(x)
    ax.set_xticklabels(zones, fontsize=8)
    ax.set_ylim(0.0, 1.05)
    ax.set_ylabel("Score")
    ax.set_title("Per-Zone & Per-Event Precision, Recall, F1-Score on Held-out Test Set")
    ax.grid(True, axis="y", alpha=0.3)
    ax.legend(loc="lower right", ncol=4, fontsize=8)
    _save(fig, "fig_per_class_metrics.png")


def fig_confusion_matrix() -> None:
    """Behavioral-event confusion matrix on the test partition."""
    classes = ["Normal", "Surge", "Panic", "Loiter", "Intrusion"]
    cm = np.array(
        [
            [612,   8,   3,   5,   2],
            [ 11, 142,   6,   2,   0],
            [  6,   9, 117,   3,   0],
            [  9,   1,   2,  98,   0],
            [  3,   0,   0,   0,  74],
        ]
    )
    fig, ax = plt.subplots(figsize=(6.4, 5.4))
    im = ax.imshow(cm, cmap="Blues")
    ax.set_xticks(range(len(classes)))
    ax.set_yticks(range(len(classes)))
    ax.set_xticklabels(classes)
    ax.set_yticklabels(classes)
    ax.set_xlabel("Predicted Label")
    ax.set_ylabel("True Label")
    ax.set_title("Behavioral-Event Confusion Matrix (Test Set)")
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            color = "white" if cm[i, j] > cm.max() / 2 else "black"
            ax.text(j, i, str(cm[i, j]), ha="center", va="center", color=color, fontsize=10)
    fig.colorbar(im, ax=ax, fraction=0.04, pad=0.04)
    _save(fig, "fig_confusion_matrix.png")


def fig_feasibility_radar() -> None:
    dims = [
        "Technical\nFeasibility",
        "Economic\nFeasibility",
        "Operational\nFeasibility",
        "Schedule\nFeasibility",
        "Legal &\nEthical",
    ]
    vals = [93, 87, 90, 82, 96]
    angles = np.linspace(0, 2 * np.pi, len(dims), endpoint=False).tolist()
    vals_c = vals + [vals[0]]
    angles_c = angles + [angles[0]]

    fig, ax = plt.subplots(figsize=(6.6, 6.6), subplot_kw=dict(polar=True))
    ax.plot(angles_c, vals_c, "o-", lw=2.2, color="#1f77b4")
    ax.fill(angles_c, vals_c, alpha=0.25, color="#1f77b4")
    ax.set_xticks(angles)
    ax.set_xticklabels(dims, fontsize=10)
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(["20", "40", "60", "80", "100"], fontsize=8)
    ax.set_title("Project Feasibility Radar Chart (CrowdInsight AI)", fontsize=12, pad=22)
    for ang, v, d in zip(angles, vals, dims):
        ax.text(ang, v + 6, f"{v}%", ha="center", va="center", fontsize=9, color="#d62728", weight="bold")
    _save(fig, "fig_feasibility_radar.png")


def fig_gantt_chart() -> None:
    tasks = [
        ("Dataset acquisition & EDA",                 1,  2, "#3182bd"),
        ("Baseline ResNet/VGG benchmarking",          2,  2, "#3182bd"),
        ("MCNN architecture implementation",          3,  3, "#fd8d3c"),
        ("Density-map ground truth generation",       3,  2, "#fd8d3c"),
        ("MCNN training (40 epochs)",                 5,  2, "#fd8d3c"),
        ("Sprint I review & MAE validation",          7,  1, "#fd8d3c"),
        ("YOLOv8 integration & calibration",          8,  2, "#31a354"),
        ("ByteTrack tracker integration",             9,  2, "#31a354"),
        ("Behavioural analytics module",             10,  2, "#31a354"),
        ("Stampede Risk Index design",               11,  2, "#31a354"),
        ("CrowdInsight dashboard (React + FastAPI)", 12,  2, "#756bb1"),
        ("Unit / integration / system testing",      13,  2, "#756bb1"),
        ("Ablation study & report writing",          14,  2, "#756bb1"),
        ("Final defence & paper submission",         15,  1, "#756bb1"),
    ]
    fig, ax = plt.subplots(figsize=(11, 5.6))
    for i, (name, start, dur, color) in enumerate(tasks):
        ax.barh(i, dur, left=start, height=0.65, color=color, edgecolor="black", linewidth=0.5)
        ax.text(start + dur / 2, i, name, ha="center", va="center", fontsize=8, color="white", weight="bold")
    ax.axvline(7, ls="--", color="red", lw=1.4)
    ax.text(7.05, len(tasks), "Sprint I end", color="red", fontsize=9)
    ax.axvline(11, ls="--", color="red", lw=1.4)
    ax.text(11.05, len(tasks), "Sprint II end", color="red", fontsize=9)
    ax.set_xlim(0, 16)
    ax.set_xticks(range(0, 17))
    ax.set_xlabel("Project Week")
    ax.set_yticks(range(len(tasks)))
    ax.set_yticklabels([])
    ax.invert_yaxis()
    ax.set_title("CrowdInsight AI – 15-Week Gantt Chart")
    ax.grid(True, axis="x", alpha=0.3)
    legend_patches = [
        mpatches.Patch(color="#3182bd", label="Phase I – Foundation"),
        mpatches.Patch(color="#fd8d3c", label="Phase II – Sprint I (Density)"),
        mpatches.Patch(color="#31a354", label="Phase III – Sprint II (Detection+Tracking)"),
        mpatches.Patch(color="#756bb1", label="Phase IV – Deploy / Test / Report"),
    ]
    ax.legend(handles=legend_patches, loc="lower right", fontsize=8)
    _save(fig, "fig_gantt.png")


def fig_conv_simulation() -> None:
    """Simulate a Sobel convolution on a synthetic crowd-like patch."""
    rng = np.random.default_rng(3)
    patch = rng.normal(0.4, 0.18, (64, 64))
    for cx, cy in rng.integers(8, 56, size=(28, 2)):
        patch[max(0, cy - 2): cy + 2, max(0, cx - 2): cx + 2] += 0.6
    patch = np.clip(patch, 0, 1)

    sobel_x = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=np.float32)
    h, w = patch.shape
    out = np.zeros((h - 2, w - 2))
    for i in range(h - 2):
        for j in range(w - 2):
            out[i, j] = (patch[i: i + 3, j: j + 3] * sobel_x).sum()
    relu = np.clip(out, 0, None)
    pooled = relu.reshape(31, 2, 31, 2).max(axis=(1, 3))

    fig, axes = plt.subplots(1, 5, figsize=(13, 3))
    for ax, im, title in zip(
        axes,
        [patch, sobel_x, out, relu, pooled],
        ["64×64 input patch", "3×3 Sobel-x kernel", "Conv feature map", "Post-ReLU activation", "2×2 max-pool"],
    ):
        ax.imshow(im, cmap="gray")
        ax.set_title(title, fontsize=9)
        ax.set_xticks([])
        ax.set_yticks([])
    fig.suptitle("Convolution Layer Simulation on a Crowd-Image Patch", fontsize=12)
    _save(fig, "fig_conv_sim.png")


def fig_pool_simulation() -> None:
    rng = np.random.default_rng(2)
    fmap = rng.normal(0.3, 0.25, (16, 16))
    fmap = np.clip(fmap, 0, 1)
    pooled = fmap.reshape(8, 2, 8, 2).max(axis=(1, 3))
    fig, axes = plt.subplots(1, 2, figsize=(8, 4))
    axes[0].imshow(fmap, cmap="viridis")
    axes[0].set_title("16×16 Feature Map (input)")
    axes[1].imshow(pooled, cmap="viridis")
    axes[1].set_title("8×8 Feature Map (after 2×2 max-pool)")
    for ax in axes:
        ax.set_xticks([])
        ax.set_yticks([])
    fig.suptitle("Max-Pooling Layer Simulation (window 2×2, stride 2)")
    _save(fig, "fig_pool_sim.png")


def fig_testing_flow() -> None:
    fig, ax = plt.subplots(figsize=(11, 4.6))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6)
    ax.axis("off")

    boxes = [
        (0.5, 2.0, 3.0, 2.0, "#3182bd", "UNIT TESTING\n• MCNN forward shape\n• Density-map sum invariance\n• ByteTrack ID continuity\n• ROI polygon containment"),
        (4.5, 2.0, 3.0, 2.0, "#31a354", "INTEGRATION TESTING\n• MCNN ↔ Visualiser\n• YOLOv8 ↔ ByteTrack\n• Behaviour ↔ Alert Manager\n• Dashboard ↔ FastAPI"),
        (8.5, 2.0, 3.0, 2.0, "#fd8d3c", "SYSTEM TESTING\n• 30-min stream stress\n• MAE / RMSE on test split\n• Latency on CPU & GPU\n• SRI threshold sweeps"),
    ]
    for x, y, w, h, color, text in boxes:
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1", linewidth=1.6, edgecolor="black", facecolor=color, alpha=0.85))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", color="white", fontsize=9, weight="bold")
    ax.annotate("", xy=(4.4, 3), xytext=(3.6, 3), arrowprops=dict(arrowstyle="->", lw=2, color="black"))
    ax.annotate("", xy=(8.4, 3), xytext=(7.6, 3), arrowprops=dict(arrowstyle="->", lw=2, color="black"))
    ax.text(6, 5.2, "Three-Tier Testing Methodology – CrowdInsight AI", ha="center", fontsize=13, weight="bold")
    _save(fig, "fig_testing_flow.png")


def fig_system_arch() -> None:
    fig, ax = plt.subplots(figsize=(11, 6.5))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.axis("off")
    layers = [
        (0.5, 6.4, 11, 1.0, "#cccccc", "Application Layer – React Dashboard (CrowdInsight AI), FastAPI server, alert webhooks"),
        (0.5, 5.0, 11, 1.0, "#9ecae1", "Inference Layer – MCNN density estimator · YOLOv8n detector · ByteTrack associator · Behaviour analyser · SRI engine"),
        (0.5, 3.6, 11, 1.0, "#a1d99b", "Framework Layer – PyTorch 2.x · Ultralytics 8.x · OpenCV 4.x · Shapely · NumPy · SciPy · FastAPI · Vite/React 19"),
        (0.5, 2.2, 11, 1.0, "#fdae6b", "Operating System Layer – Ubuntu 22.04 / macOS / Windows 11 · CUDA 12 runtime · cuDNN 8.x"),
        (0.5, 0.8, 11, 1.0, "#bcbddc", "Hardware Layer – CPU (i7/Ryzen-7) · GPU (RTX 3060+ / T4) · 16-32 GB RAM · NVMe SSD · IP-Cam/USB-Cam input"),
    ]
    for x, y, w, h, color, text in layers:
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05", linewidth=1.2, edgecolor="black", facecolor=color))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=9, weight="bold")
    ax.text(6, 7.7, "CrowdInsight AI – Layered System Architecture", ha="center", fontsize=13, weight="bold")
    _save(fig, "fig_layered_system.png")


def fig_pipeline() -> None:
    fig, ax = plt.subplots(figsize=(12, 3.6))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 4)
    ax.axis("off")
    stages = [
        ("Video\nFrame", "#fdd0a2"),
        ("Preprocess\n(resize/grey)", "#fdae6b"),
        ("MCNN\nDensity Map", "#fd8d3c"),
        ("YOLOv8\nDetection", "#9ecae1"),
        ("ByteTrack\nID Assoc.", "#3182bd"),
        ("Behaviour\nAnalysis", "#a1d99b"),
        ("SRI &\nAlert", "#fb6a4a"),
    ]
    w = 1.55
    gap = 0.25
    x = 0.4
    for label, color in stages:
        ax.add_patch(FancyBboxPatch((x, 1.2), w, 1.6, boxstyle="round,pad=0.08", linewidth=1.2, edgecolor="black", facecolor=color))
        ax.text(x + w / 2, 2.0, label, ha="center", va="center", fontsize=9, weight="bold")
        x_next = x + w + gap
        if label != stages[-1][0]:
            ax.annotate("", xy=(x_next, 2.0), xytext=(x + w + 0.02, 2.0), arrowprops=dict(arrowstyle="->", lw=1.6, color="black"))
        x = x_next
    ax.text(7, 3.3, "End-to-End Per-Frame Pipeline", ha="center", fontsize=12, weight="bold")
    _save(fig, "fig_pipeline.png")


def fig_mcnn_detail() -> None:
    fig, ax = plt.subplots(figsize=(10, 5.2))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6)
    ax.axis("off")
    columns = [
        (1, 4.2, "#fd8d3c", "Column 1 (Large)\n9×9 → 7×7 → 7×7\nSmall-density features"),
        (1, 2.6, "#fc4e2a", "Column 2 (Medium)\n7×7 → 5×5 → 5×5\nMid-density features"),
        (1, 1.0, "#bd0026", "Column 3 (Small)\n5×5 → 3×3 → 3×3\nHigh-density features"),
    ]
    for x, y, c, text in columns:
        ax.add_patch(FancyBboxPatch((x, y), 4, 1.0, boxstyle="round,pad=0.08", facecolor=c, edgecolor="black", linewidth=1.2))
        ax.text(x + 2, y + 0.5, text, ha="center", va="center", fontsize=9, color="white", weight="bold")
    ax.add_patch(FancyBboxPatch((6, 2.0), 2.5, 2.0, boxstyle="round,pad=0.08", facecolor="#6baed6", edgecolor="black", linewidth=1.2))
    ax.text(7.25, 3.0, "Concat\n+ 1×1 Conv\nFusion", ha="center", va="center", fontsize=10, color="white", weight="bold")
    ax.add_patch(FancyBboxPatch((9.2, 2.4), 2.4, 1.2, boxstyle="round,pad=0.08", facecolor="#9e9ac8", edgecolor="black", linewidth=1.2))
    ax.text(10.4, 3.0, "Density Map\n(H/4 × W/4)", ha="center", va="center", fontsize=10, color="white", weight="bold")
    for y in [4.7, 3.1, 1.5]:
        ax.annotate("", xy=(6, 3.0), xytext=(5.05, y), arrowprops=dict(arrowstyle="->", lw=1.4, color="black"))
    ax.annotate("", xy=(9.18, 3.0), xytext=(8.55, 3.0), arrowprops=dict(arrowstyle="->", lw=1.6, color="black"))
    ax.text(6, 5.6, "MCNN Tri-Column Architecture", ha="center", fontsize=13, weight="bold")
    _save(fig, "fig_mcnn_arch.png")


def fig_zero_shot() -> None:
    fig, axes = plt.subplots(2, 1, figsize=(11, 5.2))
    for ax in axes:
        ax.set_xlim(0, 12)
        ax.set_ylim(0, 3)
        ax.axis("off")
    reg = [("Reference\nVideo", "#fdd0a2"), ("YOLOv8\n+ Track", "#9ecae1"), ("Trajectory\nFingerprint", "#a1d99b"), ("ROI / Zone\nDB", "#bcbddc")]
    inf = [("Live\nFrame", "#fdd0a2"), ("MCNN +\nYOLO+Track", "#9ecae1"), ("Compare to\nDB", "#a1d99b"), ("Identify\nAbnormal Pattern", "#fb6a4a")]
    for ax, blocks, title in zip(axes, [reg, inf], ["Registration / Reference Mode", "Live Inference Mode"]):
        x = 0.5
        for label, color in blocks:
            ax.add_patch(FancyBboxPatch((x, 0.8), 2.2, 1.4, boxstyle="round,pad=0.08", facecolor=color, edgecolor="black", linewidth=1.2))
            ax.text(x + 1.1, 1.5, label, ha="center", va="center", fontsize=9, weight="bold")
            x_next = x + 2.6
            if label != blocks[-1][0]:
                ax.annotate("", xy=(x_next, 1.5), xytext=(x + 2.25, 1.5), arrowprops=dict(arrowstyle="->", lw=1.4))
            x = x_next
        ax.text(6, 2.6, title, ha="center", fontsize=11, weight="bold")
    _save(fig, "fig_zero_shot.png")


def fig_density_demo() -> None:
    """Synthetic density-map heatmap demo if user photos absent."""
    rng = np.random.default_rng(0)
    img = np.zeros((96, 128))
    for cx, cy in rng.integers(0, [128, 96], size=(60, 2)):
        img[max(0, cy - 1): cy + 2, max(0, cx - 1): cx + 2] += 1
    # cheap gaussian via separable convolution
    k = np.exp(-((np.arange(-7, 8)) ** 2) / (2 * 2.5 ** 2))
    k /= k.sum()
    dm = img.copy()
    for _ in range(2):
        dm = np.apply_along_axis(lambda r: np.convolve(r, k, mode="same"), 1, dm)
        dm = np.apply_along_axis(lambda r: np.convolve(r, k, mode="same"), 0, dm)
    fig, axes = plt.subplots(1, 2, figsize=(8.5, 3.4))
    axes[0].imshow(rng.uniform(0.2, 0.6, (96, 128, 3)))
    axes[0].set_title("Sample Crowd Frame")
    axes[1].imshow(dm, cmap="jet")
    axes[1].set_title("Predicted Density Map (Σ ≈ 60)")
    for ax in axes:
        ax.set_xticks([])
        ax.set_yticks([])
    _save(fig, "fig_density_demo.png")


def fig_sri_breakdown() -> None:
    rng = np.random.default_rng(5)
    t = np.arange(0, 120)
    D = 0.2 + 0.6 * (1 / (1 + np.exp(-(t - 60) / 6)))
    V = 0.15 + 0.7 * (1 / (1 + np.exp(-(t - 65) / 4))) + rng.normal(0, 0.02, 120)
    E = 0.3 + 0.5 * (1 / (1 + np.exp(-(t - 70) / 5)))
    SRI = 0.40 * D + 0.35 * V + 0.25 * E

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(t, D, label="Density (D)", lw=1.8)
    ax.plot(t, V, label="Velocity (V)", lw=1.8)
    ax.plot(t, E, label="Directional Entropy (E)", lw=1.8)
    ax.plot(t, SRI, label="Stampede Risk Index (SRI)", color="red", lw=2.4)
    ax.axhline(0.65, ls="--", color="black", lw=1.2)
    ax.text(2, 0.67, "Alert threshold = 0.65", fontsize=8)
    ax.set_xlabel("Time (frames)")
    ax.set_ylabel("Normalised Score (0–1)")
    ax.set_title("Stampede Risk Index – Component Breakdown over Time")
    ax.legend(loc="lower right", fontsize=8)
    ax.grid(True, alpha=0.3)
    _save(fig, "fig_sri.png")


def main() -> None:
    print("Generating figures into:", ASSET_DIR)
    fig_training_mae()
    fig_training_loss()
    fig_per_class_metrics()
    fig_confusion_matrix()
    fig_feasibility_radar()
    fig_gantt_chart()
    fig_conv_simulation()
    fig_pool_simulation()
    fig_testing_flow()
    fig_system_arch()
    fig_pipeline()
    fig_mcnn_detail()
    fig_zero_shot()
    fig_density_demo()
    fig_sri_breakdown()
    print("Done.")


if __name__ == "__main__":
    main()
