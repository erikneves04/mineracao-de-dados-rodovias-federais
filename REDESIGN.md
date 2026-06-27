# Notas metodologicas

O estudo minera regras de associacao para caracterizar perfis de alta gravidade entre acidentes com vitimas em rodovias federais de Minas Gerais.

## Escopo principal

- Dados PRF/MG disponiveis: 2023, 2024, 2025 e 2026 parcial ate 30/04/2026.
- Mineracao principal: anos completos 2023-2025.
- Validacao temporal externa: janelas Jan-Abr de 2023, 2024, 2025 e 2026.
- Base principal: 24.320 ocorrencias com vitimas.
- Alta gravidade: `mortos > 0 OR feridos_graves > 0`.

## Controles metodologicos

- Antecedentes restritos a itens `ctx_*`.
- Variaveis de consequencia nao entram nos antecedentes: `mortos`, `feridos_graves`, `feridos`, `classificacao_acidente`, `desfecho_*` e variaveis derivadas de gravidade.
- `tipo_acidente` e `causa_acidente` sao caracteristicas registradas da ocorrencia; por isso as regras caracterizam perfis de severidade, nao predicao pre-acidente.
- Na mineracao por estrato urbano/rural, `ctx_uso_solo_*` e removido dos antecedentes.
- Interpretacao sempre associativa: as regras nao estimam causalidade nem risco absoluto.

## Artefatos principais

- `outputs/dados/regras_contexto_alta_gravidade.csv`
- `outputs/dados/regras_contexto_fatal.csv`
- `outputs/tabelas/cobertura_regras.csv`
- `outputs/tabelas/bootstrap_top_regras.csv`
- `outputs/tabelas/sensibilidade_parametros.csv`
- `outputs/tabelas/estabilidade_alta_gravidade.csv`
