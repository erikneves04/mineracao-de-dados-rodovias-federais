# -*- coding: utf-8 -*-
"""Central pipeline configuration (Package A + MG multi-year)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"
OUTPUT_DIR = ROOT / "outputs"
FIGURAS_DIR = OUTPUT_DIR / "figuras"
DADOS_DIR = OUTPUT_DIR / "dados"
TABELAS_DIR = OUTPUT_DIR / "tabelas"

for _d in (PROCESSED_DIR, FIGURAS_DIR, DADOS_DIR, TABELAS_DIR):
    _d.mkdir(parents=True, exist_ok=True)

ANOS_OCORRENCIA = [2023, 2024, 2025, 2026]
FILTRO_UF = "MG"
SEP = ";"
ENCODING = "latin-1"

PADROES_ARQUIVO_OCORRENCIA = [
    "datatran{ano}.csv",
    "datatran{ano}_agrupados_por_ocorrencia.csv",
    "acidentes{ano}_agrupados_por_ocorrencia.csv",
]

COLUNAS_CONTEXTO = [
    "condicao_metereologica",
    "tipo_pista",
    "tracado_via",
    "uso_solo",
    "causa_acidente",
    "tipo_acidente",
    "fase_dia",
    "fim_de_semana",
]

ITEM_ALVO_FATAL = "desfecho_Fatal"
ITEM_ALVO_FERIDO = "desfecho_Ferido"
PREFIXO_CONTEXTO = "ctx_"

MIN_FREQ_ITEM = 0.005
MAX_FREQ_ITEM = 0.99

MIN_SUPPORT = 0.005
MIN_CONFIDENCE = 0.5
MIN_LIFT = 1.05
MIN_COUNT_ABS = 15
MAX_ANTECEDENTES = 3

THRESHOLD_ESTAVEL = 0.5
THRESHOLD_TRANSITORIO = 0.3

CLASSIF_FERIDOS = "Com V\u00edtimas Feridas"
CLASSIF_FATAIS = "Com V\u00edtimas Fatais"
CLASSIF_SEM = "Sem V\u00edtimas"
