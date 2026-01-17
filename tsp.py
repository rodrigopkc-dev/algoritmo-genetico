import threading
import pygame
from pygame.locals import *
import random
import itertools
from draw_functions import draw_paths, draw_plot, draw_cities, draw_text
import sys
import numpy as np
import pygame
import os
import json
from benchmark_att48 import *
import os
import pygame
from google import genai
from dotenv import load_dotenv
load_dotenv()


from genetic_algorithm import (
    mutate, 
    order_crossover, 
    generate_random_population, 
    calculate_fitness, 
    sort_population, 
    default_problems,
    create_distance_matrix,
    VEHICLE_AUTONOMY, # Import the vehicle autonomy constant
    VELOCIDADE
)


# Define constant values
# pygame
WIDTH, HEIGHT = 800, 400
NODE_RADIUS = 10
FPS = 30
PLOT_X_OFFSET = 450

# GA
#N_CITIES = 15
#POPULATION_SIZE = 100
POPULATION_SIZE = 1000
#POPULATION_SIZE = 2
#POPULATION_SIZE = 50

N_GENERATIONS = None
#MUTATION_PROBABILITY = 0.1
# MUTATION_PROBABILITY = 0.5
MUTATION_PROBABILITY = 0.9


# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)
GREEN = (0, 255, 0)
BASE_INDICES = [0, 10, 20, 30, 47] # Define multiple bases: main depot + 3 others

# Saving results
RESULTS_DIR = "results"
SAVE_INTERVAL = 2000 # Save results every 5000 generations


# Initialize problem
# Using Random cities generation
#cities_locations = [(random.randint(NODE_RADIUS + PLOT_X_OFFSET, WIDTH - NODE_RADIUS), random.randint(NODE_RADIUS, HEIGHT - NODE_RADIUS))
#                     for _ in range(N_CITIES)]

#print(f"Cities_locations: {cities_locations}")

# # # Using Deault Problems: 10, 12 or 15
# WIDTH, HEIGHT = 800, 400
#cities_locations = default_problems[15]
#cities_locations = default_problems[15]


# Using att48 benchmark
WIDTH, HEIGHT = 1500, 800
# As coordenadas originais do benchmark (1 unidade = 1 KM) são usadas para a lógica
att_cities_locations = np.array(att_48_cities_locations)

# As localizações na tela são escaladas apenas para fins de visualização
max_x = max(point[0] for point in att_cities_locations)
max_y = max(point[1] for point in att_cities_locations)
scale_x = (WIDTH - PLOT_X_OFFSET - 2 * NODE_RADIUS) / max_x
scale_y = (HEIGHT - 2 * NODE_RADIUS) / max_y

cities_draw_locations = [(int(point[0] * scale_x + PLOT_X_OFFSET + NODE_RADIUS),
                        int(point[1] * scale_y + NODE_RADIUS)) for point in att_cities_locations]

N_CITIES = len(att_cities_locations)

# 1. PASSO CRUCIAL: Criar a Matriz de Distâncias uma única vez
# Usando as coordenadas originais em KM.
dist_matrix = create_distance_matrix(att_cities_locations)

# 2. PASSO CRUCIAL: Gerar população baseada em ÍNDICES de ENTREGA
# O cromossomo (rota) é uma permutação apenas das cidades de entrega, excluindo os depósitos.
delivery_cities_indices = [i for i in range(N_CITIES) if i not in BASE_INDICES]
population = [random.sample(delivery_cities_indices, len(delivery_cities_indices)) for _ in range(POPULATION_SIZE)]


# Create results directory if it doesn't exist
if not os.path.exists(RESULTS_DIR):
    os.makedirs(RESULTS_DIR)

GEMINI_API_KEY = os.getenv("API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("API Key do Gemini não encontrada!")

client = genai.Client()

texto_gemini = "Pressione ESPAÇO para gerar relatório."
processando = False

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
    response = client.models.generate_content(
    model="gemini-3-flash-preview", contents=prompt
)
    return response.text

def desenhar_caixa_texto(tela, texto, x, y, largura, altura, fonte, cor_texto=(255, 255, 255), cor_fundo=(30, 30, 30), cor_borda=(200, 200, 200), padding=10):
    # Fundo
    pygame.draw.rect(tela, cor_fundo, (x, y, largura, altura))
    # Borda
    pygame.draw.rect(tela, cor_borda, (x, y, largura, altura), 2)

    print(texto)

    linhas = quebrar_texto(texto, fonte, largura - 2 * padding)

    y_texto = y + padding
    for linha in linhas:
        render = fonte.render(linha, True, cor_texto)
        tela.blit(render, (x + padding, y_texto))
        y_texto += fonte.get_height()

        if y_texto > y + altura - padding:
            break  # evita desenhar fora da caixa

def chamar_gemini(prompt, timestamp):
    global texto_gemini, processando
    texto_gemini = perguntar(prompt)
    processando = False
    data_path = os.path.join(RESULTS_DIR, f"data_{timestamp}.txt")
    with open(data_path, 'w') as f:
        f.write(texto_gemini)



# Initialize Pygame
pygame.init()
fonte = pygame.font.SysFont(None, 24)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TSP Solver using Pygame")
clock = pygame.time.Clock()
generation_counter = itertools.count(start=1)  # Start the counter at 1

delivery_data = {}

random.seed(42)
for i in range(N_CITIES):
    if i in BASE_INDICES:
        # Configuração específica para as Bases
        is_critico = False
        prazo = 99999
        demanda = 0
        is_base = True
        is_main_base = (i == BASE_INDICES[0])
    else:
        # Configuração para cidades de entrega
        is_critico = random.random() < 0.30
        prazo = 8.0 if is_critico else 24.0  # Prazos em horas
        demanda = random.randint(1, 5) # Unidades de demanda
        is_base = False
        is_main_base = False

    delivery_data[i] = {
        'prazo': prazo, 
        'critico': is_critico,
        'demanda': demanda,
        'is_base': is_base, # Add this flag for drawing
        'is_main_base': is_main_base
    }

best_fitness_values = []
best_solutions_history = []

# Variable to track the best-ever solution found, initialized to infinity
all_time_best_fitness = float('inf')

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                running = False
            # elif event.key == pygame.K_SPACE and not processando:
            #     processando = True
            #     texto_gemini = "Pensando..."
            #     with open(r'F:\Projetos_Pessoais\algoritmo-genetico\results\best_solution_ever.json') as f:
            #         resultado = json.load(f)
                

    generation = next(generation_counter)
    screen.fill(WHITE)
    desenhar_caixa_texto(
        tela=screen,
        texto=texto_gemini,
        x=50,
        y=400,
        largura=700,
        altura=150,
        fonte=fonte
    )

    # 3. CÁLCULO DE FITNESS: Calcula o fitness para toda a população.
    # O caminho completo não é necessário aqui para economizar tempo.
    population_fitness = [calculate_fitness(ind, dist_matrix, delivery_data, BASE_INDICES) for ind in population]

    # Ordenar população (Melhores primeiro)
    population, population_fitness = sort_population(population, population_fitness)

    # Para o MELHOR indivíduo, recalcula o fitness para obter o caminho completo para visualização.
    best_chromosome = population[0]
    best_fitness, best_details = calculate_fitness(best_chromosome, dist_matrix, delivery_data, BASE_INDICES, return_full_path=True)
    best_full_path_indices = best_details["full_path"]
    best_dist = best_details["distance"]
    best_penalty = best_details["penalty"]
    best_refuels = best_details["refuel_stops"]

    best_fitness_values.append(best_fitness)

    # --- SAVE BEST-EVER INDIVIDUAL ---
    if best_fitness < all_time_best_fitness:
        all_time_best_fitness = best_fitness
        
        best_solution_path = os.path.join(RESULTS_DIR, "best_solution_ever.json")
        best_screenshot_path = os.path.join(RESULTS_DIR, "best_solution_ever.png")
        
        # Prepare the data for the best-ever solution
        best_ever_data = {
            "found_at_generation": generation,
            "best_cost": best_fitness,
            "details": {
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
        
        print(f"*** New all-time best solution found at gen {generation}! Saved to '{best_solution_path}' and screenshot to '{best_screenshot_path}' ***")

    # 4. CONVERSÃO PARA DESENHO: Transformar os índices do caminho completo em coordenadas (x, y)
    best_path_coords = [cities_draw_locations[i] for i in best_full_path_indices]
    # Opcional: desenhar a segunda melhor rota também
    _, second_best_details = calculate_fitness(population[1], dist_matrix, delivery_data, BASE_INDICES, return_full_path=True)
    second_best_path_indices = second_best_details["full_path"]
    second_best_coords = [cities_draw_locations[i] for i in second_best_path_indices]
    # Opcional: desenhar a terceira melhor rota também
    _, third_best_details = calculate_fitness(population[2], dist_matrix, delivery_data, BASE_INDICES, return_full_path=True)
    third_best_path_indices = third_best_details["full_path"]
    third_best_coords = [cities_draw_locations[i] for i in third_best_path_indices]

    # --- DESENHO ---
    draw_plot(screen, list(range(len(best_fitness_values))), 
                best_fitness_values, y_label="Fitness")
        
    draw_cities(screen, cities_draw_locations, delivery_data, NODE_RADIUS)

    # Desenha as rotas da pior para a melhor, para que a melhor fique por cima
    draw_paths(screen, third_best_coords, GREEN, width=1)
    draw_paths(screen, second_best_coords, GRAY, width=1)
    draw_paths(screen, best_path_coords, BLUE, width=3)

    # --- DISPLAY INFO ON SCREEN ---
    info_text_1 = f"Generation: {generation} | Best Cost (eq. KM): {round(best_fitness, 2)}"
    info_text_2 = f"  Distance (KM): {round(best_dist, 2)} | Penalty (eq. KM): {round(best_penalty, 2)}"
    info_text_3 = f"  Refuel Stops: {best_refuels} | Speed: {VELOCIDADE} KM/h"
    info_text_4 = f"Vehicle Autonomy: {VEHICLE_AUTONOMY} KM"
    draw_text(screen, info_text_1, (PLOT_X_OFFSET + 10, 10), BLACK)
    draw_text(screen, info_text_2, (PLOT_X_OFFSET + 10, 30), BLACK)
    draw_text(screen, info_text_3, (PLOT_X_OFFSET + 10, 50), BLACK)
    draw_text(screen, info_text_4, (PLOT_X_OFFSET + 10, 70), BLACK)

    if generation % 100 == 0: # Print to console every 10 generations to reduce clutter
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
            "details": {
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
            
        

        print(f"--- Saved results for generation {generation} to '{RESULTS_DIR}' directory ---")

    # --- EVOLUÇÃO (GERAR NOVA POPULAÇÃO) ---
    new_population = [population[0]]  # ELITISMO: Mantém o melhor

    while len(new_population) < POPULATION_SIZE:

        #print(f"len(new_population): {len(new_population)}")

        # selection
        # simple selection based on first 10 best solutions
        # parent1, parent2 = random.choices(population[:10], k=2)

        # Seleção por probabilidade (Roleta baseada no inverso da distância)
        # Quanto menor a distância, maior a probabilidade
        fitness_array = np.array(population_fitness)
        # Evitar divisão por zero e inverter (minimização)
        probability = 1.0 / (fitness_array + 1e-6) 
        probability /= probability.sum()

        parents = random.choices(population, weights=probability, k=2)
        parent1, parent2 = parents[0], parents[1]

        # Crossover e Mutação trabalham com listas de inteiros agora
        child = order_crossover(parent1, parent2)
        child = mutate(child, MUTATION_PROBABILITY)

        new_population.append(child)

    population = new_population

    pygame.display.flip()
    clock.tick(FPS)


# exit software
pygame.quit()
sys.exit()
