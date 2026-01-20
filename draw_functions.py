# -*- coding: utf-8 -*-
"""
Created on Fri Dec 22 16:03:11 2023

@author: SérgioPolimante
Visual Enhancement by AI Assistant - Modern Futuristic Theme
"""
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
import matplotlib
import pygame
import math
from typing import List, Tuple, Dict, Optional

matplotlib.use("Agg")

# ============================================================================
# PALETA DE CORES MODERNA - TEMA FUTURISTA ESCURO
# ============================================================================
class Colors:
    # Fundo e painéis
    BACKGROUND = (15, 15, 35)
    PANEL_BG = (25, 25, 50)
    PANEL_BORDER = (60, 60, 120)
    
    # Cores de destaque (Neon)
    NEON_BLUE = (0, 200, 255)
    NEON_CYAN = (0, 255, 200)
    NEON_PURPLE = (180, 100, 255)
    NEON_PINK = (255, 50, 150)
    NEON_GREEN = (50, 255, 150)
    NEON_ORANGE = (255, 150, 50)
    NEON_YELLOW = (255, 230, 50)
    
    # Cores para rotas
    ROUTE_BEST = (0, 220, 255)
    ROUTE_SECOND = (100, 180, 255)
    ROUTE_THIRD = (60, 120, 180)
    
    # Cores para cidades
    CITY_CRITICAL = (255, 60, 80)
    CITY_REGULAR = (255, 200, 50)
    BASE_MAIN = (0, 150, 255)
    BASE_SECONDARY = (100, 180, 220)
    
    # Texto
    TEXT_PRIMARY = (255, 255, 255)
    TEXT_SECONDARY = (180, 180, 200)
    TEXT_ACCENT = (0, 200, 255)
    
    # Glow effects
    GLOW_BLUE = (0, 100, 150, 80)
    GLOW_RED = (150, 30, 40, 80)


def create_gradient_surface(width: int, height: int, color1: Tuple, color2: Tuple, vertical: bool = True) -> pygame.Surface:
    """Cria uma superfície com gradiente."""
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    for i in range(height if vertical else width):
        ratio = i / (height if vertical else width)
        r = int(color1[0] + (color2[0] - color1[0]) * ratio)
        g = int(color1[1] + (color2[1] - color1[1]) * ratio)
        b = int(color1[2] + (color2[2] - color1[2]) * ratio)
        if vertical:
            pygame.draw.line(surface, (r, g, b), (0, i), (width, i))
        else:
            pygame.draw.line(surface, (r, g, b), (i, 0), (i, height))
    return surface


def draw_rounded_rect(surface: pygame.Surface, color: Tuple, rect: pygame.Rect, 
                      radius: int = 10, border_color: Optional[Tuple] = None, border_width: int = 2):
    """Desenha um retângulo com bordas arredondadas."""
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    if border_color:
        pygame.draw.rect(surface, border_color, rect, border_width, border_radius=radius)


def draw_glow_circle(surface: pygame.Surface, color: Tuple, center: Tuple[int, int], 
                     radius: int, glow_radius: int = 20, intensity: int = 3):
    """Desenha um círculo com efeito de brilho (glow)."""
    glow_surface = pygame.Surface((glow_radius * 4, glow_radius * 4), pygame.SRCALPHA)
    for i in range(intensity, 0, -1):
        alpha = int(40 * (i / intensity))
        glow_color = (*color[:3], alpha)
        pygame.draw.circle(glow_surface, glow_color, (glow_radius * 2, glow_radius * 2), radius + (intensity - i + 1) * 4)
    surface.blit(glow_surface, (center[0] - glow_radius * 2, center[1] - glow_radius * 2))


def draw_panel(screen: pygame.Surface, x: int, y: int, width: int, height: int, 
               title: str = "", alpha: int = 200) -> pygame.Rect:
    """Desenha um painel moderno com título."""
    panel_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    
    # Fundo do painel com gradiente sutil
    panel_rect = pygame.Rect(0, 0, width, height)
    pygame.draw.rect(panel_surface, (*Colors.PANEL_BG, alpha), panel_rect, border_radius=15)
    pygame.draw.rect(panel_surface, Colors.PANEL_BORDER, panel_rect, 2, border_radius=15)
    
    # Linha de destaque superior
    pygame.draw.line(panel_surface, Colors.NEON_BLUE, (15, 2), (width - 15, 2), 2)
    
    screen.blit(panel_surface, (x, y))
    
    if title:
        font = pygame.font.SysFont('Segoe UI', 16, bold=True)
        title_surface = font.render(title, True, Colors.TEXT_ACCENT)
        screen.blit(title_surface, (x + 15, y + 10))
    
    return pygame.Rect(x, y, width, height)


def draw_plot(screen: pygame.Surface, x: list, y: list, x_label: str = 'Generation', 
              y_label: str = 'Fitness', plot_position: Tuple[int, int] = (15, 50)) -> None:
    """
    Desenha um gráfico moderno no estilo dark theme.
    """
    # Configuração do estilo moderno
    plt.style.use('dark_background')
    
    fig, ax = plt.subplots(figsize=(4.0, 3.2), dpi=100)
    fig.patch.set_facecolor('#0f0f23')
    ax.set_facecolor('#19193d')
    
    # Plotar com estilo moderno
    if len(x) > 1:
        # Linha principal com gradiente
        ax.plot(x, y, color='#00d4ff', linewidth=2, alpha=0.9)
        # Área preenchida com gradiente
        ax.fill_between(x, y, alpha=0.3, color='#00d4ff')
    else:
        ax.plot(x, y, 'o', color='#00d4ff', markersize=8)
    
    # Estilização dos eixos
    ax.set_ylabel(y_label, color='#b4b4c8', fontsize=11, fontweight='bold')
    ax.set_xlabel(x_label, color='#b4b4c8', fontsize=11, fontweight='bold')
    ax.tick_params(colors='#8080a0', labelsize=9)
    
    # Grid moderno
    ax.grid(True, alpha=0.2, color='#4040a0', linestyle='--')
    ax.spines['bottom'].set_color('#4040a0')
    ax.spines['top'].set_color('#4040a0')
    ax.spines['left'].set_color('#4040a0')
    ax.spines['right'].set_color('#4040a0')
    
    plt.tight_layout(pad=1.5)
    
    # Renderização
    canvas = FigureCanvasAgg(fig)
    canvas.draw()
    raw_data = canvas.buffer_rgba()
    size = canvas.get_width_height()
    raw_data_bytes = raw_data.tobytes()
    surf = pygame.image.fromstring(raw_data_bytes, size, "RGBA")
    
    # Desenha painel de fundo
    draw_panel(screen, plot_position[0] - 10, plot_position[1] - 35, 
               size[0] + 20, size[1] + 50, "CONVERGENCIA")
    
    screen.blit(surf, plot_position)
    plt.close(fig)


def draw_cities(screen: pygame.Surface, cities_locations: List[Tuple[int, int]], 
                delivery_data: dict, node_radius: int, generation: int = 0) -> None:
    """
    Desenha as cidades com visual moderno e efeitos de brilho:
    - Base Principal: Hexágono Azul com glow + número
    - Outras Bases: Hexágono Azul Claro com glow + número
    - Críticas: Diamante Vermelho com pulso + número
    - Regulares: Círculo Dourado com brilho + número
    """
    pulse = abs(math.sin(generation * 0.1)) * 0.3 + 0.7  # Efeito de pulso
    
    # Fonte para numeração das cidades
    font_size = max(10, node_radius - 2)
    try:
        city_font = pygame.font.SysFont('Segoe UI', font_size, bold=True)
    except:
        city_font = pygame.font.Font(None, font_size)
    
    for i, city_location in enumerate(cities_locations):
        x, y = city_location
        
        if delivery_data[i].get('is_base', False):
            # BASES - Desenha hexágono futurista
            if delivery_data[i].get('is_main_base', False):
                color = Colors.BASE_MAIN
                glow_color = Colors.NEON_BLUE
                size_mult = 1.3
            else:
                color = Colors.BASE_SECONDARY
                glow_color = Colors.NEON_CYAN
                size_mult = 1.1
            
            # Efeito de glow para bases
            draw_glow_circle(screen, glow_color, (x, y), int(node_radius * size_mult), 25, 4)
            
            # Desenha hexágono
            size = int(node_radius * size_mult * 1.2)
            points = []
            for j in range(6):
                angle = math.pi / 6 + j * math.pi / 3
                px = x + size * math.cos(angle)
                py = y + size * math.sin(angle)
                points.append((px, py))
            
            pygame.draw.polygon(screen, color, points)
            pygame.draw.polygon(screen, Colors.TEXT_PRIMARY, points, 2)
            
            # Número da base (centralizado)
            number_text = city_font.render(str(i), True, Colors.TEXT_PRIMARY)
            text_rect = number_text.get_rect(center=(x, y))
            screen.blit(number_text, text_rect)
            
        else:
            # CIDADES DE ENTREGA
            if delivery_data[i]['critico']:
                # Críticas - Diamante vermelho com pulso
                color = Colors.CITY_CRITICAL
                glow_color = (255, 60, 80)
                
                # Efeito de glow pulsante
                pulse_size = int(node_radius * (1 + pulse * 0.3))
                draw_glow_circle(screen, glow_color, (x, y), pulse_size, 20, 3)
                
                # Desenha diamante (losango)
                size = int(node_radius * 1.1)
                points = [
                    (x, y - size),      # Topo
                    (x + size, y),      # Direita
                    (x, y + size),      # Baixo
                    (x - size, y)       # Esquerda
                ]
                pygame.draw.polygon(screen, color, points)
                pygame.draw.polygon(screen, Colors.TEXT_PRIMARY, points, 2)
                
                # Número da cidade crítica (centralizado)
                number_text = city_font.render(str(i), True, Colors.BACKGROUND)
                text_rect = number_text.get_rect(center=(x, y))
                screen.blit(number_text, text_rect)
                
            else:
                # Regulares - Círculo dourado elegante
                color = Colors.CITY_REGULAR
                glow_color = (255, 200, 50)
                
                # Efeito de glow suave
                draw_glow_circle(screen, glow_color, (x, y), node_radius, 15, 2)
                
                # Círculo principal
                pygame.draw.circle(screen, color, (x, y), node_radius)
                pygame.draw.circle(screen, Colors.TEXT_PRIMARY, (x, y), node_radius, 2)
                
                # Número da cidade regular (centralizado)
                number_text = city_font.render(str(i), True, Colors.BACKGROUND)
                text_rect = number_text.get_rect(center=(x, y))
                screen.blit(number_text, text_rect)


def draw_paths(screen: pygame.Surface, path: List[Tuple[int, int]], 
               rgb_color: Tuple[int, int, int], width: int = 1, 
               glow: bool = False, dash: bool = False):
    """
    Desenha caminhos com efeitos visuais modernos.
    """
    if len(path) < 2:
        return
    
    if glow and width >= 2:
        # Efeito de glow na rota
        glow_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        for i in range(3, 0, -1):
            glow_color = (*rgb_color[:3], int(30 * i))
            pygame.draw.lines(glow_surface, glow_color, True, path, width=width + i * 3)
        screen.blit(glow_surface, (0, 0))
    
    if dash:
        # Desenha linha tracejada
        for i in range(len(path)):
            start = path[i]
            end = path[(i + 1) % len(path)]
            draw_dashed_line(screen, rgb_color, start, end, width, 10, 5)
    else:
        # Linha sólida
        pygame.draw.lines(screen, rgb_color, True, path, width=width)


def draw_dashed_line(surface: pygame.Surface, color: Tuple, start: Tuple, end: Tuple, 
                     width: int = 1, dash_length: int = 10, gap_length: int = 5):
    """Desenha uma linha tracejada."""
    x1, y1 = start
    x2, y2 = end
    dx = x2 - x1
    dy = y2 - y1
    distance = math.sqrt(dx * dx + dy * dy)
    
    if distance == 0:
        return
    
    dx = dx / distance
    dy = dy / distance
    
    pos = 0
    while pos < distance:
        start_pos = (int(x1 + dx * pos), int(y1 + dy * pos))
        end_pos_dist = min(pos + dash_length, distance)
        end_pos = (int(x1 + dx * end_pos_dist), int(y1 + dy * end_pos_dist))
        pygame.draw.line(surface, color, start_pos, end_pos, width)
        pos += dash_length + gap_length


def draw_text(screen: pygame.Surface, text: str, position: Tuple[int, int], 
              color: pygame.Color = None, font_size: int = 20, 
              font_name: str = 'Segoe UI', bold: bool = False) -> None:
    """
    Desenha texto com estilo moderno.
    """
    if color is None:
        color = Colors.TEXT_PRIMARY
    
    font = pygame.font.SysFont(font_name, font_size, bold=bold)
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, position)


def draw_stats_panel(screen: pygame.Surface, stats: Dict, position: Tuple[int, int] = (10, 420)):
    """
    Desenha um painel de estatísticas estilizado.
    """
    panel_width = 420
    panel_height = 180
    
    # Desenha painel principal
    draw_panel(screen, position[0], position[1], panel_width, panel_height, "ESTATISTICAS")
    
    # Conteúdo do painel
    y_offset = position[1] + 35
    x_offset = position[0] + 20
    line_height = 23
    
    # Geração
    draw_text(screen, f"Geração:", (x_offset, y_offset), Colors.TEXT_SECONDARY, 14)
    draw_text(screen, f"{stats.get('generation', 0):,}", (x_offset + 140, y_offset), Colors.NEON_CYAN, 14, bold=True)
    
    # Melhor Custo
    y_offset += line_height
    draw_text(screen, f"Melhor Custo:", (x_offset, y_offset), Colors.TEXT_SECONDARY, 14)
    cost = stats.get('best_cost', 0)
    cost_color = Colors.NEON_GREEN if cost < 100000 else Colors.NEON_ORANGE if cost < 1000000 else Colors.NEON_PINK
    draw_text(screen, f"{cost:,.2f} KM eq.", (x_offset + 140, y_offset), cost_color, 14, bold=True)
    
    # Distância
    y_offset += line_height
    draw_text(screen, f"Distância Real:", (x_offset, y_offset), Colors.TEXT_SECONDARY, 14)
    draw_text(screen, f"{stats.get('distance', 0):,.2f} KM", (x_offset + 140, y_offset), Colors.NEON_BLUE, 14, bold=True)
    
    # Penalidade
    y_offset += line_height
    draw_text(screen, f"Penalidade:", (x_offset, y_offset), Colors.TEXT_SECONDARY, 14)
    penalty = stats.get('penalty', 0)
    penalty_color = Colors.NEON_GREEN if penalty == 0 else Colors.NEON_ORANGE if penalty < 10000 else Colors.NEON_PINK
    draw_text(screen, f"{penalty:,.2f} KM eq.", (x_offset + 140, y_offset), penalty_color, 14, bold=True)
    
    # Paradas para Reabastecimento
    y_offset += line_height
    draw_text(screen, f"Reabastecimentos:", (x_offset, y_offset), Colors.TEXT_SECONDARY, 14)
    draw_text(screen, f"{stats.get('refuel_stops', 0)}", (x_offset + 140, y_offset), Colors.NEON_PURPLE, 14, bold=True)
    
    # Velocidade e Autonomia
    y_offset += line_height
    draw_text(screen, f"Velocidade:", (x_offset, y_offset), Colors.TEXT_SECONDARY, 14)
    draw_text(screen, f"{stats.get('speed', 0)} KM/h", (x_offset + 140, y_offset), Colors.TEXT_PRIMARY, 14)
    draw_text(screen, f"Autonomia:", (x_offset + 220, y_offset), Colors.TEXT_SECONDARY, 14)
    draw_text(screen, f"{stats.get('autonomy', 0)} KM", (x_offset + 320, y_offset), Colors.TEXT_PRIMARY, 14)


def draw_legend(screen: pygame.Surface, position: Tuple[int, int] = (10, 630)):
    """
    Desenha uma legenda elegante com ícones desenhados.
    """
    panel_width = 420
    panel_height = 140
    
    # Desenha painel
    draw_panel(screen, position[0], position[1], panel_width, panel_height, "LEGENDA")
    
    y_offset = position[1] + 35
    x_offset = position[0] + 20
    spacing = 20
    icon_size = 8
    
    # Base Principal - Hexágono
    _draw_hexagon(screen, Colors.BASE_MAIN, (x_offset + icon_size, y_offset + icon_size - 2), icon_size)
    draw_text(screen, "Base Principal", (x_offset + 30, y_offset), Colors.TEXT_SECONDARY, 13)
    y_offset += spacing
    
    # Bases Secundárias - Hexágono menor
    _draw_hexagon(screen, Colors.BASE_SECONDARY, (x_offset + icon_size, y_offset + icon_size - 2), icon_size - 1)
    draw_text(screen, "Bases Secundarias", (x_offset + 30, y_offset), Colors.TEXT_SECONDARY, 13)
    y_offset += spacing
    
    # Entregas Críticas - Diamante
    _draw_diamond(screen, Colors.CITY_CRITICAL, (x_offset + icon_size, y_offset + icon_size - 2), icon_size)
    draw_text(screen, "Entregas Criticas", (x_offset + 30, y_offset), Colors.TEXT_SECONDARY, 13)
    y_offset += spacing
    
    # Entregas Regulares - Círculo
    pygame.draw.circle(screen, Colors.CITY_REGULAR, (x_offset + icon_size, y_offset + icon_size - 2), icon_size)
    draw_text(screen, "Entregas Regulares", (x_offset + 30, y_offset), Colors.TEXT_SECONDARY, 13)
    y_offset += spacing
    
    # Melhor Rota - Linha
    pygame.draw.line(screen, Colors.ROUTE_BEST, (x_offset, y_offset + icon_size - 2), (x_offset + icon_size * 2, y_offset + icon_size - 2), 3)
    draw_text(screen, "Melhor Rota", (x_offset + 30, y_offset), Colors.TEXT_SECONDARY, 13)


def _draw_hexagon(surface: pygame.Surface, color: Tuple, center: Tuple[int, int], size: int):
    """Desenha um hexágono."""
    x, y = center
    points = []
    for i in range(6):
        angle = math.pi / 6 + i * math.pi / 3
        px = x + size * math.cos(angle)
        py = y + size * math.sin(angle)
        points.append((px, py))
    pygame.draw.polygon(surface, color, points)
    pygame.draw.polygon(surface, Colors.TEXT_PRIMARY, points, 1)


def _draw_diamond(surface: pygame.Surface, color: Tuple, center: Tuple[int, int], size: int):
    """Desenha um diamante (losango)."""
    x, y = center
    points = [
        (x, y - size),
        (x + size, y),
        (x, y + size),
        (x - size, y)
    ]
    pygame.draw.polygon(surface, color, points)
    pygame.draw.polygon(surface, Colors.TEXT_PRIMARY, points, 1)


def draw_header(screen: pygame.Surface, title: str = "VRP - ALGORITMO GENÉTICO", 
                subtitle: str = "Otimização de Rotas de Veículos"):
    """
    Desenha um cabeçalho elegante.
    """
    # Barra superior com gradiente
    header_height = 45
    header_surface = pygame.Surface((screen.get_width(), header_height), pygame.SRCALPHA)
    
    # Gradiente horizontal
    for x in range(screen.get_width()):
        ratio = x / screen.get_width()
        r = int(20 + 30 * ratio)
        g = int(20 + 30 * ratio)
        b = int(60 + 60 * ratio)
        pygame.draw.line(header_surface, (r, g, b, 230), (x, 0), (x, header_height))
    
    # Linha inferior brilhante
    pygame.draw.line(header_surface, Colors.NEON_BLUE, (0, header_height - 2), (screen.get_width(), header_height - 2), 2)
    
    screen.blit(header_surface, (0, 0))
    
    # Título
    font_title = pygame.font.SysFont('Segoe UI', 22, bold=True)
    title_surface = font_title.render(title, True, Colors.TEXT_PRIMARY)
    screen.blit(title_surface, (20, 10))
    
    # Subtítulo
    font_subtitle = pygame.font.SysFont('Segoe UI', 14)
    subtitle_surface = font_subtitle.render(subtitle, True, Colors.TEXT_SECONDARY)
    screen.blit(subtitle_surface, (320, 14))


def draw_route_info(screen: pygame.Surface, route_num: int, color: Tuple, 
                    position: Tuple[int, int], info: str = ""):
    """
    Desenha informação sobre uma rota específica.
    """
    # Indicador de cor da rota
    pygame.draw.rect(screen, color, (position[0], position[1] + 3, 30, 4), border_radius=2)
    draw_text(screen, f"Rota {route_num}: {info}", (position[0] + 40, position[1]), Colors.TEXT_SECONDARY, 12)

