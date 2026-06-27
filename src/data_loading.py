# -*- coding: utf-8 -*-
"""Multi-year PRF data loading and harmonization."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.config import (
    ANOS_OCORRENCIA,
    CLASSIF_FATAIS,
    CLASSIF_FERIDOS,
    CLASSIF_SEM,
    DATA_DIR,
    ENCODING,
    FILTRO_UF,
    PADROES_ARQUIVO_OCORRENCIA,
    SEP,
)

COLUNAS_ESPERADAS = [
    "id", "data_inversa", "dia_semana", "horario", "uf", "br", "km", "municipio",
    "causa_acidente", "tipo_acidente", "classificacao_acidente", "fase_dia",
    "sentido_via", "condicao_metereologica", "tipo_pista", "tracado_via", "uso_solo",
    "pessoas", "mortos", "feridos_leves", "feridos_graves", "ilesos", "ignorados",
    "feridos", "veiculos", "latitude", "longitude", "regional", "delegacia", "uop",
]


def resolver_arquivo_ocorrencia(ano: int, data_dir: Path = DATA_DIR) -> Path | None:
    for padrao in PADROES_ARQUIVO_OCORRENCIA:
        path = data_dir / padrao.format(ano=ano)
        if path.exists():
            return path
    return None


def listar_anos_disponiveis(anos=None, data_dir: Path = DATA_DIR) -> dict[int, Path]:
    anos = anos or ANOS_OCORRENCIA
    out = {}
    for ano in anos:
        path = resolver_arquivo_ocorrencia(ano, data_dir)
        if path is not None:
            out[ano] = path
    return out


def _normalizar_texto(valor) -> str:
    if pd.isna(valor):
        return "Nao Informado"
    texto = str(valor).strip()
    if texto.upper() in ("NA", "NAN", ""):
        return "Nao Informado"
    return texto


def harmonizar_dataframe(df: pd.DataFrame, ano: int) -> pd.DataFrame:
    out = df.copy()
    out.columns = [c.strip().strip('"') for c in out.columns]
    for col in COLUNAS_ESPERADAS:
        if col not in out.columns:
            out[col] = pd.NA
    out = out[COLUNAS_ESPERADAS].copy()
    out["ano"] = ano

    cat_cols = [
        "dia_semana", "causa_acidente", "tipo_acidente", "classificacao_acidente",
        "fase_dia", "sentido_via", "condicao_metereologica", "tipo_pista",
        "tracado_via", "uso_solo", "municipio", "uf",
    ]
    for col in cat_cols:
        out[col] = out[col].map(_normalizar_texto)

    mapa = {
        "Com Vitimas Feridas": CLASSIF_FERIDOS,
        "Com Vitimas Fatais": CLASSIF_FATAIS,
        "Sem Vitimas": CLASSIF_SEM,
    }
    out["classificacao_acidente"] = out["classificacao_acidente"].replace(mapa)
    out["data_inversa"] = pd.to_datetime(out["data_inversa"], errors="coerce")

    num_cols = [
        "br", "km", "pessoas", "mortos", "feridos_leves", "feridos_graves",
        "ilesos", "ignorados", "feridos", "veiculos", "latitude", "longitude",
    ]
    for col in num_cols:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")

    return out


def carregar_ano(ano: int, filtro_uf: str | None = FILTRO_UF, data_dir: Path = DATA_DIR):
    path = resolver_arquivo_ocorrencia(ano, data_dir)
    if path is None:
        raise FileNotFoundError(f"No occurrence file for year {ano} in {data_dir}")
    df = pd.read_csv(path, sep=SEP, encoding=ENCODING, low_memory=False)
    df = harmonizar_dataframe(df, ano)
    if filtro_uf:
        df = df[df["uf"] == filtro_uf].copy()
    df["arquivo_origem"] = path.name
    return df


def carregar_anos(anos=None, filtro_uf: str | None = FILTRO_UF, data_dir: Path = DATA_DIR, ignorar_ausentes=True):
    anos = anos or ANOS_OCORRENCIA
    mapa = listar_anos_disponiveis(anos, data_dir)
    if not mapa:
        raise FileNotFoundError(f"No files for years {anos}. See data/README.md")
    ausentes = [a for a in anos if a not in mapa]
    if ausentes and not ignorar_ausentes:
        raise FileNotFoundError(f"Missing years: {ausentes}")
    frames = [carregar_ano(a, filtro_uf, data_dir) for a in sorted(mapa)]
    df = pd.concat(frames, ignore_index=True).drop_duplicates(subset=["id", "ano"], keep="first")
    if ausentes:
        print(f"[AVISO] Anos nao encontrados: {ausentes}")
    print(f"[OK] Anos carregados: {sorted(mapa.keys())} | Registros: {len(df):,}")
    return df, mapa


def resumo_por_ano(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for ano, g in df.groupby("ano"):
        com_vitimas = g["classificacao_acidente"] != CLASSIF_SEM
        mortos = pd.to_numeric(g["mortos"], errors="coerce").fillna(0)
        feridos_graves = pd.to_numeric(g["feridos_graves"], errors="coerce").fillna(0)
        alta_gravidade = (mortos > 0) | (feridos_graves > 0)
        rows.append({
            "ano": ano,
            "n_ocorrencias": len(g),
            "n_com_vitimas": int(com_vitimas.sum()),
            "n_alta_gravidade": int(alta_gravidade.sum()),
            "n_fatais": int((g["classificacao_acidente"] == CLASSIF_FATAIS).sum()),
            "pct_fatais": round((g["classificacao_acidente"] == CLASSIF_FATAIS).mean() * 100, 2),
            "pct_com_vitimas": round(com_vitimas.mean() * 100, 2),
            "pct_alta_gravidade_com_vitimas": round(alta_gravidade[com_vitimas].mean() * 100, 2),
            "data_min": g["data_inversa"].min(),
            "data_max": g["data_inversa"].max(),
            "arquivo": g["arquivo_origem"].iloc[0] if "arquivo_origem" in g else "",
        })
    return pd.DataFrame(rows).sort_values("ano")
