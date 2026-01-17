import random
import math
import copy
from typing import List, Tuple, Union

default_problems = {
5: [(733, 251), (706, 87), (546, 97), (562, 49), (576, 253)],
10:[(470, 169), (602, 202), (754, 239), (476, 233), (468, 301), (522, 29), (597, 171), (487, 325), (746, 232), (558, 136)],
12:[(728, 67), (560, 160), (602, 312), (712, 148), (535, 340), (720, 354), (568, 300), (629, 260), (539, 46), (634, 343), (491, 135), (768, 161)],
15:[(512, 317), (741, 72), (552, 50), (772, 346), (637, 12), (589, 131), (732, 165), (605, 15), (730, 38), (576, 216), (589, 381), (711, 387), (563, 228), (494, 22), (787, 288)]
}

# --- NOVAS FUNÇÕES PARA MATRIZ ---

def create_distance_matrix(cities: List[Tuple[float, float]]) -> List[List[float]]:
    """Gera a matriz de consulta para evitar cálculos repetidos."""
    n = len(cities)
    matrix = [[0.0 for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j:
                d = math.sqrt((cities[i][0] - cities[j][0])**2 + (cities[i][1] - cities[j][1])**2)
                matrix[i][j] = d
    return matrix

# Agora trabalhamos com índices (inteiros)
def generate_random_population(num_cities: int, population_size: int) -> List[List[int]]:
    """Gera rotas como listas de índices (ex: [0, 3, 1, 2])."""
    indices = list(range(num_cities))
    return [random.sample(indices, num_cities) for _ in range(population_size)]

# Fitness agora recebe a matriz e os índices
#def calculate_fitness(route: List[int], dist_matrix: List[List[float]]) -> float:
#    """Calcula a distância total usando a matriz de consulta."""
#    distance = 0
#    n = len(route)
#    for i in range(n):
#        # Pega a distância entre a cidade atual e a próxima na rota
#        cidade_atual = route[i]
#        proxima_cidade = route[(i + 1) % n]
#        distance += dist_matrix[cidade_atual][proxima_cidade]
#    return distance

# --- CONSTANTES LOGÍSTICAS ---
#VELOCIDADE = 15.0      # Pixels por unidade de tempo
#PESO_CRITICO = 2000.0  # Penalidade massiva para medicamentos críticos
#PESO_REGULAR = 200.0   # Penalidade para insumos comuns

#VELOCIDADE = 10.0        # Mais lento faz o tempo ser mais precioso
VELOCIDADE = 100.0 # KM/h
PESO_CRITICO = 150.0   # Penalidade por hora de atraso ao quadrado para entregas críticas (em KM equivalentes)
PESO_REGULAR = 100.0   # Penalidade por hora de atraso ao quadrado para entregas regulares (em KM equivalentes)
VEHICLE_AUTONOMY = 1200.0  # Autonomia do veículo em KM

def find_nearest_base(current_city: int, base_indices: List[int], dist_matrix: List[List[float]]) -> Tuple[int, float]:
    """Finds the nearest base and the distance to it from a given city."""
    if not base_indices:
        # Fallback to depot 0 if no bases are defined.
        return 0, dist_matrix[current_city][0]

    # Create a list of (base_index, distance) tuples
    distances_to_bases = [(base_idx, dist_matrix[current_city][base_idx]) for base_idx in base_indices]
    
    # Find the base with the minimum distance
    nearest_base_idx, min_dist = min(distances_to_bases, key=lambda item: item[1])
    
    return nearest_base_idx, min_dist


def calculate_fitness(route: List[int], dist_matrix: List[List[float]], delivery_data: dict, base_indices: List[int], return_full_path: bool = False) -> Union[float, Tuple[float, dict]]:
    """
    Calculates the total cost for a route, considering vehicle autonomy and refueling at the nearest base.

    The cost is a sum of:
    1. Total travel distance, including trips back to the depot for refueling.
    2. Penalties for late deliveries.

    The vehicle starts at the main base (base_indices[0]), visits cities in order, and returns to the nearest base.
    If the vehicle determines it cannot reach the next planned city AND then return to the
    nearest base from there, it will first travel to its current nearest base to refuel.

    Parameters:
    - route (List[int]): A list of city indices representing the delivery order. Excludes the depot.
    - dist_matrix (List[List[float]]): Pre-calculated distance matrix between all cities.
    - delivery_data (dict): Dictionary with deadline and priority for each city.
    - base_indices (List[int]): A list of city indices that are designated as refueling bases.
    - return_full_path (bool): If True, returns the cost and a dictionary with detailed
      information about the path (full path, distance, penalty, and refuel stops).

    Returns:
    - float: The total cost of the route.
    - OR Tuple[float, dict]: The total cost and a dictionary of path details.
    """
    total_dist = 0
    tempo_atual = 0
    penalidade_total = 0
    refuel_stops = 0
    
    # Vehicle starts at the main depot (first base in the list)
    current_location = base_indices[0]
    remaining_autonomy = VEHICLE_AUTONOMY
    
    full_path_indices = [current_location] # The journey always starts at a base

    # Iterate through each destination in the proposed route
    for next_city in route:
        dist_to_next = dist_matrix[current_location][next_city]
        
        # Find the distance from the potential next city to its nearest base
        _, dist_from_next_to_nearest_base = find_nearest_base(next_city, base_indices, dist_matrix)

        # --- Autonomy Check ---
        # Does the vehicle have enough fuel to go to the next city AND make it to the nearest base from there?
        # If not, it must refuel first.
        if (dist_to_next + dist_from_next_to_nearest_base) > remaining_autonomy:
            # 1. Find the nearest base from the *current* location to refuel.
            refuel_base_idx, dist_to_refuel_base = find_nearest_base(current_location, base_indices, dist_matrix)

            # 2. Travel from the current location back to that nearest base
            total_dist += dist_to_refuel_base
            tempo_atual += (dist_to_refuel_base / VELOCIDADE)
            
            # 3. Refuel: Autonomy is reset. The vehicle is now at the refuel base.
            remaining_autonomy = VEHICLE_AUTONOMY
            current_location = refuel_base_idx
            full_path_indices.append(current_location) # Log the refueling stop
            refuel_stops += 1
            
            # 4. Update the distance for the next leg, which is now from the new base.
            dist_to_next = dist_matrix[current_location][next_city]

        # --- Travel to the next city ---
        total_dist += dist_to_next
        tempo_atual += (dist_to_next / VELOCIDADE)
        remaining_autonomy -= dist_to_next
        current_location = next_city
        full_path_indices.append(current_location) # Log the city visit

        # --- Calculate Penalties at Destination ---
        info = delivery_data[next_city]
        if tempo_atual > info['prazo']:
            atraso = tempo_atual - info['prazo']
            multiplicador = PESO_CRITICO if info['critico'] else PESO_REGULAR
            penalidade_total += (atraso ** 2) * multiplicador

    # --- Final return to a base ---
    # After visiting all cities, the vehicle must return to the nearest base.
    final_base_idx, dist_to_final_base = find_nearest_base(current_location, base_indices, dist_matrix)
    total_dist += dist_to_final_base
    full_path_indices.append(final_base_idx) # Log the final return
        
    cost = total_dist + penalidade_total
    
    if return_full_path:
        details = {
            "full_path": full_path_indices,
            "distance": total_dist,
            "penalty": penalidade_total,
            "refuel_stops": refuel_stops
        }
        return cost, details
    else:
        return cost

# O Crossover e Mutação agora manipulam inteiros (índices), não mais tuplas
def order_crossover(parent1: List[int], parent2: List[int]) -> List[int]:
    length = len(parent1)
    start_index = random.randint(0, length - 1)
    end_index = random.randint(start_index + 1, length)

    child = [None] * length
    child[start_index:end_index] = parent1[start_index:end_index]

    remaining_genes = [gene for gene in parent2 if gene not in child]
    
    gen_idx = 0
    for i in range(length):
        if child[i] is None:
            child[i] = remaining_genes[gen_idx]
            gen_idx += 1
    return child

def mutate(solution: List[int], mutation_probability: float) -> List[int]:
    # Add a guard to ensure there are at least 2 cities to swap
    if len(solution) > 1 and random.random() < mutation_probability:
        idx1, idx2 = random.sample(range(len(solution)), 2)
        solution[idx1], solution[idx2] = solution[idx2], solution[idx1]
    return solution

def sort_population(population: List[List[int]], fitness: List[float]) -> Tuple[List[List[int]], List[float]]:
    combined = sorted(zip(population, fitness), key=lambda x: x[1])
    if not combined:
        return [], []
    sorted_pop, sorted_fit = map(list, zip(*combined))
    return sorted_pop, sorted_fit