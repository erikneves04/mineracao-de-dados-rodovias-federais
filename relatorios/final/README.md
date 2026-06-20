# Relatorio Final � Grupo 18 (Overleaf)

Projeto autocontido para upload no [Overleaf](https://www.overleaf.com).

## Conteudo

- `main.tex` � documento principal (~10 paginas)
- `figuras/` � 9 PNGs exportados do pipeline
- `tabelas/` � tabelas LaTeX geradas a partir dos CSVs Pacote A

## Como usar no Overleaf

1. Crie um novo projeto em branco (ou upload ZIP desta pasta `relatorios/final/`).
2. Defina `main.tex` como documento principal.
3. Compile com **pdfLaTeX** (padrao do Overleaf; nao requer `shell-escape`).
4. Se necessario, recompile duas vezes para referencias cruzadas.

## Regenerar tabelas

A partir da raiz do repositorio:

```bash
set PYTHONPATH=.
python scripts/build_final_report_tables.py
```

## Dados citados no relatorio

- 30.858 ocorrencias MG (2023�2026)
- 26.899 transacoes com vitimas (7,8% Fatal)
- 76 regras contexto ? Fatal (lift max. 5,44)
- 87 regras estaveis; 19 urbano / 54 rural por estrato
