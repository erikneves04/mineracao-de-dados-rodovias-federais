# -*- coding: utf-8 -*-
"""Restricted association rule mining (FP-Growth)."""
from __future__ import annotations

import time
from itertools import combinations

import pandas as pd
from mlxtend.frequent_patterns import association_rules, fpgrowth

from src.config import (
    ALVO_PRINCIPAL,
    ANOS_COMPLETOS,
    DATA_MAX_2026_ESPERADA,
    ITEM_ALVO_ALTA_GRAVIDADE,
    ITEM_ALVO_FATAL,
    MAX_ANTECEDENTES,
    MIN_CONFIDENCE,
    MIN_CONFIDENCE_ALTA_GRAVIDADE,
    MIN_CONFIDENCE_FATAL,
    MIN_COUNT_ABS,
    MIN_LIFT,
    MIN_SUPPORT,
    PREFIXO_CONTEXTO,
)


def _frozenset_to_str(s) -> str:
    return ", ".join(sorted(s)) if isinstance(s, frozenset) else str(s)


def is_item_contexto(item: str) -> bool:
    return str(item).startswith(PREFIXO_CONTEXTO)


def is_item_desfecho(item: str) -> bool:
    return str(item).startswith("desfecho_")


def extrair_itemsets_e_regras(df_onehot, min_support=MIN_SUPPORT, gerar_regras=True):
    t0 = time.time()
    itemsets = fpgrowth(df_onehot, min_support=min_support, use_colnames=True)
    elapsed = time.time() - t0
    if itemsets.empty or not gerar_regras:
        return itemsets, pd.DataFrame(), elapsed
    rules = association_rules(itemsets, metric="confidence", min_threshold=MIN_CONFIDENCE)
    rules = rules[rules["lift"] > MIN_LIFT].sort_values("lift", ascending=False).reset_index(drop=True)
    return itemsets, rules, elapsed


def _support_conjunto(df_onehot: pd.DataFrame, items: frozenset) -> float:
    if len(items) == 0:
        return 0.0
    cols = list(items)
    return df_onehot[cols].all(axis=1).mean()


def gerar_regras_contexto_para_alvo(
    df_onehot: pd.DataFrame,
    itemsets: pd.DataFrame,
    consequente: str = ALVO_PRINCIPAL,
    max_antecedentes: int = MAX_ANTECEDENTES,
    min_confidence: float = MIN_CONFIDENCE_ALTA_GRAVIDADE,
    min_lift: float = MIN_LIFT,
    min_count_abs: int = MIN_COUNT_ABS,
    itens_contexto_excluir: tuple[str, ...] = (),
) -> pd.DataFrame:
    """
    Gera regras contexto -> alvo a partir de itemsets frequentes.
    Descarta itemsets com outros desfechos para evitar suporte contaminado por
    tautologias entre alvos (por exemplo, AltaGravidade + Fatal).
    """
    n_total = len(df_onehot)
    p_consequente = df_onehot[consequente].mean() if consequente in df_onehot.columns else 0
    if p_consequente == 0:
        return pd.DataFrame()

    rows = []
    support_cache = {}
    for _, row in itemsets.iterrows():
        items = row["itemsets"]
        if not isinstance(items, frozenset) or consequente not in items:
            continue
        if any((not is_item_contexto(i)) and i != consequente for i in items):
            continue
        ctx = [
            i for i in items
            if is_item_contexto(i) and not any(str(i).startswith(prefix) for prefix in itens_contexto_excluir)
        ]
        if not ctx:
            continue

        sup_joint = row["support"]
        count_joint = sup_joint * n_total
        if count_joint < min_count_abs:
            continue

        max_k = min(len(ctx), max_antecedentes)
        for k in range(1, max_k + 1):
            for ante_tuple in combinations(ctx, k):
                ante = frozenset(ante_tuple)
                if ante not in support_cache:
                    support_cache[ante] = _support_conjunto(df_onehot, ante)
                sup_ante = support_cache[ante]
                if sup_ante == 0:
                    continue
                conf = sup_joint / sup_ante
                lift = conf / p_consequente
                if conf < min_confidence or lift < min_lift:
                    continue
                rows.append({
                    "antecedents": ante,
                    "consequents": frozenset({consequente}),
                    "antecedent support": sup_ante,
                    "consequent support": p_consequente,
                    "support": sup_joint,
                    "confidence": conf,
                    "lift": lift,
                    "leverage": sup_joint - sup_ante * p_consequente,
                })

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    df = df.sort_values(["lift", "confidence", "support"], ascending=False)
    df = df.drop_duplicates(subset=["antecedents", "consequents"], keep="first")
    return df.reset_index(drop=True)


def gerar_regras_contexto_para_fatal(
    df_onehot: pd.DataFrame,
    itemsets: pd.DataFrame,
    consequente: str = ITEM_ALVO_FATAL,
    max_antecedentes: int = MAX_ANTECEDENTES,
    min_confidence: float = MIN_CONFIDENCE_FATAL,
    min_lift: float = MIN_LIFT,
    min_count_abs: int = MIN_COUNT_ABS,
    itens_contexto_excluir: tuple[str, ...] = (),
) -> pd.DataFrame:
    return gerar_regras_contexto_para_alvo(
        df_onehot=df_onehot,
        itemsets=itemsets,
        consequente=consequente,
        max_antecedentes=max_antecedentes,
        min_confidence=min_confidence,
        min_lift=min_lift,
        min_count_abs=min_count_abs,
        itens_contexto_excluir=itens_contexto_excluir,
    )


def filtrar_regras_contexto_para_alvo(rules, consequente_alvo=ALVO_PRINCIPAL, max_antecedentes=MAX_ANTECEDENTES, min_count_abs=MIN_COUNT_ABS, n_total=None):
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


def _colunas_para_mineracao(df_onehot, alvo, itens_contexto_excluir=()):
    cols = []
    for col in df_onehot.columns:
        if col == alvo:
            cols.append(col)
        elif is_item_contexto(col) and not any(str(col).startswith(prefix) for prefix in itens_contexto_excluir):
            cols.append(col)
    return cols


def minerar_regras_alvo(
    df_onehot,
    alvo=ALVO_PRINCIPAL,
    min_support=MIN_SUPPORT,
    min_confidence=MIN_CONFIDENCE_ALTA_GRAVIDADE,
    min_lift=MIN_LIFT,
    min_count_abs=MIN_COUNT_ABS,
    itens_contexto_excluir=(),
):
    cols = _colunas_para_mineracao(df_onehot, alvo, itens_contexto_excluir)
    df_mining = df_onehot[cols].copy()
    itemsets, rules_all, _ = extrair_itemsets_e_regras(df_mining, min_support, gerar_regras=False)
    rules_ctx = gerar_regras_contexto_para_alvo(
        df_mining,
        itemsets,
        consequente=alvo,
        min_confidence=min_confidence,
        min_lift=min_lift,
        min_count_abs=min_count_abs,
        itens_contexto_excluir=itens_contexto_excluir,
    )
    rules_ctx = adicionar_colunas_legiveis(podar_regras_nao_minimais(rules_ctx))
    return itemsets, rules_all, rules_ctx


def minerar_regras_alta_gravidade(df_onehot, min_support=MIN_SUPPORT, min_count_abs=MIN_COUNT_ABS):
    return minerar_regras_alvo(
        df_onehot,
        alvo=ITEM_ALVO_ALTA_GRAVIDADE,
        min_support=min_support,
        min_confidence=MIN_CONFIDENCE_ALTA_GRAVIDADE,
        min_lift=MIN_LIFT,
        min_count_abs=min_count_abs,
    )


def minerar_regras_fatais(df_onehot, min_support=MIN_SUPPORT, min_count_abs=MIN_COUNT_ABS):
    return minerar_regras_alvo(
        df_onehot,
        alvo=ITEM_ALVO_FATAL,
        min_support=min_support,
        min_confidence=MIN_CONFIDENCE_FATAL,
        min_lift=MIN_LIFT,
        min_count_abs=min_count_abs,
    )


def minerar_por_ano(
    df_onehot,
    df_meta,
    alvo=ALVO_PRINCIPAL,
    min_support=MIN_SUPPORT,
    min_confidence=MIN_CONFIDENCE_ALTA_GRAVIDADE,
    min_lift=MIN_LIFT,
    min_count_abs=MIN_COUNT_ABS,
    anos=None,
    janela_jan_abr=False,
    itens_contexto_excluir=(),
):
    rules_por_ano = {}
    anos_disponiveis = sorted(df_meta["ano"].dropna().unique())
    anos = anos or anos_disponiveis
    for ano in anos:
        mask = df_meta["ano"] == ano
        if janela_jan_abr and "data_inversa" in df_meta.columns:
            datas = pd.to_datetime(df_meta["data_inversa"], errors="coerce")
            mask = mask & datas.dt.month.between(1, 4)
        idx = df_meta.index[mask]
        if len(idx) < min_count_abs:
            continue
        _, _, rules = minerar_regras_alvo(
            df_onehot.loc[idx],
            alvo=alvo,
            min_support=min_support,
            min_confidence=min_confidence,
            min_lift=min_lift,
            min_count_abs=min_count_abs,
            itens_contexto_excluir=itens_contexto_excluir,
        )
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


def comparar_uso_solo(
    df_onehot,
    df_meta,
    alvo=ALVO_PRINCIPAL,
    min_support=MIN_SUPPORT,
    min_confidence=MIN_CONFIDENCE_ALTA_GRAVIDADE,
    min_lift=MIN_LIFT,
):
    resultados = {}
    for valor, label in [("Sim", "urbano"), ("N\u00e3o", "rural"), ("Nao", "rural")]:
        mask = df_meta["uso_solo"] == valor
        if mask.sum() < 15:
            continue
        _, _, rules = minerar_regras_alvo(
            df_onehot.loc[df_meta.index[mask]],
            alvo=alvo,
            min_support=min_support,
            min_confidence=min_confidence,
            min_lift=min_lift,
            min_count_abs=15,
            itens_contexto_excluir=("ctx_uso_solo_",),
        )
        if not rules.empty:
            rules = rules.copy()
            rules["estrato"] = label
        resultados[label] = rules
    return resultados


def analise_sensibilidade(
    df_onehot,
    alvo=ALVO_PRINCIPAL,
    supports=(0.005, 0.01, 0.02),
    confidences=(0.35, 0.40, 0.50),
    lifts=(1.05, 1.10, 1.25),
):
    rows = []
    for min_support in supports:
        itemsets, _, _ = extrair_itemsets_e_regras(
            df_onehot[_colunas_para_mineracao(df_onehot, alvo)], min_support, gerar_regras=False
        )
        for min_confidence in confidences:
            for min_lift in lifts:
                rules = gerar_regras_contexto_para_alvo(
                    df_onehot[_colunas_para_mineracao(df_onehot, alvo)],
                    itemsets,
                    consequente=alvo,
                    min_confidence=min_confidence,
                    min_lift=min_lift,
                    min_count_abs=MIN_COUNT_ABS,
                )
                rules = podar_regras_nao_minimais(rules)
                rows.append({
                    "min_support": min_support,
                    "min_confidence": min_confidence,
                    "min_lift": min_lift,
                    "n_regras": len(rules),
                    "lift_max": round(rules["lift"].max(), 4) if not rules.empty else 0,
                    "confidence_max": round(rules["confidence"].max(), 4) if not rules.empty else 0,
                })
    return pd.DataFrame(rows)


def regras_estabilidade_principal(df_onehot, df_meta):
    return minerar_por_ano(
        df_onehot,
        df_meta,
        alvo=ALVO_PRINCIPAL,
        anos=ANOS_COMPLETOS,
        janela_jan_abr=False,
    )


def regras_estabilidade_jan_abr(df_onehot, df_meta):
    return minerar_por_ano(
        df_onehot,
        df_meta,
        alvo=ALVO_PRINCIPAL,
        anos=ANOS_COMPLETOS + [2026],
        janela_jan_abr=True,
    )
