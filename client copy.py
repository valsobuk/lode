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

def init_font():
    global FONT, FONT_LARGE, FONT_NORMAL
    pygame.font.init()
    FONT = pygame.font.Font(None, 24)
    FONT_LARGE = pygame.font.Font(None, 36)
    FONT_NORMAL = pygame.font.Font(None, 28)

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

def redrawWindow(win, player, opponent, hover_cell=None):
    draw_gradient_background(win, width, height)
    
    # Panels with rounded corners
    own_panel = pygame.Rect(20, 20, BattleshipsGame.BOARD_SIZE * BattleshipsGame.CELL_SIZE + 20,
                            BattleshipsGame.BOARD_SIZE * BattleshipsGame.CELL_SIZE + 60)
    opp_panel = pygame.Rect(width // 2 + 10, 20, BattleshipsGame.BOARD_SIZE * BattleshipsGame.CELL_SIZE + 20,
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
    
    # Stats panel
    stats_y = own_panel.bottom + 15
    stats_panel = pygame.Rect(20, stats_y, width - 40, 50)
    pygame.draw.rect(win, COLOR_PANEL, stats_panel, border_radius=8)
    pygame.draw.rect(win, COLOR_GRID, stats_panel, width=2, border_radius=8)
    
    draw_label(win, f"Shots: {len(player.shots_fired)}", (stats_panel.x + 20, stats_panel.y + 15), size=24)
    draw_label(win, f"Hits: {len(player.hits)}", (stats_panel.x + 200, stats_panel.y + 15), size=24)
    
    if opponent:
        draw_label(win, f"Enemy Shots: {len(opponent.shots_fired)}", (stats_panel.x + 400, stats_panel.y + 15), size=24)
        draw_label(win, f"Enemy Hits: {len(opponent.hits)}", (stats_panel.x + 600, stats_panel.y + 15), size=24)
    
    # Turn status
    if not player.game_over and (not opponent or not opponent.game_over):
        if player.current_turn == player.player_id:
            turn_text = "Your Turn"
            turn_color = COLOR_HOVER
        else:
            turn_text = "Opponent's Turn"
            turn_color = COLOR_MISS
        draw_label(win, turn_text, (width // 2 - 80, height - 80), size=28, color=turn_color)
    
    # Game status with glow
    if player.game_over or (opponent and opponent.game_over):
        if player.game_over and player.winner != player.player_id:
            status_text = "You Lose!"
            status_color = COLOR_HIT
        elif opponent and opponent.game_over and opponent.winner != player.player_id:
            status_text = "You Win!"
            status_color = COLOR_HOVER
        elif player.game_over:
            status_text = "You Win!"
            status_color = COLOR_HOVER
        else:
            status_text = "You Lose!"
            status_color = COLOR_HIT
        
        # Glow effect
        for i in range(5):
            glow_surf = FONT_LARGE.render(status_text, True, tuple(min(255, c + (5-i) * 10) for c in status_color[:3]))
            glow_rect = glow_surf.get_rect(center=(width // 2 + i, height - 40 + i))
            win.blit(glow_surf, glow_rect)
        
        # Shadow
        shadow_surf = FONT_LARGE.render(status_text, True, (0, 0, 0))
        shadow_rect = shadow_surf.get_rect(center=(width // 2 + 3, height - 37))
        win.blit(shadow_surf, shadow_rect)
        
        # Text
        text_surf = FONT_LARGE.render(status_text, True, status_color)
        text_rect = text_surf.get_rect(center=(width // 2, height - 40))
        win.blit(text_surf, text_rect)
    
    pygame.display.update()

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
    
    if p is None:
        print("Failed to connect")
        pygame.quit()
        return
    
    print(f"Selected game mode: {selected_mode}")
    
    while run:
        clock.tick(60)
        
        # Send current state and receive updated self + opponent state
        resp = n.send(p)
        if resp:
            p, p2 = resp
        else:
            p2 = None
        
        # Track hover cell on opponent grid
        mouse_pos = pygame.mouse.get_pos()
        opponent_board_x = width // 2 + 20  # opp_panel.x + 10
        opponent_board_y = 65  # opp_panel.y + 45
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
                opponent_board_x = width // 2 + 20  # opp_panel.x + 10
                opponent_board_y = 65  # opp_panel.y + 45
                if (opponent_board_x <= mouse_pos[0] < opponent_board_x + BattleshipsGame.BOARD_SIZE * BattleshipsGame.CELL_SIZE and
                    opponent_board_y <= mouse_pos[1] < opponent_board_y + BattleshipsGame.BOARD_SIZE * BattleshipsGame.CELL_SIZE):
                    
                    grid_x, grid_y = get_grid_pos(mouse_pos, opponent_board_x, opponent_board_y)
                    
                    if 0 <= grid_x < BattleshipsGame.BOARD_SIZE and 0 <= grid_y < BattleshipsGame.BOARD_SIZE:
                        # Only allow shooting if it's this player's turn
                        if p.current_turn == p.player_id:
                            p.shoot(grid_x, grid_y)
        
        redrawWindow(win, p, p2, hover_cell)

if __name__ == "__main__":
    main()
