#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Executa o pipeline final: regras contexto -> AltaGravidade."""
from __future__ import annotations

import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import (
    ALVO_PRINCIPAL,
    ANOS_COMPLETOS,
    DATA_MAX_2026_ESPERADA,
    DADOS_DIR,
    ITEM_ALVO_BAIXA_GRAVIDADE,
    ITEM_ALVO_FATAL,
    MIN_SUPPORT,
    PROCESSED_DIR,
    TABELAS_DIR,
)
from src.data_loading import carregar_anos, resumo_por_ano
from src.evaluation import (
    disclaimer,
    exportar_top_regras_latex,
    resumo_qualidade_regras,
    traduzir_regras,
)
from src.mining import (
    analise_sensibilidade,
    classificar_estabilidade_temporal,
    comparar_uso_solo,
    minerar_por_ano,
    minerar_regras_alta_gravidade,
    minerar_regras_fatais,
    regras_estabilidade_jan_abr,
    regras_estabilidade_principal,
)
from src.preparation import preparar_pipeline, preparar_transacional


def _support_conjunto(df_onehot, items):
    cols = list(items)
    if not cols:
        return 0.0
    return df_onehot[cols].all(axis=1).mean()


def comparar_contextos_desfechos(df_onehot, rules, n=10):
    rows = []
    p_alta = df_onehot[ALVO_PRINCIPAL].mean()
    p_baixa = df_onehot[ITEM_ALVO_BAIXA_GRAVIDADE].mean()
    p_fatal = df_onehot[ITEM_ALVO_FATAL].mean()
    for _, row in rules.head(n).iterrows():
        ante = row["antecedents"]
        sup_ante = _support_conjunto(df_onehot, ante)
        if sup_ante == 0:
            continue
        sup_alta = _support_conjunto(df_onehot, set(ante) | {ALVO_PRINCIPAL})
        sup_baixa = _support_conjunto(df_onehot, set(ante) | {ITEM_ALVO_BAIXA_GRAVIDADE})
        sup_fatal = _support_conjunto(df_onehot, set(ante) | {ITEM_ALVO_FATAL})
        conf_alta = sup_alta / sup_ante
        conf_baixa = sup_baixa / sup_ante
        conf_fatal = sup_fatal / sup_ante
        rows.append({
            "contexto": row["antecedents_str"],
            "n_contexto": int(round(sup_ante * len(df_onehot))),
            "n_alta": int(round(sup_alta * len(df_onehot))),
            "support_alta": sup_alta,
            "conf_alta": conf_alta,
            "lift_alta": conf_alta / p_alta if p_alta else 0,
            "conf_baixa": conf_baixa,
            "lift_baixa": conf_baixa / p_baixa if p_baixa else 0,
            "conf_fatal": conf_fatal,
            "lift_fatal": conf_fatal / p_fatal if p_fatal else 0,
        })
    return pd.DataFrame(rows)


def avaliar_cobertura_regras(df_onehot, rules, limites=(5, 10, 20)):
    alvo = df_onehot[ALVO_PRINCIPAL].to_numpy(dtype=bool)
    total = len(df_onehot)
    total_alta = int(alvo.sum())
    rows = []
    cortes = [(f"top-{k}", min(k, len(rules))) for k in limites]
    cortes.append(("todas", len(rules)))

    for label, n_rules in cortes:
        if n_rules == 0:
            continue
        coberto = np.zeros(total, dtype=bool)
        for _, row in rules.head(n_rules).iterrows():
            cols = list(row["antecedents"])
            if not cols:
                continue
            coberto |= df_onehot[cols].all(axis=1).to_numpy(dtype=bool)
        n_cobertos = int(coberto.sum())
        n_alta_cobertos = int((coberto & alvo).sum())
        rows.append({
            "conjunto": label,
            "n_regras": n_rules,
            "n_ocorrencias_cobertas": n_cobertos,
            "pct_base_coberta": n_cobertos / total if total else 0,
            "n_alta_cobertas": n_alta_cobertos,
            "pct_alta_coberta": n_alta_cobertos / total_alta if total_alta else 0,
            "precisao_alta_entre_cobertos": n_alta_cobertos / n_cobertos if n_cobertos else 0,
        })
    return pd.DataFrame(rows)


def bootstrap_top_regras(df_onehot, rules, n=5, n_boot=400, seed=18):
    rng = np.random.default_rng(seed)
    target = df_onehot[ALVO_PRINCIPAL].to_numpy(dtype=bool)
    n_total = len(df_onehot)
    rows = []

    for i, (_, row) in enumerate(rules.head(n).iterrows(), start=1):
        cols = list(row["antecedents"])
        if not cols:
            continue
        ante_mask = df_onehot[cols].all(axis=1).to_numpy(dtype=bool)
        confs, lifts = [], []
        for _ in range(n_boot):
            idx = rng.integers(0, n_total, size=n_total)
            ante_b = ante_mask[idx]
            target_b = target[idx]
            denom = int(ante_b.sum())
            base = float(target_b.mean())
            if denom == 0 or base == 0:
                continue
            conf = float((ante_b & target_b).sum() / denom)
            confs.append(conf)
            lifts.append(conf / base)
        if not confs:
            continue
        conf_arr = np.asarray(confs)
        lift_arr = np.asarray(lifts)
        rows.append({
            "rank": i,
            "contexto": row["antecedents_str"],
            "confidence": row["confidence"],
            "lift": row["lift"],
            "confidence_boot_mean": float(conf_arr.mean()),
            "confidence_ic95_low": float(np.quantile(conf_arr, 0.025)),
            "confidence_ic95_high": float(np.quantile(conf_arr, 0.975)),
            "lift_boot_mean": float(lift_arr.mean()),
            "lift_ic95_low": float(np.quantile(lift_arr, 0.025)),
            "lift_ic95_high": float(np.quantile(lift_arr, 0.975)),
        })
    return pd.DataFrame(rows)


def main():
    print("=" * 60)
    print("Pipeline Grupo 18 - Regras contexto -> AltaGravidade")
    print("=" * 60)

    df, _mapa = carregar_anos(ignorar_ausentes=True)
    data_max = df["data_inversa"].max()
    print("\nResumo por ano:")
    print(resumo_por_ano(df).to_string(index=False))
    print(f"\nJanela dos dados: {df['data_inversa'].min().date()} a {data_max.date()}")
    print(f"2026 parcial esperado ate {DATA_MAX_2026_ESPERADA}")

    resumo_por_ano(df).to_csv(TABELAS_DIR / "resumo_por_ano.csv", index=False)

    df_principal = df[df["ano"].isin(ANOS_COMPLETOS)].copy()
    print(f"\nRecorte principal da mineracao: anos completos {ANOS_COMPLETOS}")
    print(resumo_por_ano(df_principal).to_string(index=False))
    resumo_por_ano(df_principal).to_csv(TABELAS_DIR / "resumo_recorte_principal.csv", index=False)

    df_onehot, df_meta, _info = preparar_pipeline(df_principal)
    _df_prep_validacao, df_onehot_validacao, df_meta_validacao, _info_validacao = preparar_transacional(df)

    itemsets, rules_all, rules_alta = minerar_regras_alta_gravidade(
        df_onehot, min_support=MIN_SUPPORT
    )
    rules_alta = traduzir_regras(rules_alta)

    _, _, rules_fatal = minerar_regras_fatais(df_onehot, min_support=MIN_SUPPORT)
    rules_fatal = traduzir_regras(rules_fatal)

    print(f"\n[OK] Itemsets: {len(itemsets):,} | Regras totais: {len(rules_all):,}")
    print(f"[OK] Regras contexto->AltaGravidade: {len(rules_alta):,}")
    print(f"[OK] Regras contexto->Fatal (robustez): {len(rules_fatal):,}")
    qual = resumo_qualidade_regras(rules_alta)
    print(f"     Lift max: {qual.get('lift_max')} | mediano: {qual.get('lift_mediano')}")

    if len(rules_alta) > 0:
        print("\nTop 10 regras contexto -> AltaGravidade:")
        for i, row in rules_alta.head(10).iterrows():
            print(f"  {i+1}. {row['explicacao_natural']}")

    rules_por_ano = regras_estabilidade_principal(df_onehot, df_meta)
    estabilidade = classificar_estabilidade_temporal(rules_por_ano)
    n_estaveis = (estabilidade["status"] == "estavel").sum() if not estabilidade.empty else 0
    print(f"\n[OK] Estabilidade temporal ({ANOS_COMPLETOS}): {n_estaveis} regras estaveis")

    rules_jan_abr = regras_estabilidade_jan_abr(df_onehot_validacao, df_meta_validacao)
    estabilidade_jan_abr = classificar_estabilidade_temporal(rules_jan_abr)
    n_estaveis_jan_abr = (estabilidade_jan_abr["status"] == "estavel").sum() if not estabilidade_jan_abr.empty else 0
    print(f"[OK] Robustez Jan-Abr 2023-2026: {n_estaveis_jan_abr} regras estaveis")

    rules_estratos = comparar_uso_solo(df_onehot, df_meta)
    for estrato, rules in rules_estratos.items():
        print(f"[OK] Estrato {estrato}: {len(rules)} regras contexto->AltaGravidade")

    sensibilidade = analise_sensibilidade(df_onehot)
    comparacao = comparar_contextos_desfechos(df_onehot, rules_alta)
    cobertura = avaliar_cobertura_regras(df_onehot, rules_alta)
    incerteza = bootstrap_top_regras(df_onehot, rules_alta)
    estratos_export = pd.concat(rules_estratos.values(), ignore_index=True) if rules_estratos else pd.DataFrame()

    itemsets.to_csv(DADOS_DIR / "itemsets_frequentes.csv", index=False)
    rules_all.to_csv(DADOS_DIR / "regras_completas.csv", index=False)
    rules_alta.to_csv(DADOS_DIR / "regras_contexto_alta_gravidade.csv", index=False)
    rules_fatal.to_csv(DADOS_DIR / "regras_contexto_fatal.csv", index=False)
    rules_alta.head(20).to_csv(TABELAS_DIR / "top20_regras_alta_gravidade.csv", index=False)
    rules_alta.head(20).to_csv(TABELAS_DIR / "top_regras_alta_gravidade.csv", index=False)
    rules_fatal.head(20).to_csv(TABELAS_DIR / "top20_regras_contexto_fatal.csv", index=False)
    rules_alta.head(15).to_csv(
        TABELAS_DIR / "top15_regras_traduzidas.csv", index=False
    )
    sensibilidade.to_csv(TABELAS_DIR / "sensibilidade_parametros.csv", index=False)
    comparacao.to_csv(TABELAS_DIR / "comparacao_alta_baixa_fatal.csv", index=False)
    cobertura.to_csv(TABELAS_DIR / "cobertura_regras.csv", index=False)
    incerteza.to_csv(TABELAS_DIR / "bootstrap_top_regras.csv", index=False)
    if not estratos_export.empty:
        estratos_export.to_csv(TABELAS_DIR / "estratos_uso_solo.csv", index=False)
    if not estabilidade.empty:
        estabilidade.to_csv(TABELAS_DIR / "estabilidade_alta_gravidade.csv", index=False)
        estabilidade.to_csv(TABELAS_DIR / "regras_estabilidade_temporal.csv", index=False)
    if not estabilidade_jan_abr.empty:
        estabilidade_jan_abr.to_csv(TABELAS_DIR / "estabilidade_jan_abr.csv", index=False)
    exportar_top_regras_latex(rules_alta, TABELAS_DIR / "regras_top15_latex.tex")

    with open(PROCESSED_DIR / "rules_por_ano.pkl", "wb") as f:
        pickle.dump(rules_por_ano, f)
    with open(PROCESSED_DIR / "rules_jan_abr.pkl", "wb") as f:
        pickle.dump(rules_jan_abr, f)
    rules_alta.to_pickle(PROCESSED_DIR / "rules_alta_gravidade.pkl")
    rules_fatal.to_pickle(PROCESSED_DIR / "rules_fatal.pkl")

    print("\n" + disclaimer())
    print("\n[OK] Pipeline concluido.")


if __name__ == "__main__":
    main()
