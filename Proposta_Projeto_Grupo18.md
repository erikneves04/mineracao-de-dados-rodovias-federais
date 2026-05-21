# **Universidade Federal de Minas Gerais**

# **Departamento de Ciência da Computação**

**Proposta de Projeto Final**

**Erik Roberto Reis Neves, Gabriel Campos Prudente, Felipe Silva Fraga Damasceno**

# **Contexto e Motivação** 

Os acidentes de trânsito em rodovias federais constituem um problema complexo de infraestrutura e saúde pública no Brasil, implicando perdas humanas significativas e elevados custos socioeconômicos. A Polícia Rodoviária Federal (PRF) registra essas ocorrências de forma sistemática, gerando uma base de dados extensa e multifacetada, composta por variáveis que descrevem condições ambientais, temporais, estruturais e comportamentais (como clima, luminosidade, características da via e tipologia dos veículos envolvidos).

Apesar da riqueza informacional disponível, análises tradicionais de caráter descritivo ou univariado são insuficientes para capturar a complexidade inerente ao fenômeno, uma vez que a gravidade dos acidentes emerge, em geral, da **interação simultânea entre múltiplos fatores de risco**, e não de variáveis isoladas. Nesse contexto, técnicas de mineração de dados tornam-se particularmente adequadas, pois permitem identificar **padrões ocultos, correlações não triviais e estruturas latentes** em grandes volumes de dados.

Este projeto propõe a aplicação de métodos de mineração de padrões frequentes para extrair conhecimento acionável a partir dos dados da PRF, com o objetivo de subsidiar análises mais profundas sobre fatores associados à severidade dos acidentes. 

**Objetivos** 

O presente projeto tem como objetivo geral desenvolver um estudo completo de Mineração de Dados, indo além de análises estatísticas descritivas, com o intuito de identificar **padrões ocultos e correlações não triviais** nos dados de acidentes rodoviários registrados pela Polícia Rodoviária Federal.

Como objetivo principal, busca-se descobrir **regras de associação estatisticamente relevantes** que representem combinações recorrentes de fatores de risco — envolvendo aspectos ambientais, temporais, estruturais e veiculares — que estejam associadas ao aumento da severidade dos acidentes, especialmente aqueles com vítimas graves ou fatais. Como objetivos específicos, pretende-se, se possível:

* Identificar conjuntos frequentes de itens que caracterizem cenários de risco elevado;  
* Gerar e analisar regras de associação utilizando métricas como suporte, confiança e lift, priorizando padrões não triviais e interpretáveis;  
* Construir perfis distintos de acidentes a partir da segmentação da base de dados, investigando diferenças estruturais entre contextos (por exemplo, trechos urbanos versus trechos rurais de rodovias); (se houver tempo)  
* Fornecer uma análise granular que permita compreender como diferentes combinações de fatores influenciam a severidade dos acidentes em distintos cenários. (se houver tempo)

Dessa forma, o projeto busca não apenas identificar padrões relevantes, mas também contribuir para uma compreensão mais aprofundada da dinâmica dos acidentes, possibilitando a geração de insights úteis para estratégias de prevenção e segurança viária.

# **Problema a ser investigado** 

O problema central deste projeto consiste em identificar **regras de associação estatisticamente significativas e não triviais** que relacionem combinações de fatores contextuais à ocorrência de acidentes de alta gravidade em rodovias federais. Em particular, busca-se investigar como variáveis ambientais (como condições climáticas adversas), temporais (como períodos noturnos e finais de semana), características da via (como tipo de pista e presença de acostamento) e tipologia veicular (como envolvimento de veículos pesados) **interagem de forma conjunta** para aumentar a probabilidade de acidentes com vítimas graves ou fatais.

Diferentemente de abordagens tradicionais centradas em variáveis isoladas, o foco deste projeto está na descoberta de **padrões multivariados de coocorrência**, capazes de revelar estruturas latentes e relações complexas presentes nos dados. Nesse contexto, o desafio não reside apenas em identificar padrões frequentes, mas em extrair regras que sejam simultaneamente **interpretáveis, relevantes e não redundantes**.

Adicionalmente, pretende-se analisar como essas regras variam entre diferentes subconjuntos da base de dados, investigando a existência de **heterogeneidades estruturais** associadas ao perfil dos trechos rodoviários (por exemplo, trechos urbanos versus rurais, ou regiões com diferentes níveis de fluxo e infraestrutura). Essa análise permitirá avaliar se padrões globais mascaram comportamentos locais, contribuindo para uma compreensão mais contextualizada do fenômeno.

# **Método Principal** 

O presente projeto tem como método central a **mineração de padrões frequentes e regras de associação**, com o objetivo de identificar combinações recorrentes de fatores que caracterizam cenários associados a acidentes de alta gravidade.

Para a extração dos padrões, será utilizado o algoritmo **FP-Growth**, escolhido por sua eficiência computacional em bases de grande escala. Diferentemente de abordagens baseadas na geração explícita de candidatos, o método utiliza uma estrutura compacta denominada **FP-Tree (Frequent Pattern Tree)**, que permite representar a base transacional de forma condensada e realizar a mineração de itemsets frequentes de maneira escalável. Essa característica o torna particularmente adequado ao contexto deste projeto, que envolve dados de alta dimensionalidade e grande volume provenientes da Polícia Rodoviária Federal.

A geração de regras de associação será conduzida a partir dos itemsets frequentes extraídos, utilizando métricas como **suporte**, **confiança**, **lift** e, complementarmente, **conviction**, de modo a priorizar padrões estatisticamente relevantes e evitar relações espúrias ou triviais. Será realizado também um processo de **pós-processamento das regras**, com foco na remoção de redundâncias e na seleção de padrões interpretáveis e informativos.

Como etapa complementar, serão aplicadas técnicas de **agrupamento (clustering)** com o objetivo de segmentar a base de dados em subconjuntos mais homogêneos antes da mineração. Essa segmentação permitirá identificar diferentes perfis de acidentes — por exemplo, variações entre trechos urbanos e rurais de rodovias ou entre contextos de diferentes níveis de fluxo — possibilitando a extração de regras mais específicas e sensíveis ao contexto.

A mineração será então realizada de forma independente em cada agrupamento, permitindo capturar **padrões locais** que poderiam ser mascarados em uma análise global. Além disso, essa abordagem contribui para reduzir efeitos de desbalanceamento e aumentar a relevância prática dos resultados.

Por fim, destaca-se que, embora o uso de clustering enriqueça a análise, o foco principal do projeto permanece na descoberta de padrões frequentes e regras de associação, que constituem o núcleo metodológico da investigação.

Porém, ressaltamos que essa é apenas a ideia inicial. Caso haja indisponibilidade de tempo, iremos focar na ideia central, isto é, **mineração de padrões frequentes e regras de associação,** e iremos avaliar a viabilidade e demanda de tempo para implementar a clusterização, e outras análises.

# **Dados Pretendidos** 

O conjunto de dados utilizado neste projeto é proveniente dos **Dados Abertos de Acidentes de Trânsito** disponibilizados pela Polícia Rodoviária Federal, especificamente a base consolidada por ocorrência. Trata-se de uma fonte pública, amplamente documentada e estruturada, contendo informações detalhadas sobre acidentes em rodovias federais brasileiras, o que a torna altamente adequada ao problema proposto e ao enfoque transacional requerido pela mineração de padrões frequentes.

A base apresenta elevado nível de granularidade, com cada registro correspondendo a uma ocorrência individual de acidente em rodovia federal e contemplando dezenas de atributos distribuídos em múltiplas dimensões analíticas. Compõem o conjunto variáveis temporais (data, dia da semana e horário da ocorrência), espaciais (unidade federativa, município, identificação da BR e quilometragem), ambientais (condição meteorológica, fase do dia e tipo de pista), relativas à infraestrutura viária (traçado, sentido e uso do solo no entorno), à dinâmica do evento (tipo de acidente e causa atribuída) e às consequências registradas (classificação da gravidade, número de envolvidos, feridos leves, feridos graves e óbitos). Essa diversidade de atributos possibilita a construção de representações multidimensionais das ocorrências, favorecendo a identificação de padrões complexos de ocorrência entre fatores ambientais, viários e comportamentais. 

Para garantir viabilidade computacional e maior foco analítico, será realizado um recorte geográfico concentrado no estado de Minas Gerais, que possui uma das maiores malhas rodoviárias do país e volume expressivo de ocorrências registradas. Esse recorte permite equilibrar escala e profundidade analítica, mantendo representatividade sem comprometer a eficiência do processamento.

# **Metodologia Preliminar** 

O trabalho deverá ser organizado de forma coerente com o framework CRISP-DM, seguindo as fases:

* **Business & Data Understanding:**  
  Definição do contexto, objetivos e problema analítico. Será realizada a compreensão da base da Polícia Rodoviária Federal, incluindo análise exploratória inicial para identificar distribuições, padrões básicos e possíveis inconsistências nos dados (como valores ausentes ou categorias dominantes).  
* **Data Preparation:**  
  Etapa crítica envolvendo limpeza, seleção e transformação dos dados. Variáveis numéricas contínuas (ex: idade, quilometragem) serão discretizadas em intervalos, enquanto atributos categóricos serão convertidos para uma representação transacional (itens binários). Será dada atenção ao controle da granularidade para evitar explosão de itens pouco frequentes, que prejudicam a mineração.  
* **Modeling:**  
  Aplicação do método principal. Inicialmente, técnicas de clustering serão utilizadas para segmentar a base em subconjuntos mais homogêneos. Em seguida, o algoritmo FP-Growth será aplicado em cada segmento para extração de itemsets frequentes e geração de regras de associação.  
* **Evaluation:**  
  Análise crítica dos resultados obtidos. As regras serão filtradas com base em métricas como suporte, confiança e lift, além de critérios de não redundância e interpretabilidade. Também serão discutidas limitações do modelo e riscos de interpretações indevidas, especialmente no que se refere à distinção entre correlação e causalidade.


# **Diretrizes de IA Responsável** 

O projeto incorporará explicitamente duas diretrizes de IA responsável: Explicabilidade e Monitoramento e Avaliação. Essas diretrizes foram escolhidas por sua relação direta com o método adotado, com o domínio analisado e com a necessidade de interpretar os resultados de forma crítica e responsável.

**1\. Explicabilidade**  
**Por que ela é pertinente:** A explicabilidade é uma diretriz fundamental neste projeto, pois a mineração de regras de associação pode gerar uma grande quantidade de padrões, nem todos necessariamente úteis, compreensíveis ou relevantes. Como o objetivo do projeto é identificar combinações de fatores associadas à gravidade de acidentes em rodovias federais, é essencial que os resultados possam ser interpretados de forma clara.

Além disso, o domínio de segurança viária envolve consequências sociais relevantes. Regras mal interpretadas podem levar a conclusões equivocadas, como atribuir causalidade a uma simples associação estatística ou supervalorizar padrões pouco representativos. Portanto, os resultados precisam ser apresentados de maneira compreensível, acompanhados de métricas e explicações que deixem claro seu significado e suas limitações.

**Como foi incorporada ao projeto**: A explicabilidade será incorporada ao projeto por meio da seleção, filtragem e apresentação das regras de associação geradas. Serão priorizadas regras com antecedentes curtos, interpretação clara e métricas relevantes, como suporte, confiança, lift, leverage e conviction.

As regras selecionadas serão acompanhadas de uma explicação textual, indicando o que o padrão representa no contexto dos acidentes analisados. Além disso, regras excessivamente longas, redundantes, triviais ou de difícil interpretação serão removidas ou despriorizadas, a fim de evitar a apresentação de um grande volume de padrões pouco informativos.

Também será explicitada a diferença entre associação e causalidade. As regras encontradas não serão tratadas como prova de que determinados fatores causam acidentes graves, mas sim como evidências de coocorrência entre condições presentes nos dados analisados.

**Quais impactos, limitações ou trade-offs ela gerou**: A adoção da explicabilidade melhora a qualidade da análise e facilita a comunicação dos resultados, tornando as regras mais compreensíveis e úteis para interpretação. No entanto, essa escolha também gera trade-offs.

Ao priorizar regras mais simples e interpretáveis, pode-se deixar de lado padrões mais complexos que, embora potencialmente relevantes, seriam difíceis de explicar ou comunicar. Além disso, o processo de filtragem pode reduzir o número de regras analisadas, exigindo critérios cuidadosos para não descartar padrões importantes.

Outro impacto é a necessidade de complementar as métricas quantitativas com uma análise qualitativa das regras, o que aumenta o esforço de avaliação. Ainda assim, esse cuidado é necessário para garantir que os resultados sejam não apenas estatisticamente interessantes, mas também compreensíveis e responsáveis.

**2\. Monitoramento e Avaliação**  
**Por que ela é pertinente**: A diretriz de monitoramento e avaliação é pertinente porque os padrões associados à gravidade dos acidentes podem mudar ao longo do tempo. Fatores como alterações na legislação de trânsito, mudanças na infraestrutura das rodovias, variações no fluxo de veículos, evolução tecnológica da frota e mudanças nas políticas de fiscalização podem influenciar a dinâmica dos acidentes.

Dessa forma, uma regra identificada em um determinado período pode não permanecer válida em anos posteriores. Avaliar a estabilidade temporal dos padrões é importante para evitar que conclusões sejam baseadas em relações pontuais, transitórias ou específicas de um intervalo de tempo.

**Como foi incorporada ao projeto**: Essa diretriz será incorporada por meio da avaliação temporal das regras de associação. O pipeline de mineração poderá ser executado em diferentes janelas de tempo, como anos individuais ou grupos de anos, permitindo comparar os padrões encontrados em cada período.

As regras serão analisadas quanto à sua recorrência e estabilidade. Regras que aparecem de forma consistente em diferentes períodos serão consideradas mais robustas e receberão maior atenção na análise. Por outro lado, regras que surgirem apenas em uma janela temporal específica serão interpretadas com cautela, podendo indicar padrões transitórios, mudanças contextuais ou ruído nos dados.

Além disso, a avaliação dos resultados não se limitará às métricas tradicionais de regras de associação. Também serão considerados aspectos como estabilidade temporal, interpretabilidade, não redundância e relevância para o problema investigado.

**Quais impactos, limitações ou trade-offs ela gerou**: A incorporação de monitoramento e avaliação torna a análise mais robusta, pois permite verificar se os padrões encontrados são consistentes ao longo do tempo ou se dependem de períodos específicos. Isso contribui para uma interpretação mais cuidadosa dos resultados e reduz o risco de generalizações indevidas.

Por outro lado, essa abordagem aumenta a complexidade experimental do projeto. Executar a mineração em diferentes janelas temporais exige maior organização do pipeline, mais etapas de comparação e maior custo computacional.

Além disso, ao dividir a base por períodos, o número de registros em cada subconjunto diminui. Isso pode reduzir o suporte de algumas regras e dificultar a identificação de padrões estatisticamente robustos, especialmente para acidentes graves ou fatais, que tendem a ser menos frequentes. Portanto, será necessário equilibrar granularidade temporal e volume de dados disponível para garantir uma análise confiável.

# **Referências**

* ZAKI, M. J.; MEIRA JR, W. Data Mining and Machine Learning: Fundamental Concepts and Algorithms. 2nd Edition. Cambridge University Press, 2020\.  
* WIRTH, R.; HIPP, J. CRISP-DM: Towards a standard process model for data mining. In: Proceedings of the 4th international conference on the practical applications of knowledge discovery and data mining, 2000\.  
* BRASIL. Polícia Rodoviária Federal. **Dados Abertos da PRF**. Brasília. Disponível em: [https://www.gov.br/prf/pt-br/acesso-a-informacao/dados-abertos/dados-abertos-da-prf](https://www.gov.br/prf/pt-br/acesso-a-informacao/dados-abertos/dados-abertos-da-prf).