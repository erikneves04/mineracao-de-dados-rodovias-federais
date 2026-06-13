# -*- coding: utf-8 -*-
"""Gera notebooks finais (Pacote A + multi-ano MG) delegando logica ao src/."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NB_DIR = ROOT / "notebooks"


def md(text: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": text.strip().splitlines(keepends=True)}


def code(text: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": text.strip().splitlines(keepends=True),
    }


def nb(cells: list) -> dict:
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
    ANOS_OCORRENCIA,
    COLUNAS_CONTEXTO,
    DATA_DIR,
    DADOS_DIR,
    FIGURAS_DIR,
    FILTRO_UF,
    MIN_SUPPORT,
    PROCESSED_DIR,
    TABELAS_DIR,
)

plt.rcParams["figure.figsize"] = (11, 5)
sns.set_style("whitegrid")
FIGURAS_DIR.mkdir(parents=True, exist_ok=True)
""".strip()


def notebook_01() -> dict:
    return nb([
        md("# Fase 1 - Setup e Carregamento dos Dados\n\n"
           "**Grupo 18 - Mineracao de Dados - UFMG**\n\n"
           "Carregamento multi-ano (2023-2026) de ocorrencias da PRF em MG via `src/data_loading.py`.\n"
           "Arquivos em `data/`: `datatran{ano}.csv` (ver `data/README.md`)."),
        code(SETUP),
        md("## 1.1 Anos disponiveis e carregamento"),
        code("""
from src.data_loading import carregar_anos, listar_anos_disponiveis, resumo_por_ano

mapa = listar_anos_disponiveis()
print("Arquivos encontrados:")
for ano, path in sorted(mapa.items()):
    print(f"  {ano}: {path.name}")

df, mapa_anos = carregar_anos(ignorar_ausentes=True)
print(f"\\nUF filtro: {FILTRO_UF} | Anos: {ANOS_OCORRENCIA}")
print(f"Registros totais: {len(df):,} | Colunas: {len(df.columns)}")
"""),
        md("## 1.2 Resumo por ano"),
        code("""
resumo = resumo_por_ano(df)
display(resumo)

fig, ax = plt.subplots(figsize=(9, 4))
ax.bar(resumo["ano"].astype(str), resumo["n_ocorrencias"], color="#3498db")
ax.set_title("Ocorrencias por ano (MG)")
ax.set_ylabel("N")
fig.tight_layout()
fig.savefig(FIGURAS_DIR / "00_ocorrencias_por_ano.png", dpi=200)
plt.show()
"""),
        md("## 1.3 Qualidade e amostra"),
        code("""
print("Valores ausentes (top 10):")
print(df.isna().sum().sort_values(ascending=False).head(10))
print("\\nClassificacao bruta:")
print(df["classificacao_acidente"].value_counts())
display(df[["id", "ano", "data_inversa", "municipio", "br", "classificacao_acidente", "tipo_acidente"]].head(8))
"""),
        md("## 1.4 Checklist"),
        code("""
for k, v in {
    "Anos carregados": sorted(mapa_anos.keys()),
    "Registros MG": len(df),
    "Arquivos em data/": len(mapa),
    "Pct com vitimas (media)": round(resumo["pct_com_vitimas"].mean(), 1),
}.items():
    print(f"  [OK] {k}: {v}")
"""),
    ])


def notebook_02() -> dict:
    return nb([
        md("# Fase 2 - Analise Exploratoria (EDA)\n\n"
           "MG multi-ano com foco no **Pacote A**:\n"
           "- Distribuicao bruta e alvo `desfecho` (Fatal | Ferido)\n"
           "- Variaveis de contexto (`COLUNAS_CONTEXTO`)\n"
           "- Hipoteses H1-H5 para regras contexto -> Fatal"),
        code(SETUP + """

from src.data_loading import carregar_anos, resumo_por_ano
from src.preparation import criar_desfecho, criar_fim_de_semana, subset_com_vitimas

df, _ = carregar_anos(ignorar_ausentes=True)
resumo = resumo_por_ano(df)
"""),
        md("## 2.1 Visao geral multi-ano"),
        code("""
print(f"Periodo: {df['ano'].min()}-{df['ano'].max()} | Ocorrencias: {len(df):,}")
display(resumo)

fig, axes = plt.subplots(1, 2, figsize=(12, 4))
axes[0].plot(resumo["ano"], resumo["pct_fatais"], marker="o", color="#c0392b")
axes[0].set_title("% fatais por ano")
axes[1].bar(resumo["ano"].astype(str), resumo["pct_com_vitimas"], color="#2980b9")
axes[1].set_title("% com vitimas por ano")
fig.tight_layout()
fig.savefig(FIGURAS_DIR / "02_tendencia_anual.png", dpi=200)
plt.show()
"""),
        md("## 2.2 Classificacao bruta vs. desfecho"),
        code("""
fig, axes = plt.subplots(1, 2, figsize=(12, 4))
df["classificacao_acidente"].value_counts().plot(kind="bar", ax=axes[0], color=["#95a5a6", "#3498db", "#c0392b"])
axes[0].set_title("Todas as ocorrencias")
axes[0].tick_params(axis="x", rotation=20)

df_cv = subset_com_vitimas(df).copy()
df_cv["desfecho"] = criar_desfecho(df_cv)
df_cv["desfecho"].value_counts().plot(kind="bar", ax=axes[1], color=["#c0392b", "#3498db"])
axes[1].set_title("Com vitimas - alvo desfecho")
fig.tight_layout()
fig.savefig(FIGURAS_DIR / "02_classificacao_vs_desfecho.png", dpi=200)
plt.show()

pct_fatal = (df_cv["desfecho"] == "Fatal").mean() * 100
print(f"Base com vitimas: {len(df_cv):,} ({len(df_cv)/len(df)*100:.1f}% do total)")
print(f"Desbalanceamento: Fatal {pct_fatal:.2f}% | Ferido {100-pct_fatal:.2f}%")
"""),
        md("## 2.3 Analise temporal"),
        code("""
df_cv["mes"] = df_cv["data_inversa"].dt.month
df_cv["fim_de_semana"] = criar_fim_de_semana(df_cv)

ct_fase = pd.crosstab(df_cv["fase_dia"], df_cv["desfecho"], normalize="index") * 100
display(ct_fase.sort_values("Fatal", ascending=False).round(1))

fig, ax = plt.subplots(figsize=(10, 4))
ct_fase["Fatal"].sort_values(ascending=True).plot(kind="barh", ax=ax, color="#c0392b")
ax.set_xlabel("% Fatal")
ax.set_title("Taxa de fatalidade por fase do dia")
fig.tight_layout()
fig.savefig(FIGURAS_DIR / "02_fatal_por_fase_dia.png", dpi=200)
plt.show()

mensal = df_cv.groupby(["ano", "mes"]).size().reset_index(name="n")
mensal.pivot(index="mes", columns="ano", values="n").plot(figsize=(10, 4), marker="o")
plt.title("Ocorrencias com vitimas por mes/ano")
fig.tight_layout()
fig.savefig(FIGURAS_DIR / "02_sazonalidade_mensal.png", dpi=200)
plt.show()
"""),
        md("## 2.4 Analise geografica"),
        code("""
fig, axes = plt.subplots(1, 2, figsize=(13, 4))
df_cv["municipio"].value_counts().head(12).sort_values().plot(kind="barh", ax=axes[0], color="#8e44ad")
axes[0].set_title("Top municipios")
df_cv["br"].value_counts().head(10).sort_values().plot(kind="barh", ax=axes[1], color="#16a085")
axes[1].set_title("Top BRs")
fig.tight_layout()
fig.savefig(FIGURAS_DIR / "02_geo_top_mun_br.png", dpi=200)
plt.show()

geo = df_cv.copy()
geo["latitude"] = pd.to_numeric(geo["latitude"], errors="coerce")
geo["longitude"] = pd.to_numeric(geo["longitude"], errors="coerce")

if geo["latitude"].notna().sum() > 100:
    sample = geo.dropna(subset=["latitude", "longitude"]).sample(min(3000, len(geo)), random_state=42)
    fig, ax = plt.subplots(figsize=(7, 6))
    colors = sample["desfecho"].map({"Fatal": "#c0392b", "Ferido": "#3498db"})
    ax.scatter(sample["longitude"].astype(float), sample["latitude"].astype(float), c=colors, alpha=0.35, s=8)
    ax.set_title("Amostra espacial (com vitimas)")
    fig.tight_layout()
    fig.savefig(FIGURAS_DIR / "02_mapa_amostra.png", dpi=200)
    plt.show()
"""),
        md("## 2.5 Variaveis categ?ricas de contexto"),
        code("""
for col in COLUNAS_CONTEXTO:
    ct = pd.crosstab(df_cv[col], df_cv["desfecho"])
    ct["pct_fatal"] = (ct.get("Fatal", 0) / ct.sum(axis=1) * 100).round(1)
    print(f"\\n=== {col} (top 5 % fatal) ===")
    display(ct.sort_values("pct_fatal", ascending=False).head(5))
"""),
        md("## 2.6 Cramer's V (contexto x desfecho)"),
        code("""
from scipy.stats import chi2_contingency

def cramers_v(x, y):
    ct = pd.crosstab(x, y)
    chi2 = chi2_contingency(ct)[0]
    n = ct.sum().sum()
    r, k = ct.shape
    return (chi2 / (n * min(r - 1, k - 1))) ** 0.5

cv_df = pd.DataFrame([
    {"variavel": col, "cramers_v": round(cramers_v(df_cv[col], df_cv["desfecho"]), 3)}
    for col in COLUNAS_CONTEXTO
]).sort_values("cramers_v", ascending=False)
display(cv_df)

fig, ax = plt.subplots(figsize=(8, 4))
cv_df.plot(x="variavel", y="cramers_v", kind="bar", ax=ax, legend=False, color="#e67e22")
ax.tick_params(axis="x", rotation=30)
fig.tight_layout()
fig.savefig(FIGURAS_DIR / "02_cramers_v_desfecho.png", dpi=200)
plt.show()
"""),
        md("## 2.7 Hipoteses H1-H5\n\n"
           "| ID | Hipotese |\n|----|----------|\n"
           "| H1 | Plena Noite + Pista Simples + rural elevam risco de Fatal |\n"
           "| H2 | Fim de semana + noite tem padroes distintos |\n"
           "| H3 | Colisao frontal e atropelamento associam-se a Fatal |\n"
           "| H4 | Meteorologia adversa + pista influenciam desfecho |\n"
           "| H5 | Padroes diferem entre urbano e rural |\n\n"
           "**Excluidos da mineracao:** gravidade_binaria, classificacao_acidente, faixa_horaria, dia_semana."),
        md("## 2.8 Implicacoes para o pipeline"),
        code("""
print("Design Pacote A:")
print("  - Subset: com vitimas")
print("  - Alvo: desfecho_Fatal | desfecho_Ferido")
print("  - Antecedentes: apenas ctx_*")
print(f"  - Colunas: {COLUNAS_CONTEXTO}")
print(f"  - min_support: {MIN_SUPPORT}")
print("\\nProximo: preparar_pipeline() no notebook 03")
"""),
    ])


def notebook_03() -> dict:
    return nb([
        md("# Fase 3 - Preparacao dos Dados (Pacote A)\n\n"
           "Matriz transacional one-hot: subset com vitimas, alvo `desfecho`, itens `ctx_*`."),
        code(SETUP),
        md("## 3.1 Pipeline"),
        code("""
from src.data_loading import carregar_anos
from src.preparation import preparar_pipeline

df_raw, _ = carregar_anos(ignorar_ausentes=True)
df_onehot, df_meta, info = preparar_pipeline(df_raw)
for k, v in info.items():
    print(f"  {k}: {v}")
"""),
        md("## 3.2 Validacao"),
        code("""
ctx_cols = [c for c in df_onehot.columns if c.startswith("ctx_")]
alvo_cols = [c for c in df_onehot.columns if c.startswith("desfecho_")]
proibidos = [c for c in df_onehot.columns if any(x in c for x in ("gravidade", "classificacao", "faixa_horaria"))]
assert not proibidos
print(f"Contexto: {len(ctx_cols)} | Alvo: {alvo_cols} | Transacoes: {len(df_onehot):,}")
display(df_onehot.sum().sort_values(ascending=False).head(12).to_frame("freq_abs"))
"""),
        md("## 3.3 Amostra"),
        code("""
display(df_meta.head(8))
idx = df_onehot[df_onehot["desfecho_Fatal"]].index[0]
print("Itens ativos (exemplo fatal):", df_onehot.columns[df_onehot.loc[idx]].tolist())
"""),
        md("## 3.4 Artefatos"),
        code("""
for p in [PROCESSED_DIR / "df_limpo.pkl", PROCESSED_DIR / "transacional.pkl",
          PROCESSED_DIR / "transacional_meta.pkl", PROCESSED_DIR / "preparacao_metadata.json"]:
    print(f"  {'[OK]' if p.exists() else '[--]'} {p.relative_to(ROOT)}")
"""),
    ])


def notebook_04() -> dict:
    return nb([
        md("# Fase 4 - Modelagem (FP-Growth restrito)\n\n"
           "Regras **contexto -> desfecho_Fatal** via `src/mining.py`.\n\n"
           "> `association_rules` tende a colocar Fatal no antecedente; "
           "usamos `gerar_regras_contexto_para_fatal()` a partir dos itemsets."),
        code(SETUP + """

import pickle
from src.mining import (
    classificar_estabilidade_temporal,
    comparar_uso_solo,
    minerar_por_ano,
    minerar_regras_fatais,
)
from src.evaluation import resumo_qualidade_regras, traduzir_regras
"""),
        md("## 4.1 Carregamento"),
        code("""
df_onehot = pd.read_pickle(PROCESSED_DIR / "transacional.pkl")
df_meta = pd.read_pickle(PROCESSED_DIR / "transacional_meta.pkl")
print(f"Matriz: {df_onehot.shape}")
"""),
        md("## 4.2 Mineracao contexto -> Fatal"),
        code("""
itemsets, rules_all, rules_fatal = minerar_regras_fatais(df_onehot, min_support=MIN_SUPPORT)
rules_fatal = traduzir_regras(rules_fatal)
print(f"Itemsets: {len(itemsets):,} | Regras contexto->Fatal: {len(rules_fatal):,}")
print(resumo_qualidade_regras(rules_fatal))
if len(rules_fatal):
    display(rules_fatal[["antecedents_str", "support", "confidence", "lift", "explicacao_natural"]].head(15))
"""),
        md("## 4.3 Estabilidade temporal"),
        code("""
rules_por_ano = minerar_por_ano(df_onehot, df_meta, min_support=MIN_SUPPORT)
estabilidade = classificar_estabilidade_temporal(rules_por_ano)
print("Regras por ano:", {k: len(v) for k, v in rules_por_ano.items()})
if not estabilidade.empty:
    print(estabilidade["status"].value_counts())
    display(estabilidade.head(12))
with open(PROCESSED_DIR / "rules_por_ano.pkl", "wb") as f:
    pickle.dump(rules_por_ano, f)
"""),
        md("## 4.4 Estratos urbano vs. rural (H5)"),
        code("""
for estrato, rules in comparar_uso_solo(df_onehot, df_meta).items():
    print(f"\\n=== {estrato.upper()} ({len(rules)} regras) ===")
    if len(rules):
        display(rules[["antecedents_str", "lift", "confidence"]].head(5))
"""),
        md("## 4.5 Exportacao"),
        code("""
itemsets.to_csv(DADOS_DIR / "itemsets_frequentes.csv", index=False)
rules_all.to_csv(DADOS_DIR / "regras_completas.csv", index=False)
rules_fatal.to_csv(DADOS_DIR / "regras_contexto_fatal.csv", index=False)
rules_fatal.head(20).to_csv(TABELAS_DIR / "top20_regras_contexto_fatal.csv", index=False)
if not estabilidade.empty:
    estabilidade.to_csv(TABELAS_DIR / "regras_estabilidade_temporal.csv", index=False)
rules_fatal.to_pickle(PROCESSED_DIR / "rules_fatal.pkl")
print("[OK] Artefatos exportados")
"""),
    ])


def notebook_05() -> dict:
    return nb([
        md("# Fase 5 - Avaliacao e IA Responsavel\n\n"
           "Explicabilidade (traducao NL) e Monitoramento (estabilidade temporal)."),
        code(SETUP + """
from src.evaluation import disclaimer, exportar_top_regras_latex, resumo_qualidade_regras, traduzir_regras
"""),
        md("## 5.1 Regras"),
        code("""
rules = pd.read_csv(DADOS_DIR / "regras_contexto_fatal.csv")
for col in ("lift", "confidence", "support"):
    rules[col] = pd.to_numeric(rules[col])
print(resumo_qualidade_regras(rules))
"""),
        md("## 5.2 Explicabilidade"),
        code("""
for i, txt in enumerate(rules["explicacao_natural"].head(10), 1):
    print(f"{i:2d}. {txt}")
"""),
        md("## 5.3 Estabilidade temporal"),
        code("""
est = pd.read_csv(TABELAS_DIR / "regras_estabilidade_temporal.csv")
estaveis = est[est["status"] == "estavel"]
print(f"Estaveis: {len(estaveis)} | Transitorias: {(est['status']=='transitoria').sum()}")
display(estaveis[["regra", "n_anos_presente", "lift_medio", "confianca_media"]].head(10))
"""),
        md("## 5.4 Qualidade"),
        code("""
rules["faixa_lift"] = pd.cut(rules["lift"], bins=[1.05, 1.5, 2, 3, 10], labels=["1-1.5", "1.5-2", "2-3", "3+"])
print(rules["faixa_lift"].value_counts().sort_index())
print(f"Regras lift >= 3: {(rules['lift'] >= 3).sum()}")
"""),
        md("## 5.5 Limitacoes"),
        code('print(disclaimer())'),
        md("## 5.6 Export LaTeX"),
        code("""
if (PROCESSED_DIR / "rules_fatal.pkl").exists():
    rules_pk = pd.read_pickle(PROCESSED_DIR / "rules_fatal.pkl")
    exportar_top_regras_latex(rules_pk, TABELAS_DIR / "regras_top15_latex.tex")
    traduzir_regras(rules_pk).head(15).to_csv(TABELAS_DIR / "top15_regras_traduzidas.csv", index=False)
    print("[OK] LaTeX e CSV exportados")
"""),
    ])


def notebook_06() -> dict:
    return nb([
        md("# Fase 6 - Visualizacao e Consolidacao"),
        code(SETUP + "\nfrom IPython.display import Image, display\nimport subprocess"),
        md("## 6.1 Gerar figuras"),
        code("subprocess.run([sys.executable, str(ROOT / 'scripts' / 'generate_figures.py')], check=True)"),
        md("## 6.2 Galeria"),
        code("""
for p in sorted(FIGURAS_DIR.glob("*.png")):
    print(p.name)
    display(Image(filename=str(p)))
"""),
        md("## 6.3 Tabelas"),
        code("""
display(pd.read_csv(DADOS_DIR / "regras_contexto_fatal.csv").head(10))
est = pd.read_csv(TABELAS_DIR / "regras_estabilidade_temporal.csv")
est4 = est[(est["status"] == "estavel") & (est["n_anos_presente"] == est["n_anos_total"])]
print(f"Estaveis em todos os anos: {len(est4)}")
display(est4.head(8))
"""),
        md("## 6.4 Artefatos finais"),
        code("""
for folder in (DADOS_DIR, TABELAS_DIR, FIGURAS_DIR):
    files = sorted(folder.iterdir())
    print(f"\\n{folder.relative_to(ROOT)}/ ({len(files)})")
    for f in files:
        print(f"  - {f.name}")
"""),
    ])


def main():
    for name, fn in [
        ("01_setup_e_carregamento.ipynb", notebook_01),
        ("02_analise_exploratoria.ipynb", notebook_02),
        ("03_preparacao_dados.ipynb", notebook_03),
        ("04_modelagem.ipynb", notebook_04),
        ("05_avaliacao_ia_responsavel.ipynb", notebook_05),
        ("06_visualizacao_resultados.ipynb", notebook_06),
    ]:
        path = NB_DIR / name
        with open(path, "w", encoding="utf-8") as f:
            json.dump(fn(), f, ensure_ascii=False, indent=1)
        print(f"[OK] {path.name}")


if __name__ == "__main__":
    main()
