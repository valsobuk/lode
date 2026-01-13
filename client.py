import pygame
from network import Network
from player import BattleshipsGame
from menu import Menu
import math

width = 900
height = 520

# Colors (same as menu)
COLOR_BG = (8, 12, 24)           # Darker navy background
COLOR_BG_GRADIENT = (15, 23, 42)  # Lighter navy
COLOR_PANEL = (30, 41, 59)
COLOR_GRID = (59, 130, 246)      # Accent blue
COLOR_SHIP = (99, 102, 241)      # Indigo
COLOR_HIT = (239, 68, 68)        # Red
COLOR_MISS = (148, 163, 184)     # Slate
COLOR_TEXT = (226, 232, 240)
COLOR_TEXT_BRIGHT = (255, 255, 255)
COLOR_HOVER = (94, 234, 212)     # Cyan for hover

FONT = None
FONT_LARGE = None
FONT_NORMAL = None
FONT_VICTORY = None

def init_font():
    global FONT, FONT_LARGE, FONT_NORMAL, FONT_VICTORY
    pygame.font.init()
    FONT = pygame.font.Font(None, 24)
    FONT_LARGE = pygame.font.Font(None, 36)
    FONT_NORMAL = pygame.font.Font(None, 28)
    FONT_VICTORY = pygame.font.Font(None, 56)

def draw_gradient_background(surface, width, height):
    """Draw gradient background"""
    for y in range(height):
        ratio = y / height
        r = int(COLOR_BG[0] * (1 - ratio) + COLOR_BG_GRADIENT[0] * ratio)
        g = int(COLOR_BG[1] * (1 - ratio) + COLOR_BG_GRADIENT[1] * ratio)
        b = int(COLOR_BG[2] * (1 - ratio) + COLOR_BG_GRADIENT[2] * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (width, y))

def draw_label(surface, text, pos, size=24, color=COLOR_TEXT, shadow=True):
    if size == 36:
        font = FONT_LARGE
    elif size == 28:
        font = FONT_NORMAL
    else:
        font = FONT
    
    if shadow:
        shadow_surf = font.render(text, True, (0, 0, 0))
        surface.blit(shadow_surf, (pos[0] + 2, pos[1] + 2))
    
    text_surf = font.render(text, True, color)
    surface.blit(text_surf, pos)

def redrawWindow(win, player, opponent, hover_cell=None, game_time=0):
    draw_gradient_background(win, width, height)
    
    # Panels with rounded corners (moved down to make space for turn status)
    panel_top = 75
    own_panel = pygame.Rect(20, panel_top, BattleshipsGame.BOARD_SIZE * BattleshipsGame.CELL_SIZE + 20,
                            BattleshipsGame.BOARD_SIZE * BattleshipsGame.CELL_SIZE + 60)
    opp_panel = pygame.Rect(width // 2 + 10, panel_top, BattleshipsGame.BOARD_SIZE * BattleshipsGame.CELL_SIZE + 20,
                            BattleshipsGame.BOARD_SIZE * BattleshipsGame.CELL_SIZE + 60)
    
    # Panel glow effect
    for i in range(3):
        glow_own = pygame.Rect(own_panel.x - i, own_panel.y - i,
                              own_panel.width + i * 2, own_panel.height + i * 2)
        glow_opp = pygame.Rect(opp_panel.x - i, opp_panel.y - i,
                              opp_panel.width + i * 2, opp_panel.height + i * 2)
        glow_color = tuple(min(255, c + (3-i) * 5) for c in COLOR_PANEL[:3])
        pygame.draw.rect(win, glow_color, glow_own, border_radius=8 + i)
        pygame.draw.rect(win, glow_color, glow_opp, border_radius=8 + i)
    
    pygame.draw.rect(win, COLOR_PANEL, own_panel, border_radius=8)
    pygame.draw.rect(win, COLOR_PANEL, opp_panel, border_radius=8)
    pygame.draw.rect(win, COLOR_GRID, own_panel, width=2, border_radius=8)
    pygame.draw.rect(win, COLOR_GRID, opp_panel, width=2, border_radius=8)
    
    # Titles with shadow
    draw_label(win, "Your Fleet", (own_panel.x + 15, own_panel.y + 12), size=28, color=COLOR_TEXT_BRIGHT)
    draw_label(win, "Enemy Waters", (opp_panel.x + 15, opp_panel.y + 12), size=28, color=COLOR_TEXT_BRIGHT)
    
    # Own board
    player.draw(win, own_panel.x + 10, own_panel.y + 45, show_ships=True)
    
    # Opponent board grid
    offset_x = opp_panel.x + 10
    offset_y = opp_panel.y + 45
    
    # Draw grid with glow
    for i in range(BattleshipsGame.BOARD_SIZE + 1):
        # Vertical lines
        pygame.draw.line(
            win, COLOR_GRID,
            (offset_x + i * BattleshipsGame.CELL_SIZE, offset_y),
            (offset_x + i * BattleshipsGame.CELL_SIZE, offset_y + BattleshipsGame.BOARD_SIZE * BattleshipsGame.CELL_SIZE), 2
        )
        # Horizontal lines
        pygame.draw.line(
            win, COLOR_GRID,
            (offset_x, offset_y + i * BattleshipsGame.CELL_SIZE),
            (offset_x + BattleshipsGame.BOARD_SIZE * BattleshipsGame.CELL_SIZE, offset_y + i * BattleshipsGame.CELL_SIZE), 2
        )
    
    # Hover highlight on opponent board
    if hover_cell:
        hx, hy = hover_cell
        if 0 <= hx < BattleshipsGame.BOARD_SIZE and 0 <= hy < BattleshipsGame.BOARD_SIZE:
            if player.opponent_board[hy][hx] == 0:
                rect = pygame.Rect(
                    offset_x + hx * BattleshipsGame.CELL_SIZE + 1,
                    offset_y + hy * BattleshipsGame.CELL_SIZE + 1,
                    BattleshipsGame.CELL_SIZE - 2,
                    BattleshipsGame.CELL_SIZE - 2,
                )
                # Glow effect
                for i in range(3):
                    glow_rect = pygame.Rect(
                        rect.x - i, rect.y - i,
                        rect.width + i * 2, rect.height + i * 2
                    )
                    glow_color = tuple(min(255, c + (3-i) * 20) for c in COLOR_HOVER[:3])
                    pygame.draw.rect(win, glow_color, glow_rect, width=1, border_radius=4)
                pygame.draw.rect(win, COLOR_HOVER, rect, width=2, border_radius=4)
    
    # Draw hits and misses on opponent board
    for y in range(BattleshipsGame.BOARD_SIZE):
        for x in range(BattleshipsGame.BOARD_SIZE):
            cell_x = offset_x + x * BattleshipsGame.CELL_SIZE + 1
            cell_y = offset_y + y * BattleshipsGame.CELL_SIZE + 1
            cell_rect = pygame.Rect(cell_x, cell_y, BattleshipsGame.CELL_SIZE - 2, BattleshipsGame.CELL_SIZE - 2)
            
            if player.opponent_board[y][x] == 2:
                # Hit with glow
                for i in range(2):
                    glow_rect = pygame.Rect(
                        cell_rect.x - i, cell_rect.y - i,
                        cell_rect.width + i * 2, cell_rect.height + i * 2
                    )
                    glow_color = tuple(min(255, c + (2-i) * 30) for c in COLOR_HIT[:3])
                    pygame.draw.rect(win, glow_color, glow_rect, border_radius=4)
                pygame.draw.rect(win, COLOR_HIT, cell_rect, border_radius=4)
                pygame.draw.circle(win, COLOR_TEXT_BRIGHT,
                                 (cell_x + BattleshipsGame.CELL_SIZE // 2, cell_y + BattleshipsGame.CELL_SIZE // 2),
                                 BattleshipsGame.CELL_SIZE // 4)
            elif player.opponent_board[y][x] == -1:
                # Miss
                pygame.draw.rect(win, COLOR_PANEL, cell_rect, border_radius=4)
                pygame.draw.circle(win, COLOR_MISS,
                                 (cell_x + BattleshipsGame.CELL_SIZE // 2, cell_y + BattleshipsGame.CELL_SIZE // 2),
                                 BattleshipsGame.CELL_SIZE // 5)
    
    # Turn status (placed between panels at top)
    if not player.game_over and (not opponent or not opponent.game_over):
        if player.current_turn == player.player_id:
            turn_text = "Si na rade!"
            turn_color = COLOR_HOVER
        else:
            turn_text = "Čakáš na súpera"
            turn_color = COLOR_MISS
        
        # Turn status panel
        turn_panel_width = 250
        turn_panel_height = 45
        turn_panel = pygame.Rect(width // 2 - turn_panel_width // 2, 20, turn_panel_width, turn_panel_height)
        
        # Glow effect
        for i in range(3):
            glow_turn = pygame.Rect(
                turn_panel.x - i, turn_panel.y - i,
                turn_panel.width + i * 2, turn_panel.height + i * 2
            )
            glow_color = tuple(min(255, c + (3-i) * 8) for c in turn_color[:3])
            pygame.draw.rect(win, glow_color, glow_turn, border_radius=10 + i)
        
        pygame.draw.rect(win, COLOR_PANEL, turn_panel, border_radius=10)
        pygame.draw.rect(win, turn_color, turn_panel, width=2, border_radius=10)
        
        # Turn text
        turn_surf = FONT_NORMAL.render(turn_text, True, turn_color)
        turn_rect = turn_surf.get_rect(center=turn_panel.center)
        shadow_turn = FONT_NORMAL.render(turn_text, True, (0, 0, 0))
        win.blit(shadow_turn, (turn_rect.x + 2, turn_rect.y + 2))
        win.blit(turn_surf, turn_rect)
    
    # Stats panel (bottom, improved styling)
    stats_y = own_panel.bottom + 15
    stats_panel = pygame.Rect(20, stats_y, width - 40, 60)
    
    # Panel glow effect
    for i in range(3):
        glow_stats = pygame.Rect(
            stats_panel.x - i, stats_panel.y - i,
            stats_panel.width + i * 2, stats_panel.height + i * 2
        )
        glow_color = tuple(min(255, c + (3-i) * 4) for c in COLOR_PANEL[:3])
        pygame.draw.rect(win, glow_color, glow_stats, border_radius=10 + i)
    
    pygame.draw.rect(win, COLOR_PANEL, stats_panel, border_radius=10)
    pygame.draw.rect(win, COLOR_GRID, stats_panel, width=2, border_radius=10)
    
    # Inner highlight
    highlight_stats = pygame.Rect(stats_panel.x + 2, stats_panel.y + 2, stats_panel.width - 4, 25)
    highlight_color = tuple(min(255, c + 10) for c in COLOR_PANEL[:3])
    pygame.draw.rect(win, highlight_color, highlight_stats, border_radius=8)
    
    # Stats text with better spacing
    stats_spacing = 180
    draw_label(win, f"Výstrely: {len(player.shots_fired)}", (stats_panel.x + 25, stats_panel.y + 20), size=24)
    draw_label(win, f"Zásahy: {len(player.hits)}", (stats_panel.x + 25 + stats_spacing, stats_panel.y + 20), size=24)
    
    if opponent:
        draw_label(win, f"Súper - Výstrely: {len(opponent.shots_fired)}", (stats_panel.x + 25 + stats_spacing * 2, stats_panel.y + 20), size=24)
        draw_label(win, f"Súper - Zásahy: {len(opponent.hits)}", (stats_panel.x + 25 + stats_spacing * 3, stats_panel.y + 20), size=24)
    
    # Game status with glow
    if player.game_over or (opponent and opponent.game_over):
        # Determine winner and loser
        if player.game_over:
            winner_id = player.winner
            loser_id = player.player_id
        elif opponent and opponent.game_over:
            winner_id = opponent.winner
            loser_id = opponent.player_id
        else:
            winner_id = None
            loser_id = None
        
        if winner_id is not None:
            # Determine if current player won or lost
            player_won = (winner_id == player.player_id)
            
            if player_won:
                status_text = f"Vyhral si"
                status_color = COLOR_HOVER
                loser_text = f"Hráč {loser_id + 1} prehral"
            else:
                status_text = f"Druhý hráč vyhral!"
                status_color = COLOR_HOVER
                loser_text = f"Prehral si"
            
            # Center positions
            center_y_winner = height // 2 - 30
            center_y_loser = height // 2 + 30
            
            # Winner text with glow
            for i in range(8):
                glow_surf = FONT_VICTORY.render(status_text, True, tuple(min(255, c + (8-i) * 8) for c in status_color[:3]))
                glow_rect = glow_surf.get_rect(center=(width // 2 + i, center_y_winner + i))
                win.blit(glow_surf, glow_rect)
            
            # Winner shadow
            shadow_surf = FONT_VICTORY.render(status_text, True, (0, 0, 0))
            shadow_rect = shadow_surf.get_rect(center=(width // 2 + 4, center_y_winner + 4))
            win.blit(shadow_surf, shadow_rect)
            
            # Winner text
            text_surf = FONT_VICTORY.render(status_text, True, status_color)
            text_rect = text_surf.get_rect(center=(width // 2, center_y_winner))
            win.blit(text_surf, text_rect)
            
            # Particles around winner text
            draw_victory_particles(win, width // 2, center_y_winner, game_time, status_color)
            
            # Loser text
            loser_color = COLOR_HIT if player_won else COLOR_MISS
            loser_surf = FONT_LARGE.render(loser_text, True, loser_color)
            loser_rect = loser_surf.get_rect(center=(width // 2, center_y_loser))
            shadow_loser = FONT_LARGE.render(loser_text, True, (0, 0, 0))
            win.blit(shadow_loser, (loser_rect.x + 3, loser_rect.y + 3))
            win.blit(loser_surf, loser_rect)
            
            # Particles around loser text (smaller)
            for i in range(15):
                angle = (game_time * 0.015 + i * (2 * math.pi / 15)) % (2 * math.pi)
                distance = 60 + math.sin(game_time * 0.08 + i) * 15
                x = width // 2 + math.cos(angle) * distance
                y = center_y_loser + math.sin(angle) * distance
                size = 2 + math.sin(game_time * 0.12 + i) * 1.5
                brightness = int(120 + math.sin(game_time * 0.18 + i) * 80)
                particle_color = tuple(min(255, c * brightness // 200) for c in loser_color[:3])
                pygame.draw.circle(win, particle_color, (int(x), int(y)), int(size))
    
    pygame.display.update()

def draw_victory_particles(surface, center_x, center_y, time, color):
    """Draw particles around victory text"""
    particle_count = 30
    for i in range(particle_count):
        angle = (time * 0.02 + i * (2 * math.pi / particle_count)) % (2 * math.pi)
        distance = 120 + math.sin(time * 0.05 + i) * 30
        x = center_x + math.cos(angle) * distance
        y = center_y + math.sin(angle) * distance
        size = 4 + math.sin(time * 0.1 + i) * 2.5
        brightness = int(150 + math.sin(time * 0.15 + i) * 105)
        particle_color = tuple(min(255, c * brightness // 255) for c in color[:3])
        pygame.draw.circle(surface, particle_color, (int(x), int(y)), int(size))

def get_grid_pos(mouse_pos, offset_x, offset_y):
    """Convert mouse position to grid coordinates"""
    x, y = mouse_pos
    grid_x = (x - offset_x) // BattleshipsGame.CELL_SIZE
    grid_y = (y - offset_y) // BattleshipsGame.CELL_SIZE
    return grid_x, grid_y

def main():
    pygame.init()
    
    # Show menu first
    menu = Menu(width, height)
    selected_mode, start_game = menu.run()
    
    if not start_game:
        pygame.quit()
        return
    
    # Initialize game window
    win = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Battleships")
    
    run = True
    n = Network()
    p = n.getP()
    clock = pygame.time.Clock()
    init_font()
    hover_cell = None
    game_time = 0
    
    if p is None:
        print("\nFailed to connect to server.")
        print("Press Enter to exit...")
        try:
            input()
        except:
            pass
        pygame.quit()
        return
    
    print(f"Selected game mode: {selected_mode}")
    
    while run:
        clock.tick(60)
        game_time += 1
        
        # Send current state and receive updated self + opponent state
        resp = n.send(p)
        if resp:
            p, p2 = resp
        else:
            p2 = None
        
        # Track hover cell on opponent grid
        mouse_pos = pygame.mouse.get_pos()
        panel_top = 75
        opponent_board_x = width // 2 + 20  # opp_panel.x + 10
        opponent_board_y = panel_top + 45  # opp_panel.y + 45
        if (opponent_board_x <= mouse_pos[0] < opponent_board_x + BattleshipsGame.BOARD_SIZE * BattleshipsGame.CELL_SIZE and
            opponent_board_y <= mouse_pos[1] < opponent_board_y + BattleshipsGame.BOARD_SIZE * BattleshipsGame.CELL_SIZE):
            grid_x, grid_y = get_grid_pos(mouse_pos, opponent_board_x, opponent_board_y)
            hover_cell = (grid_x, grid_y)
        else:
            hover_cell = None
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                return
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                
                # Check if click is on opponent board
                panel_top = 75
                opponent_board_x = width // 2 + 20  # opp_panel.x + 10
                opponent_board_y = panel_top + 45  # opp_panel.y + 45
                if (opponent_board_x <= mouse_pos[0] < opponent_board_x + BattleshipsGame.BOARD_SIZE * BattleshipsGame.CELL_SIZE and
                    opponent_board_y <= mouse_pos[1] < opponent_board_y + BattleshipsGame.BOARD_SIZE * BattleshipsGame.CELL_SIZE):
                    
                    grid_x, grid_y = get_grid_pos(mouse_pos, opponent_board_x, opponent_board_y)
                    
                    if 0 <= grid_x < BattleshipsGame.BOARD_SIZE and 0 <= grid_y < BattleshipsGame.BOARD_SIZE:
                        # Only allow shooting if it's this player's turn
                        if p.current_turn == p.player_id:
                            p.shoot(grid_x, grid_y)
        
        redrawWindow(win, p, p2, hover_cell, game_time)

if __name__ == "__main__":
    main()
