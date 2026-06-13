# Dados PRF — Minera??o de Dados (Grupo 18)

## Arquivos necess?rios (por ocorr?ncia)

Coloque em `data/` os CSVs **agrupados por ocorr?ncia** da PRF:

| Ano | Nome sugerido | Origem |
|-----|---------------|--------|
| 2023 | `datatran2023.csv` | [Dados Abertos PRF](https://www.gov.br/prf/pt-br/acesso-a-informacao/dados-abertos/dados-abertos-da-prf) ? Acidentes 2023 (Agrupados por ocorr?ncia) |
| 2024 | `datatran2024.csv` | Idem para 2024 |
| 2025 | `datatran2025.csv` | Idem para 2025 |
| 2026 | `datatran2026.csv` ou `datatran2026_agrupados_por_ocorrencia.csv` | Parcial (j? inclu?do no repo) |

Os arquivos v?m compactados (.zip) no portal. Ap?s extrair, renomeie para o padr?o acima ou ajuste `PADROES_ARQUIVO_OCORRENCIA` em `src/config.py`.

## Formato

- Separador: `;`
- Encoding: `latin-1` (ISO-8859-1)
- Granularidade: **1 linha = 1 ocorr?ncia** de acidente

## Recorte do projeto

- **UF:** Minas Gerais (`MG`)
- **Per?odo:** 2023 em diante (p?s-pandemia), conforme decis?o metodol?gica

## Verificar arquivos dispon?veis

```bash
python -c "from src.data_loading import listar_anos_disponiveis; print(listar_anos_disponiveis())"
```

## Pipeline completo

```bash
python scripts/run_pipeline.py
```

Isso carrega os anos dispon?veis, prepara dados (Pacote A), minera regras contexto?fatal e exporta resultados em `outputs/`.
