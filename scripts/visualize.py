"""
Visualization helpers for evaluation metrics and scalability experiments.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict

import matplotlib.pyplot as plt
import pandas as pd


def plot_metric_comparison(metrics_df: pd.DataFrame, output_path: Path) -> None:
    """
    Generate a grouped bar chart comparing precision, recall, and NDCG.
    """

    metrics_df = metrics_df.set_index("algorithm")
    ax = metrics_df[["precision@10", "recall@10", "ndcg@10"]].plot(kind="bar")
    ax.set_ylabel("Score")
    ax.set_title("Recommendation Quality Comparison")
    ax.legend(loc="lower right")
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path)
    plt.close()


def plot_runtime_scaling(runtime_stats: Dict[str, float], output_path: Path) -> None:
    """
    Plot runtime scaling across dataset sizes (e.g., 1M vs 32M ratings).
    """

    labels = list(runtime_stats.keys())
    values = list(runtime_stats.values())
    fig, ax = plt.subplots()
    ax.plot(labels, values, marker="o", color="#10B981")
    ax.set_xlabel("Dataset Size")
    ax.set_ylabel("Runtime (seconds)")
    ax.set_title("Offline Pipeline Runtime Scaling")
    ax.grid(True, linestyle="--", alpha=0.4)
    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path)
    plt.close()

