import random
import math
import copy 
from typing import List, Tuple

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
VELOCIDADE = 0.8
#PESO_CRITICO = 50000.0  # Torna o atraso crítico um erro "fatal"
#PESO_CRITICO = 5000.0  # Torna o atraso crítico um erro "fatal"
PESO_CRITICO = 2000.0
#PESO_REGULAR = 2000.0
PESO_REGULAR = 500.0


# Sorteia de 1 a 4 veículos no início do sistema
#NUM_VEICULOS = random.randint(1, 4)
NUM_VEICULOS = 3 # FIXO

print(f"Sistema iniciado com {NUM_VEICULOS} veículos.")

def calculate_fitness(route: List[int], dist_matrix: List[List[float]], delivery_data: dict) -> float:
    """
    Calcula o custo total dividindo a rota entre os veículos sorteados.
    """
    total_cost = 0
    # O ponto 0 é o depósito. Removemos para redistribuir.
    cidades_clientes = [c for c in route if c != 0]
    
    n = len(cidades_clientes)
    # Define quantas cidades cada veículo pega (divisão equilibrada)
    tam = math.ceil(n / NUM_VEICULOS) if n > 0 else 0
    
    for v in range(NUM_VEICULOS):
        # Extrai a fatia de cidades do veículo atual
        sub_rota_clientes = cidades_clientes[v * tam : (v + 1) * tam]
        
        if not sub_rota_clientes:
            continue
            
        # A rota real SEMPRE começa no depósito (0) e volta para o depósito (0)
        rota_completa = [0] + sub_rota_clientes + [0]
        
        tempo_atual = 0
        distancia_veiculo = 0
        
        for i in range(len(rota_completa) - 1):
            atual = rota_completa[i]
            proximo = rota_completa[i+1]
            
            d = dist_matrix[atual][proximo]
            distancia_veiculo += d
            tempo_atual += (d / VELOCIDADE)
            
            # Penalidade de atraso (apenas para cidades, não para a volta ao depósito)
            if proximo != 0:
                info = delivery_data[proximo]
                if tempo_atual > info['prazo']:
                    atraso = tempo_atual - info['prazo']
                    multiplicador = PESO_CRITICO if info['critico'] else PESO_REGULAR
                    total_cost += (atraso ** 2) * multiplicador
        
        # O fitness é a soma das distâncias de todos os veículos + penalidades
        total_cost += distancia_veiculo
        
    return total_cost

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
    if random.random() < mutation_probability:
        idx1, idx2 = random.sample(range(len(solution)), 2)
        solution[idx1], solution[idx2] = solution[idx2], solution[idx1]
    return solution

def sort_population(population: List[List[int]], fitness: List[float]) -> Tuple[List[List[int]], List[float]]:
    combined = sorted(zip(population, fitness), key=lambda x: x[1])
    sorted_pop, sorted_fit = zip(*combined)
    return list(sorted_pop), list(sorted_fit)