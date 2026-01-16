import pygame
from pygame.locals import *
import random
import itertools
from draw_functions import draw_paths, draw_plot, draw_cities
import sys
import numpy as np
import pygame
from benchmark_att48 import *
import time

from genetic_algorithm import (
    mutate, 
    order_crossover, 
    generate_random_population, 
    calculate_fitness, 
    sort_population, 
    default_problems,
    create_distance_matrix # Nova função necessária
)

from genetic_algorithm import NUM_VEICULOS
import math
# No topo, importe o NUM_VEICULOS que foi sorteado
#from genetic_algorithm import NUM_VEICULOS, VELOCIDADE, PESO_CRITICO #... e as outras

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
MUTATION_PROBABILITY = 0.2

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)


# Cores exclusivas para cada veículo (1 a 4)
CORES_VEICULOS = [
    (0, 0, 255),     # Azul (Veículo 1)
    (0, 150, 0),     # Verde Escuro (Veículo 2)
    (255, 140, 0),   # Laranja (Veículo 3)
    (150, 0, 150)    # Roxo (Veículo 4)
]

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
att_cities_locations = np.array(att_48_cities_locations)
max_x = max(point[0] for point in att_cities_locations)
max_y = max(point[1] for point in att_cities_locations)
scale_x = (WIDTH - PLOT_X_OFFSET - NODE_RADIUS) / max_x
scale_y = HEIGHT / max_y

cities_locations = [(int(point[0] * scale_x + PLOT_X_OFFSET),
                     int(point[1] * scale_y)) for point in att_cities_locations]

#target_solution = [cities_locations[i-1] for i in att_48_cities_order]
#fitness_target_solution = calculate_fitness(target_solution)
#print(f"Best Solution: {fitness_target_solution}")
# ----- Using att48 benchmark


#cities_locations = default_problems[15]
N_CITIES = len(cities_locations)

# 1. PASSO CRUCIAL: Criar a Matriz de Distâncias uma única vez
dist_matrix = create_distance_matrix(cities_locations)

# 2. PASSO CRUCIAL: Gerar população baseada em ÍNDICES (0 a 14) e não coordenadas
population = generate_random_population(N_CITIES, POPULATION_SIZE)



# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TSP Solver using Pygame")
clock = pygame.time.Clock()
generation_counter = itertools.count(start=1)  # Start the counter at 1


# Create Initial Population
# TODO:- use some heuristic like Nearest Neighbour our Convex Hull to initialize
#population = generate_random_population(cities_locations, POPULATION_SIZE)

#print(f"population: {population}")

#best_fitness_values = []
#best_solutions = []

# --- CONFIGURAÇÃO DE PRAZOS E MEDICAMENTOS ---
#delivery_data = {}
#for i in range(N_CITIES):
#    # Definimos que as cidades com índice par recebem medicamentos críticos
#    is_critico = (i % 3 == 0) 
#    # Críticos: Prazo curto (100-500). Regulares: Prazo longo (1000-3000)
#    prazo = random.randint(100, 500) if is_critico else random.randint(1000, 3000)
#    
#    delivery_data[i] = {
#        'prazo': prazo, 
#        'critico': is_critico,
#        'demanda': random.randint(1, 5) # Futuro: Capacidade de Carga
#    }

# --- CONFIGURAÇÃO DE PRAZOS E MEDICAMENTOS (DINÂMICO 30%) ---
#delivery_data = {}
# Definimos a semente para que as prioridades não mudem a cada frame, 
# mas sejam diferentes a cada execução se desejar (ou fixa para testes)
# random.seed(42)
#for i in range(N_CITIES):
#    # Define aleatoriamente se é crítico (30% de chance)
#    is_critico = random.random() < 0.30
#    
#    # Críticos: Prazo curto (100-500). Regulares: Prazo longo (1000-3000)
#    prazo = random.randint(100, 500) if is_critico else random.randint(1000, 3000)
#    
#    delivery_data[i] = {
#        'prazo': prazo, 
#        'critico': is_critico,
#        'demanda': random.randint(1, 5) # Futuro: Capacidade de Carga
#    }

delivery_data = {}

#random.seed(42)
#random.seed(41)
random.seed(38)
for i in range(N_CITIES):
    if i == 0:
        # Configuração específica para o Depósito (Quadrado Azul)
        is_critico = False
        prazo = 99999  # Prazo muito alto pois é o ponto de partida/retorno
        demanda = 0    # Depósito não consome carga
    else:
        # Define aleatoriamente se é crítico (30% de chance) para as demais cidades
        #random.seed(42)
        is_critico = random.random() < 0.30
        # Críticos: Prazo curto (100-500). Regulares: Prazo longo (1000-3000)
        #prazo = random.randint(100, 500) if is_critico else random.randint(1000, 3000)
        #alterado
        prazo = 400.0 if is_critico else 2500.0
        demanda = random.randint(1, 5)

    delivery_data[i] = {
        'prazo': prazo, 
        'critico': is_critico,
        'demanda': demanda
    }

best_fitness_values = []
best_solutions_history = []


# Preparar divisões de rotas para desenho
def separar_rotas(indices_lista):
    """Auxiliar para transformar o DNA em sub-rotas visuais."""
    cidades = [c for c in indices_lista if c != 0]
    n = len(cidades)
    tam = math.ceil(n / NUM_VEICULOS)
    return [[0] + cidades[i*tam : (i+1)*tam] + [0] for i in range(NUM_VEICULOS)]

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                running = False

    generation = next(generation_counter)
    screen.fill(WHITE)

    # 3. CÁLCULO DE FITNESS: Usando a Matriz para alta performance
    #population_fitness = [calculate_fitness(ind, dist_matrix) for ind in population]
    # 3. CÁLCULO DE FITNESS: Agora passando os dados de entrega
    population_fitness = [calculate_fitness(ind, dist_matrix, delivery_data) for ind in population]

    # Ordenar população (Melhores primeiro)
    population, population_fitness = sort_population(population, population_fitness)

    best_indices = population[0]
    best_fitness = population_fitness[0]
    
    best_fitness_values.append(best_fitness)

    # 4. CONVERSÃO PARA DESENHO: Transformar índices em coordenadas (x, y)
    # Apenas os melhores para não pesar o render
    best_path_coords = [cities_locations[i] for i in best_indices]
    second_best_coords = [cities_locations[i] for i in population[1]]

    # --- DESENHO ---
    # Aqui chamamos suas funções de desenho originais
    #try:
        #from draw_functions import draw_paths, draw_plot, draw_cities
    draw_plot(screen, list(range(len(best_fitness_values))), 
                  best_fitness_values, y_label="Fitness")

    

    # 1. Desenhar SEGUNDA melhor rota (Cinza)
    #segunda_melhor_raw = population[1]
    #rotas_cinza = separar_rotas(segunda_melhor_raw)
    #for r_indices in rotas_cinza:
        #r_coords = [cities_locations[idx] for idx in r_indices]
        #draw_paths(screen, r_coords, GRAY, width=1)

    if len(population) > 1:
        rotas_cinza = separar_rotas(population[1])
        for sub_indices in rotas_cinza:
            coords = [cities_locations[idx] for idx in sub_indices]
            draw_paths(screen, coords, GRAY, width=1)

    # 2. Desenhar MELHOR rota (Colorida por veículo)
    #melhor_raw = population[0]
    #rotas_coloridas = separar_rotas(melhor_raw)
    #for i, r_indices in enumerate(rotas_coloridas):
        #if i < len(CORES_VEICULOS):
            #cor = CORES_VEICULOS[i]
            #r_coords = [cities_locations[idx] for idx in r_indices]
            #draw_paths(screen, r_coords, cor, width=3)

    # 2. Desenhar a MELHOR rota (Colorida por Veículo)
    melhor_solucao = population[0]
    rotas_coloridas = separar_rotas(melhor_solucao)
    
    for i, sub_indices in enumerate(rotas_coloridas):
        if not sub_indices or len(sub_indices) < 2: continue
        
        coords = [cities_locations[idx] for idx in sub_indices]
        cor_veiculo = CORES_VEICULOS[i % len(CORES_VEICULOS)]
        
        # Desenha a linha da rota do veículo i
        draw_paths(screen, coords, cor_veiculo, width=3)


    #draw_cities(screen, cities_locations, RED, NODE_RADIUS)
    # 3. Desenhar as cidades por cima
    draw_cities(screen, cities_locations, delivery_data, NODE_RADIUS)
    
    

    # Desenha a melhor rota em azul
    #draw_paths(screen, best_path_coords, BLUE, width=3)
    # Desenha a segunda melhor em cinza (opcional)
    #draw_paths(screen, second_best_coords, GRAY, width=1)
    #except ImportError:
        # Fallback caso não tenha o arquivo draw_functions
        #for city in cities_locations:
            #pygame.draw.circle(screen, RED, city, NODE_RADIUS)
        #if len(best_path_coords) > 1:
            #pygame.draw.lines(screen, BLUE, True, best_path_coords, 3)

    #print(f"Geracao {generation}: Melhor Fitness = {round(best_fitness, 2)}")
    # Exibir quantos veículos estão operando
    print(f"Geracao {generation}: Veículos: {NUM_VEICULOS} | Melhor Fitness/Custo = {round(best_fitness, 2)}")

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


# TODO: save the best individual in a file if it is better than the one saved.

print("")
print("Processamento finalizado.")
print("Após a última análise pressione 'Q' para sair.")

clock.tick(5) # Baixo FPS apenas para não consumir CPU na pausa

runningFinal = True
while runningFinal:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            runningFinal = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                runningFinal = False
    #print("Iniciando pausa...")
    time.sleep(1)  # Pausa por X segundos - pra nao pesar muito o while
    #print("Fim da pausa.")



# exit software
pygame.quit()
sys.exit()
