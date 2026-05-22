# Plano de Execução — Mineração de Dados: Acidentes em Rodovias Federais

> **Grupo 18** — Erik Roberto Reis Neves, Gabriel Campos Prudente, Felipe Silva Fraga Damasceno  
> **Disciplina**: Mineração de Dados — UFMG  
> **Metodologia**: CRISP-DM  
> **Método principal**: Mineração de Padrões Frequentes e Regras de Associação (FP-Growth)

---

## Inventário de Dados (`data/`)

| Arquivo | Granularidade | Registros | Colunas | Separador |
|---|---|---|---|---|
| `acidentes2026_agrupados_por_pessoa.csv` | 1 linha por **pessoa** envolvida | ~64 125 | 35 | `;` |
| `acidentes2026_todas_causas_tipos.csv` | 1 linha por **causa×tipo×pessoa** (explode multicausa) | ~196 099 | 37 | `;` |
| `datatran2026_agrupados_por_ocorrencia.csv` | 1 linha por **ocorrência** | ~23 475 | 30 | `;` |

### Colunas por arquivo

#### `acidentes2026_agrupados_por_pessoa.csv` (35 cols)
```
id, pesid, data_inversa, dia_semana, horario, uf, br, km, municipio,
causa_acidente, tipo_acidente, classificacao_acidente, fase_dia, sentido_via,
condicao_metereologica, tipo_pista, tracado_via, uso_solo, id_veiculo,
tipo_veiculo, marca, ano_fabricacao_veiculo, tipo_envolvido, estado_fisico,
idade, sexo, ilesos, feridos_leves, feridos_graves, mortos,
latitude, longitude, regional, delegacia, uop
```

#### `acidentes2026_todas_causas_tipos.csv` (37 cols)
```
id, pesid, data_inversa, dia_semana, horario, uf, br, km, municipio,
causa_principal, causa_acidente, ordem_tipo_acidente, tipo_acidente,
classificacao_acidente, fase_dia, sentido_via, condicao_metereologica,
tipo_pista, tracado_via, uso_solo, id_veiculo, tipo_veiculo, marca,
ano_fabricacao_veiculo, tipo_envolvido, estado_fisico, idade, sexo,
ilesos, feridos_leves, feridos_graves, mortos, latitude, longitude,
regional, delegacia, uop
```

#### `datatran2026_agrupados_por_ocorrencia.csv` (30 cols)
```
id, data_inversa, dia_semana, horario, uf, br, km, municipio,
causa_acidente, tipo_acidente, classificacao_acidente, fase_dia, sentido_via,
condicao_metereologica, tipo_pista, tracado_via, uso_solo,
pessoas, mortos, feridos_leves, feridos_graves, ilesos, ignorados, feridos,
veiculos, latitude, longitude, regional, delegacia, uop
```

> [!IMPORTANT]
> O código deve ser **maleável**: usar constantes/dicionários para selecionar colunas e arquivos, permitindo trocar a granularidade (por ocorrência vs. por pessoa) ou concatenar múltiplos CSVs sem reescrever lógica.

---

## Estrutura de Notebooks Proposta

```
notebooks/
├── 01_setup_e_carregamento.ipynb
├── 02_analise_exploratoria.ipynb
├── 03_preparacao_dados.ipynb
├── 04_modelagem.ipynb
├── 05_avaliacao_ia_responsavel.ipynb
└── 06_visualizacao_resultados.ipynb
```

> [!TIP]
> Alternativamente, pode-se usar um único notebook grande dividido em seções com headers Markdown, mas a separação em 6 notebooks facilita o trabalho paralelo do grupo e o rastreamento de progresso.

---

## Fase 1 — Setup e Carregamento dos Dados

**Notebook**: `01_setup_e_carregamento.ipynb`  
**Objetivo**: Criar infraestrutura reutilizável de carregamento e configuração.  
**Alinhamento CRISP-DM**: *Business Understanding* + início do *Data Understanding*

### 1.1 Instalação e Imports

Célula inicial com todas as dependências:

```python
# Bibliotecas necessárias
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from mlxtend.frequent_patterns import fpgrowth, association_rules
from mlxtend.preprocessing import TransactionEncoder
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.decomposition import PCA
import warnings
warnings.filterwarnings('ignore')

# Configurações de visualização
plt.rcParams['figure.figsize'] = (14, 6)
plt.rcParams['font.size'] = 12
sns.set_style('whitegrid')
```

### 1.2 Configuração Flexível de Dados

Criar um **dicionário de configuração** que permita trocar facilmente qual arquivo e quais colunas usar:

```python
# ====== CONFIGURAÇÃO CENTRAL — ALTERE AQUI ======
DATA_DIR = '../data/'

# Mapa dos arquivos disponíveis e suas granularidades
DATASETS = {
    'por_ocorrencia': {
        'file': 'datatran2026_agrupados_por_ocorrencia.csv',
        'granularity': 'ocorrência',
        'id_col': 'id',
    },
    'por_pessoa': {
        'file': 'acidentes2026_agrupados_por_pessoa.csv',
        'granularity': 'pessoa',
        'id_col': 'pesid',
    },
    'todas_causas': {
        'file': 'acidentes2026_todas_causas_tipos.csv',
        'granularity': 'causa×pessoa',
        'id_col': 'pesid',
    },
}

# >>> SELECIONE O DATASET ATIVO <<<
ACTIVE_DATASET = 'por_ocorrencia'  # Trocar conforme necessidade

# Colunas categóricas para mineração (selecionar conforme dataset)
COLUNAS_CATEGORICAS = [
    'dia_semana', 'uf', 'causa_acidente', 'tipo_acidente',
    'classificacao_acidente', 'fase_dia', 'sentido_via',
    'condicao_metereologica', 'tipo_pista', 'tracado_via', 'uso_solo',
]

# Colunas numéricas de interesse
COLUNAS_NUMERICAS = ['km', 'mortos', 'feridos_leves', 'feridos_graves', 'ilesos']

# Colunas de data/hora
COLUNAS_TEMPORAIS = ['data_inversa', 'horario']

# Filtro geográfico (proposta: MG)
FILTRO_UF = 'MG'

# Separador CSV
SEP = ';'
```

### 1.3 Funções de Carregamento

```python
def carregar_dataset(dataset_key, filtro_uf=None):
    """Carrega o dataset selecionado com filtro opcional por UF."""
    info = DATASETS[dataset_key]
    path = DATA_DIR + info['file']
    df = pd.read_csv(path, sep=SEP, encoding='latin-1')

    if filtro_uf:
        df = df[df['uf'] == filtro_uf].copy()

    print(f"Dataset: {info['file']}")
    print(f"Granularidade: {info['granularity']}")
    print(f"Registros: {len(df):,}")
    print(f"Colunas: {df.shape[1]}")
    if filtro_uf:
        print(f"Filtro UF: {filtro_uf}")
    return df


def carregar_e_concatenar(dataset_keys, filtro_uf=None):
    """Carrega e concatena múltiplos datasets (alinha pelas colunas em comum)."""
    dfs = []
    for key in dataset_keys:
        dfs.append(carregar_dataset(key, filtro_uf))
    df = pd.concat(dfs, ignore_index=True, join='inner')
    print(f"\n--- Concatenado: {len(df):,} registros, {df.shape[1]} colunas ---")
    return df
```

### 1.4 Carregamento Efetivo

```python
# Carregamento do dataset ativo
df = carregar_dataset(ACTIVE_DATASET, filtro_uf=FILTRO_UF)
df.head()
```

### Critérios de Conclusão da Fase 1
- [x] Todos os 3 CSVs podem ser carregados individualmente
- [x] É possível trocar o dataset ativo alterando UMA variável
- [x] O filtro por UF funciona corretamente
- [x] A função de concatenação funciona quando colunas em comum existem

---

## Fase 2 — Análise Exploratória (EDA)

**Notebook**: `02_analise_exploratoria.ipynb`  
**Objetivo**: Compreender a estrutura, distribuição e qualidade dos dados.  
**Alinhamento CRISP-DM**: *Data Understanding*

### 2.1 Visão Geral do Dataset

```python
# Informações gerais
df.info()
df.describe(include='all')
df.isnull().sum().sort_values(ascending=False)
```

Produzir tabela de resumo:
- Nº de valores únicos por coluna
- % de valores nulos
- Tipo de dado (categórico/numérico/temporal)

### 2.2 Distribuição da Variável-Alvo: Classificação do Acidente

```python
# Distribuição de gravidade
df['classificacao_acidente'].value_counts(normalize=True).plot(kind='bar')
```

Analisar o desbalanceamento entre classes:
- "Sem Vítimas"
- "Com Vítimas Feridas"
- "Com Vítimas Fatais"
- "Ignorado" / NA

> [!WARNING]
> Acidentes fatais tendem a ser minoria (~3-5%). Isso impacta diretamente o suporte mínimo no FP-Growth. Documentar essa distribuição.

### 2.3 Análise Temporal

- Distribuição por **dia da semana**
- Distribuição por **fase do dia** (Plena Noite, Amanhecer, Pleno dia, etc.)
- Distribuição por **mês** (extrair de `data_inversa`)
- **Série temporal**: acidentes por semana/mês
- Cruzamento: gravidade × dia da semana × fase do dia (heatmap)

### 2.4 Análise Geográfica

- Top 10 BRs com mais acidentes (e mais acidentes graves)
- Top 10 municípios
- Distribuição por `uso_solo` (Urbano vs. Rural)
- Mapa de calor com `latitude` × `longitude` (se viável, com folium ou scatter)

### 2.5 Análise das Variáveis Categóricas

Para cada coluna em `COLUNAS_CATEGORICAS`:
- `value_counts()` com barplot
- Cruzamento com `classificacao_acidente` (stacked bar ou heatmap normalizado)
- Identificar categorias raras (< 1%) que podem precisar de agrupamento

### 2.6 Análise de Correlações

- Heatmap de correlação entre variáveis numéricas
- Análise de associação entre categóricas via **Cramér's V** (tabela cruzada)

### 2.7 Insights Preliminares

Célula Markdown documentando:
- Principais padrões observados
- Hipóteses a investigar na modelagem
- Problemas de qualidade identificados

### Critérios de Conclusão da Fase 2
- [x] Pelo menos 10 visualizações produzidas (17 visualizações geradas e salvas em `outputs/figuras/`)
- [x] Distribuição de gravidade documentada com % (seção 2.2: Com Vítimas Feridas 79.3%, Sem Vítimas 13.6%, Com Vítimas Fatais 7.1%)
- [x] Análise temporal completa (dia, fase, mês) (seções 2.3.1 a 2.3.6)
- [x] Cramér's V ou tabela de contingência entre categóricas e gravidade (seções 2.6.2 e 2.6.3)
- [x] Lista de hipóteses formuladas (seção 2.8 com 5 hipóteses H1-H5)

---

## Fase 3 — Preparação dos Dados

**Notebook**: `03_preparacao_dados.ipynb`  
**Objetivo**: Limpar, transformar e criar a representação transacional para FP-Growth.  
**Alinhamento CRISP-DM**: *Data Preparation*

### 3.1 Tratamento de Valores Ausentes

```python
# Estratégia por coluna
# - classificacao_acidente == NA → tratar como 'Não Informado' ou remover
# - Colunas com > 30% nulos → avaliar exclusão
# - Demais → preencher com 'Não Informado' (categóricas) ou mediana (numéricas)
```

### 3.2 Limpeza e Padronização

- Remover espaços extras em strings
- Padronizar encoding (caracteres especiais como `Colisão`, `Reação`, etc.)
- Unificar categorias similares (ex: `tracado_via` pode ter valores compostos como `"Aclive;Reta"` — decidir se split ou manter)
- Tratar `km` (vírgula como decimal → converter para float)

### 3.3 Feature Engineering

Criar novas variáveis derivadas:

| Nova Coluna | Origem | Transformação |
|---|---|---|
| `mes` | `data_inversa` | Extração do mês |
| `faixa_horaria` | `horario` | Discretizar em faixas (Madrugada: 00-06, Manhã: 06-12, Tarde: 12-18, Noite: 18-24) |
| `fim_de_semana` | `dia_semana` | Booleano (sáb/dom) |
| `gravidade_binaria` | `classificacao_acidente` | 1 se "Com Vítimas Fatais", 0 caso contrário |
| `faixa_km` | `km` | Discretizar em intervalos (0-50, 50-100, 100-200, 200+) |
| `idade_faixa` | `idade` | Se disponível: Jovem (18-25), Adulto (26-59), Idoso (60+) |
| `veiculo_pesado` | `tipo_veiculo` | Booleano se caminhão/ônibus/trator |

> [!NOTE]
> As faixas de discretização devem ser calibradas com base nos percentis reais da EDA (Fase 2). Os valores acima são sugestões iniciais.

### 3.4 Seleção de Colunas para Mineração

```python
# Configuração flexível: selecionar colunas para a representação transacional
COLUNAS_TRANSACIONAIS = [
    'dia_semana',
    'fase_dia',
    'condicao_metereologica',
    'tipo_pista',
    'tracado_via',
    'uso_solo',
    'causa_acidente',
    'tipo_acidente',
    'classificacao_acidente',
    'faixa_horaria',       # engineered
    'fim_de_semana',       # engineered
    'gravidade_binaria',   # engineered
    # Adicionar/remover conforme necessidade:
    # 'tipo_veiculo',      # disponível apenas em datasets por pessoa
    # 'sexo',              # disponível apenas em datasets por pessoa
    # 'idade_faixa',       # disponível apenas em datasets por pessoa
    # 'veiculo_pesado',    # engineered
]
```

### 3.5 Construção da Representação Transacional (One-Hot Encoding)

Transformar cada registro em uma "transação" binária para o FP-Growth:

```python
def criar_representacao_transacional(df, colunas):
    """
    Cria DataFrame binário (one-hot) para FP-Growth.
    Cada coluna vira um item no formato 'nome_coluna=valor'.
    """
    df_trans = pd.DataFrame()
    for col in colunas:
        if col in df.columns:
            dummies = pd.get_dummies(df[col], prefix=col, dtype=bool)
            df_trans = pd.concat([df_trans, dummies], axis=1)
    return df_trans
```

### 3.6 Controle de Granularidade de Itens

- Remover itens com frequência < 1% (muito raros, não gerarão padrões úteis)
- Remover itens com frequência > 99% (triviais, presentes em quase tudo)
- Documentar quantos itens restam após filtragem

```python
# Filtrar itens muito raros ou muito frequentes
freq = df_onehot.mean()
itens_validos = freq[(freq >= 0.01) & (freq <= 0.99)].index
df_onehot_filtrado = df_onehot[itens_validos]
print(f"Itens antes: {df_onehot.shape[1]}, depois: {df_onehot_filtrado.shape[1]}")
```

### 3.7 Salvamento dos Dados Processados

```python
# Salvar para uso nos notebooks seguintes
df_onehot_filtrado.to_pickle('../data/processed/transacional.pkl')
df.to_pickle('../data/processed/df_limpo.pkl')
```

### Critérios de Conclusão da Fase 3
- [x] Zero valores nulos nas colunas usadas (0 nulos nas 12 colunas transacionais)
- [x] Todas as features categóricas padronizadas (12 colunas: 7+4+8+3+99+2+57+16+3+4+2+2 categorias)
- [x] Features derivadas criadas e validadas (5 features: mes, faixa_horaria, fim_de_semana, gravidade_binaria, faixa_km)
- [x] Representação transacional one-hot gerada (2,985 transações × 207 itens)
- [x] Itens filtrados (1% ≤ freq ≤ 99%): 207 → 83 itens (124 raros removidos, 0 triviais)
- [x] Dados processados salvos em `data/processed/` (df_limpo.pkl, transacional.pkl, transacional_completo.pkl, preparacao_metadata.json)

---

## Fase 4 — Modelagem

**Notebook**: `04_modelagem.ipynb`  
**Objetivo**: Aplicar FP-Growth para mineração de padrões frequentes e regras de associação, opcionalmente precedido de clustering.  
**Alinhamento CRISP-DM**: *Modeling*

### 4.1 Mineração Global — FP-Growth

```python
# Carregar dados processados
df_onehot = pd.read_pickle('../data/processed/transacional.pkl')

# FP-Growth — Extração de Itemsets Frequentes
min_support = 0.05  # Calibrar com base na EDA
itemsets = fpgrowth(df_onehot, min_support=min_support, use_colnames=True)
print(f"Itemsets frequentes encontrados: {len(itemsets)}")
```

### 4.2 Geração de Regras de Associação

```python
# Gerar regras
rules = association_rules(itemsets, metric='confidence', min_threshold=0.5)

# Adicionar métricas complementares
# conviction e leverage já são calculados pelo mlxtend

# Filtrar regras redundantes e triviais
rules = rules[rules['lift'] > 1.0]  # Apenas associações positivas

# Ordenar por lift (ou conviction)
rules = rules.sort_values('lift', ascending=False)
print(f"Regras geradas: {len(rules)}")
rules.head(20)
```

### 4.3 Foco em Regras de Gravidade

Filtrar regras onde o **consequente** contém indicadores de gravidade:

```python
# Regras que predizem acidentes fatais
rules_fatais = rules[rules['consequents'].apply(
    lambda x: any('classificacao_acidente=Com Vítimas Fatais' in str(i) for i in x)
)]

# Regras que predizem acidentes graves (fatais + feridos graves)
rules_graves = rules[rules['consequents'].apply(
    lambda x: any('gravidade_binaria=1' in str(i) for i in x)
)]
```

### 4.4 Experimentação com Parâmetros

Criar grid de experimentos variando:

| Parâmetro | Valores a testar |
|---|---|
| `min_support` | 0.01, 0.03, 0.05, 0.10 |
| `min_confidence` | 0.3, 0.5, 0.7 |
| `min_lift` | 1.0, 1.5, 2.0 |

Registrar para cada combinação: nº de itemsets, nº de regras, tempo de execução.

### 4.5 (Opcional) Clustering + Mineração Local

> [!NOTE]
> Esta etapa é **opcional/complementar**, conforme indicado na proposta. Implementar se houver tempo.

#### 4.5.1 Preparação para Clustering

```python
# Usar colunas numéricas/categóricas (label encoded) para clustering
from sklearn.preprocessing import LabelEncoder

df_cluster = df[COLUNAS_CATEGORICAS].copy()
le = LabelEncoder()
for col in df_cluster.columns:
    df_cluster[col] = le.fit_transform(df_cluster[col].astype(str))

scaler = StandardScaler()
X_scaled = scaler.fit_transform(df_cluster)
```

#### 4.5.2 Determinação do Número de Clusters

```python
# Método do cotovelo
from sklearn.metrics import silhouette_score

inertias = []
silhouettes = []
K_range = range(2, 10)
for k in K_range:
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = km.fit_predict(X_scaled)
    inertias.append(km.inertia_)
    silhouettes.append(silhouette_score(X_scaled, labels, sample_size=5000))

# Plotar cotovelo + silhouette
```

#### 4.5.3 Aplicação do Clustering e Mineração por Segmento

```python
# Aplicar K-Means com k escolhido
k_final = 4  # Definir após análise do cotovelo
km = KMeans(n_clusters=k_final, random_state=42, n_init=10)
df['cluster'] = km.fit_predict(X_scaled)

# Mineração de regras por cluster
rules_por_cluster = {}
for c in range(k_final):
    mask = df['cluster'] == c
    df_c = df_onehot[mask]
    itemsets_c = fpgrowth(df_c, min_support=0.05, use_colnames=True)
    rules_c = association_rules(itemsets_c, metric='confidence', min_threshold=0.5)
    rules_c = rules_c[rules_c['lift'] > 1.0]
    rules_por_cluster[c] = rules_c
    print(f"Cluster {c}: {mask.sum()} registros, {len(rules_c)} regras")
```

### 4.6 Análise Temporal (Monitoramento)

Para a diretriz de **Monitoramento e Avaliação**, executar a mineração em janelas temporais:

```python
# Executar FP-Growth por mês ou trimestre
df['mes'] = pd.to_datetime(df['data_inversa']).dt.month

rules_por_periodo = {}
for mes in sorted(df['mes'].unique()):
    mask = df['mes'] == mes
    df_m = df_onehot[mask]
    if len(df_m) < 100:
        continue
    itemsets_m = fpgrowth(df_m, min_support=0.05, use_colnames=True)
    if len(itemsets_m) > 0:
        rules_m = association_rules(itemsets_m, metric='confidence', min_threshold=0.5)
        rules_m = rules_m[rules_m['lift'] > 1.0]
        rules_por_periodo[mes] = rules_m
```

### Critérios de Conclusão da Fase 4
- [x] FP-Growth global executado com sucesso (2467 itemsets, 0.3s)
- [x] Regras de associação geradas e filtradas (lift > 1) (7923 regras)
- [x] Regras focadas em gravidade extraídas separadamente (0 regras puramente focadas em gravidade encontradas devido à distribuição dos dados, registradas para análise)
- [x] Grid de parâmetros experimentado e documentado (36 combinações testadas e exportadas)
- [x] Mineração temporal por período executada (4 meses avaliados, 9021 regras estáveis)
- [x] (Opcional) Clustering aplicado e mineração por segmento (k=2, 2 clusters com regras distintas)

---

## Fase 5 — Avaliação e IA Responsável

**Notebook**: `05_avaliacao_ia_responsavel.ipynb`  
**Objetivo**: Avaliar as regras, incorporar diretrizes de IA responsável, análise crítica.  
**Alinhamento CRISP-DM**: *Evaluation*

### 5.1 Avaliação Quantitativa das Regras

Tabela comparativa das top regras:

| # | Antecedente | Consequente | Suporte | Confiança | Lift | Conviction | Leverage |
|---|---|---|---|---|---|---|---|

Produzir essa tabela para:
- Top 20 regras globais (por lift)
- Top 10 regras de gravidade fatal
- Top 10 regras por cluster (se aplicável)

### 5.2 Diretriz 1: Explicabilidade

**Implementação concreta**:

1. **Filtragem de regras interpretáveis**: manter apenas regras com ≤ 3 itens no antecedente
2. **Remoção de redundâncias**: se A→C e A∪B→C têm confiança similar, manter a mais simples
3. **Tradução para linguagem natural**: para cada regra top, gerar descrição textual

```python
def regra_para_texto(row):
    """Converte uma regra de associação para linguagem natural."""
    ante = ' E '.join([str(i).replace('_', ' ') for i in row['antecedents']])
    cons = ' E '.join([str(i).replace('_', ' ') for i in row['consequents']])
    return (f"Quando {ante}, então {cons} "
            f"(confiança: {row['confidence']:.1%}, "
            f"lift: {row['lift']:.2f})")
```

4. **Disclaimer de causalidade**: seção explícita documentando que associação ≠ causalidade

### 5.3 Diretriz 2: Monitoramento e Avaliação

**Implementação concreta**:

1. **Estabilidade temporal**: comparar regras entre períodos distintos
   - Calcular **recorrência**: em quantos períodos cada regra aparece
   - Marcar regras **estáveis** (aparecem em ≥ 50% dos períodos) vs. **transitórias**

```python
# Avaliar estabilidade temporal das regras
from collections import Counter

# Converter regras para string para comparação
def regra_key(row):
    return (frozenset(row['antecedents']), frozenset(row['consequents']))

contagem = Counter()
for periodo, rules_p in rules_por_periodo.items():
    for _, row in rules_p.iterrows():
        contagem[regra_key(row)] += 1

n_periodos = len(rules_por_periodo)
regras_estaveis = {k for k, v in contagem.items() if v >= n_periodos * 0.5}
regras_transitorias = {k for k, v in contagem.items() if v < n_periodos * 0.3}
```

2. **Variação de métricas**: para regras estáveis, plotar evolução do lift/confiança ao longo dos meses

3. **Documentação**: tabela indicando para cada top regra se é estável ou transitória

### 5.4 Análise Crítica

Célula Markdown com:
- Limitações do método (FP-Growth trabalha com dados categóricos, perde nuances)
- Viés nos dados (auto-seleção: só acidentes registrados pela PRF)
- Risco de confundimento (correlação ≠ causalidade — repetir e aprofundar)
- Impacto do filtro geográfico (MG) na generalização
- Discussão sobre suporte mínimo e impacto no desbalanceamento de classes

### Critérios de Conclusão da Fase 5
- [x] Tabelas comparativas de regras com todas as métricas (top20 globais, top10 por cluster salvos)
- [x] Regras traduzidas para linguagem natural (top 15-20 com antecedente <= 3 geradas e salvas em `top15_regras_traduzidas.csv`)
- [x] Análise de estabilidade temporal documentada (regras cruzadas através dos 4 períodos; 9021 regras estáveis)
- [x] Disclaimer de causalidade presente (Aviso forte em console e exportação textual advertindo "Correlação != Causalidade")
- [x] Seção de limitações escrita (Limitações de variabilidade categórica contínua, fatores latentes e viés de seleção catalogados)
- [x] Ambas as diretrizes de IA responsável operacionalizadas com código + análise

---

## Fase 6 — Visualização e Consolidação de Resultados

**Notebook**: `06_visualizacao_resultados.ipynb`  
**Objetivo**: Produzir visualizações finais e consolidar material para o relatório.  
**Alinhamento CRISP-DM**: *Evaluation* + *Deployment* (no sentido de comunicação)

### 6.1 Visualizações Obrigatórias

| # | Visualização | Tipo | Descrição |
|---|---|---|---|
| 1 | Distribuição de gravidade | Barplot | Proporção das classes de gravidade |
| 2 | Heatmap temporal | Heatmap | Gravidade × dia da semana × fase do dia |
| 3 | Top causas por gravidade | Barplot horizontal empilhado | Causas de acidente coloridas por gravidade |
| 4 | Mapa de calor geográfico | Scatter/Folium | Lat/Long colorido por gravidade |
| 5 | Distribuição de suporte dos itemsets | Histograma | Frequência dos itemsets vs. suporte |
| 6 | Top 15 regras por lift | Barplot horizontal | Regras com lift mais alto |
| 7 | Scatter suporte × confiança | Scatter | Colorido por lift, tamanho por leverage |
| 8 | Rede de regras | Grafo (networkx) | Nós = itens, arestas = regras fortes |
| 9 | Evolução temporal de regras | Line plot | Lift/confiança de regras estáveis ao longo do tempo |
| 10 | Perfis de clusters | Radar/Spider chart | Características médias por cluster (se aplicável) |

### 6.2 Exportação para Relatório

```python
# Exportar tabelas para LaTeX/Markdown
rules_top20.to_latex('../outputs/tabela_regras_top20.tex', index=False)
rules_top20.to_markdown('../outputs/tabela_regras_top20.md', index=False)

# Salvar figuras em alta resolução
plt.savefig('../outputs/figuras/heatmap_temporal.png', dpi=300, bbox_inches='tight')
```

### 6.3 Estrutura de Saídas

```
outputs/
├── figuras/
│   ├── distribuicao_gravidade.png
│   ├── heatmap_temporal.png
│   ├── top_causas_gravidade.png
│   ├── mapa_calor.png
│   ├── scatter_suporte_confianca.png
│   ├── rede_regras.png
│   └── evolucao_temporal.png
├── tabelas/
│   ├── regras_top20.tex
│   ├── regras_fatais.tex
│   └── estabilidade_temporal.tex
└── dados/
    ├── regras_completas.csv
    └── itemsets_frequentes.csv
```

### Critérios de Conclusão da Fase 6
- [ ] Pelo menos 10 visualizações de alta qualidade geradas
- [ ] Figuras salvas em 300 dpi
- [ ] Tabelas exportadas em formato compatível com LaTeX
- [ ] Todos os resultados salvos em `outputs/`

---

## Cronograma Sugerido

| Fase | Estimativa | Deadline sugerida |
|---|---|---|
| 1. Setup e Carregamento | 1 sessão | Semana 1 |
| 2. Análise Exploratória | 2-3 sessões | Semana 1-2 |
| 3. Preparação dos Dados | 2 sessões | Semana 2 |
| 4. Modelagem | 3-4 sessões | Semana 2-3 |
| 5. Avaliação e IA Responsável | 2 sessões | Semana 3 |
| 6. Visualização e Resultados | 1-2 sessões | Semana 3-4 |
| **Relatório de Progresso** | — | **01/06/2026** |
| **Relatório Final** | — | **30/06/2026** |

---

## Decisões de Design Importantes

> [!IMPORTANT]
> ### Escolha do dataset principal
> Recomenda-se usar `datatran2026_agrupados_por_ocorrencia.csv` como dataset principal para a mineração de regras, pois cada linha = 1 acidente (transação natural). Os datasets por pessoa podem ser usados para análises complementares que envolvam variáveis demográficas (idade, sexo, tipo_veiculo).

> [!IMPORTANT]
> ### Tratamento do campo `tracado_via`
> Este campo contém valores compostos separados por `;` (ex: `"Aclive;Reta"`). Duas opções:
> 1. Manter como string composta (mais fiel ao dado original)
> 2. Fazer split e criar múltiplos itens (mais granular para mineração)
>
> **Recomendação**: Opção 2 (split), criando itens como `tracado_via=Aclive` e `tracado_via=Reta`.

> [!WARNING]
> ### Encoding dos CSVs
> Os arquivos usam encoding `latin-1` (ISO-8859-1). Caracteres como `ç`, `ã`, `é` aparecem como mojibake se lidos com UTF-8. Usar `encoding='latin-1'` em todos os `pd.read_csv()`.

---

## Dependências Python

```
pandas>=2.0
numpy>=1.24
matplotlib>=3.7
seaborn>=0.12
mlxtend>=0.22
scikit-learn>=1.3
networkx>=3.0       # para grafo de regras
folium>=0.14        # (opcional) mapas interativos
```
