# -*- coding: utf-8 -*-
"""Restricted association rule mining (FP-Growth)."""
from __future__ import annotations

import time

import pandas as pd
from mlxtend.frequent_patterns import association_rules, fpgrowth

from src.config import (
    ITEM_ALVO_FATAL,
    MAX_ANTECEDENTES,
    MIN_CONFIDENCE,
    MIN_COUNT_ABS,
    MIN_LIFT,
    MIN_SUPPORT,
    PREFIXO_CONTEXTO,
)


def _frozenset_to_str(s) -> str:
    return ", ".join(sorted(s)) if isinstance(s, frozenset) else str(s)


def is_item_contexto(item: str) -> bool:
    return str(item).startswith(PREFIXO_CONTEXTO)


def extrair_itemsets_e_regras(df_onehot, min_support=MIN_SUPPORT):
    t0 = time.time()
    itemsets = fpgrowth(df_onehot, min_support=min_support, use_colnames=True)
    elapsed = time.time() - t0
    if itemsets.empty:
        return itemsets, pd.DataFrame(), elapsed
    rules = association_rules(itemsets, metric="confidence", min_threshold=MIN_CONFIDENCE)
    rules = rules[rules["lift"] > MIN_LIFT].sort_values("lift", ascending=False).reset_index(drop=True)
    return itemsets, rules, elapsed


def filtrar_regras_contexto_para_alvo(rules, consequente_alvo=ITEM_ALVO_FATAL, max_antecedentes=MAX_ANTECEDENTES, min_count_abs=MIN_COUNT_ABS, n_total=None):
    if rules.empty:
        return rules.copy()
    out = []
    for _, row in rules.iterrows():
        ante, cons = row["antecedents"], row["consequents"]
        if not isinstance(ante, frozenset) or cons != frozenset({consequente_alvo}):
            continue
        if len(ante) == 0 or len(ante) > max_antecedentes:
            continue
        if not all(is_item_contexto(i) for i in ante):
            continue
        if n_total and row["support"] * n_total < min_count_abs:
            continue
        out.append(row)
    return pd.DataFrame(out).sort_values("lift", ascending=False).reset_index(drop=True) if out else pd.DataFrame(columns=rules.columns)


def podar_regras_nao_minimais(rules: pd.DataFrame) -> pd.DataFrame:
    if rules.empty:
        return rules
    kept = []
    for _, row in rules.sort_values(["confidence", "lift"], ascending=False).iterrows():
        dominated = any(
            prev["consequents"] == row["consequents"]
            and prev["antecedents"].issubset(row["antecedents"])
            and prev["confidence"] >= row["confidence"]
            for prev in kept
        )
        if not dominated:
            kept.append(row)
    return pd.DataFrame(kept).sort_values("lift", ascending=False).reset_index(drop=True)


def adicionar_colunas_legiveis(rules: pd.DataFrame) -> pd.DataFrame:
    out = rules.copy()
    out["antecedents_str"] = out["antecedents"].apply(_frozenset_to_str)
    out["consequents_str"] = out["consequents"].apply(_frozenset_to_str)
    out["n_antecedentes"] = out["antecedents"].apply(len)
    return out


def minerar_regras_fatais(df_onehot, min_support=MIN_SUPPORT, min_count_abs=MIN_COUNT_ABS):
    n_total = len(df_onehot)
    itemsets, rules_all, _ = extrair_itemsets_e_regras(df_onehot, min_support)
    rules_ctx = filtrar_regras_contexto_para_alvo(rules_all, min_count_abs=min_count_abs, n_total=n_total)
    rules_ctx = adicionar_colunas_legiveis(podar_regras_nao_minimais(rules_ctx))
    return itemsets, rules_all, rules_ctx


def minerar_por_ano(df_onehot, df_meta, min_support=MIN_SUPPORT, min_count_abs=MIN_COUNT_ABS):
    rules_por_ano = {}
    for ano in sorted(df_meta["ano"].dropna().unique()):
        idx = df_meta.index[df_meta["ano"] == ano]
        if len(idx) < min_count_abs:
            continue
        _, _, rules = minerar_regras_fatais(df_onehot.loc[idx], min_support, min_count_abs)
        if not rules.empty:
            rules = rules.copy()
            rules["ano"] = int(ano)
        rules_por_ano[int(ano)] = rules
    return rules_por_ano


def classificar_estabilidade_temporal(rules_por_ano, threshold_estavel=0.5, threshold_transitorio=0.3):
    if not rules_por_ano:
        return pd.DataFrame()
    anos = sorted(rules_por_ano.keys())
    n_anos = len(anos)
    contagem = {}
    for ano in anos:
        for _, row in rules_por_ano[ano].iterrows():
            key = f"{row['antecedents_str']} => {row['consequents_str']}"
            contagem.setdefault(key, {"anos": [], "lifts": [], "confidences": []})
            contagem[key]["anos"].append(ano)
            contagem[key]["lifts"].append(row["lift"])
            contagem[key]["confidences"].append(row["confidence"])

    rows = []
    for key, data in contagem.items():
        freq = len(data["anos"]) / n_anos
        status = "estavel" if freq >= threshold_estavel else ("transitoria" if freq < threshold_transitorio else "intermediaria")
        rows.append({
            "regra": key,
            "n_anos_presente": len(data["anos"]),
            "n_anos_total": n_anos,
            "freq_relativa": round(freq, 3),
            "status": status,
            "lift_medio": round(sum(data["lifts"]) / len(data["lifts"]), 4),
            "confianca_media": round(sum(data["confidences"]) / len(data["confidences"]), 4),
            "anos": sorted(data["anos"]),
        })
    return pd.DataFrame(rows).sort_values(["status", "lift_medio"], ascending=[True, False]) if rows else pd.DataFrame(
        columns=["regra", "n_anos_presente", "n_anos_total", "freq_relativa", "status", "lift_medio", "confianca_media", "anos"]
    )


def comparar_uso_solo(df_onehot, df_meta, min_support=MIN_SUPPORT):
    resultados = {}
    for valor, label in [("Sim", "urbano"), ("N\u00e3o", "rural"), ("Nao", "rural")]:
        mask = df_meta["uso_solo"] == valor
        if mask.sum() < 15:
            continue
        _, _, rules = minerar_regras_fatais(df_onehot.loc[df_meta.index[mask]], min_support, min_count_abs=15)
        if not rules.empty:
            rules = rules.copy()
            rules["estrato"] = label
        resultados[label] = rules
    return resultados
