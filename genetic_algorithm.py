import random
import math
import copy
from typing import List, Tuple, Union

# Dicionário de problemas de teste legados.
default_problems = {
5: [(733, 251), (706, 87), (546, 97), (562, 49), (576, 253)],
10:[(470, 169), (602, 202), (754, 239), (476, 233), (468, 301), (522, 29), (597, 171), (487, 325), (746, 232), (558, 136)],
12:[(728, 67), (560, 160), (602, 312), (712, 148), (535, 340), (720, 354), (568, 300), (629, 260), (539, 46), (634, 343), (491, 135), (768, 161)],
15:[(512, 317), (741, 72), (552, 50), (772, 346), (637, 12), (589, 131), (732, 165), (605, 15), (730, 38), (576, 216), (589, 381), (711, 387), (563, 228), (494, 22), (787, 288)]
}

def create_distance_matrix(cities: List[Tuple[float, float]]) -> List[List[float]]:
    """
    Cria uma matriz de distâncias euclidianas entre uma lista de cidades.
    A matriz é pré-calculada para otimizar as consultas de distância durante a execução.

    Args:
        cities: Uma lista de tuplas, onde cada tupla contém as coordenadas (x, y) de uma cidade.

    Returns:
        Uma matriz (lista de listas) onde matrix[i][j] é a distância entre a cidade i e a cidade j.
    """
    num_cities = len(cities)
    matrix = [[0.0 for _ in range(num_cities)] for _ in range(num_cities)]
    for i in range(num_cities):
        for j in range(i, num_cities):
            if i != j:
                dist = math.sqrt((cities[i][0] - cities[j][0])**2 + (cities[i][1] - cities[j][1])**2)
                matrix[i][j] = dist
                matrix[j][i] = dist # A matriz é simétrica
    return matrix

# --- CONSTANTES LOGÍSTICAS ---
VELOCIDADE = 200.0  # Velocidade do veículo em KM/h
PESO_CRITICO = 0.5   # Penalidade por hora de atraso ao quadrado para entregas críticas (em KM equivalentes) - AJUSTADO
PESO_REGULAR = 0.1   # Penalidade por hora de atraso ao quadrado para entregas regulares (em KM equivalentes) - AJUSTADO
VEHICLE_AUTONOMY = 10000.0  # Autonomia do veículo em KM - AJUSTADO

def find_nearest_base(current_city: int, base_indices: List[int], dist_matrix: List[List[float]]) -> Tuple[int, float]:
    """
    Encontra a base de reabastecimento mais próxima de uma cidade e a distância até ela.

    Args:
        current_city: O índice da cidade atual.
        base_indices: Uma lista com os índices de todas as bases.
        dist_matrix: A matriz de distâncias pré-calculada.

    Returns:
        Uma tupla contendo o índice da base mais próxima e a distância até ela.
    """
    if not base_indices:
        # Caso nenhuma base seja definida, retorna para o depósito principal (índice 0).
        return 0, dist_matrix[current_city][0]

    # Cria uma lista de tuplas (índice_da_base, distância)
    distances_to_bases = [(base_idx, dist_matrix[current_city][base_idx]) for base_idx in base_indices]
    
    # Encontra a base com a distância mínima
    nearest_base_idx, min_dist = min(distances_to_bases, key=lambda item: item[1])
    
    return nearest_base_idx, min_dist


def calculate_fitness(route: List[int], dist_matrix: List[List[float]], delivery_data: dict, base_indices: List[int], return_full_path: bool = False) -> Union[float, Tuple[float, dict]]:
    """
    Calcula o custo (fitness) total de uma rota, considerando distância, penalidades por atraso e autonomia do veículo.

    A função simula uma viagem que:
    - Começa na base principal.
    - Segue a ordem de entregas da rota.
    - Proativamente, desvia para a base mais próxima para reabastecer se a autonomia não for suficiente para o próximo trecho mais o retorno seguro a uma base.
    - Acumula penalidades quadráticas por atrasos nas entregas.
    - Retorna à base mais próxima no final da rota.

    Args:
        route: Uma lista de índices de cidades que representa a ordem das entregas.
        dist_matrix: A matriz de distâncias pré-calculada.
        delivery_data: Um dicionário com informações de prazo e criticidade para cada cidade.
        base_indices: Uma lista com os índices das cidades que são bases.
        return_full_path: Se True, retorna detalhes completos da rota para visualização.

    Returns:
        O custo total da rota, ou uma tupla (custo, detalhes) se return_full_path for True.
    """
    total_dist = 0
    tempo_atual = 0
    penalidade_total = 0
    refuel_stops = 0
    
    # O veículo começa na base principal (a primeira da lista) com tanque cheio.
    current_location = base_indices[0]
    remaining_autonomy = VEHICLE_AUTONOMY
    
    full_path_indices = [current_location]  # O caminho completo sempre começa em uma base.

    # Itera sobre cada destino na rota proposta.
    for next_city in route:
        dist_to_next = dist_matrix[current_location][next_city]
        
        # Calcula a distância da *próxima* cidade até a base mais próxima dela.
        _, dist_from_next_to_nearest_base = find_nearest_base(next_city, base_indices, dist_matrix)

        # --- Verificação de Autonomia ---
        # O veículo tem combustível para ir à próxima cidade E, de lá, chegar à base mais próxima?
        # Se não, ele deve reabastecer primeiro.
        if (dist_to_next + dist_from_next_to_nearest_base) > remaining_autonomy:
            # 1. Encontra a base mais próxima da localização *atual* para reabastecer.
            refuel_base_idx, dist_to_refuel_base = find_nearest_base(current_location, base_indices, dist_matrix)

            # 2. Viaja da localização atual até a base de reabastecimento.
            total_dist += dist_to_refuel_base
            tempo_atual += (dist_to_refuel_base / VELOCIDADE)
            
            # 3. Reabastece: A autonomia é restaurada e a localização atual passa a ser a base.
            remaining_autonomy = VEHICLE_AUTONOMY
            current_location = refuel_base_idx
            full_path_indices.append(current_location)  # Registra a parada para reabastecer.
            refuel_stops += 1
            
            # 4. Atualiza a distância para o próximo trecho, que agora parte da nova base.
            dist_to_next = dist_matrix[current_location][next_city]

        # --- Viagem para a Próxima Cidade ---
        total_dist += dist_to_next
        tempo_atual += (dist_to_next / VELOCIDADE)
        remaining_autonomy -= dist_to_next
        current_location = next_city
        full_path_indices.append(current_location)  # Registra a visita à cidade.

        # --- Cálculo de Penalidades no Destino ---
        info = delivery_data[next_city]
        if tempo_atual > info['prazo']:
            atraso = tempo_atual - info['prazo']
            multiplicador = PESO_CRITICO if info['critico'] else PESO_REGULAR
            penalidade_total += (atraso ** 2) * multiplicador

    # --- Retorno Final à Base ---
    # Após visitar todas as cidades, o veículo deve retornar à base mais próxima.
    final_base_idx, dist_to_final_base = find_nearest_base(current_location, base_indices, dist_matrix)
    total_dist += dist_to_final_base
    full_path_indices.append(final_base_idx)  # Registra o retorno final.
        
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

def order_crossover(parent1: List[int], parent2: List[int]) -> List[int]:
    """
    Executa o operador de crossover de ordem (OX1) para criar um filho a partir de dois pais.
    Este método preserva um segmento de um pai e a ordem relativa dos genes do outro.

    Args:
        parent1: O primeiro cromossomo pai.
        parent2: O segundo cromossomo pai.

    Returns:
        O cromossomo filho resultante.
    """
    size = len(parent1)
    child = [None] * size

    # 1. Seleciona um segmento aleatório do primeiro pai.
    start, end = sorted(random.sample(range(size), 2))

    # 2. Copia o segmento para o filho.
    child[start:end] = parent1[start:end]

    # 3. Coleta os genes do segundo pai que não estão no segmento copiado, mantendo a ordem.
    # Usa-se um set para uma verificação de existência (in) mais rápida.
    genes_in_segment = set(child[start:end])
    genes_from_parent2 = [gene for gene in parent2 if gene not in genes_in_segment]

    # 4. Preenche as posições restantes (None) do filho com os genes do segundo pai.
    pointer = 0
    for i in range(size):
        if child[i] is None:
            child[i] = genes_from_parent2[pointer]
            pointer += 1
            
    return child

def mutate(solution: List[int], mutation_probability: float) -> List[int]:
    """
    Aplica uma mutação de troca (swap mutation) em um cromossomo.
    Com uma dada probabilidade, dois genes aleatórios da solução trocam de posição.

    Args:
        solution: O cromossomo a ser mutado.
        mutation_probability: A probabilidade de que a mutação ocorra.

    Returns:
        O cromossomo mutado (ou o original, se a mutação não ocorrer).
    """
    if len(solution) > 1 and random.random() < mutation_probability:
        idx1, idx2 = random.sample(range(len(solution)), 2)
        solution[idx1], solution[idx2] = solution[idx2], solution[idx1]
    return solution

def sort_population(population: List[List[int]], fitness: List[float]) -> Tuple[List[List[int]], List[float]]:
    """
    Ordena uma população de cromossomos com base em seus valores de fitness (custo).
    A ordenação é feita em ordem crescente de fitness (menor custo é melhor).
    """
    combined = sorted(zip(population, fitness), key=lambda x: x[1])
    if not combined:
        return [], []
    sorted_pop, sorted_fit = map(list, zip(*combined))
    return sorted_pop, sorted_fit