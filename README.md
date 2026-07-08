# Mineração de Dados: Rodovias Federais 🛣️

Repositório contendo o projeto final da disciplina de Mineração de Dados da Universidade Federal de Minas Gerais (UFMG). O projeto tem como foco a análise e mineração de dados referentes às rodovias federais brasileiras, com um aprofundamento na malha rodoviária e incidentes no estado de Minas Gerais.

## 📌 Sobre o Projeto

O objetivo principal deste trabalho foi aplicar técnicas de pré-processamento, análise exploratória e mineração de dados sobre bases públicas da infraestrutura rodoviária e registros de ocorrências. A partir disso, extraímos padrões e construímos visualizações que auxiliam na compreensão dos desafios de segurança viária.

### Destaques e Entregas
* **Pré-processamento:** Tratamento de uma base extensa, incluindo seleção de colunas, imputação de valores e tratamento de dados ruidosos.
* **Análise Exploratória (EDA):** Identificação de sazonalidades e fatores recorrentes associados a ocorrências nas vias.
* **Visualização Geoespacial:** Geração de um mapa de calor detalhado para o estado de Minas Gerais, mapeando claramente "hotspots" e zonas críticas de atenção.

## 📁 Estrutura do Repositório

O repositório foi organizado para facilitar a reprodutibilidade da análise:

    ├── data/                         # Dados brutos e processados utilizados no projeto
    ├── notebooks/                    # Jupyter Notebooks com análises exploratórias, limpeza e visualizações
    ├── outputs/                      # Mapas de calor gerados, gráficos e arquivos de saída
    ├── relatorios/                   # Documentação detalhada e relatórios do projeto
    ├── scripts/                      # Scripts auxiliares para manipulação de rotinas rápidas
    ├── src/                          # Código-fonte e módulos de processamento estruturados
    ├── Proposta_Projeto_Grupo18.md   # Proposta inicial submetida à disciplina
    └── requirements.txt              # Dependências e bibliotecas Python necessárias

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python
* **Manipulação de Dados:** Pandas, NumPy
* **Visualização de Dados e Mapas:** Matplotlib, Seaborn, Folium (ou bibliotecas similares de geolocalização)
* **Modelagem e Mineração:** Scikit-Learn
* **Ambiente de Desenvolvimento:** Jupyter Notebook

## 🚀 Como Executar Localmente

1. Clone o repositório:
   git clone https://github.com/erikneves04/mineracao-de-dados-rodovias-federais.git
   cd mineracao-de-dados-rodovias-federais

2. Crie e ative um ambiente virtual (recomendado):
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows

3. Instale as dependências listadas:
   pip install -r requirements.txt

4. Execute os notebooks para reproduzir as análises:
   jupyter notebook

*(Navegue até a pasta notebooks/ e abra os arquivos sequencialmente para ver a geração do mapa de calor de Minas Gerais).*

## 👥 Autores

* Erik Neves
* Felipe Damasceno
* Gabriel Prudente
