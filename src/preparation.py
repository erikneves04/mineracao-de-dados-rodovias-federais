# -*- coding: utf-8 -*-
"""Transactional preparation - Package A (context + target)."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.config import (
    CLASSIF_FATAIS,
    CLASSIF_FERIDOS,
    CLASSIF_SEM,
    COLUNAS_CONTEXTO,
    ITEM_ALVO_FATAL,
    ITEM_ALVO_FERIDO,
    MAX_FREQ_ITEM,
    MIN_FREQ_ITEM,
    PREFIXO_CONTEXTO,
    PROCESSED_DIR,
)

DIAS_FIM_SEMANA = {"s\u00e1bado", "sabado", "domingo"}


def criar_fim_de_semana(df: pd.DataFrame) -> pd.Series:
    dia = df["dia_semana"].str.lower().str.strip()
    return dia.isin(DIAS_FIM_SEMANA).map({True: "Sim", False: "N\u00e3o"})


def criar_desfecho(df: pd.DataFrame) -> pd.Series:
    return df["classificacao_acidente"].map({CLASSIF_FATAIS: "Fatal", CLASSIF_FERIDOS: "Ferido"})


def limpar_categoricas(df: pd.DataFrame, colunas: list[str]) -> pd.DataFrame:
    out = df.copy()
    for col in colunas:
        if col in out.columns:
            out[col] = out[col].astype(str).str.strip()
            out[col] = out[col].replace({"nan": "Nao Informado", "NA": "Nao Informado"})
    return out


def subset_com_vitimas(df: pd.DataFrame) -> pd.DataFrame:
    return df.loc[df["classificacao_acidente"] != CLASSIF_SEM].dropna(subset=["classificacao_acidente"]).copy()


def engenharia_atributos(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["fim_de_semana"] = criar_fim_de_semana(out)
    out["desfecho"] = criar_desfecho(out)
    return out.dropna(subset=["desfecho"])


def _item_name(col: str, val: str, prefixo: str = "") -> str:
    return f"{prefixo}{col}_{str(val).replace(' ', '_')}"


def construir_transacional(df, colunas_contexto=None, min_freq=MIN_FREQ_ITEM, max_freq=MAX_FREQ_ITEM):
    colunas_contexto = colunas_contexto or COLUNAS_CONTEXTO
    registros, meta_rows = [], []

    for _, row in df.iterrows():
        items = []
        for col in colunas_contexto:
            val = row.get(col)
            if pd.notna(val) and str(val) not in ("Nao Informado", "nan"):
                items.append(_item_name(col, val, PREFIXO_CONTEXTO))
        items.append(ITEM_ALVO_FATAL if row["desfecho"] == "Fatal" else ITEM_ALVO_FERIDO)
        registros.append(items)
        meta_rows.append({"id": row.get("id"), "ano": row.get("ano"), "desfecho": row["desfecho"], "uso_solo": row.get("uso_solo")})

    all_items = sorted({it for row in registros for it in row})
    df_onehot = pd.DataFrame(False, index=range(len(registros)), columns=all_items)
    for i, items in enumerate(registros):
        for it in items:
            df_onehot.at[i, it] = True

    df_meta = pd.DataFrame(meta_rows)
    freq = df_onehot.mean()
    cols_keep = freq.index[(freq >= min_freq) & (freq <= max_freq)].tolist()
    for alvo in (ITEM_ALVO_FATAL, ITEM_ALVO_FERIDO):
        if alvo in df_onehot.columns and alvo not in cols_keep:
            cols_keep.append(alvo)

    info = {
        "n_registros": len(df),
        "n_itens_total": len(all_items),
        "n_itens_filtrado": len(cols_keep),
        "min_freq": min_freq,
        "max_freq": max_freq,
        "colunas_contexto": colunas_contexto,
        "pct_fatal": round((df_meta["desfecho"] == "Fatal").mean() * 100, 2),
        "pct_ferido": round((df_meta["desfecho"] == "Ferido").mean() * 100, 2),
        "design": "pacote_a_contexto_para_desfecho",
    }
    return df_onehot[cols_keep].copy(), df_meta, info


def preparar_pipeline(df: pd.DataFrame, processed_dir: Path = PROCESSED_DIR):
    cols_limpeza = COLUNAS_CONTEXTO + ["classificacao_acidente", "dia_semana"]
    df_prep = engenharia_atributos(subset_com_vitimas(limpar_categoricas(df, cols_limpeza)))
    df_onehot, df_meta, info = construir_transacional(df_prep)

    df_prep.to_pickle(processed_dir / "df_limpo.pkl")
    df_onehot.to_pickle(processed_dir / "transacional.pkl")
    df_meta.to_pickle(processed_dir / "transacional_meta.pkl")
    df_onehot.to_pickle(processed_dir / "transacional_contexto.pkl")

    info["anos"] = sorted(df_prep["ano"].dropna().unique().tolist()) if "ano" in df_prep else []
    with open(processed_dir / "preparacao_metadata.json", "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=2)

    print(f"[OK] Preparacao: {info['n_registros']:,} transacoes | Itens: {info['n_itens_total']} -> {info['n_itens_filtrado']}")
    print(f"     Fatal: {info['pct_fatal']}% | Ferido: {info['pct_ferido']}%")
    return df_onehot, df_meta, info
