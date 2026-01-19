# Solucionador de Problema de Roteirização de Veículos (VRP) com Algoritmo Genético

Este projeto implementa um Algoritmo Genético (AG) para resolver uma variação complexa do Problema de Roteirização de Veículos (VRP). A solução é visualizada em tempo real usando a biblioteca Pygame.

## Visão Geral

O objetivo é encontrar as rotas ótimas para uma frota de veículos que parte de um depósito principal, realiza uma série de entregas em diferentes cidades e retorna a um dos múltiplos depósitos disponíveis. O problema é baseado no benchmark `att48` e inclui as seguintes restrições:

*   **Múltiplos Depósitos:** Existem várias bases que podem ser usadas para reabastecimento e como ponto final das rotas.
*   **Autonomia do Veículo:** Os veículos têm uma autonomia limitada e precisam reabastecer na base mais próxima quando o combustível não é suficiente para chegar ao próximo destino e, de lá, a uma base.
*   **Janelas de Tempo e Prioridades:** Cada entrega tem um prazo e pode ser classificada como "crítica". Atrasos geram penalidades na função de custo, com pesos maiores para entregas críticas.

## Funcionalidades

*   **Algoritmo Genético:** Utiliza elitismo, seleção por roleta, crossover de ordem (OX1) e mutação de troca (swap mutation).
*   **Visualização em Tempo Real:** Uma interface Pygame exibe as cidades, as melhores rotas da geração atual, um gráfico de convergência do fitness e informações detalhadas da execução.
*   **Modelo de Custo Complexo:** A função de fitness combina a distância total percorrida com penalidades quadráticas por atrasos, incentivando soluções que são tanto curtas quanto pontuais.
*   **Lógica de Reabastecimento Inteligente:** O algoritmo decide proativamente quando um veículo deve desviar para uma base para reabastecer.
*   **Salvamento de Resultados:** A cada `N` gerações, o sistema salva uma captura de tela e um arquivo JSON com os dados da melhor solução daquela geração.
*   **Análise com IA Generativa:** O projeto possui uma funcionalidade para, periodicamente, enviar os dados da melhor solução para uma API de IA (como o Gemini) e gerar um relatório técnico. Esses relatórios analisam a viabilidade da solução, a eficiência da rota e sugerem melhorias, atuando como um especialista em Pesquisa Operacional.
*   **Rastreamento da Melhor Solução:** O sistema mantém e atualiza constantemente os arquivos `best_solution_ever.json` e `best_solution_ever.png` com a melhor solução encontrada em toda a execução.

## Como Funciona

### Representação do Cromossomo

Cada indivíduo (cromossomo) na população representa uma ordem de visitação para as cidades de entrega. É uma permutação dos índices das cidades que não são bases. O algoritmo então constrói o caminho completo, inserindo o depósito inicial, as paradas para reabastecimento e o depósito final.

### Função de Fitness

O custo (fitness) de uma rota é calculado como:
`Custo Total = Distância Total Percorrida + Penalidade Total`

*   **Distância Total:** Soma das distâncias euclidianas de todo o percurso, incluindo os desvios para reabastecimento.
*   **Penalidade Total:** Calculada com base nos atrasos. Se `tempo_chegada > prazo_entrega`, uma penalidade é adicionada: `penalidade = (atraso^2) * PESO`. O `PESO` é maior para entregas críticas.

### Estrutura do Código

*   `tsp.py`: O arquivo principal que gerencia a simulação do Pygame, o loop do algoritmo genético e a visualização dos dados.
*   `genetic_algorithm.py`: Contém a lógica central do AG, incluindo a função de fitness, operadores de crossover e mutação, e a lógica de cálculo de rotas com reabastecimento.
*   `benchmark_att48.py`: Fornece as coordenadas das 48 cidades do problema benchmark.
*   `draw_functions.py`: Funções auxiliares para desenhar os elementos na tela do Pygame.
*   `results/`: Diretório onde as capturas de tela e os arquivos JSON de resultados são salvos.

## Como Executar

### Pré-requisitos

Certifique-se de ter o Python 3 instalado. Em seguida, instale as bibliotecas necessárias:

```bash
pip install -r requirements.txt
```

### Configuração

Você pode ajustar os hiperparâmetros do algoritmo diretamente nos arquivos:

*   **Em `tsp.py`:**
    *   `POPULATION_SIZE`: Tamanho da população.
    *   `MUTATION_PROBABILITY`: Probabilidade de mutação.
    *   `BASE_INDICES`: Índices das cidades que funcionam como depósitos/bases.
*   **Em `genetic_algorithm.py`:**
    *   `VELOCIDADE`: Velocidade do veículo (km/h), usada para calcular o tempo de viagem.
    *   `PESO_CRITICO` / `PESO_REGULAR`: Pesos para as penalidades de atraso.
    *   `VEHICLE_AUTONOMY`: Autonomia do veículo em quilômetros.

### Execução

Para iniciar a simulação, execute o seguinte comando no terminal:

```bash
python tsp.py
```

A janela do Pygame será aberta e o algoritmo começará a evoluir. Pressione `Q` para encerrar a simulação.

## Análise dos Resultados

Os resultados são salvos no diretório `results/`.

*   `data_gen_XXXX.json`: Contém os detalhes da melhor solução na geração `XXXX`, incluindo custo, distância, penalidade, ordem de entrega e o caminho completo com as bases.
*   `screenshot_gen_XXXX.png`: Uma imagem da visualização na geração `XXXX`.
*   `data_gen_XXXX.txt`: Um relatório técnico gerado por IA que analisa a solução do arquivo `.json` correspondente, oferecendo uma perspectiva de Pesquisa Operacional sobre a viabilidade e eficiência da rota.
*   `best_solution_ever.json` e `best_solution_ever.png`: O melhor resultado encontrado durante toda a execução, atualizado em tempo real.

Esses arquivos são essenciais para analisar a convergência do algoritmo e a qualidade logística das rotas encontradas.