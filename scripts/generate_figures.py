# -*- coding: utf-8 -*-
"""Generate figures for Package A results."""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import FIGURAS_DIR, PROCESSED_DIR, TABELAS_DIR

plt.rcParams["figure.figsize"] = (12, 6)
sns.set_style("whitegrid")


def plot_distribuicao_desfecho():
    df = pd.read_pickle(PROCESSED_DIR / "df_limpo.pkl")
    if "desfecho" not in df.columns:
        return
    fig, ax = plt.subplots(figsize=(8, 5))
    df["desfecho"].value_counts().plot(kind="bar", ax=ax, color=["#c0392b", "#3498db"])
    ax.set_title("Distribuicao do desfecho (com vitimas, MG)")
    ax.set_ylabel("Ocorrencias")
    fig.tight_layout()
    fig.savefig(FIGURAS_DIR / "01_distribuicao_desfecho.png", dpi=300)
    plt.close(fig)


def plot_scatter_regras():
    path = ROOT / "outputs" / "dados" / "regras_contexto_fatal.csv"
    if not path.exists():
        return
    rules = pd.read_csv(path)
    if rules.empty:
        return
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(rules["support"], rules["confidence"], c=rules["lift"], cmap="YlOrRd", s=80)
    ax.set_xlabel("Suporte")
    ax.set_ylabel("Confianca")
    ax.set_title("Regras contexto -> Fatal (cor = lift)")
    fig.tight_layout()
    fig.savefig(FIGURAS_DIR / "05_scatter_suporte_confianca_fatal.png", dpi=300)
    plt.close(fig)


def plot_estabilidade():
    path = TABELAS_DIR / "regras_estabilidade_temporal.csv"
    if not path.exists():
        return
    df = pd.read_csv(path)
    if df.empty:
        return
    fig, ax = plt.subplots(figsize=(10, max(4, len(df) * 0.4)))
    colors = df["status"].map({"estavel": "#27ae60", "intermediaria": "#f39c12", "transitoria": "#e74c3c"})
    ax.barh(df["regra"].str[:80], df["lift_medio"], color=colors)
    ax.set_xlabel("Lift medio")
    ax.set_title("Estabilidade temporal das regras contexto->Fatal")
    fig.tight_layout()
    fig.savefig(FIGURAS_DIR / "06_estabilidade_temporal.png", dpi=300)
    plt.close(fig)


def main():
    plot_distribuicao_desfecho()
    plot_scatter_regras()
    plot_estabilidade()
    print(f"[OK] Figuras salvas em {FIGURAS_DIR}")


if __name__ == "__main__":
    main()
