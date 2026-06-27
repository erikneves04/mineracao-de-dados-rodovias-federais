# -*- coding: utf-8 -*-
"""Generate LaTeX tables for relatorios/final/."""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import ANOS_COMPLETOS
from src.data_loading import carregar_anos
from src.preparation import criar_desfecho_alta_gravidade, subset_com_vitimas

TABELAS_DIR = ROOT / "relatorios" / "final" / "tabelas"
POSTER_TABELAS_DIR = ROOT / "relatorios" / "poster" / "tabelas"


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
    def compact_value(col: str, val: str) -> str:
        val = val.replace("_", " ")
        if col == "uso_solo":
            return "Urbano" if val.lower() == "sim" else "Rural"
        if col == "fim_de_semana":
            return "Fim de semana" if val.lower() == "sim" else "Dia útil"
        repl = {
            "Pedestre andava na pista": "Pedestre na pista",
            "Atropelamento de Pedestre": "Atrop. pedestre",
            "Colisão frontal": "Col. frontal",
            "Transitar na contramão": "Contramão",
            "Céu Claro": "Céu claro",
            "Plena Noite": "Plena noite",
        }
        return repl.get(val, val)

    parts = []
    for raw in antecedents_str.split(", "):
        raw = raw.replace("ctx_", "")
        col = None
        val = None
        for c in sorted(COLUNAS_CTX, key=len, reverse=True):
            prefix = c + "_"
            if raw.startswith(prefix):
                col = c
                val = compact_value(c, raw[len(prefix) :])
                break
        if col and val:
            parts.append(val)
    return " + ".join(parts)


def write_distribuicao_desfecho() -> None:
    df, _ = carregar_anos(anos=ANOS_COMPLETOS, ignorar_ausentes=True)
    df_cv = subset_com_vitimas(df)
    df_cv["desfecho_alta_gravidade"] = criar_desfecho_alta_gravidade(df_cv)
    n = len(df_cv)
    counts = df_cv["desfecho_alta_gravidade"].value_counts()
    alta = counts.get("AltaGravidade", 0)
    baixa = counts.get("BaixaGravidade", 0)
    lines = [
        r"\begin{tabular}{@{}lrr@{}}",
        r"\toprule",
        r"\textbf{Desfecho} & \textbf{$n$} & \textbf{\%} \\",
        r"\midrule",
        f"Baixa gravidade & {baixa:,}".replace(",", ".") + " & " + f"{100 * baixa / n:.1f}".replace(".", ",") + r" \\",
        f"Alta gravidade & {alta:,}".replace(",", ".") + " & " + f"{100 * alta / n:.1f}".replace(".", ",") + r" \\",
        r"\midrule",
        f"Total (com v\\'itimas) & {n:,}".replace(",", ".") + r" & 100,0 \\",
        r"\bottomrule",
        r"\end{tabular}",
    ]
    (TABELAS_DIR / "distribuicao_desfecho.tex").write_text("\n".join(lines), encoding="utf-8")
    (TABELAS_DIR / "distribuicao_alta_gravidade.tex").write_text("\n".join(lines), encoding="utf-8")


def write_resumo_por_ano() -> None:
    df = pd.read_csv(ROOT / "outputs" / "tabelas" / "resumo_por_ano.csv")
    rows = []
    for _, r in df.iterrows():
        ano = int(r["ano"])
        n = f"{int(r['n_ocorrencias']):,}".replace(",", ".")
        vit = f"{int(r['n_com_vitimas']):,}".replace(",", ".")
        alta = f"{int(r['n_alta_gravidade']):,}".replace(",", ".")
        fatal = f"{int(r['n_fatais']):,}".replace(",", ".")
        data_max = str(r["data_max"])[:10]
        rows.append(f"{ano} & {n} & {vit} & {alta} & {fatal} & {data_max} \\\\")
    lines = [
        r"\begin{tabular}{@{}lrrrrl@{}}",
        r"\toprule",
        r"\textbf{Ano} & \textbf{Ocorr.} & \textbf{Com v\'itimas} & \textbf{Alta grav.} & \textbf{Fatais} & \textbf{Data final} \\",
        r"\midrule",
        *rows,
        r"\bottomrule",
        r"\end{tabular}",
    ]
    (TABELAS_DIR / "resumo_por_ano.tex").write_text("\n".join(lines), encoding="utf-8")


def write_top_regras_alta(n: int = 8) -> None:
    df = pd.read_csv(ROOT / "outputs" / "tabelas" / "top_regras_alta_gravidade.csv")
    df = df.head(n)
    rows = []
    for _, r in df.iterrows():
        ant = latex_escape(ctx_to_readable(r["antecedents_str"]))
        sup = f"{100 * r['support']:.1f}".replace(".", ",")
        conf = f"{100 * r['confidence']:.1f}".replace(".", ",")
        lift = f"{r['lift']:.2f}".replace(".", ",")
        rows.append(f"{ant} & {sup} & {conf} & {lift} \\\\")
    lines = [
        r"\begin{tabular}{@{}>{\raggedright\arraybackslash}p{7.3cm}rrr@{}}",
        r"\toprule",
        r"\textbf{Antecedente (contexto)} & \textbf{Sup. (\%)} & \textbf{Conf. (\%)} & \textbf{Lift} \\",
        r"\midrule",
        *rows,
        r"\bottomrule",
        r"\end{tabular}",
    ]
    (TABELAS_DIR / "top_regras_alta.tex").write_text("\n".join(lines), encoding="utf-8")
    (TABELAS_DIR / "top_regras_fatal.tex").write_text("\n".join(lines), encoding="utf-8")


def write_estabilidade(n: int = 8) -> None:
    df = pd.read_csv(ROOT / "outputs" / "tabelas" / "estabilidade_alta_gravidade.csv")
    df = df[(df["status"] == "estavel") & (df["n_anos_presente"] == 3)].sort_values(
        "lift_medio", ascending=False
    ).head(n)
    rows = []
    for _, r in df.iterrows():
        regra = r["regra"].split(" => ")[0]
        regra = latex_escape(ctx_to_readable(regra))
        anos = r["n_anos_presente"]
        lift = f"{r['lift_medio']:.2f}".replace(".", ",")
        conf = f"{100 * r['confianca_media']:.1f}".replace(".", ",")
        rows.append(f"{regra} & {anos}/3 & {conf} & {lift} \\\\")
    lines = [
        r"\begin{tabular}{@{}>{\raggedright\arraybackslash}p{6.5cm}rrr@{}}",
        r"\toprule",
        r"\textbf{Regra (antecedente)} & \textbf{Anos} & \textbf{Conf. (\%)} & \textbf{Lift m\'ed.} \\",
        r"\midrule",
        *rows,
        r"\bottomrule",
        r"\end{tabular}",
    ]
    (TABELAS_DIR / "estabilidade.tex").write_text("\n".join(lines), encoding="utf-8")


def write_comparacao(n: int = 7) -> None:
    df = pd.read_csv(ROOT / "outputs" / "tabelas" / "comparacao_alta_baixa_fatal.csv").head(n)
    rows = []
    for _, r in df.iterrows():
        ctx = latex_escape(ctx_to_readable(r["contexto"]))
        conf_alta = f"{100 * r['conf_alta']:.1f}".replace(".", ",")
        lift_alta = f"{r['lift_alta']:.2f}".replace(".", ",")
        lift_baixa = f"{r['lift_baixa']:.2f}".replace(".", ",")
        lift_fatal = f"{r['lift_fatal']:.2f}".replace(".", ",")
        rows.append(f"{ctx} & {conf_alta} & {lift_alta} & {lift_baixa} & {lift_fatal} \\\\")
    lines = [
        r"\begin{tabular}{@{}>{\raggedright\arraybackslash}p{5.9cm}rrrr@{}}",
        r"\toprule",
        r"\textbf{Contexto} & \textbf{Conf. alta (\%)} & \textbf{Lift alta} & \textbf{Lift baixa} & \textbf{Lift fatal} \\",
        r"\midrule",
        *rows,
        r"\bottomrule",
        r"\end{tabular}",
    ]
    (TABELAS_DIR / "comparacao_alta_baixa_fatal.tex").write_text("\n".join(lines), encoding="utf-8")

    poster_rows = []
    for _, r in df.head(5).iterrows():
        ctx = latex_escape(ctx_to_readable(r["contexto"]))
        conf_alta = f"{100 * r['conf_alta']:.1f}".replace(".", ",")
        lift_alta = f"{r['lift_alta']:.2f}".replace(".", ",")
        lift_fatal = f"{r['lift_fatal']:.2f}".replace(".", ",")
        poster_rows.append(f"{ctx} & {conf_alta}\\% & {lift_alta} & {lift_fatal} \\\\")
    poster_lines = [
        r"\begin{tabular}{@{}p{8.7cm}rrr@{}}",
        r"\toprule",
        r"\textbf{Contexto} & \textbf{Conf. alta} & \textbf{Lift alta} & \textbf{Lift fatal} \\",
        r"\midrule",
        *poster_rows,
        r"\bottomrule",
        r"\end{tabular}",
    ]
    POSTER_TABELAS_DIR.mkdir(parents=True, exist_ok=True)
    (POSTER_TABELAS_DIR / "comparacao_alta_baixa_fatal.tex").write_text("\n".join(poster_lines), encoding="utf-8")


def write_cobertura() -> None:
    df = pd.read_csv(ROOT / "outputs" / "tabelas" / "cobertura_regras.csv")
    rows = []
    for _, r in df.iterrows():
        label = str(r["conjunto"]).replace("top-", "Top-").replace("todas", "Todas")
        n_regras = int(r["n_regras"])
        n_cob = f"{int(r['n_ocorrencias_cobertas']):,}".replace(",", ".")
        n_alta = f"{int(r['n_alta_cobertas']):,}".replace(",", ".")
        pct_alta = f"{100 * r['pct_alta_coberta']:.1f}".replace(".", ",")
        prec = f"{100 * r['precisao_alta_entre_cobertos']:.1f}".replace(".", ",")
        rows.append(f"{label} & {n_regras} & {n_cob} & {n_alta} & {pct_alta} & {prec} \\\\")
    lines = [
        r"\begin{tabular}{@{}lrrrrr@{}}",
        r"\toprule",
        r"\textbf{Conjunto} & \textbf{Regras} & \textbf{Ocorr. cobertas} & \textbf{Alta coberta} & \textbf{\% alta} & \textbf{Precis\~ao} \\",
        r"\midrule",
        *rows,
        r"\bottomrule",
        r"\end{tabular}",
    ]
    (TABELAS_DIR / "cobertura_regras.tex").write_text("\n".join(lines), encoding="utf-8")


def write_bootstrap(n: int = 5) -> None:
    df = pd.read_csv(ROOT / "outputs" / "tabelas" / "bootstrap_top_regras.csv").head(n)
    rows = []
    for _, r in df.iterrows():
        ctx = latex_escape(ctx_to_readable(r["contexto"]))
        conf = f"{100 * r['confidence_boot_mean']:.1f}".replace(".", ",")
        conf_low = f"{100 * r['confidence_ic95_low']:.1f}".replace(".", ",")
        conf_high = f"{100 * r['confidence_ic95_high']:.1f}".replace(".", ",")
        lift = f"{r['lift_boot_mean']:.2f}".replace(".", ",")
        lift_low = f"{r['lift_ic95_low']:.2f}".replace(".", ",")
        lift_high = f"{r['lift_ic95_high']:.2f}".replace(".", ",")
        rows.append(f"{ctx} & {conf} [{conf_low}; {conf_high}] & {lift} [{lift_low}; {lift_high}] \\\\")
    lines = [
        r"\begin{tabular}{@{}>{\raggedright\arraybackslash}p{6.6cm}rr@{}}",
        r"\toprule",
        r"\textbf{Contexto} & \textbf{Conf. bootstrap IC95\%} & \textbf{Lift bootstrap IC95\%} \\",
        r"\midrule",
        *rows,
        r"\bottomrule",
        r"\end{tabular}",
    ]
    (TABELAS_DIR / "bootstrap_top_regras.tex").write_text("\n".join(lines), encoding="utf-8")


def write_sensibilidade() -> None:
    df = pd.read_csv(ROOT / "outputs" / "tabelas" / "sensibilidade_parametros.csv")
    df = df[df["min_lift"].round(2) == 1.10].copy()
    df = df.sort_values(["min_support", "min_confidence"])
    rows = []
    for _, r in df.iterrows():
        sup = f"{100 * r['min_support']:.1f}".replace(".", ",")
        conf = f"{100 * r['min_confidence']:.0f}".replace(".", ",")
        n = int(r["n_regras"])
        lift = f"{r['lift_max']:.2f}".replace(".", ",")
        rows.append(f"{sup} & {conf} & {n} & {lift} \\\\")
    lines = [
        r"\begin{tabular}{@{}rrrr@{}}",
        r"\toprule",
        r"\textbf{Sup. m\'in. (\%)} & \textbf{Conf. m\'in. (\%)} & \textbf{N regras} & \textbf{Lift m\'ax.} \\",
        r"\midrule",
        *rows,
        r"\bottomrule",
        r"\end{tabular}",
    ]
    (TABELAS_DIR / "sensibilidade.tex").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    TABELAS_DIR.mkdir(parents=True, exist_ok=True)
    write_distribuicao_desfecho()
    write_resumo_por_ano()
    write_top_regras_alta()
    write_estabilidade()
    write_comparacao()
    write_cobertura()
    write_bootstrap()
    write_sensibilidade()
    print(f"Tabelas geradas em {TABELAS_DIR}")


if __name__ == "__main__":
    main()
