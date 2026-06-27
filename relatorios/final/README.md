# Relatorio Final - Grupo 18

Projeto autocontido para upload no Overleaf.

## Conteudo

- `main.tex` - documento principal
- `figuras/` - PNGs exportados do pipeline
- `tabelas/` - tabelas LaTeX geradas a partir dos CSVs finais

## Como usar no Overleaf

1. Crie um novo projeto em branco ou faca upload da pasta `relatorios/final/`.
2. Defina `main.tex` como documento principal.
3. Compile com pdfLaTeX.
4. Recompile duas vezes se necessario para referencias cruzadas.

## Regenerar tabelas

A partir da raiz do repositorio:

```bash
F:\Anaconda3\python.exe scripts\build_final_report_tables.py
```

## Dados citados no relatorio

- 30.858 ocorrencias MG disponiveis no conjunto 2023-2026.
- 2026 e parcial ate 30/04/2026 e entra apenas na validacao Jan-Abr.
- Recorte principal: 2023-2025 completos, 27.873 ocorrencias MG.
- 24.320 ocorrencias com vitimas no recorte principal.
- 8.156 ocorrencias de alta gravidade (33,54% da base com vitimas).
- 154 regras perfil -> AltaGravidade (lift max. 2,43).
- 75 regras perfil -> Fatal como validacao secundaria.
- Top-20 regras cobrem 12,5% dos casos de alta gravidade; o conjunto completo cobre 78,5%.
- 142 regras estaveis em pelo menos 2/3 anos completos; 60 em 3/3 anos.
