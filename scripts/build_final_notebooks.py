# -*- coding: utf-8 -*-
"""Generate final notebooks for the high-severity project."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NB_DIR = ROOT / "notebooks"


def md(text):
    return {"cell_type": "markdown", "metadata": {}, "source": text.strip().splitlines(keepends=True)}


def code(text):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": text.strip().splitlines(keepends=True),
    }


def nb(cells):
    return {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "pygments_lexer": "ipython3"},
        },
        "cells": cells,
    }


SETUP = """
import sys
from pathlib import Path

ROOT = Path.cwd()
if not (ROOT / "src").exists():
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT))

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from src.config import (
    ANOS_COMPLETOS,
    COLUNAS_CONTEXTO,
    DADOS_DIR,
    FIGURAS_DIR,
    MIN_SUPPORT,
    PROCESSED_DIR,
    TABELAS_DIR,
)

plt.rcParams["figure.figsize"] = (11, 5)
sns.set_style("whitegrid")
""".strip()


def notebook_01():
    return nb([
        md("# Fase 1 - Setup e Carregamento\n\nCarrega dados PRF de MG para 2023-2025 completos e 2026 parcial."),
        code(SETUP),
        code("""
from src.data_loading import carregar_anos, resumo_por_ano

df, mapa = carregar_anos(ignorar_ausentes=True)
display(resumo_por_ano(df))
print(f"Registros MG: {len(df):,}")
print(f"Janela: {df['data_inversa'].min().date()} a {df['data_inversa'].max().date()}")
"""),
    ])


def notebook_02():
    return nb([
        md("# Fase 2 - Analise Exploratoria\n\nDefine alta gravidade e avalia contexto contra o alvo nos anos completos."),
        code(SETUP),
        code("""
from scipy.stats import chi2_contingency
from src.data_loading import carregar_anos
from src.preparation import criar_desfecho_alta_gravidade, subset_com_vitimas

df, _ = carregar_anos(ignorar_ausentes=True)
df = df[df["ano"].isin(ANOS_COMPLETOS)].copy()
df_cv = subset_com_vitimas(df).copy()
df_cv["desfecho_alta_gravidade"] = criar_desfecho_alta_gravidade(df_cv)
print(df_cv["desfecho_alta_gravidade"].value_counts())
print((df_cv["desfecho_alta_gravidade"].value_counts(normalize=True) * 100).round(2))
"""),
        code("""
def cramers_v(x, y):
    ct = pd.crosstab(x, y)
    chi2 = chi2_contingency(ct)[0]
    n = ct.values.sum()
    r, k = ct.shape
    return ((chi2 / n) / (min(r, k) - 1)) ** 0.5 if min(r, k) > 1 else 0

cv = pd.DataFrame([
    {"variavel": col, "cramers_v": cramers_v(df_cv[col], df_cv["desfecho_alta_gravidade"])}
    for col in COLUNAS_CONTEXTO
]).sort_values("cramers_v", ascending=False)
display(cv)
"""),
        md("Hipoteses H1-H5: noite/rural, fim de semana, colisao frontal/atropelamento, clima e heterogeneidade urbano-rural."),
    ])


def notebook_03():
    return nb([
        md("# Fase 3 - Preparacao dos Dados\n\nMatriz transacional com itens `ctx_*` e alvo principal `desfecho_AltaGravidade`."),
        code(SETUP),
        code("""
from src.data_loading import carregar_anos
from src.preparation import preparar_pipeline

df, _ = carregar_anos(ignorar_ausentes=True)
df = df[df["ano"].isin(ANOS_COMPLETOS)].copy()
df_onehot, df_meta, info = preparar_pipeline(df)
display(pd.Series(info))
print(df_onehot.shape)
print([c for c in df_onehot.columns if c.startswith("desfecho_")])
"""),
    ])


def notebook_04():
    return nb([
        md("# Fase 4 - Modelagem\n\nFP-Growth restrito a regras `contexto -> AltaGravidade`."),
        code(SETUP),
        code("""
from src.evaluation import traduzir_regras
from src.mining import (
    analise_sensibilidade,
    classificar_estabilidade_temporal,
    comparar_uso_solo,
    minerar_regras_alta_gravidade,
    regras_estabilidade_jan_abr,
    regras_estabilidade_principal,
)

df_onehot = pd.read_pickle(PROCESSED_DIR / "transacional.pkl")
df_meta = pd.read_pickle(PROCESSED_DIR / "transacional_meta.pkl")
itemsets, rules_all, rules_alta = minerar_regras_alta_gravidade(df_onehot, min_support=MIN_SUPPORT)
rules_alta = traduzir_regras(rules_alta)
print(f"Itemsets: {len(itemsets):,} | Regras alta gravidade: {len(rules_alta):,}")
display(rules_alta[["antecedents_str", "support", "confidence", "lift", "explicacao_natural"]].head(15))
"""),
        code("""
rules_por_ano = regras_estabilidade_principal(df_onehot, df_meta)
estabilidade = classificar_estabilidade_temporal(rules_por_ano)
print(estabilidade["status"].value_counts())
display(estabilidade.head(12))
"""),
        code("""
for estrato, rules in comparar_uso_solo(df_onehot, df_meta).items():
    print(estrato, len(rules))
    display(rules[["antecedents_str", "confidence", "lift"]].head(5))
"""),
    ])


def notebook_05():
    return nb([
        md("# Fase 5 - Avaliacao e IA Responsavel\n\nExplicabilidade e Monitoramento/Avaliacao."),
        code(SETUP),
        code("""
from src.evaluation import disclaimer

rules = pd.read_csv(DADOS_DIR / "regras_contexto_alta_gravidade.csv")
display(rules[["antecedents_str", "support", "confidence", "lift", "explicacao_natural"]].head(10))
print(disclaimer())
"""),
        code("""
est = pd.read_csv(TABELAS_DIR / "estabilidade_alta_gravidade.csv")
print("Estaveis:", (est["status"] == "estavel").sum())
print("Presentes nos 3 anos completos:", ((est["status"] == "estavel") & (est["n_anos_presente"] == 3)).sum())
display(est.head(10))
"""),
        code("""
sens = pd.read_csv(TABELAS_DIR / "sensibilidade_parametros.csv")
display(sens)
display(pd.read_csv(TABELAS_DIR / "cobertura_regras.csv"))
display(pd.read_csv(TABELAS_DIR / "bootstrap_top_regras.csv"))
"""),
    ])


def notebook_06():
    return nb([
        md("# Fase 6 - Visualizacao e Consolidacao\n\nGaleria dos principais artefatos finais."),
        code(SETUP),
        code("""
from IPython.display import Image, display

for name in [
    "01_distribuicao_desfecho.png",
    "02_cramers_v_desfecho.png",
    "05_scatter_suporte_confianca_alta.png",
    "09_comparacao_alta_baixa_fatal.png",
    "08_mineracao_por_ano.png",
    "07_estratos_uso_solo.png",
]:
    path = FIGURAS_DIR / name
    print(name, path.exists())
    if path.exists():
        display(Image(filename=str(path)))
"""),
        code("""
display(pd.read_csv(TABELAS_DIR / "top_regras_alta_gravidade.csv").head(12))
display(pd.read_csv(TABELAS_DIR / "comparacao_alta_baixa_fatal.csv").head(8))
"""),
    ])


def notebook_07():
    return nb([
        md("# Fase 7 - Comparacao Alta, Baixa e Fatal\n\nNotebook complementar para mostrar que os principais contextos de alta gravidade nao descrevem apenas acidentes comuns."),
        code(SETUP),
        code("""
comp = pd.read_csv(TABELAS_DIR / "comparacao_alta_baixa_fatal.csv")
display(comp.head(10))
"""),
        code("""
fig, ax = plt.subplots(figsize=(11, 6))
plot_df = comp.head(8).iloc[::-1]
y = range(len(plot_df))
ax.barh([i + 0.22 for i in y], plot_df["lift_alta"], height=0.22, label="Alta gravidade")
ax.barh(y, plot_df["lift_baixa"], height=0.22, label="Baixa gravidade")
ax.barh([i - 0.22 for i in y], plot_df["lift_fatal"], height=0.22, label="Fatal")
ax.axvline(1, color="black", linestyle="--")
ax.set_yticks(list(y))
ax.set_yticklabels(plot_df["contexto"].str.replace("ctx_", "", regex=False).str[:70])
ax.set_xlabel("Lift")
ax.set_title("Mesmos contextos contra alta, baixa gravidade e fatalidade")
ax.legend()
plt.show()
"""),
        md("Interpretacao: os contextos top têm lift alto para alta gravidade e fatalidade, mas lift abaixo de 1 para baixa gravidade. Isso indica especificidade de severidade, nao apenas frequencia geral de acidentes."),
    ])


def main():
    NB_DIR.mkdir(parents=True, exist_ok=True)
    notebooks = [
        ("01_setup_e_carregamento.ipynb", notebook_01),
        ("02_analise_exploratoria.ipynb", notebook_02),
        ("03_preparacao_dados.ipynb", notebook_03),
        ("04_modelagem.ipynb", notebook_04),
        ("05_avaliacao_ia_responsavel.ipynb", notebook_05),
        ("06_visualizacao_resultados.ipynb", notebook_06),
        ("07_comparacao_fatal_vs_nao_fatal.ipynb", notebook_07),
    ]
    for name, fn in notebooks:
        path = NB_DIR / name
        path.write_text(json.dumps(fn(), ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"[OK] {path.name}")


if __name__ == "__main__":
    main()
