# -*- coding: utf-8 -*-
"""Generate LaTeX tables for relatorios/final/."""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from src.data_loading import carregar_anos
from src.preparation import criar_desfecho, subset_com_vitimas

ROOT = Path(__file__).resolve().parents[1]
TABELAS_DIR = ROOT / "relatorios" / "final" / "tabelas"


def latex_escape(text: str) -> str:
    repl = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    out = text
    for k, v in repl.items():
        out = out.replace(k, v)
    return out


COLUNAS_CTX = [
    "condicao_metereologica",
    "tipo_pista",
    "tracado_via",
    "uso_solo",
    "causa_acidente",
    "tipo_acidente",
    "fase_dia",
    "fim_de_semana",
]


def ctx_to_readable(antecedents_str: str) -> str:
    parts = []
    for raw in antecedents_str.split(", "):
        raw = raw.replace("ctx_", "")
        col = None
        val = None
        for c in sorted(COLUNAS_CTX, key=len, reverse=True):
            prefix = c + "_"
            if raw.startswith(prefix):
                col = c.replace("_", " ")
                val = raw[len(prefix) :].replace("_", " ")
                break
        if col and val:
            parts.append(f"{col}={val}")
    return "; ".join(parts)


def write_distribuicao_desfecho() -> None:
    df, _ = carregar_anos(ignorar_ausentes=True)
    df_cv = subset_com_vitimas(df)
    df_cv["desfecho"] = criar_desfecho(df_cv)
    n = len(df_cv)
    counts = df_cv["desfecho"].value_counts()
    fatal = counts.get("Fatal", 0)
    ferido = counts.get("Ferido", 0)
    lines = [
        r"\begin{tabular}{@{}lrr@{}}",
        r"\toprule",
        r"\textbf{Desfecho} & \textbf{$n$} & \textbf{\%} \\",
        r"\midrule",
        f"Ferido & {ferido:,}".replace(",", ".") + f" & {100 * ferido / n:.1f} \\\\",
        f"Fatal & {fatal:,}".replace(",", ".") + f" & {100 * fatal / n:.1f} \\\\",
        r"\midrule",
        f"Total (com v\\'timas) & {n:,}".replace(",", ".") + r" & 100,0 \\",
        r"\bottomrule",
        r"\end{tabular}",
    ]
    (TABELAS_DIR / "distribuicao_desfecho.tex").write_text("\n".join(lines), encoding="utf-8")


def write_top_regras_fatal(n: int = 12) -> None:
    df = pd.read_csv(ROOT / "outputs" / "tabelas" / "top15_regras_traduzidas.csv")
    df = df.head(n)
    rows = []
    for _, r in df.iterrows():
        ant = latex_escape(ctx_to_readable(r["antecedents_str"]))
        sup = f"{100 * r['support']:.1f}".replace(".", ",")
        conf = f"{100 * r['confidence']:.1f}".replace(".", ",")
        lift = f"{r['lift']:.2f}".replace(".", ",")
        rows.append(f"{ant} & {sup} & {conf} & {lift} \\\\")
    lines = [
        r"\begin{tabular}{@{}p{6.8cm}rrr@{}}",
        r"\toprule",
        r"\textbf{Antecedente (contexto)} & \textbf{Sup. (\%)} & \textbf{Conf. (\%)} & \textbf{Lift} \\",
        r"\midrule",
        *rows,
        r"\bottomrule",
        r"\end{tabular}",
    ]
    (TABELAS_DIR / "top_regras_fatal.tex").write_text("\n".join(lines), encoding="utf-8")


def write_estabilidade(n: int = 8) -> None:
    df = pd.read_csv(ROOT / "outputs" / "tabelas" / "regras_estabilidade_temporal.csv")
    df = df[(df["status"] == "estavel") & (df["n_anos_presente"] == 4)].sort_values(
        "lift_medio", ascending=False
    ).head(n)
    rows = []
    for _, r in df.iterrows():
        regra = r["regra"].split(" => ")[0]
        regra = latex_escape(ctx_to_readable(regra))
        anos = r["n_anos_presente"]
        lift = f"{r['lift_medio']:.2f}".replace(".", ",")
        conf = f"{100 * r['confianca_media']:.1f}".replace(".", ",")
        rows.append(f"{regra} & {anos}/4 & {conf} & {lift} \\\\")
    lines = [
        r"\begin{tabular}{@{}p{6.5cm}rrr@{}}",
        r"\toprule",
        r"\textbf{Regra (antecedente)} & \textbf{Anos} & \textbf{Conf. (\%)} & \textbf{Lift m\'ed.} \\",
        r"\midrule",
        *rows,
        r"\bottomrule",
        r"\end{tabular}",
    ]
    (TABELAS_DIR / "estabilidade.tex").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    TABELAS_DIR.mkdir(parents=True, exist_ok=True)
    write_distribuicao_desfecho()
    write_top_regras_fatal()
    write_estabilidade()
    print(f"Tabelas geradas em {TABELAS_DIR}")


if __name__ == "__main__":
    main()
