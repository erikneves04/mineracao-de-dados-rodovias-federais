# -*- coding: utf-8 -*-
"""Generate figures for high-severity final results."""
from __future__ import annotations

import pickle
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import COLUNAS_CONTEXTO, FIGURAS_DIR, PROCESSED_DIR, TABELAS_DIR
from src.data_loading import resumo_por_ano
from src.mining import comparar_uso_solo

plt.rcParams["figure.figsize"] = (12, 6)
sns.set_style("whitegrid")


def _ctx_readable(text):
    repl = {
        "ctx_causa_acidente_": "",
        "ctx_tipo_acidente_": "",
        "ctx_fase_dia_": "",
        "ctx_uso_solo_N\u00e3o": "Rural",
        "ctx_uso_solo_Nao": "Rural",
        "ctx_uso_solo_Sim": "Urbano",
        "ctx_tipo_pista_": "",
        "ctx_condicao_metereologica_": "",
        "ctx_tracado_via_": "",
        "ctx_fim_de_semana_Sim": "Fim de semana",
        "ctx_fim_de_semana_N\u00e3o": "Dia util",
        "ctx_fim_de_semana_Nao": "Dia util",
    }
    out = str(text)
    for a, b in repl.items():
        out = out.replace(a, b)
    out = out.replace("_", " ").replace(", ", " + ")
    out = out.replace("Atropelamento de Pedestre", "Atrop. pedestre")
    out = out.replace("Colis\u00e3o frontal", "Col. frontal")
    out = out.replace("Transitar na contram\u00e3o", "Contram\u00e3o")
    out = out.replace("Pedestre andava na pista", "Pedestre na pista")
    return out[:80]


def plot_distribuicao_desfecho():
    df = pd.read_pickle(PROCESSED_DIR / "df_limpo.pkl")
    if "desfecho_alta_gravidade" not in df.columns:
        return
    fig, ax = plt.subplots(figsize=(8, 5))
    ordem = ["BaixaGravidade", "AltaGravidade"]
    vc = df["desfecho_alta_gravidade"].value_counts().reindex(ordem)
    vc.plot(kind="bar", ax=ax, color=["#3498db", "#c0392b"])
    ax.set_title("Distribuicao do desfecho de alta gravidade (com vitimas, MG)")
    ax.set_ylabel("Ocorrencias")
    ax.set_xticklabels(["Baixa gravidade", "Alta gravidade"], rotation=0)
    total = vc.sum()
    for i, v in enumerate(vc):
        ax.text(i, v + total * 0.01, f"{v:,.0f}\n({100*v/total:.1f}%)".replace(",", "."), ha="center")
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
    axes[1].plot(resumo["ano"], resumo["pct_alta_gravidade_com_vitimas"], marker="o", color="#c0392b")
    axes[1].set_title("% alta gravidade por ano")
    fig.tight_layout()
    fig.savefig(FIGURAS_DIR / "02_tendencia_anual_pipeline.png", dpi=300)
    plt.close(fig)


def plot_heatmap_temporal_gravidade():
    df = pd.read_pickle(PROCESSED_DIR / "df_limpo.pkl")
    if not {"fase_dia", "dia_semana", "desfecho_alta_gravidade"}.issubset(df.columns):
        return
    ordem_dias = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado", "domingo"]
    pivot = (
        df.assign(alta=(df["desfecho_alta_gravidade"] == "AltaGravidade").astype(int))
        .pivot_table(index="fase_dia", columns="dia_semana", values="alta", aggfunc="mean")
        .reindex(columns=[d for d in ordem_dias if d in df["dia_semana"].unique()])
    )
    if pivot.empty:
        return
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.heatmap(pivot * 100, annot=True, fmt=".1f", cmap="Reds", ax=ax, cbar_kws={"label": "% alta gravidade"})
    ax.set_title("Alta gravidade por fase do dia e dia da semana")
    ax.set_xlabel("")
    ax.set_ylabel("")
    fig.tight_layout()
    fig.savefig(FIGURAS_DIR / "02_heatmap_temporal_gravidade.png", dpi=300)
    plt.close(fig)


def plot_scatter_regras():
    path = ROOT / "outputs" / "dados" / "regras_contexto_alta_gravidade.csv"
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
    ax.set_title("Regras contexto -> Alta gravidade (cor = lift)")
    fig.tight_layout()
    fig.savefig(FIGURAS_DIR / "05_scatter_suporte_confianca_alta.png", dpi=300)
    plt.close(fig)


def plot_estabilidade():
    path = TABELAS_DIR / "estabilidade_alta_gravidade.csv"
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
    ax.set_title("Top 20 regras - estabilidade temporal (2023-2025)")
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
            rows.append({"estrato": nome, "regra": _ctx_readable(r["antecedents_str"]), "lift": r["lift"]})

    if not rows:
        return
    df = pd.DataFrame(rows)
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(data=df, x="lift", y="regra", hue="estrato", ax=ax, dodge=False)
    ax.set_title("Top regras por estrato (sem uso_solo no antecedente)")
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
    ax1.set_title("Mineracao por ano (anos completos)")
    fig.tight_layout()
    fig.savefig(FIGURAS_DIR / "08_mineracao_por_ano.png", dpi=300)
    plt.close(fig)


def plot_cramers_v_alta():
    try:
        from scipy.stats import chi2_contingency
    except Exception:
        return
    df = pd.read_pickle(PROCESSED_DIR / "df_limpo.pkl")
    if "desfecho_alta_gravidade" not in df.columns:
        return

    def cramers_v(x, y):
        ct = pd.crosstab(x, y)
        chi2 = chi2_contingency(ct)[0]
        n = ct.values.sum()
        r, k = ct.shape
        if min(r, k) <= 1:
            return 0
        return ((chi2 / n) / (min(r, k) - 1)) ** 0.5

    rows = [{"variavel": col.replace("_", " "), "cramers_v": cramers_v(df[col], df["desfecho_alta_gravidade"])}
            for col in COLUNAS_CONTEXTO if col in df.columns]
    cv = pd.DataFrame(rows).sort_values("cramers_v")
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.barh(cv["variavel"], cv["cramers_v"], color="#e67e22")
    ax.set_xlabel("Cramer's V")
    ax.set_title("Associacao entre contexto e alta gravidade")
    fig.tight_layout()
    fig.savefig(FIGURAS_DIR / "02_cramers_v_desfecho.png", dpi=300)
    plt.close(fig)


def plot_comparacao_alta_baixa_fatal():
    path = TABELAS_DIR / "comparacao_alta_baixa_fatal.csv"
    if not path.exists():
        return
    df = pd.read_csv(path).head(8).iloc[::-1]
    if df.empty:
        return
    fig, ax = plt.subplots(figsize=(11, 6))
    y = range(len(df))
    ax.barh([i + 0.22 for i in y], df["lift_alta"], height=0.22, color="#c0392b", label="Lift Alta gravidade")
    ax.barh(y, df["lift_baixa"], height=0.22, color="#3498db", label="Lift Baixa gravidade")
    ax.barh([i - 0.22 for i in y], df["lift_fatal"], height=0.22, color="#7f1d1d", label="Lift Fatal")
    ax.axvline(1, color="#333333", linestyle="--", linewidth=1)
    ax.set_yticks(list(y))
    ax.set_yticklabels([_ctx_readable(x) for x in df["contexto"]])
    ax.set_xlabel("Lift")
    ax.set_title("Mesmos contextos: alta, baixa gravidade e fatalidade")
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(FIGURAS_DIR / "09_comparacao_alta_baixa_fatal.png", dpi=300)
    plt.close(fig)


def plot_cobertura_regras():
    path = TABELAS_DIR / "cobertura_regras.csv"
    if not path.exists():
        return
    df = pd.read_csv(path)
    if df.empty:
        return
    fig, ax = plt.subplots(figsize=(8, 4.5))
    labels = df["conjunto"].str.replace("top-", "Top ", regex=False).str.replace("todas", "Todas", regex=False)
    ax.bar(labels, df["pct_alta_coberta"] * 100, color="#c0392b")
    ax.set_ylim(0, max(10, df["pct_alta_coberta"].max() * 115))
    ax.set_ylabel("% dos casos de alta gravidade")
    ax.set_title("Cobertura unica das regras")
    for i, v in enumerate(df["pct_alta_coberta"] * 100):
        ax.text(i, v + 0.8, f"{v:.1f}%", ha="center")
    fig.tight_layout()
    fig.savefig(FIGURAS_DIR / "10_cobertura_regras.png", dpi=300)
    plt.close(fig)


def main():
    plot_distribuicao_desfecho()
    plot_ocorrencias_por_ano()
    plot_heatmap_temporal_gravidade()
    plot_cramers_v_alta()
    plot_scatter_regras()
    plot_estabilidade()
    plot_estratos_uso_solo()
    plot_lift_por_ano()
    plot_comparacao_alta_baixa_fatal()
    plot_cobertura_regras()
    print(f"[OK] Figuras salvas em {FIGURAS_DIR}")


if __name__ == "__main__":
    main()
