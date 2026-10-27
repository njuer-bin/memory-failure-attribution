"""Generate the three paper figures (deterministic, matplotlib only).

Outputs (docs/paper/figures/):
    fig1_lifecycle.{pdf,png}   lifecycle stages + RM/OM/OC conditions
    fig2_ladder.{pdf,png}      oracle ladder, auto vs corrected labels
    fig3_fingerprint.{pdf,png} failure-stage distributions, LoCoMo n=100

All numbers are read from the stored analysis artifacts; nothing is retyped.
Run from the repository root:
    python docs/paper/figures/gen_figures.py
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, Patch, Rectangle

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "DejaVu Serif"],
    "font.size": 9,
    "axes.titlesize": 10,
    "axes.titleweight": "bold",
    "axes.labelsize": 9,
    "legend.fontsize": 8,
    "legend.frameon": False,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.15,
    "grid.linestyle": "-",
})

# Okabe-Ito (colorblind-safe)
BLUE_DARK = "#0072B2"
BLUE_LIGHT = "#56B4E9"
ORANGE = "#E69F00"
GREEN = "#009E73"
VERMILLION = "#D55E00"
PINK = "#CC79A7"
GRAY = "#7F7F7F"
LIGHT = "#D9D9D9"
INK = "#333333"

STAGES = [
    ("formation", "F1"),
    ("storage", "F2"),
    ("evolution", "F3$^{\\ast}$"),
    ("retrieval", "F4"),
    ("context", "F5"),
    ("reasoning", "F6"),
]
CONDITIONS = [
    ("RM", [1, 1, 1, 1, 1, 1]),
    ("OM", [0, 0, 0, 1, 1, 1]),
    ("OC", [0, 0, 0, 0, 1, 1]),
]


def _load(name: str) -> dict:
    return json.loads((ROOT / "results" / name).read_text(encoding="utf-8"))


def fig1_lifecycle() -> None:
    fig, ax = plt.subplots(figsize=(6.8, 2.7))
    ax.set_xlim(0, 10.4)
    ax.set_ylim(0, 4.05)
    ax.axis("off")

    x0, width, gap = 0.75, 1.38, 1.58
    top, height = 2.72, 0.82

    for i, (stage, tag) in enumerate(STAGES):
        x = x0 + i * gap
        ax.add_patch(Rectangle((x, top), width, height,
                               facecolor="#E3EEF7", edgecolor="#4A7BA7", linewidth=0.9))
        ax.text(x + width / 2, top + height / 2 + 0.08, stage,
                ha="center", va="center", fontsize=9, color=INK)
        ax.text(x + width / 2, top + height / 2 - 0.24, tag,
                ha="center", va="center", fontsize=8, color="#4A7BA7")
        if i < len(STAGES) - 1:
            ax.add_patch(FancyArrowPatch(
                (x + width + 0.03, top + height / 2),
                (x + gap - 0.03, top + height / 2),
                arrowstyle="-|>", mutation_scale=12, color=GRAY, linewidth=1.2))

    ax.text(x0 - 0.1, top + height / 2 + 0.16, "conversation\nhistory",
            ha="right", va="center", fontsize=8, color=GRAY)
    ax.text(x0 + 5 * gap + width + 0.14, top + height / 2 + 0.16, "answer",
            ha="left", va="center", fontsize=8, color=GRAY)

    row_y0, row_h, row_gap = 1.98, 0.34, 0.60
    for r, (name, flags) in enumerate(CONDITIONS):
        y = row_y0 - r * row_gap
        ax.text(0.62, y + row_h / 2, name, ha="right", va="center",
                fontsize=9, fontweight="bold", color=INK)
        for i, flag in enumerate(flags):
            x = x0 + i * gap
            if flag:
                ax.add_patch(Rectangle((x, y), width, row_h,
                                       facecolor="#2A9D8F", edgecolor="none", alpha=0.85))
            else:
                ax.add_patch(Rectangle((x, y), width, row_h,
                                       facecolor="white", edgecolor="#B0B0B0",
                                       linewidth=0.7, hatch="///"))

    ax.legend(
        handles=[
            Patch(facecolor="#2A9D8F", alpha=0.85, label="measured"),
            Patch(facecolor="white", edgecolor="#B0B0B0", hatch="///",
                  label="controlled / not measured"),
        ],
        loc="lower right", bbox_to_anchor=(0.995, -0.02), ncol=2,
        fontsize=7.5, handlelength=1.4, columnspacing=1.2,
    )

    ax.text(0.02, -0.16,
            "F1–F6: first lifecycle stage at which the question's gold evidence becomes unobservable.  "
            "E0: gold evidence insufficient for the reference answer (measured against the reference, not the model).  "
            "EVAL: instrument uncertainty.",
            ha="left", va="top", fontsize=7.2, color="#444444", wrap=True)
    ax.text(0.02, -0.40,
            "$^{\\ast}$Evolution (F3) is measured only on a controlled probe; it cannot fire on the benchmark runs reported here.",
            ha="left", va="top", fontsize=7.2, color="#444444")

    fig.savefig(OUT / "fig1_lifecycle.pdf")
    fig.savefig(OUT / "fig1_lifecycle.png")
    plt.close(fig)


def _wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n <= 0:
        return 0.0, 1.0
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    margin = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / denom
    return max(0.0, centre - margin), min(1.0, centre + margin)


def _acc_ci(system: dict) -> tuple[float, float, float]:
    """Semantic accuracy on judged rows + Wilson 95% CI.

    Note: the stored ``accuracy_ci95`` in the analysis artifacts is computed on
    *attributed* accuracy over all rows, not on the canonical semantic accuracy
    over judged rows, so the interval is recomputed here from the judged count.
    """
    acc = system.get("semantic_accuracy") or 0.0
    judged = int(system.get("semantic_judged") or 0)
    k = round(acc * judged)
    lo, hi = _wilson(k, judged)
    return acc, acc - lo, hi - acc


def fig2_ladder() -> None:
    benchmarks = [
        ("LoCoMo", "analysis_ladder_locomo_n200_auto.json",
         "analysis_ladder_locomo_n200_corrected.json",
         "OM→OC:  0.54 (auto)  →  0.015 (corrected)"),
        ("LongMemEval", "analysis_ladder_longmemeval_n200_auto.json",
         "analysis_ladder_longmemeval_n200_corrected.json",
         "OM→OC:  0.041 (auto)  →  0.078 (n.s.)"),
    ]
    fig, axes = plt.subplots(1, 2, figsize=(6.8, 2.7), sharey=True)
    x = np.arange(3)
    width = 0.36
    modes = ["real_memory", "oracle_memory", "oracle_context"]
    labels = ["real\nmemory", "oracle\nmemory", "oracle\ncontext"]

    for ax, (title, auto_file, corr_file, note) in zip(axes, benchmarks):
        auto = _load(auto_file)["systems"]
        corr = _load(corr_file)["systems"]
        for k, (vals, name, color, offset) in enumerate([
            (auto, "auto", BLUE_LIGHT, -width / 2 - 0.01),
            (corr, "abstention-corrected", BLUE_DARK, width / 2 + 0.01),
        ]):
            accs, lows, highs = [], [], []
            for mode in modes:
                acc, lo, hi = _acc_ci(vals[mode])
                accs.append(acc)
                lows.append(lo)
                highs.append(hi)
            bars = ax.bar(x + offset, accs, width * 0.95, color=color,
                          edgecolor="white", linewidth=0.6,
                          label=name, zorder=2)
            ax.errorbar(x + offset, accs, yerr=[lows, highs],
                        fmt="none", ecolor="#555555", elinewidth=0.8,
                        capsize=2.2, capthick=0.8, zorder=3)
            for bar, acc in zip(bars, accs):
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.035,
                        f"{acc:.2f}", ha="center", va="bottom", fontsize=6.8,
                        color="#444444", zorder=4)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=8)
        ax.set_title(title)
        ax.set_ylim(0, 1.02)
        ax.text(0.05, 0.90, note, transform=ax.transAxes, fontsize=7.0,
                color=INK, ha="left", va="top",
                bbox=dict(boxstyle="round,pad=0.25", facecolor="white",
                          edgecolor="#CCCCCC", linewidth=0.6))
    axes[0].set_ylabel("semantic accuracy\n(judged rows)")
    handles, labels_ = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels_, loc="upper center", bbox_to_anchor=(0.5, -0.24),
               ncol=2, fontsize=7.5)
    fig.savefig(OUT / "fig2_ladder.pdf")
    fig.savefig(OUT / "fig2_ladder.png")
    plt.close(fig)


def fig3_fingerprint() -> None:
    data = _load("analysis_ladder_locomo_n100_fixedgate.json")["systems"]
    systems = [("semantic", "semantic (fact extraction)"),
               ("summary", "summary (session compression)"),
               ("verbatim", "verbatim (raw-turn retrieval)")]
    classes = [
        ("none", "none", LIGHT, INK),
        ("E0_EVIDENCE_INSUFFICIENT", "E0", ORANGE, "white"),
        ("F1_FORMATION", "F1", BLUE_LIGHT, INK),
        ("F4_RETRIEVAL", "F4", VERMILLION, "white"),
        ("F5_CONTEXT", "F5", GREEN, "white"),
        ("F6_REASONING_CANDIDATE", "F6", PINK, INK),
        ("EVAL_SEMANTIC_UNCERTAIN", "EVAL", GRAY, "white"),
    ]
    fig, ax = plt.subplots(figsize=(6.8, 2.15))
    y = np.arange(len(systems))[::-1]
    for yi, (key, _) in zip(y, systems):
        dist = data[key]["failure_distribution"]
        n = data[key]["n"]
        left = 0.0
        for label, short, color, textcolor in classes:
            count = dist.get(label, 0)
            share = count / n
            ax.barh(yi, share, left=left, height=0.62, color=color,
                    edgecolor="white", linewidth=0.7,
                    label=short if yi == y[0] else None, zorder=2)
            if share >= 0.07:
                ax.text(left + share / 2, yi, str(count), ha="center", va="center",
                        fontsize=7.2, color=textcolor, zorder=3)
            left += share
    ax.set_yticks(y)
    ax.set_yticklabels([label for _, label in systems], fontsize=8.5)
    ax.set_xlim(0, 1.0)
    ax.set_xticks([0, 0.25, 0.50, 0.75, 1.0])
    ax.set_xticklabels(["0", "25", "50", "75", "100%"], fontsize=8)
    ax.set_xlabel("share of questions (n = 100 per system)")
    ax.set_axisbelow(True)
    ax.grid(axis="y", visible=False)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.30), ncol=7,
              fontsize=7.3, handlelength=1.0, columnspacing=1.0,
              handletextpad=0.4)
    ax.text(1.02, 1.02, "Stuart–Maxwell,\nHolm $p \\leq 3\\times10^{-4}$\nfor all three pairs",
            transform=ax.transAxes, fontsize=7.2, ha="right", va="bottom",
            color=INK)
    fig.savefig(OUT / "fig3_fingerprint.pdf")
    fig.savefig(OUT / "fig3_fingerprint.png")
    plt.close(fig)


if __name__ == "__main__":
    fig1_lifecycle()
    fig2_ladder()
    fig3_fingerprint()
    print("wrote fig1_lifecycle, fig2_ladder, fig3_fingerprint (.pdf/.png)")
