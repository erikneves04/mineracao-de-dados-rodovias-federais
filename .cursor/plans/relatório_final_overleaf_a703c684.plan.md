---
name: Relatório Final Overleaf
overview: Criar um relatório final em LaTeX (pronto para Overleaf), autocontido em relatorios/final/, com até 10 páginas, fundamentado e integrando todos os dados agregados (figuras, tabelas e métricas multi-ano MG 2023–2026 do Pacote A).
todos:
  - id: scaffold
    content: Criar pasta relatorios/final/ e copiar figuras selecionadas de outputs/figuras/ para relatorios/final/figuras/
    status: completed
  - id: tables
    content: Gerar tabelas .tex limpas (top regras fatal, estabilidade, distribuição desfecho) a partir dos CSVs Pacote A, evitando artefatos legados
    status: completed
  - id: maintex
    content: Escrever main.tex completo (preâmbulo + todas as seções) com figuras, tabelas e métricas reais
    status: completed
  - id: verify
    content: Verificar caminhos de figuras/inputs, sintaxe LaTeX e tentar compilar (pdflatex) ou documentar prontidão para Overleaf
    status: completed
isProject: false
---

## Relatório Final — Mineração de Regras de Associação (PRF / MG)

### Objetivo
Produzir `relatorios/final/main.tex` autocontido para upload no Overleaf, com até 10 páginas, bem fundamentado, cobrindo Introdução, Trabalhos Relacionados, Metodologia, Implementação, Resultados, Análise, IA Responsável e Conclusão — usando os resultados reais do pipeline Pacote A multi-ano.

### Estrutura de entrega
- Nova pasta `relatorios/final/` autocontida (Overleaf precisa de projeto fechado):
  - `main.tex` — documento único (`article`, 12pt, `babel` brazilian, `booktabs`, `graphicx`, `subcaption`, `float`, `hyperref`, `tikz`). Preâmbulo baseado no já validado em [relatorios/progresso/main.tex](relatorios/progresso/main.tex), **sem** `minted` (evita `shell-escape` no Overleaf).
  - `figuras/` — cópia dos PNGs relevantes de `outputs/figuras/`.
  - `tabelas/` — tabelas `.tex` limpas, regeneradas (ver abaixo).

### Dados/resultados reais que serão citados (Pacote A, MG 2023–2026)
- 30.858 ocorrências MG → 26.899 transações com vítimas; alvo `desfecho` com 7,83% Fatal.
- 76 regras contexto→`desfecho_Fatal` (lift máx. 5,44; mediana 1,81).
- 87 regras estáveis (presentes em ≥50% dos anos); estratos por uso do solo: 19 urbano / 54 rural.
- Regra-topo: {Plena Noite, Atropelamento de Pedestre, uso\_solo=Não} → Fatal (sup 0,5%, conf 42,6%, lift 5,44).
- Regra estável 4/4 anos: {Transitar na contramão, Colisão frontal, uso\_solo=Não} → Fatal (sup 0,7%, conf 42,3%, lift 5,40).

### Figuras a incluir (copiadas de `outputs/figuras/`)
- `01_distribuicao_desfecho.png` (desbalanceamento Fatal/Ferido)
- `02_cramers_v_desfecho.png` (associação contexto×desfecho)
- `02_mapa_amostra.png` (novo mapa espacial com fundo Brasil/MG)
- `02_fatal_por_fase_dia.png` e/ou `02_sazonalidade_mensal.png` (perfil temporal)
- `05_scatter_suporte_confianca_fatal.png` (suporte×confiança, cor=lift)
- `06_estabilidade_temporal.png` (monitoramento/IA responsável)
- `07_estratos_uso_solo.png` (urbano vs rural)
- `08_mineracao_por_ano.png` (regras por ano)

### Tabelas (regeneradas limpas — NÃO usar artefatos legados)
- `tabelas/top_regras_fatal.tex`: Top ~12 regras contexto→Fatal a partir de [outputs/tabelas/top15_regras_traduzidas.csv](outputs/tabelas/top15_regras_traduzidas.csv) / [outputs/dados/regras_contexto_fatal.csv](outputs/dados/regras_contexto_fatal.csv), com colunas Antecedente (contexto) / Sup. / Conf. / Lift. Substitui [outputs/tabelas/regras_top15_latex.tex](outputs/tabelas/regras_top15_latex.tex), cujo texto de explicação está truncado.
- `tabelas/estabilidade.tex`: amostra de regras estáveis (anos presentes, lift médio) de [outputs/tabelas/regras_estabilidade_temporal.csv](outputs/tabelas/regras_estabilidade_temporal.csv).
- `tabelas/distribuicao_desfecho.tex`: proporção Fatal/Ferido + n.
- Importante: **ignorar** `top10_regras_cluster_0.csv`/`_1.csv` (regras tautológicas `gravidade_binaria`→`classificacao`, do desenho antigo).

### Seções do `main.tex` (orçamento ~10 págs)
1. Título + autores (Erik, Gabriel, Felipe) + Resumo.
2. Introdução: contexto/motivação, objetivo geral e específicos, problema (multivariado, não trivial). Base em [Proposta_Projeto_Grupo18.md](Proposta_Projeto_Grupo18.md).
3. Trabalhos Relacionados: FP-Growth/FP-Tree, regras de associação e métricas; CRISP-DM; dados PRF. Ampliar referências (Han/Pei/Yin 2000; Agrawal/Srikant 1994; Tan/Steinbach/Kumar; Zaki/Meira 2020; Wirth/Hipp 2000; PRF).
4. Metodologia (CRISP-DM): dados e recorte MG multi-ano; preparação Pacote A (subset com vítimas, alvo `desfecho`, one-hot `ctx_*`, filtro de itens); FP-Growth restrito (antecedentes só `ctx_*`, consequente `desfecho_Fatal`, poda não-minimal); métricas (suporte, confiança, lift, leverage, conviction). Figura TikZ do fluxo CRISP-DM. Parâmetros de [src/config.py](src/config.py).
5. Implementação: organização em `src/` + `scripts/run_pipeline.py` + notebooks 01–06; reprodutibilidade.
6. Resultados Experimentais: achados da EDA (desbalanceamento, Cramér's V, mapa, perfil temporal) + mineração (76 regras, tabela top, scatter) + estabilidade temporal + estratos urbano/rural.
7. Análise dos Resultados: discussão das hipóteses H1–H5; interpretação dos padrões; associação ≠ causalidade.
8. Diretrizes de IA Responsável: Explicabilidade (tradução/filtragem/disclaimer) e Monitoramento e Avaliação (estabilidade multi-ano) — operacionalizadas, com trade-offs.
9. Conclusões e Perspectivas.
10. Referências (`thebibliography`).

### Verificação
- Conferir que todos os `\includegraphics` e `\input` apontam para arquivos existentes em `relatorios/final/`.
- Tentar compilar com `pdflatex` se disponível no ambiente; caso contrário, validar manualmente caminhos/sintaxe e documentar que o projeto está pronto para compilar no Overleaf.
- Não alterar `relatorios/progresso/` nem dados/figuras de `outputs/`.