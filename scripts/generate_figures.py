# -*- coding: utf-8 -*-
"""Generate figures for Package A results."""
from __future__ import annotations

import pickle
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import FIGURAS_DIR, PROCESSED_DIR, TABELAS_DIR
from src.data_loading import resumo_por_ano
from src.mining import comparar_uso_solo

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


def plot_ocorrencias_por_ano():
    df = pd.read_pickle(PROCESSED_DIR / "df_limpo.pkl")
    if "ano" not in df.columns:
        return
    resumo = resumo_por_ano(df)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    axes[0].bar(resumo["ano"].astype(str), resumo["n_ocorrencias"], color="#3498db")
    axes[0].set_title("Ocorrencias com vitimas por ano")
    axes[1].plot(resumo["ano"], resumo["pct_fatais"], marker="o", color="#c0392b")
    axes[1].set_title("% fatais por ano")
    fig.tight_layout()
    fig.savefig(FIGURAS_DIR / "02_tendencia_anual_pipeline.png", dpi=300)
    plt.close(fig)


def plot_scatter_regras():
    path = ROOT / "outputs" / "dados" / "regras_contexto_fatal.csv"
    if not path.exists():
        return
    rules = pd.read_csv(path)
    if rules.empty:
        return
    fig, ax = plt.subplots(figsize=(8, 6))
    sc = ax.scatter(
        rules["support"],
        rules["confidence"],
        c=rules["lift"],
        cmap="YlOrRd",
        s=80,
    )
    plt.colorbar(sc, ax=ax, label="Lift")
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
    top = df.nlargest(20, "lift_medio")
    fig, ax = plt.subplots(figsize=(10, max(4, len(top) * 0.35)))
    colors = top["status"].map(
        {"estavel": "#27ae60", "intermediaria": "#f39c12", "transitoria": "#e74c3c"}
    )
    ax.barh(top["regra"].str[:70], top["lift_medio"], color=colors)
    ax.set_xlabel("Lift medio")
    ax.set_title("Top 20 regras - estabilidade temporal")
    fig.tight_layout()
    fig.savefig(FIGURAS_DIR / "06_estabilidade_temporal.png", dpi=300)
    plt.close(fig)


def plot_estratos_uso_solo():
    onehot_path = PROCESSED_DIR / "transacional.pkl"
    meta_path = PROCESSED_DIR / "transacional_meta.pkl"
    if not onehot_path.exists() or not meta_path.exists():
        return
    df_onehot = pd.read_pickle(onehot_path)
    df_meta = pd.read_pickle(meta_path)
    estratos = comparar_uso_solo(df_onehot, df_meta)
    if not estratos:
        return

    rows = []
    for nome, rules in estratos.items():
        if rules.empty:
            continue
        for _, r in rules.head(5).iterrows():
            rows.append({"estrato": nome, "regra": r["antecedents_str"][:50], "lift": r["lift"]})

    if not rows:
        return
    df = pd.DataFrame(rows)
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(data=df, x="lift", y="regra", hue="estrato", ax=ax, dodge=False)
    ax.set_title("Top regras por estrato (uso do solo)")
    fig.tight_layout()
    fig.savefig(FIGURAS_DIR / "07_estratos_uso_solo.png", dpi=300)
    plt.close(fig)


def plot_lift_por_ano():
    path = PROCESSED_DIR / "rules_por_ano.pkl"
    if not path.exists():
        return
    with open(path, "rb") as f:
        rules_por_ano = pickle.load(f)
    if not rules_por_ano:
        return

    rows = []
    for ano, rules in rules_por_ano.items():
        if rules.empty:
            continue
        rows.append({"ano": ano, "lift_medio_top10": rules["lift"].head(10).mean(), "n_regras": len(rules)})
    if not rows:
        return
    df = pd.DataFrame(rows).sort_values("ano")
    fig, ax1 = plt.subplots(figsize=(8, 4))
    ax1.bar(df["ano"].astype(str), df["n_regras"], color="#3498db", alpha=0.7, label="N regras")
    ax2 = ax1.twinx()
    ax2.plot(df["ano"].astype(str), df["lift_medio_top10"], color="#c0392b", marker="o", label="Lift medio top10")
    ax1.set_title("Mineracao por ano")
    fig.tight_layout()
    fig.savefig(FIGURAS_DIR / "08_mineracao_por_ano.png", dpi=300)
    plt.close(fig)


def main():
    plot_distribuicao_desfecho()
    plot_ocorrencias_por_ano()
    plot_scatter_regras()
    plot_estabilidade()
    plot_estratos_uso_solo()
    plot_lift_por_ano()
    print(f"[OK] Figuras salvas em {FIGURAS_DIR}")


if __name__ == "__main__":
    main()
