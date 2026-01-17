# -*- coding: utf-8 -*-
"""
Created on Fri Dec 22 16:03:11 2023

@author: SérgioPolimante
"""
#import pylab
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
import matplotlib
import pygame
from typing import List, Tuple

matplotlib.use("Agg")


#def draw_plot(screen: pygame.Surface, x: list, y: list, x_label: str = 'Generation', y_label: str = 'Fitness') -> None:
    #"""
    #Draw a plot on a Pygame screen using Matplotlib.

    #Parameters:
    #- screen (pygame.Surface): The Pygame surface to draw the plot on.
    #- x (list): The x-axis values.
    #- y (list): The y-axis values.
    #- x_label (str): Label for the x-axis (default is 'Generation').
    #- y_label (str): Label for the y-axis (default is 'Fitness').
    #"""
    #fig, ax = plt.subplots(figsize=(4, 4), dpi=100)
    #ax.plot(x, y)
    #ax.set_ylabel(y_label)
    #ax.set_xlabel(x_label)
    #plt.tight_layout()

    #canvas = FigureCanvasAgg(fig)
    #canvas.draw()
    #renderer = canvas.get_renderer()
    #raw_data = renderer.tostring_rgb()

    #size = canvas.get_width_height()
    #surf = pygame.image.fromstring(raw_data, size, "RGB")
    #screen.blit(surf, (0, 0))

def draw_plot(screen: pygame.Surface, x: list, y: list, x_label: str = 'Generation', y_label: str = 'Fitness') -> None:
    """
    Draw a plot on a Pygame screen using Matplotlib.

    Parameters:
    - screen (pygame.Surface): The Pygame surface to draw the plot on.
    - x (list): The x-axis values.
    - y (list): The y-axis values.
    - x_label (str): Label for the x-axis (default is 'Generation').
    - y_label (str): Label for the y-axis (default is 'Fitness').
    """
    # Criamos a figura
    fig, ax = plt.subplots(figsize=(4, 4), dpi=100)
    ax.plot(x, y)
    ax.set_ylabel(y_label)
    ax.set_xlabel(x_label)
    plt.tight_layout()

    # Renderizamos o canvas
    canvas = FigureCanvasAgg(fig)
    canvas.draw()
    
    # AJUSTE AQUI: Usamos buffer_rgba() em vez de tostring_rgb()
    raw_data = canvas.buffer_rgba()
    size = canvas.get_width_height()


    # 2. CONVERSÃO: Transforme memoryview em bytes antes de passar para o Pygame
    raw_data_bytes = raw_data.tobytes()

    # AJUSTE AQUI: Mudamos o formato de "RGB" para "RGBA" para coincidir com o buffer
    #surf = pygame.image.fromstring(raw_data, size, "RGBA")
    # 3. Agora use os bytes na função do Pygame
    surf = pygame.image.fromstring(raw_data_bytes, size, "RGBA")
    
    screen.blit(surf, (0, 0))
    
    # Importante: Fechar a figura para não consumir memória a cada geração
    plt.close(fig)

    
#def draw_cities(screen: pygame.Surface, cities_locations: List[Tuple[int, int]], rgb_color: Tuple[int, int, int], node_radius: int) -> None:
#    """
#    Draws circles representing cities on the given Pygame screen.
#
#    Parameters:
#    - screen (pygame.Surface): The Pygame surface on which to draw the cities.
#    - cities_locations (List[Tuple[int, int]]): List of (x, y) coordinates representing the locations of cities.
#    - rgb_color (Tuple[int, int, int]): Tuple of three integers (R, G, B) representing the color of the city circles.
#    - node_radius (int): The radius of the city circles.
#
#    Returns:
#    None
#    """
#    for city_location in cities_locations:
#        pygame.draw.circle(screen, rgb_color, city_location, node_radius)

#def draw_cities(screen: pygame.Surface, cities_locations: List[Tuple[int, int]], delivery_data: dict, node_radius: int) -> None:
#    """
#    Desenha círculos representando as cidades com cores baseadas na prioridade do medicamento.
#    - Vermelho (255, 0, 0): Crítico
#    - Amarelo (255, 255, 0): Regular
#    """
#    for i, city_location in enumerate(cities_locations):
#        # Define a cor baseada no dicionário de prioridades
#        if i in delivery_data and delivery_data[i]['critico']:
#            color = (255, 0, 0)    # Vermelho para Críticos
#        else:
#            color = (255, 255, 0)  # Amarelo para Regulares
#        
#        # Desenha o círculo da cidade
#        pygame.draw.circle(screen, color, city_location, node_radius)
#        
#        # Adiciona uma borda preta para destacar as cidades no fundo branco
#        pygame.draw.circle(screen, (0, 0, 0), city_location, node_radius, 2)

def draw_cities(screen: pygame.Surface, cities_locations: List[Tuple[int, int]], delivery_data: dict, node_radius: int) -> None:
    """
    Desenha as cidades:
    - Base Principal: Quadrado Azul
    - Outras Bases: Quadrado Azul Claro
    - Críticas: Círculo Vermelho
    - Regulares: Círculo Amarelo
    """
    for i, city_location in enumerate(cities_locations):
        # 1. Identifica se é uma base de reabastecimento
        if delivery_data[i].get('is_base', False):
            if delivery_data[i].get('is_main_base', False):
                color = (0, 0, 255)  # Azul para a base principal
            else:
                color = (135, 206, 250)  # Azul claro para outras bases
            # Define o retângulo (centralizado na coordenada x, y)
            rect_size = node_radius * 2
            rect = pygame.Rect(
                city_location[0] - node_radius, 
                city_location[1] - node_radius, 
                rect_size, 
                rect_size
            )
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (0, 0, 0), rect, 2) # Borda
            
        else:
            # 2. Define a cor para as cidades de entrega baseada na criticidade
            if delivery_data[i]['critico']:
                color = (255, 0, 0)    # Vermelho para Críticos
            else:
                color = (255, 255, 0)  # Amarelo para Regulares
            
            # Desenha o círculo da cidade
            pygame.draw.circle(screen, color, city_location, node_radius)
            pygame.draw.circle(screen, (0, 0, 0), city_location, node_radius, 2) # Borda

def draw_paths(screen: pygame.Surface, path: List[Tuple[int, int]], rgb_color: Tuple[int, int, int], width: int = 1):
    """
    Draw a path on a Pygame screen.

    Parameters:
    - screen (pygame.Surface): The Pygame surface to draw the path on.
    - path (List[Tuple[int, int]]): List of tuples representing the coordinates of the path.
    - rgb_color (Tuple[int, int, int]): RGB values for the color of the path.
    - width (int): Width of the path lines (default is 1).
    """
    pygame.draw.lines(screen, rgb_color, True, path, width=width)


def draw_text(screen: pygame.Surface, text: str, position: Tuple[int, int], color: pygame.Color, font_size: int = 20) -> None:
    """
    Draw text on a Pygame screen.

    Parameters:
    - screen (pygame.Surface): The Pygame surface to draw the text on.
    - text (str): The text to be displayed.
    - position (Tuple[int, int]): The (x, y) coordinates to draw the text.
    - color (pygame.Color): The color of the text.
    - font_size (int): The size of the font.
    """
    # The font module is initialized by pygame.init() in the main script.
    my_font = pygame.font.SysFont('Arial', font_size)
    text_surface = my_font.render(text, True, color)
    screen.blit(text_surface, position)
