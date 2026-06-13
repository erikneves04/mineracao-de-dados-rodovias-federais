#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Executa o pipeline redesenhado (Pacote A + MG multi-ano)."""
from __future__ import annotations

import pickle
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import DADOS_DIR, MIN_SUPPORT, PROCESSED_DIR, TABELAS_DIR
from src.data_loading import carregar_anos, resumo_por_ano
from src.evaluation import (
    disclaimer,
    exportar_top_regras_latex,
    resumo_qualidade_regras,
    traduzir_regras,
)
from src.mining import (
    classificar_estabilidade_temporal,
    comparar_uso_solo,
    minerar_por_ano,
    minerar_regras_fatais,
)
from src.preparation import preparar_pipeline


def main():
    print("=" * 60)
    print("Pipeline Grupo 18 - Regras contexto -> Fatal (Pacote A)")
    print("=" * 60)

    df, _mapa = carregar_anos(ignorar_ausentes=True)
    print("\nResumo por ano:")
    print(resumo_por_ano(df).to_string(index=False))

    df_onehot, df_meta, _info = preparar_pipeline(df)

    itemsets, rules_all, rules_fatal = minerar_regras_fatais(
        df_onehot, min_support=MIN_SUPPORT
    )
    rules_fatal = traduzir_regras(rules_fatal)

    print(f"\n[OK] Itemsets: {len(itemsets):,} | Regras totais: {len(rules_all):,}")
    print(f"[OK] Regras contexto->Fatal: {len(rules_fatal):,}")
    qual = resumo_qualidade_regras(rules_fatal)
    print(f"     Lift max: {qual.get('lift_max')} | mediano: {qual.get('lift_mediano')}")

    if len(rules_fatal) > 0:
        print("\nTop 10 regras contexto -> Fatal:")
        for i, row in rules_fatal.head(10).iterrows():
            print(f"  {i+1}. {row['explicacao_natural']}")

    rules_por_ano = minerar_por_ano(df_onehot, df_meta, min_support=MIN_SUPPORT)
    estabilidade = classificar_estabilidade_temporal(rules_por_ano)
    n_estaveis = (estabilidade["status"] == "estavel").sum() if not estabilidade.empty else 0
    print(f"\n[OK] Estabilidade temporal: {n_estaveis} regras estaveis")

    rules_estratos = comparar_uso_solo(df_onehot, df_meta)
    for estrato, rules in rules_estratos.items():
        print(f"[OK] Estrato {estrato}: {len(rules)} regras contexto->Fatal")

    itemsets.to_csv(DADOS_DIR / "itemsets_frequentes.csv", index=False)
    rules_all.to_csv(DADOS_DIR / "regras_completas.csv", index=False)
    rules_fatal.to_csv(DADOS_DIR / "regras_contexto_fatal.csv", index=False)
    rules_fatal.head(20).to_csv(TABELAS_DIR / "top20_regras_contexto_fatal.csv", index=False)
    traduzir_regras(rules_fatal).head(15).to_csv(
        TABELAS_DIR / "top15_regras_traduzidas.csv", index=False
    )
    if not estabilidade.empty:
        estabilidade.to_csv(TABELAS_DIR / "regras_estabilidade_temporal.csv", index=False)
    exportar_top_regras_latex(rules_fatal, TABELAS_DIR / "regras_top15_latex.tex")

    with open(PROCESSED_DIR / "rules_por_ano.pkl", "wb") as f:
        pickle.dump(rules_por_ano, f)
    rules_fatal.to_pickle(PROCESSED_DIR / "rules_fatal.pkl")

    print("\n" + disclaimer())
    print("\n[OK] Pipeline concluido.")


if __name__ == "__main__":
    main()
