"""Generate the paper figures from frozen result artifacts.

Every number is read from an analysis artifact; nothing is transcribed by hand.
Writes vector PDFs (ACL column widths) and PNG previews to paper/figures/.

Usage:
    G:/aconda/python.exe -m experiments.make_paper_figures
"""

from __future__ import annotations

import csv
import json
import math
import shutil
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

# Categorical slots 1-3 of the validated palette (all-pairs CVD-safe in light
# mode); aqua is below 3:1 contrast, so every aqua mark carries a direct label.
BLUE = "#2a78d6"
ORANGE = "#eb6834"
AQUA = "#1baf7a"
INK = "#0b0b0b"
INK_2 = "#52514e"
GRID = "#d8d7d2"

SINGLE_COL = 3.3
DOUBLE_COL = 6.9

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "DejaVu Serif"],
    "font.size": 8,
    "axes.labelsize": 8,
    "axes.titlesize": 9,
    "xtick.labelsize": 7.5,
    "ytick.labelsize": 7.5,
    "legend.fontsize": 7.5,
    "axes.edgecolor": INK_2,
    "axes.linewidth": 0.6,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.dpi": 150,
    "savefig.bbox": "standard",
    "savefig.pad_inches": 0.02,
})

OUT = Path("paper/figures")

# The submission builds keep their own figure copies (some with different file
# names). Mirror every generated figure into both so the compiled PDFs never
# embed a stale vector file.
SUBMISSION_DIRS = (Path("paper/submission_ecai/figures"), Path("paper/submission/figures"))
SUBMISSION_NAMES = {
    "fig1_design": "fig1_design",
    "fig2_p3_omission": "fig2_omission",
    "fig3_p3_mechanism": "fig3_mechanism",
    "fig4_behavior": "fig4_behavior",
    "fig5_mitigation": "fig5_mitigation",
    "fig6_real_calibration": "fig6_calibration",
}


def mirror_to_submissions() -> None:
    for directory in SUBMISSION_DIRS:
        if not directory.is_dir():
            continue
        for master, target in SUBMISSION_NAMES.items():
            source = OUT / f"{master}.pdf"
            if source.exists():
                shutil.copy2(source, directory / f"{target}.pdf")
                print(f"mirrored {source} -> {directory / (target + '.pdf')}")


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return 0.0, 0.0
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return max(0.0, centre - half), min(1.0, centre + half)


def save(fig: plt.Figure, name: str, tight: bool = True) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    if tight:
        fig.tight_layout(pad=0.25)
    fig.savefig(OUT / f"{name}.pdf")
    fig.savefig(OUT / f"{name}.png", dpi=220)
    plt.close(fig)
    print(f"wrote {OUT / name}.pdf")


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------
# Fig 2 — P3 status omission among proposition-preserved items
# --------------------------------------------------------------------------
P3_FAMILY = {
    "raw": ("source", "raw"),
    "direct": ("direct", "direct"),
    "repeated_direct": ("direct", "repeated\ndirect"),
    "recursive": ("chained", "recursive"),
    "rewrite_matched": ("chained", "rewrite\nmatched"),
    "para": ("chained", "paraphrase"),
    "temp1": ("chained", "temp 1"),
    "temp2": ("chained", "temp 2"),
    "path_s2": ("chained", "schedule S2"),
    "source_peek": ("source", "source peek"),
    "retrieval": ("source", "retrieval"),
}
FAMILY_COLOR = {"direct": BLUE, "chained": ORANGE, "source": AQUA}
FAMILY_LABEL = {"direct": "direct rewriting", "chained": "chained rewriting",
                "source": "source access / raw"}


def fig2_p3_omission() -> None:
    rows = read_csv(Path("results/status_drift_v3_p2/analysis/condition_table.csv"))
    data = []
    for row in rows:
        condition = row["condition"]
        if condition not in P3_FAMILY:
            continue
        k = int(row["omission_n"])
        n = int(row["preserved_n"])
        family, label = P3_FAMILY[condition]
        data.append((k / n if n else 0.0, k, n, family, label))
    data.sort(key=lambda item: item[0])

    fig, ax = plt.subplots(figsize=(SINGLE_COL, 2.6))
    ys = range(len(data))
    for y, (rate, k, n, family, label) in zip(ys, data):
        low, high = wilson(k, n)
        ax.barh(y, rate, height=0.62, color=FAMILY_COLOR[family], linewidth=0)
        ax.plot([low, high], [y, y], color=INK, linewidth=0.9, solid_capstyle="butt")
        ax.annotate(f"{rate:.0%}", (max(high, rate) + 0.015, y), va="center",
                    ha="left", fontsize=7, color=INK)
    ax.set_yticks(list(ys))
    ax.set_yticklabels([entry[4] for entry in data])
    ax.set_xlim(0, 0.80)
    ax.set_xlabel("status omission among proposition-preserved items")
    ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    ax.grid(axis="x", color=GRID, linewidth=0.5)
    ax.set_axisbelow(True)
    handles = [plt.Rectangle((0, 0), 1, 1, color=FAMILY_COLOR[f]) for f in ("direct", "chained", "source")]
    ax.legend(handles, [FAMILY_LABEL[f] for f in ("direct", "chained", "source")],
              frameon=False, loc="lower right", handlelength=1.0, handleheight=0.8)
    ax.set_title("Qwen writer, 30 trajectories\nwhiskers: 95% Wilson interval",
                 loc="left", pad=4)
    save(fig, "fig2_p3_omission")


# --------------------------------------------------------------------------
# Fig 3 — P3 mechanism contrasts
# --------------------------------------------------------------------------
def fig3_p3_mechanism() -> None:
    rows = read_csv(Path("results/status_drift_v3_p2/analysis/paired_contrasts.csv"))
    wanted = {
        ("rewrite_matched", "recursive"): ("rewrite-matched\nvs recursive", "chained"),
        ("repeated_direct", "direct"): ("repeated-direct\nvs direct", "direct"),
        ("source_peek", "recursive"): ("source peek\nvs recursive", "source"),
    }
    data = []
    for row in rows:
        key = (row["condition"], row["reference"])
        if key in wanted and row["outcome"] == "omission":
            label, family = wanted[key]
            data.append((float(row["mean_difference"]), float(row["bootstrap_low"]),
                         float(row["bootstrap_high"]), label, family))

    fig, ax = plt.subplots(figsize=(SINGLE_COL, 1.7))
    for y, (mean, low, high, label, family) in enumerate(data):
        ax.plot([low, high], [y, y], color=FAMILY_COLOR[family], linewidth=1.6,
                solid_capstyle="round")
        ax.plot([mean], [y], "o", color=FAMILY_COLOR[family], markersize=5.5,
                markeredgecolor="white", markeredgewidth=0.8)
        ax.annotate(f"{mean:+.2f}", xy=(0.98, y),
                    xycoords=("axes fraction", "data"),
                    ha="right", va="center", fontsize=7, color=INK)
    ax.axvline(0, color=INK_2, linewidth=0.7)
    ax.set_yticks(range(len(data)))
    ax.set_yticklabels([entry[3] for entry in data])
    ax.set_ylim(-0.6, len(data) - 0.4)
    ax.set_xlim(-0.7, 0.5)
    ax.set_xticks([-0.6, -0.4, -0.2, 0.0, 0.2, 0.4])
    ax.set_xlabel("paired change in omission")
    ax.grid(axis="x", color=GRID, linewidth=0.5)
    ax.set_axisbelow(True)
    save(fig, "fig3_p3_mechanism")


# --------------------------------------------------------------------------
# Fig 4 — downstream behavior: P4 and P4.2
# --------------------------------------------------------------------------
def fig4_behavior() -> None:
    p4 = read_json(Path("results/status_drift_v3_p4/summary.json"))["by_variant"]
    local = read_json(Path("results/status_drift_v3_p4_2_v3_v31/analysis/p4_2_v31_summary.json"))
    gateway = read_json(Path(
        "results/status_drift_v3_p4_2_v3_v31_api/analysis/p4_2_v31_summary.json"))
    models = [
        ("qwen2.5:7b", local["qwen2.5:7b"], BLUE),
        ("gemma3:12b", local["gemma3:12b"], ORANGE),
        ("glm-5.3-flash", gateway["glm-5.3-flash"], AQUA),
    ]

    variants = ["present", "omitted", "distorted", "no_memory"]
    display = {"present": "present", "omitted": "omitted",
               "distorted": "distorted", "no_memory": "no mem."}

    fig, (ax1, ax2, ax3) = plt.subplots(
        1, 3, figsize=(DOUBLE_COL, 2.55),
        gridspec_kw={"width_ratios": [0.78, 1.15, 1.15]})

    for i, variant in enumerate(variants):
        cell = p4[variant]["unauthorized_action"]
        k, n = cell["count"], cell["denominator"]
        low, high = wilson(k, n)
        ax1.bar(i, k / n, width=0.62, color=BLUE, linewidth=0)
        ax1.plot([i, i], [low, high], color=INK, linewidth=0.9)
        ax1.annotate(f"{k}/{n}", (i, max(high, k / n) + 0.03), ha="center",
                     fontsize=6.6, color=INK, rotation=90)
    ax1.set_xticks(range(len(variants)))
    ax1.set_xticklabels([display[v] for v in variants], rotation=30, ha="right")
    ax1.set_ylim(0, 1.0)
    ax1.set_ylabel("unauthorized action")
    ax1.set_title("(a) Study 2a: synthetic\n(primary agent qwen)", loc="left", pad=3)
    ax1.grid(axis="y", color=GRID, linewidth=0.5)
    ax1.set_axisbelow(True)

    width = 0.26
    for ax, form, title in ((ax2, "neutral", "(b) Study 2b: permission judgment"),
                            (ax3, "action", "(c) Study 2b: action request")):
        for j, (model, data, color) in enumerate(models):
            table = data["tables"]["all_over_commitment"][form]
            for i, variant in enumerate(variants):
                cell = table[variant]["unauthorized_execute"]
                k, n = cell["count"], cell["denominator"]
                low, high = wilson(k, n)
                x = i + (j - 1) * width
                ax.bar(x, k / n, width=width - 0.02, color=color, linewidth=0)
                ax.plot([x, x], [low, high], color=INK, linewidth=0.7)
                ax.annotate(f"{k}/{n}", (x, max(high, k / n) + 0.015),
                            ha="center", fontsize=5.2, color=INK, rotation=90)
        ax.set_xticks(range(len(variants)))
        ax.set_xticklabels([display[v] for v in variants], rotation=30, ha="right")
        ax.set_ylim(0, 1.0)
        ax.set_title(title, loc="left", pad=3)
        ax.grid(axis="y", color=GRID, linewidth=0.5)
        ax.set_axisbelow(True)
    handles = [plt.Rectangle((0, 0), 1, 1, color=color) for _, _, color in models]
    ax2.legend(handles, [m for m, _, _ in models], frameon=False,
               loc="upper left", handlelength=0.9, handleheight=0.7,
               fontsize=6.2)
    save(fig, "fig4_behavior")


# --------------------------------------------------------------------------
# Fig 5 — mitigation 2x2 interaction
# --------------------------------------------------------------------------
def fig5_mitigation() -> None:
    primary = {row["condition"]: row for row in
               read_csv(Path("results/status_drift_v3_p5/analysis_v324/condition_table.csv"))}
    replication = {row["condition"]: row for row in
                   read_csv(Path("results/status_drift_v3_replication_writer/analysis_v325/condition_table.csv"))}
    panels = [
        ("qwen2.5:7b writer (primary, n=30)",
         [("neutral", "neutral", BLUE), ("status_aware", "status-aware", BLUE),
          ("neutral_source", "neutral\n+ source", ORANGE),
          ("status_aware_source", "status-aware\n+ source", ORANGE)],
         primary),
        ("gemma3:12b writer (pre-registered, n=12)",
         [("direct", "direct\n(baseline)", BLUE), ("status_aware", "status-aware", BLUE),
          ("neutral_source", "neutral\n+ source", ORANGE),
          ("status_aware_source", "status-aware\n+ source", ORANGE)],
         replication),
    ]

    fig, axes = plt.subplots(1, 2, figsize=(DOUBLE_COL, 2.6), sharey=True)
    fig.subplots_adjust(left=0.10, right=0.98, top=0.90, bottom=0.28, wspace=0.12)
    for ax, (title, cells, data) in zip(axes, panels):
        for i, (condition, label, color) in enumerate(cells):
            row = data[condition]
            k, n = int(row["faithful_n"]), int(row["n"])
            low, high = wilson(k, n)
            ax.bar(i, k / n, width=0.6, color=color, linewidth=0)
            ax.plot([i, i], [low, high], color=INK, linewidth=0.9)
            ax.annotate(f"{k}/{n}", (i, max(high, k / n) + 0.025),
                        ha="center", fontsize=6.8, color=INK)
        ax.set_xticks(range(len(cells)))
        ax.set_xticklabels([label for _, label, _ in cells])
        ax.set_ylim(0, 1.1)
        ax.set_title(title, loc="left", pad=4, fontsize=8)
        ax.grid(axis="y", color=GRID, linewidth=0.5)
        ax.set_axisbelow(True)
    axes[0].set_ylabel("faithful status (joint fidelity)")
    handles = [plt.Rectangle((0, 0), 1, 1, color=BLUE),
               plt.Rectangle((0, 0), 1, 1, color=ORANGE)]
    fig.legend(handles, ["memory only", "+ source access"], frameon=False,
               loc="lower center", bbox_to_anchor=(0.5, 0.012), ncol=2,
               handlelength=1.0, handleheight=0.8)
    save(fig, "fig5_mitigation", tight=False)


# --------------------------------------------------------------------------
# Fig 1 — design schematic
# --------------------------------------------------------------------------
def fig1_design() -> None:
    fig, ax = plt.subplots(figsize=(DOUBLE_COL, 2.35))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3.6)
    ax.axis("off")

    def box(x, y, w, h, text, color=INK_2, face="white", size=7.2, weight="normal"):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
                                    linewidth=0.8, edgecolor=color, facecolor=face))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
                fontsize=size, color=INK, fontweight=weight, linespacing=1.25)

    def arrow(x1, y1, x2, y2):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                     mutation_scale=7, linewidth=0.8, color=INK_2,
                                     shrinkA=1, shrinkB=1))

    box(0.1, 1.15, 1.75, 1.3, "dialogue\n(source)", size=7.6)
    arrow(1.9, 1.8, 2.35, 1.8)

    box(2.4, 0.25, 2.1, 0.75, "direct / repeated-direct", color=BLUE)
    box(2.4, 1.4, 2.1, 0.75, "recursive / rewrite-matched", color=ORANGE)
    box(2.4, 2.55, 2.1, 0.75, "source access (peek, retrieval)", color=AQUA)
    for y in (0.62, 1.78, 2.92):
        arrow(2.35, 1.8, 2.42, y)

    for y in (0.62, 1.78, 2.92):
        arrow(4.52, y, 5.0, 1.8)
    box(5.05, 1.15, 2.0, 1.3, "memory\nproposition + status", size=7.6)
    arrow(7.1, 1.8, 7.55, 1.8)
    box(7.6, 1.55, 1.05, 0.6, "variants", size=7.2)
    arrow(8.68, 1.8, 9.05, 1.8)
    box(9.1, 1.05, 0.85, 1.5, "agent\ndecision", size=7.2)

    ax.text(5.0, 0.05, "proposition identity held fixed",
            ha="center", fontsize=7, color=INK_2, style="italic")
    ax.annotate("", xy=(6.0, 0.3), xytext=(4.0, 0.3),
                arrowprops={"arrowstyle": "<->", "linewidth": 0.6, "color": INK_2})
    ax.text(3.45, 3.35, "transformation history", ha="center", fontsize=7.2, color=INK_2)
    ax.text(6.05, 2.75, "status tuple: epistemic / intentional / conditional",
            ha="left", fontsize=7, color=INK_2)
    save(fig, "fig1_design")


# --------------------------------------------------------------------------
# Fig 6 (appendix) — real-data calibration gates
# --------------------------------------------------------------------------
# Gates from V3_REAL_STAGE2_PREFREEZE.md: gold fields raw >=0.85 / kappa >=0.70;
# identity raw >=0.90 / kappa >=0.80; LSF raw >=0.85 / kappa >=0.70; SSF
# raw >=0.80 / kappa >=0.65.
def fig6_real_calibration() -> None:
    gold = read_json(Path("results/status_drift_v3_real_audit/stage2_calibration_40_intent_epi/analysis/agreement_adjudicated.json"))
    lsf = read_json(Path("results/status_drift_v3_real_audit/stage2_lsf_ssf/analysis/agreement.json"))

    rows = [
        ("gold dimension (adj.)", gold["adjudicated"]["gold_dimension"]["raw"],
         gold["adjudicated"]["gold_dimension"]["kappa"], 0.70),
        ("gold status (adj.)", gold["adjudicated"]["gold_status"]["raw"],
         gold["adjudicated"]["gold_status"]["kappa"], 0.70),
        ("LSF outcome", lsf["fields"]["lsf_outcome"]["raw_agreement"],
         lsf["fields"]["lsf_outcome"]["cohen_kappa"], 0.70),
        ("SSF outcome", lsf["fields"]["ssf_outcome"]["raw_agreement"],
         lsf["fields"]["ssf_outcome"]["cohen_kappa"], 0.65),
        ("proposition identity", lsf["fields"]["proposition_identity_in_memory"]["raw_agreement"],
         lsf["fields"]["proposition_identity_in_memory"]["cohen_kappa"], 0.80),
    ]
    rows.sort(key=lambda row: row[2])

    fig, ax = plt.subplots(figsize=(SINGLE_COL, 2.0))
    for i, (label, raw, kappa, gate) in enumerate(rows):
        color = BLUE if kappa >= gate else ORANGE
        ax.barh(i, kappa, height=0.55, color=color, linewidth=0)
        ax.plot([gate, gate], [i - 0.32, i + 0.32], color=INK, linewidth=0.9)
        ax.annotate(f"$\\kappa$ {kappa:.2f}\nraw {raw:.2f}",
                    (max(kappa, gate) + 0.02, i),
                    va="center", fontsize=6.5, color=INK, linespacing=1.1)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([row[0] for row in rows])
    ax.set_xlim(0, 1.4)
    ax.set_xticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2])
    ax.set_xlabel("Cohen's $\\kappa$ (tick = gate)")
    ax.grid(axis="x", color=GRID, linewidth=0.5)
    ax.set_axisbelow(True)
    handles = [plt.Rectangle((0, 0), 1, 1, color=BLUE),
               plt.Rectangle((0, 0), 1, 1, color=ORANGE)]
    ax.legend(handles, ["passes gate", "fails gate"], frameon=False,
              loc="upper center", bbox_to_anchor=(0.5, -0.22), ncol=2,
              handlelength=1.0, handleheight=0.8)
    save(fig, "fig6_real_calibration")


def main() -> None:
    fig1_design()
    fig2_p3_omission()
    fig3_p3_mechanism()
    fig4_behavior()
    fig5_mitigation()
    fig6_real_calibration()
    mirror_to_submissions()


if __name__ == "__main__":
    main()
