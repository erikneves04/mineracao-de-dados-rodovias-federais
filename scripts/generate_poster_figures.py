# -*- coding: utf-8 -*-
"""Regera as figuras do poster em alta resolucao (300 DPI) e com fontes grandes.

Salva diretamente em relatorios/poster/figuras/. Nao altera a logica de mineracao:
reutiliza dados ja processados (data/processed, outputs/) e helpers de src/.

Observacao: strings exibidas usam escapes \\uXXXX para evitar problemas de
codificacao do arquivo-fonte em ambiente Windows (cp1252).
"""
from __future__ import annotations

import pickle
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import COLUNAS_CONTEXTO, PROCESSED_DIR  # noqa: E402
from src.mining import comparar_uso_solo  # noqa: E402

POSTER_FIG = ROOT / "relatorios" / "poster" / "figuras"
POSTER_FIG.mkdir(parents=True, exist_ok=True)
OUT_TAB = ROOT / "outputs" / "tabelas"

sns.set_style("whitegrid")
plt.rcParams.update({
    "font.size": 21,
    "axes.titlesize": 25,
    "axes.titleweight": "bold",
    "axes.labelsize": 22,
    "xtick.labelsize": 20,
    "ytick.labelsize": 20,
    "legend.fontsize": 20,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "axes.edgecolor": "#444444",
    "grid.color": "#d9d9d9",
})

COR_FATAL = "#C8102E"
COR_FERIDO = "#1D3142"
COR_AUX = "#E67E22"

# Strings com acentos (escapes para seguranca de codificacao)
T_DISTRIB = "Desfecho das ocorr\u00eancias com v\u00edtimas (MG)"
T_OCORR = "N\u00ba de ocorr\u00eancias"
T_MAPA = "Distribui\u00e7\u00e3o espacial dos acidentes \u2014 MG"
T_FASE = "Taxa de fatalidade por fase do dia"
T_FASE_X = "% de acidentes fatais"
T_CRAMER = "Quais fatores mais se associam \u00e0 gravidade"
T_CRAMER_X = "Cram\u00e9r's V (associa\u00e7\u00e3o com o desfecho)"
T_COMP = "Mesmos contextos, desfechos opostos"
T_COMP_X = "Lift (vezes acima da m\u00e9dia do desfecho)"
T_INDEP = "independ\u00eancia (lift = 1)"
T_ANO = "Minera\u00e7\u00e3o por ano: volume e for\u00e7a das regras"
T_ANO_Y1 = "N\u00ba de regras"
T_ANO_Y2 = "Lift m\u00e9dio (top 10)"
T_ESTR = "Top regras por ambiente (uso do solo)"
T_ESTR_X = "Lift (risco relativo de morte)"
L_FATAL = "Lift para Fatal"
L_FERIDO = "Lift para Ferido"

_TRACADO = "Tra\u00e7ado da via"
_REPL_SHORT = {
    "Atropelamento de Pedestre": "Atrop. pedestre",
    "Transitar na contram\u00e3o": "Contram\u00e3o",
    "Colis\u00e3o frontal": "Col. frontal",
    "Plena Noite": "Noite",
    "C\u00e9u Claro": "C\u00e9u claro",
    "Simples": "Pista simples",
}


def _save(fig, nome):
    out = POSTER_FIG / nome
    fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"[OK] {out.relative_to(ROOT)}")


def _readable_var(col):
    return {
        "tipo_acidente": "Tipo de acidente",
        "causa_acidente": "Causa do acidente",
        "tracado_via": _TRACADO,
        "fase_dia": "Fase do dia",
        "tipo_pista": "Tipo de pista",
        "uso_solo": "Uso do solo",
        "condicao_metereologica": "Clima",
        "fim_de_semana": "Fim de semana",
    }.get(col, col)


def _short_ctx(texto):
    for a, b in _REPL_SHORT.items():
        texto = texto.replace(a, b)
    return texto


def fig_distribuicao():
    df = pd.read_pickle(PROCESSED_DIR / "df_limpo.pkl")
    vc = df["desfecho"].value_counts().reindex(["Ferido", "Fatal"])
    total = vc.sum()
    fig, ax = plt.subplots(figsize=(8.5, 6.5))
    bars = ax.bar(vc.index, vc.values, color=[COR_FERIDO, COR_FATAL], width=0.62)
    ax.set_ylabel(T_OCORR)
    ax.set_title(T_DISTRIB)
    ax.set_ylim(0, vc.max() * 1.18)
    for b, v in zip(bars, vc.values):
        ax.text(b.get_x() + b.get_width() / 2, v + total * 0.012,
                f"{v:,.0f}\n({100*v/total:.1f}%)".replace(",", "."),
                ha="center", va="bottom", fontsize=21, fontweight="bold")
    ax.margins(x=0.15)
    _save(fig, "01_distribuicao_desfecho.png")


def fig_mapa():
    df = pd.read_pickle(PROCESSED_DIR / "df_limpo.pkl").copy()
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    geo = df.dropna(subset=["latitude", "longitude"])
    geo = geo[(geo["latitude"].between(-23, -14)) & (geo["longitude"].between(-51, -39))]
    sample = geo.sample(min(6000, len(geo)), random_state=42)

    fig, ax = plt.subplots(figsize=(8.5, 8.5))
    fatal = sample[sample["desfecho"] == "Fatal"]
    ferido = sample[sample["desfecho"] == "Ferido"]
    ax.scatter(ferido["longitude"], ferido["latitude"], s=10, c=COR_FERIDO,
               alpha=0.35, label="Ferido", edgecolors="none")
    ax.scatter(fatal["longitude"], fatal["latitude"], s=22, c=COR_FATAL,
               alpha=0.75, label="Fatal", edgecolors="none")
    ax.set_title(T_MAPA)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    leg = ax.legend(loc="lower right", markerscale=2.2, framealpha=0.9)
    leg.get_frame().set_edgecolor("#888888")

    try:
        import contextily as cx
        import geopandas as gpd
        gdf = gpd.GeoDataFrame(
            sample, geometry=gpd.points_from_xy(sample["longitude"], sample["latitude"]),
            crs="EPSG:4326").to_crs(epsg=3857)
        ax.clear()
        fat = gdf[gdf["desfecho"] == "Fatal"]
        fer = gdf[gdf["desfecho"] == "Ferido"]
        ax.scatter(fer.geometry.x, fer.geometry.y, s=10, c=COR_FERIDO, alpha=0.35, label="Ferido", edgecolors="none")
        ax.scatter(fat.geometry.x, fat.geometry.y, s=24, c=COR_FATAL, alpha=0.8, label="Fatal", edgecolors="none")
        cx.add_basemap(ax, source=cx.providers.CartoDB.Positron, attribution_size=6)
        ax.set_axis_off()
        ax.set_title(T_MAPA)
        leg = ax.legend(loc="lower right", markerscale=2.2, framealpha=0.9, fontsize=20)
        leg.get_frame().set_edgecolor("#888888")
    except Exception as exc:  # pragma: no cover
        print(f"[aviso] basemap indisponivel ({exc}); usando scatter simples")
    _save(fig, "02_mapa_amostra.png")


def fig_fase_dia():
    df = pd.read_pickle(PROCESSED_DIR / "df_limpo.pkl")
    ct = pd.crosstab(df["fase_dia"], df["desfecho"], normalize="index") * 100
    serie = ct["Fatal"].sort_values()
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(serie.index, serie.values, color=COR_FATAL, height=0.62)
    ax.set_xlabel(T_FASE_X)
    ax.set_title(T_FASE)
    ax.set_xlim(0, serie.max() * 1.16)
    for b, v in zip(bars, serie.values):
        ax.text(v + serie.max() * 0.015, b.get_y() + b.get_height() / 2,
                f"{v:.1f}%", va="center", ha="left", fontsize=20, fontweight="bold")
    _save(fig, "02_fatal_por_fase_dia.png")


def _cramers_v(x, y):
    from scipy.stats import chi2_contingency
    ct = pd.crosstab(x, y)
    chi2 = chi2_contingency(ct)[0]
    n = ct.values.sum()
    r, k = ct.shape
    return np.sqrt((chi2 / n) / (min(r, k) - 1))


def fig_cramers():
    df = pd.read_pickle(PROCESSED_DIR / "df_limpo.pkl")
    rows = [{"variavel": _readable_var(c), "v": _cramers_v(df[c], df["desfecho"])}
            for c in COLUNAS_CONTEXTO if c in df.columns]
    cv = pd.DataFrame(rows).sort_values("v")
    fig, ax = plt.subplots(figsize=(10, 6.5))
    bars = ax.barh(cv["variavel"], cv["v"], color=COR_AUX, height=0.66)
    ax.set_xlabel(T_CRAMER_X)
    ax.set_title(T_CRAMER)
    ax.set_xlim(0, cv["v"].max() * 1.16)
    for b, v in zip(bars, cv["v"]):
        ax.text(v + cv["v"].max() * 0.015, b.get_y() + b.get_height() / 2,
                f"{v:.2f}".replace(".", ","), va="center", ha="left", fontsize=19, fontweight="bold")
    _save(fig, "02_cramers_v_desfecho.png")


def fig_comparacao():
    try:
        df = pd.read_csv(OUT_TAB / "comparacao_fatal_ferido.csv", encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(OUT_TAB / "comparacao_fatal_ferido.csv", encoding="latin-1")
    df = df.head(7).iloc[::-1].reset_index(drop=True)
    labels = [_short_ctx(c) for c in df["contexto"]]
    y = np.arange(len(df))
    h = 0.4
    fig, ax = plt.subplots(figsize=(12, 7.5))
    ax.barh(y + h / 2, df["lift_fatal"], height=h, color=COR_FATAL, label=L_FATAL)
    ax.barh(y - h / 2, df["lift_ferido"], height=h, color=COR_FERIDO, label=L_FERIDO)
    ax.axvline(1.0, color="#333333", linestyle="--", linewidth=2)
    ax.text(1.04, len(df) - 0.45, T_INDEP, fontsize=17, color="#333333")
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=18)
    ax.set_xlabel(T_COMP_X)
    ax.set_title(T_COMP)
    for yi, vf, vr in zip(y, df["lift_fatal"], df["lift_ferido"]):
        ax.text(vf + 0.06, yi + h / 2, f"{vf:.1f}".replace(".", ","), va="center", fontsize=16, fontweight="bold", color=COR_FATAL)
        ax.text(vr + 0.06, yi - h / 2, f"{vr:.2f}".replace(".", ","), va="center", fontsize=16, color=COR_FERIDO)
    ax.legend(loc="lower right", framealpha=0.95)
    ax.set_xlim(0, df["lift_fatal"].max() * 1.2)
    _save(fig, "09_comparacao_fatal_ferido.png")


def fig_por_ano():
    with open(PROCESSED_DIR / "rules_por_ano.pkl", "rb") as f:
        rules_por_ano = pickle.load(f)
    rows = []
    for ano, rules in rules_por_ano.items():
        if rules is None or rules.empty:
            continue
        rows.append({"ano": int(ano), "n": len(rules), "lift": rules["lift"].head(10).mean()})
    d = pd.DataFrame(rows).sort_values("ano")
    fig, ax1 = plt.subplots(figsize=(10, 6))
    bars = ax1.bar(d["ano"].astype(str), d["n"], color=COR_FERIDO, alpha=0.85, width=0.6)
    ax1.set_ylabel(T_ANO_Y1, color=COR_FERIDO)
    ax1.tick_params(axis="y", labelcolor=COR_FERIDO)
    ax1.set_ylim(0, d["n"].max() * 1.2)
    for b, v in zip(bars, d["n"]):
        ax1.text(b.get_x() + b.get_width() / 2, v + d["n"].max() * 0.02, f"{v:.0f}",
                 ha="center", va="bottom", fontsize=19, fontweight="bold", color=COR_FERIDO)
    ax2 = ax1.twinx()
    ax2.plot(d["ano"].astype(str), d["lift"], color=COR_FATAL, marker="o", markersize=12, linewidth=3, label=T_ANO_Y2)
    ax2.set_ylabel(T_ANO_Y2, color=COR_FATAL)
    ax2.tick_params(axis="y", labelcolor=COR_FATAL)
    ax2.grid(False)
    ax1.set_title(T_ANO)
    _save(fig, "08_mineracao_por_ano.png")


def _readable_rule(ante_str):
    mapa = {
        "condicao_metereologica": "Clima", "tipo_pista": "Pista", "tracado_via": "Tra\u00e7ado",
        "uso_solo": "Entorno", "causa_acidente": "Causa", "tipo_acidente": "Tipo",
        "fase_dia": "Fase", "fim_de_semana": "FimSem",
    }
    cols = sorted(mapa, key=len, reverse=True)
    parts = []
    for raw in str(ante_str).split(", "):
        raw = raw.replace("ctx_", "")
        for c in cols:
            if raw.startswith(c + "_"):
                val = raw[len(c) + 1:].replace("_", " ")
                low = val.strip().lower()
                if c == "uso_solo":
                    val = "Urbano" if low == "sim" else "Rural"
                elif c == "fim_de_semana":
                    val = "Fim de semana" if low == "sim" else "Dia \u00fatil"
                parts.append(val)
                break
    return _short_ctx(" + ".join(parts))


def fig_estratos():
    df_onehot = pd.read_pickle(PROCESSED_DIR / "transacional.pkl")
    df_meta = pd.read_pickle(PROCESSED_DIR / "transacional_meta.pkl")
    estratos = comparar_uso_solo(df_onehot, df_meta)
    nome_legivel = {"urbano": "Urbano", "rural": "Rural"}
    cor = {"Urbano": COR_FERIDO, "Rural": COR_FATAL}
    rows = []
    for nome, rules in estratos.items():
        if rules is None or rules.empty:
            continue
        for _, r in rules.head(5).iterrows():
            rows.append({"estrato": nome_legivel.get(nome, nome.title()),
                         "regra": _readable_rule(r["antecedents_str"]), "lift": r["lift"]})
    d = pd.DataFrame(rows).sort_values("lift")
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.barh(d["regra"], d["lift"], color=[cor.get(e, COR_AUX) for e in d["estrato"]], height=0.72)
    ax.set_xlabel(T_ESTR_X)
    ax.set_title(T_ESTR)
    ax.set_xlim(0, d["lift"].max() * 1.12)
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in [COR_FATAL, COR_FERIDO]]
    ax.legend(handles, ["Rural", "Urbano"], loc="lower right", framealpha=0.9)
    _save(fig, "07_estratos_uso_solo.png")


def main():
    fig_distribuicao()
    fig_fase_dia()
    fig_cramers()
    fig_comparacao()
    fig_por_ano()
    fig_estratos()
    fig_mapa()
    print("[OK] Figuras do poster regeradas em 300 DPI.")


if __name__ == "__main__":
    main()
