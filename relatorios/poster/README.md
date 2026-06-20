# Pôster A1 — Grupo 18 (DCC/UFMG)

Pôster acadêmico para a disciplina de **Mineração de Dados** (2026/1), baseado no template [Gemini](https://github.com/anishathalye/gemini) (beamerposter).

## Conteúdo

- `poster.tex` — documento principal (A1 retrato, 2 colunas)
- `beamercolorthemeufmg.sty` — tema de cores UFMG/DCC
- `logos/` — logos oficiais UFMG e DCC
- `figuras/` — 10 PNGs exportados do pipeline (cópia autocontida), incluindo `09_comparacao_fatal_ferido.png`
- `tabelas/` — tabela LaTeX da comparação fatal vs. não-fatal (`comparacao_fatal_ferido.tex`)

A figura e a tabela de comparação são geradas por [notebooks/07_comparacao_fatal_vs_nao_fatal.ipynb](../../notebooks/07_comparacao_fatal_vs_nao_fatal.ipynb), que reaproveita `src/mining.py` (sem alterar a lógica consolidada).

## Compilar localmente

Requisitos: LuaLaTeX, `latexmk`, fontes **Raleway** e **Lato**.

```bash
cd relatorios/poster
make
```

Saída: `poster.pdf`

## Compilar no Overleaf

1. Faça upload da pasta `relatorios/poster/` (já inclui `figuras/` e `tabelas/`).
2. Defina `poster.tex` como documento principal.
3. Compile com **pdfLaTeX** (padrão do Overleaf) ou **LuaLaTeX** (fontes Raleway/Lato do tema Gemini).
4. Se aparecer erro de `fontspec`, recompile após atualizar `beamerthemegemini.sty` (fallback pdfLaTeX) ou altere em Menu → Settings → Compiler → **LuaLaTeX**.

## Dados destacados no pôster

- 30.858 ocorrências MG (2023–2026)
- 26.899 transações com vítimas (7,8% Fatal)
- 76 regras contexto → Fatal (lift máx. 5,44)
- 87 regras estáveis; 19 urbano / 54 rural por estrato
- Comparação fatal vs. não-fatal: contextos de alto lift para Fatal têm lift < 1 para Ferido (específicos da fatalidade)
