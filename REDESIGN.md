# Redesign metodologico (Pacote A)

## Problema identificado

A mineracao simetrica com `classificacao_acidente` + `gravidade_binaria` + temporais redundantes gerava regras tautologicas (lift ~14) e de calendario, sem valor analitico.

## Solucao implementada

1. **Multi-ano MG (2023+)**: `src/data_loading.py` concatena `datatran<ano>.csv`
2. **Subset com vitimas**: remove "Sem Vitimas"
3. **Alvo unico `desfecho`**: Fatal | Ferido (somente consequente)
4. **Itens de contexto**: 8 colunas com prefixo `ctx_`
5. **Filtros pos-mineracao**: antecedente so contexto, poda nao minimal, lift >= 1.05
6. **Estabilidade temporal** e **estrato urbano/rural** (H5)

## Executar pipeline

```bash
pip install -r requirements.txt
python scripts/run_pipeline.py
python scripts/generate_figures.py
```

## Dados necessarios

Baixar CSVs da PRF para `data/` — ver [data/README.md](data/README.md).

## Resultado exemplo (2026 parcial, MG)

Regra contexto -> Fatal (lift 6.40):

> Quando causa=Transitar na contramao E tipo=Colisao frontal E entorno=rural, entao desfecho fatal.

## Modulos

- `src/config.py` — parametros
- `src/data_loading.py` — carregamento multi-ano
- `src/preparation.py` — preparacao transacional
- `src/mining.py` — FP-Growth restrito
- `src/evaluation.py` — explicabilidade

Notebooks V2: secoes `3.V2`, `4.V2`, `5.V2`, `6.V2` nos notebooks 03-06.
