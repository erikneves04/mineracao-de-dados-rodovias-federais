# -*- coding: utf-8 -*-
"""Rule evaluation and natural-language translation."""
from __future__ import annotations

import pandas as pd

from src.config import (
    COLUNAS_CONTEXTO,
    ITEM_ALVO_ALTA_GRAVIDADE,
    ITEM_ALVO_BAIXA_GRAVIDADE,
    ITEM_ALVO_FATAL,
    ITEM_ALVO_FERIDO,
    PREFIXO_CONTEXTO,
)


def _limpar_item(item: str) -> str:
    s = str(item)
    if s.startswith(PREFIXO_CONTEXTO):
        s = s[len(PREFIXO_CONTEXTO):]
    mapa = {
        "condicao_metereologica": "clima",
        "tipo_pista": "tipo de pista",
        "tracado_via": "tracado da via",
        "uso_solo": "entorno",
        "causa_acidente": "causa",
        "tipo_acidente": "tipo de acidente",
        "fase_dia": "fase do dia",
        "fim_de_semana": "fim de semana",
    }
    alvo_map = {
        ITEM_ALVO_ALTA_GRAVIDADE: "alta gravidade",
        ITEM_ALVO_BAIXA_GRAVIDADE: "baixa gravidade",
        ITEM_ALVO_FATAL: "desfecho fatal",
        ITEM_ALVO_FERIDO: "desfecho ferido",
    }
    if s in alvo_map:
        return alvo_map[s]
    for col in sorted(COLUNAS_CONTEXTO, key=len, reverse=True):
        prefixo = f"{col}_"
        if s.startswith(prefixo):
            val = s[len(prefixo):].replace("_", " ")
            nome = mapa.get(col, col.replace("_", " "))
            if col == "uso_solo":
                val = "urbano" if val.lower() == "sim" else "rural"
            return f"{nome}={val}"
    return s.replace("_", " ")


def _consequente_texto(row: pd.Series) -> str:
    cons = row.get("consequents")
    if isinstance(cons, frozenset) and len(cons) == 1:
        return _limpar_item(next(iter(cons)))
    cons_str = str(row.get("consequents_str", ""))
    if cons_str:
        return _limpar_item(cons_str)
    return "desfecho"


def regra_para_texto(row: pd.Series) -> str:
    if isinstance(row.get("antecedents"), frozenset):
        ante_items = [_limpar_item(i) for i in sorted(row["antecedents"])]
    else:
        ante_items = [_limpar_item(x.strip()) for x in str(row.get("antecedents_str", "")).split(",")]
    ante_txt = " E ".join(ante_items)
    sup, conf, lift = row.get("support", 0) * 100, row.get("confidence", 0) * 100, row.get("lift", 0)
    return f"Quando {ante_txt}, entao {_consequente_texto(row)}. [Suporte: {sup:.1f}% | Confianca: {conf:.1f}% | Lift: {lift:.2f}]"


def traduzir_regras(rules: pd.DataFrame) -> pd.DataFrame:
    out = rules.copy()
    out["explicacao_natural"] = out.apply(regra_para_texto, axis=1)
    return out


def disclaimer() -> str:
    return (
        "AVISO: Regras representam coocorrencias estatisticas. "
        "Associacao nao implica causalidade."
    )


def resumo_qualidade_regras(rules: pd.DataFrame) -> dict:
    if rules.empty:
        return {"n_regras": 0, "lift_max": 0, "lift_mediano": 0}
    return {
        "n_regras": len(rules),
        "lift_max": round(rules["lift"].max(), 4),
        "lift_mediano": round(rules["lift"].median(), 4),
    }


def exportar_top_regras_latex(rules: pd.DataFrame, path, n=15):
    top = traduzir_regras(rules.head(n))
    lines = ["\\begin{tabular}{@{}p{7cm}rrr@{}}", "\\toprule", "Regra & Sup. & Conf. & Lift \\\\", "\\midrule"]
    for _, row in top.iterrows():
        txt = row["explicacao_natural"].replace("&", "\\&")[:120]
        lines.append(f"{txt} & {row['support']:.3f} & {row['confidence']:.3f} & {row['lift']:.2f} \\\\")
    lines.extend(["\\bottomrule", "\\end{tabular}"])
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
