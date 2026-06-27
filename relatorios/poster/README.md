# Poster A1 - Grupo 18 (DCC/UFMG)

Poster academico para a disciplina de Mineracao de Dados (2026/1), baseado no template Gemini.

## Conteudo

- `poster.tex` - documento principal (A1 retrato, 2 colunas)
- `beamercolorthemeufmg.sty` - tema de cores UFMG/DCC
- `logos/` - logos UFMG e DCC
- `figuras/` - PNGs exportados do pipeline
- `tabelas/` - tabela LaTeX da comparacao alta/baixa/fatal

## Compilar localmente

Requisitos: distribuicao LaTeX com beamerposter.

```bash
cd relatorios/poster
make
```

Saida esperada: `poster.pdf`

## Compilar no Overleaf

1. Faca upload da pasta `relatorios/poster/`.
2. Defina `poster.tex` como documento principal.
3. Compile com pdfLaTeX ou LuaLaTeX.

## Dados destacados no poster

- 30.858 ocorrencias MG disponiveis no conjunto 2023-2026.
- Mineracao principal em 2023-2025 completos: 24.320 ocorrencias com vitimas.
- 8.156 ocorrencias de alta gravidade (33,54%).
- 154 regras perfil -> AltaGravidade (lift max. 2,43).
- 75 regras perfil -> Fatal como validacao secundaria.
- Top-20 regras cobrem 12,5% dos casos de alta gravidade; o conjunto completo cobre 78,5%.
- 142 regras estaveis em pelo menos 2/3 anos completos; 60 em 3/3 anos.
