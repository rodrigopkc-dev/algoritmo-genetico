

#python - IA- algotirmo genetico - criar um exemplo de funcao fitness - 

#Criar uma função fitness que considere (distância e prioridade de entregas)

#Com Prioridades de entregas sendo (medicamentos críticos vs. medicamentos regulares).

#import numpy as np

def fitness_priorizada(rota, matriz_distancias, info_entregas):
    """
    rota: lista com a ordem dos índices, ex: [2, 0, 3, 1]
    matriz_distancias: distâncias entre todos os pontos (0 é o depósito)
    info_entregas: dicionário mapeando índice para nível de prioridade
                   (ex: 10 para crítico, 1 para regular)
    """
    distancia_total = 0
    penalidade_atraso = 0
    tempo_acumulado = 0
    ponto_atual = 0  # Início no Depósito
    
    # Peso para a prioridade (ajuste conforme a necessidade)
    FATOR_URGENCIA = 5 

    for destino in rota:
        # 1. Calcula distância e "tempo" (simplificado como distância)
        trecho = matriz_distancias[ponto_atual][destino]
        distancia_total += trecho
        tempo_acumulado += trecho 
        
        # 2. Verifica a prioridade do medicamento
        nivel_prioridade = info_entregas[destino]['prioridade']
        
        # 3. Calcula a penalidade: quanto mais tempo um crítico 
        # demora para ser entregue, maior o custo da rota.
        if nivel_prioridade == "critico":
            penalidade_atraso += (tempo_acumulado * FATOR_URGENCIA)
        else:
            penalidade_atraso += tempo_acumulado * 1 # Regular tem peso menor
            
        ponto_atual = destino

    # Retorno ao depósito final
    distancia_total += matriz_distancias[ponto_atual][0]
    
    # O fitness final é a soma dos dois "problemas"
    return distancia_total + penalidade_atraso

# --- Exemplo de uso ---
# Prioridades: 10 para Crítico, 1 para Regular
entregas = {
    1: {'nome': 'Aspirina', 'prioridade': 'regular'},
    2: {'nome': 'Insulina', 'prioridade': 'critico'},
    3: {'nome': 'Antibiótico', 'prioridade': 'critico'}
}

# Matriz simplificada (4x4: Depósito + 3 Entregas)
distancias = [
    [0, 10, 20, 30], # Depósito
    [10, 0, 15, 25], # Entrega 1
    [20, 15, 0, 10], # Entrega 2
    [30, 25, 10, 0]  # Entrega 3
]

# Rota A: Entrega o regular (1) primeiro
# Rota B: Entrega os críticos (2 e 3) primeiro
rota_a = [1, 2, 3]
rota_b = [2, 3, 1]

print(f"Custo Rota A (Regular primeiro): {fitness_priorizada(rota_a, distancias, entregas)}")
print(f"Custo Rota B (Crítico primeiro): {fitness_priorizada(rota_b, distancias, entregas)}")

