"""
Script principal para execução do Algoritmo Genético para o Problema de Roteirização de Veículos (VRP).
Este script inicializa o Pygame, configura os parâmetros do problema e do AG,
e executa o loop principal de evolução e visualização.
"""

# --- Importações ---
# Bibliotecas padrão
import sys
import random
import itertools
import os
import json
import threading
import google.generativeai as genai

# Bibliotecas de terceiros
import pygame
from pygame.locals import *
import numpy as np
from dotenv import load_dotenv
load_dotenv()


# Módulos locais
from benchmark_att48 import att_48_cities_locations
from draw_functions import (
    draw_paths, draw_plot, draw_cities, draw_text,
    draw_stats_panel, draw_legend, draw_header, Colors, draw_panel
)
from genetic_algorithm import (
    mutate, 
    order_crossover, 
    calculate_fitness, 
    sort_population, 
    create_distance_matrix,
    VEHICLE_AUTONOMY,
    VELOCIDADE
)


# Define constant values
# --- Constantes de Configuração ---

# Configurações da Janela Pygame
WIDTH, HEIGHT = 1600, 900
NODE_RADIUS = 12
FPS = 120
PLOT_X_OFFSET = 450

# Parâmetros do Algoritmo Genético
POPULATION_SIZE = 1000
MUTATION_PROBABILITY = 0.9 # Probabilidade alta para maior exploração

# Cores para Visualização - Tema Futurista (importado de draw_functions)

# Configurações do Problema de Roteirização
# Índices das cidades que funcionarão como bases/depósitos.
BASE_INDICES = [0, 10, 20, 30, 47] 


# Configura um id único para cada resultado baseado nos paramentos
id_execucao = f"VRP_AG_POP{POPULATION_SIZE}_MUT{int(MUTATION_PROBABILITY*100)}_VELOC{int(VELOCIDADE)}_AUTON{int(VEHICLE_AUTONOMY)}"

# Configurações de Salvamento de Resultados
RESULTS_DIR = rf"results\{id_execucao}"
SAVE_INTERVAL = 2000 # Salva resultados a cada 2000 gerações

# --- Função Principal ---
def main():
    """
    Função principal que executa o simulador do Algoritmo Genético.
    """
    # --- 1. Inicialização do Problema ---
    
    # Carrega as coordenadas do benchmark att48 (1 unidade = 1 KM)
    benchmark_coords = np.array(att_48_cities_locations)
    N_CITIES = len(benchmark_coords)

    # Cria a matriz de distâncias usando as coordenadas originais em KM.
    dist_matrix = create_distance_matrix(benchmark_coords)

    # Gera a população inicial. Cada cromossomo é uma permutação das cidades de entrega.
    delivery_cities_indices = [i for i in range(N_CITIES) if i not in BASE_INDICES]
    population = [random.sample(delivery_cities_indices, len(delivery_cities_indices)) for _ in range(POPULATION_SIZE)]

    # --- 2. Geração de Dados de Entrega (Prazos, Criticidade) ---
    # Define prazos e criticidade aleatórios para cada cidade.
    delivery_data = {}
    random.seed(42) # Garante que os dados sejam os mesmos a cada execução
    for i in range(N_CITIES):
        is_base = i in BASE_INDICES
        delivery_data[i] = {
            'prazo': 99999 if is_base else (8.0 if random.random() < 0.30 else 24.0),
            'critico': False if is_base else (random.random() < 0.30),
            'demanda': 0 if is_base else random.randint(1, 5),
            'is_base': is_base,
            'is_main_base': i == BASE_INDICES[0] if is_base else False
        }

    # --- 3. Inicialização do Pygame e Visualização ---
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("🚀 VRP Solver - Algoritmo Genético | Otimização de Rotas")
    clock = pygame.time.Clock()
    generation_counter = itertools.count(start=1)

    # Calcula as coordenadas para desenho na tela (escalonado)
    max_x = max(point[0] for point in benchmark_coords)
    max_y = max(point[1] for point in benchmark_coords)
    scale_x = (WIDTH - PLOT_X_OFFSET - 2 * NODE_RADIUS) / max_x
    scale_y = (HEIGHT - 2 * NODE_RADIUS) / max_y

    cities_draw_locations = [(int(point[0] * scale_x + PLOT_X_OFFSET + NODE_RADIUS),
                            int(point[1] * scale_y + NODE_RADIUS)) for point in benchmark_coords]

    # Cria o diretório de resultados se ele não existir
    if not os.path.exists(RESULTS_DIR):
        os.makedirs(RESULTS_DIR)

    # --- 4. Loop Principal do Algoritmo Genético ---
    best_fitness_history = []
    all_time_best_fitness = float('inf')
    running = True

    GEMINI_API_KEY = os.getenv("API_KEY")

    if not GEMINI_API_KEY:
        raise RuntimeError("API Key do Gemini não encontrada!")

    genai.configure(api_key=GEMINI_API_KEY)

    def quebrar_texto(texto, fonte, largura_max):
        palavras = texto.split(" ")
        linhas = []
        linha_atual = ""

        for palavra in palavras:
            teste = linha_atual + palavra + " "
            if fonte.size(teste)[0] <= largura_max:
                linha_atual = teste
            else:
                linhas.append(linha_atual)
                linha_atual = palavra + " "

        if linha_atual:
            linhas.append(linha_atual)

        return linhas

    def perguntar(prompt: str) -> str:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text

    def chamar_gemini(prompt, timestamp):
        global texto_gemini, processando
        texto_gemini = perguntar(prompt)
        processando = False
        data_path = os.path.join(RESULTS_DIR, f"data_{timestamp}.txt")
        with open(data_path, 'w') as f:
            f.write(texto_gemini)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False

        generation = next(generation_counter)
        
        # Fundo escuro moderno com gradiente sutil
        screen.fill(Colors.BACKGROUND)
        
        # Desenha grid de fundo sutil na área do mapa
        grid_surface = pygame.Surface((WIDTH - PLOT_X_OFFSET, HEIGHT), pygame.SRCALPHA)
        for x in range(0, WIDTH - PLOT_X_OFFSET, 50):
            pygame.draw.line(grid_surface, (30, 30, 60, 50), (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, 50):
            pygame.draw.line(grid_surface, (30, 30, 60, 50), (0, y), (WIDTH - PLOT_X_OFFSET, y))
        screen.blit(grid_surface, (PLOT_X_OFFSET, 0))


        # 3. CÁLCULO DE FITNESS: Calcula o fitness para toda a população.
        # O caminho completo não é necessário aqui para economizar tempo.
        population_fitness = [calculate_fitness(ind, dist_matrix, delivery_data, BASE_INDICES) for ind in population]
        
        # Ordenar população (Melhores primeiro)
        population, population_fitness = sort_population(population, population_fitness)

        # --- Visualização e Análise dos Melhores Indivíduos ---
        # Para os 3 melhores indivíduos, recalcula o fitness para obter os detalhes completos para visualização.
        # Nota: Esta é uma simplificação. Em uma implementação de alta performance, os detalhes poderiam ser
        # armazenados durante o primeiro cálculo de fitness para evitar recálculos.
        
        # Melhor indivíduo
        best_chromosome = population[0]
        best_fitness, best_details = calculate_fitness(best_chromosome, dist_matrix, delivery_data, BASE_INDICES, return_full_path=True)
        best_full_path_indices = best_details["full_path"]
        best_dist = best_details["distance"]
        best_penalty = best_details["penalty"]
        best_refuels = best_details["refuel_stops"]
        best_path_coords = [cities_draw_locations[i] for i in best_full_path_indices]

        # Segundo melhor indivíduo
        _, second_best_details = calculate_fitness(population[1], dist_matrix, delivery_data, BASE_INDICES, return_full_path=True)
        second_best_path_indices = second_best_details["full_path"]
        second_best_coords = [cities_draw_locations[i] for i in second_best_path_indices]

        # Terceiro melhor indivíduo
        _, third_best_details = calculate_fitness(population[2], dist_matrix, delivery_data, BASE_INDICES, return_full_path=True)
        third_best_path_indices = third_best_details["full_path"]
        third_best_coords = [cities_draw_locations[i] for i in third_best_path_indices]

        # --- DESENHO ---
        best_fitness_history.append(best_fitness)
        
        # Cabeçalho elegante
        draw_header(screen, "VRP - ALGORITMO GENÉTICO", "Sistema de Otimização de Rotas de Veículos")
        
        # Desenha as rotas da pior para a melhor, para que a melhor fique por cima
        draw_paths(screen, third_best_coords, Colors.ROUTE_THIRD, width=2, dash=True)
        draw_paths(screen, second_best_coords, Colors.ROUTE_SECOND, width=2)
        draw_paths(screen, best_path_coords, Colors.ROUTE_BEST, width=4, glow=True)
        
        # Desenha cidades com efeitos visuais
        draw_cities(screen, cities_draw_locations, delivery_data, NODE_RADIUS, generation)
        
        # Painel de gráfico
        draw_plot(screen, list(range(len(best_fitness_history))), best_fitness_history, 
                  y_label="Fitness (Custo)", plot_position=(15, 80))
        
        # Painel de estatísticas
        stats = {
            'generation': generation,
            'best_cost': best_fitness,
            'distance': best_dist,
            'penalty': best_penalty,
            'refuel_stops': best_refuels,
            'speed': VELOCIDADE,
            'autonomy': VEHICLE_AUTONOMY
        }
        draw_stats_panel(screen, stats, position=(5, 410))
        
        # Legenda
        draw_legend(screen, position=(5, 600))
        
        # Informações de rotas no mapa
        draw_text(screen, f"🏆 Melhor Rota: {round(best_dist, 1)} KM", 
                  (PLOT_X_OFFSET + 10, HEIGHT - 60), Colors.NEON_CYAN, 14, bold=True)
        draw_text(screen, f"📍 Cidades: {len(best_chromosome)} | 🔋 Recargas: {best_refuels}", 
                  (PLOT_X_OFFSET + 10, HEIGHT - 35), Colors.TEXT_SECONDARY, 13)

        # --- SAVE BEST-EVER INDIVIDUAL ---
        if best_fitness < all_time_best_fitness:
            all_time_best_fitness = best_fitness
            
            best_solution_path = os.path.join(RESULTS_DIR, "best_solution_ever.json")
            best_screenshot_path = os.path.join(RESULTS_DIR, "best_solution_ever.png")
            
            # Prepare the data for the best-ever solution
            best_ever_data = {
                "found_at_generation": generation,
                "best_cost": best_fitness,
                "detalhes": {
                    "distance": best_dist,
                    "penalty": best_penalty,
                    "refuel_stops": best_refuels
                },
                "best_chromosome (delivery_order)": best_chromosome,
                "full_path_with_bases": best_full_path_indices
            }

            # Write the data to a JSON file, overwriting the previous best
            with open(best_solution_path, 'w') as f:
                json.dump(best_ever_data, f, indent=4)
            
            # Save a screenshot of the best-ever solution
            pygame.image.save(screen, best_screenshot_path)
            
            print(f"*** Nova melhor solução encontrada na geração {generation}! Salva em '{best_solution_path}' ***")
        if generation % 100 == 0: # Imprime no console a cada 100 gerações para não poluir
            print(f"Generation {generation}: Best Cost (eq. KM) = {round(best_fitness, 2)} (Dist: {round(best_dist, 2)}, Penalty: {round(best_penalty, 2)}, Refuels: {best_refuels})")

        # --- SAVE RESULTS AT INTERVALS ---
        if generation % SAVE_INTERVAL == 0 or generation == 1:
            # Create a unique filename for this save instance
            timestamp = f"gen_{generation}"
            screenshot_path = os.path.join(RESULTS_DIR, f"screenshot_{timestamp}.png")
            data_path = os.path.join(RESULTS_DIR, f"data_{timestamp}.json")

            # Save the current screen as a PNG image
            pygame.image.save(screen, screenshot_path)

            # Prepare the data to be saved in a JSON file
            results_data = {
                "generation": generation,
                "best_cost": best_fitness,
                "detalhes": {
                    "distance": best_dist,
                    "penalty": best_penalty,
                    "refuel_stops": best_refuels
                },
                "best_chromosome (delivery_order)": best_chromosome,
                "full_path_with_bases": best_full_path_indices
            }

            if generation > 1:
                # Write the data to a JSON file
                with open(data_path, 'w') as f:
                    json.dump(results_data, f, indent=4)

                threading.Thread(target=chamar_gemini(rf'''Atue como um especialista em Pesquisa Operacional e Ciência de Dados. Analise os resultados de uma execução de Algoritmo Genético aplicado ao Problema do Caixeiro Viajante (TSP) 
                                                      com restrições (de tempo de entrega, autonomia dos veículos e prioridades de algumas cidades).
                                                                    Dados da Execução:
                                                                    {results_data}
                                                                    Objetivo: Fornecer um relatório técnico resumido para um trabalho de pós-graduação, abordando:
                                                                    Eficiência de Convergência: O que o 'found_at_generation' indica sobre o esforço computacional?
                                                                    Decomposição do Custo: Analise a relação entre distância real e penalidades. O que o 'best_cost' bilionário sugere sobre a viabilidade da solução?
                                                                    Logística e Roteirização: Interprete a estrutura do 'full_path_with_bases' (uso de bases 0, 10, 20 e paradas de reabastecimento).
                                                                    Conclusão Técnica: A solução é satisfatória ou o algoritmo precisa de ajuste de hiperparâmetros ou da função de fitness?''', timestamp=timestamp), daemon=True).start()
            

            print(f"--- Resultados da geração {generation} salvos no diretório '{RESULTS_DIR}' ---")

        # --- EVOLUÇÃO (GERAR NOVA POPULAÇÃO) ---
        new_population = [population[0]]  # ELITISMO: Mantém o melhor

        while len(new_population) < POPULATION_SIZE:
            # --- Seleção (Roleta) ---
            # A probabilidade de um indivíduo ser escolhido é inversamente proporcional ao seu custo (fitness).
            # Quanto menor o custo, maior a chance de ser selecionado.
            fitness_array = np.array(population_fitness)
            # Adiciona-se um valor pequeno (1e-6) para evitar divisão por zero.
            probabilities = 1.0 / (fitness_array + 1e-6) 
            probabilities /= probabilities.sum() # Normaliza as probabilidades para que somem 1.

            parent1, parent2 = random.choices(population, weights=probabilities, k=2)

            # --- Crossover ---
            child = order_crossover(parent1, parent2)
            
            # --- Mutação ---
            child = mutate(child, MUTATION_PROBABILITY)

            new_population.append(child)

        population = new_population

        # Atualiza a tela
        pygame.display.flip()
        clock.tick(FPS)

    # --- Finalização ---
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
