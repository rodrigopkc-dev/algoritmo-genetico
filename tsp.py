import pygame
from pygame.locals import *
import random
import itertools
from draw_functions import draw_paths, draw_plot, draw_cities
import sys
import numpy as np
import pygame
from benchmark_att48 import *

from genetic_algorithm import (
    mutate, 
    order_crossover, 
    generate_random_population, 
    calculate_fitness, 
    sort_population, 
    default_problems,
    create_distance_matrix # Nova função necessária
)


# Define constant values
# pygame
WIDTH, HEIGHT = 800, 400
NODE_RADIUS = 10
FPS = 30
PLOT_X_OFFSET = 450

# GA
#N_CITIES = 15
POPULATION_SIZE = 100
#POPULATION_SIZE = 2
#POPULATION_SIZE = 50

N_GENERATIONS = None
MUTATION_PROBABILITY = 0.5

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)


# Initialize problem
# Using Random cities generation
#cities_locations = [(random.randint(NODE_RADIUS + PLOT_X_OFFSET, WIDTH - NODE_RADIUS), random.randint(NODE_RADIUS, HEIGHT - NODE_RADIUS))
#                     for _ in range(N_CITIES)]

#print(f"Cities_locations: {cities_locations}")

# # # Using Deault Problems: 10, 12 or 15
# WIDTH, HEIGHT = 800, 400
#cities_locations = default_problems[15]
#cities_locations = default_problems[15]

cities_locations = default_problems[15]
N_CITIES = len(cities_locations)


# Using att48 benchmark
WIDTH, HEIGHT = 1500, 800
att_cities_locations = np.array(att_48_cities_locations)
max_x = max(point[0] for point in att_cities_locations)
max_y = max(point[1] for point in att_cities_locations)
scale_x = (WIDTH - PLOT_X_OFFSET - NODE_RADIUS) / max_x
scale_y = HEIGHT / max_y

#cities_locations = [(int(point[0] * scale_x + PLOT_X_OFFSET),
#                     int(point[1] * scale_y)) for point in att_cities_locations]

#target_solution = [cities_locations[i-1] for i in att_48_cities_order]
#fitness_target_solution = calculate_fitness(target_solution)
#print(f"Best Solution: {fitness_target_solution}")
# ----- Using att48 benchmark

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

best_fitness_values = []
best_solutions_history = []


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
    population_fitness = [calculate_fitness(ind, dist_matrix) for ind in population]

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
                  best_fitness_values, y_label="Distancia (px)")
        
    draw_cities(screen, cities_locations, RED, NODE_RADIUS)
    # Desenha a melhor rota em azul
    draw_paths(screen, best_path_coords, BLUE, width=3)
    # Desenha a segunda melhor em cinza (opcional)
    draw_paths(screen, second_best_coords, GRAY, width=1)
    #except ImportError:
        # Fallback caso não tenha o arquivo draw_functions
        #for city in cities_locations:
            #pygame.draw.circle(screen, RED, city, NODE_RADIUS)
        #if len(best_path_coords) > 1:
            #pygame.draw.lines(screen, BLUE, True, best_path_coords, 3)

    print(f"Geracao {generation}: Melhor Distancia = {round(best_fitness, 2)}")

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

# exit software
pygame.quit()
sys.exit()
