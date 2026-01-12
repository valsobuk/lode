import pygame
from network import Network
from player import BattleshipsGame

width = 800
height = 400
win = pygame.display.set_mode((width, height))
pygame.display.set_caption("Battleships")

FONT = None

def init_font():
    global FONT
    pygame.font.init()
    FONT = pygame.font.Font(None, 24)

def redrawWindow(win, player, opponent):
    win.fill((255, 255, 255))
    
    # Draw own board (left)
    font = pygame.font.Font(None, 20)
    text = font.render("Your Board", True, (0, 0, 0))
    win.blit(text, (10, 10))
    player.draw(win, 10, 40, show_ships=True)
    
    # Draw opponent board (right) - use player's opponent_board which tracks hits/misses
    text = font.render("Opponent Board", True, (0, 0, 0))
    win.blit(text, (width // 2 + 10, 10))
    
    # Draw opponent board grid
    offset_x = width // 2 + 10
    offset_y = 40
    for i in range(BattleshipsGame.BOARD_SIZE + 1):
        pygame.draw.line(win, (0, 0, 0), 
                       (offset_x + i * BattleshipsGame.CELL_SIZE, offset_y),
                       (offset_x + i * BattleshipsGame.CELL_SIZE, offset_y + BattleshipsGame.BOARD_SIZE * BattleshipsGame.CELL_SIZE), 1)
        pygame.draw.line(win, (0, 0, 0),
                       (offset_x, offset_y + i * BattleshipsGame.CELL_SIZE),
                       (offset_x + BattleshipsGame.BOARD_SIZE * BattleshipsGame.CELL_SIZE, offset_y + i * BattleshipsGame.CELL_SIZE), 1)
    
    # Draw hits and misses on opponent board
    for y in range(BattleshipsGame.BOARD_SIZE):
        for x in range(BattleshipsGame.BOARD_SIZE):
            cell_x = offset_x + x * BattleshipsGame.CELL_SIZE + 1
            cell_y = offset_y + y * BattleshipsGame.CELL_SIZE + 1
            
            if player.opponent_board[y][x] == 2:
                # Hit
                pygame.draw.rect(win, (200, 0, 0),
                               pygame.Rect(cell_x, cell_y, BattleshipsGame.CELL_SIZE - 2, BattleshipsGame.CELL_SIZE - 2))
                pygame.draw.circle(win, (255, 255, 255),
                                 (cell_x + BattleshipsGame.CELL_SIZE // 2, cell_y + BattleshipsGame.CELL_SIZE // 2),
                                 BattleshipsGame.CELL_SIZE // 3)
            elif player.opponent_board[y][x] == -1:
                # Miss
                pygame.draw.circle(win, (150, 150, 150),
                                 (cell_x + BattleshipsGame.CELL_SIZE // 2, cell_y + BattleshipsGame.CELL_SIZE // 2),
                                 BattleshipsGame.CELL_SIZE // 4)
    
    # Draw game status
    if player.game_over or (opponent and opponent.game_over):
        font = pygame.font.Font(None, 36)
        if player.game_over and player.winner != player.player_id:
            text = font.render("You Lose!", True, (200, 0, 0))
        elif opponent and opponent.game_over and opponent.winner != player.player_id:
            text = font.render("You Win!", True, (0, 200, 0))
        elif player.game_over:
            text = font.render("You Win!", True, (0, 200, 0))
        else:
            text = font.render("You Lose!", True, (200, 0, 0))
        win.blit(text, (width // 2 - 80, height - 50))
    
    pygame.display.update()

def get_grid_pos(mouse_pos, offset_x, offset_y):
    """Convert mouse position to grid coordinates"""
    x, y = mouse_pos
    grid_x = (x - offset_x) // BattleshipsGame.CELL_SIZE
    grid_y = (y - offset_y) // BattleshipsGame.CELL_SIZE
    return grid_x, grid_y

def main():
    run = True
    n = Network()
    p = n.getP()
    clock = pygame.time.Clock()
    init_font()
    
    if p is None:
        print("Failed to connect")
        return
    
    while run:
        clock.tick(60)
        
        # Send current state and receive updated self + opponent state
        resp = n.send(p)
        if resp:
            p, p2 = resp
        else:
            p2 = None
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                return
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                
                # Check if click is on opponent board
                opponent_board_x = width // 2 + 10
                opponent_board_y = 40
                if (opponent_board_x <= mouse_pos[0] < opponent_board_x + BattleshipsGame.BOARD_SIZE * BattleshipsGame.CELL_SIZE and
                    opponent_board_y <= mouse_pos[1] < opponent_board_y + BattleshipsGame.BOARD_SIZE * BattleshipsGame.CELL_SIZE):
                    
                    grid_x, grid_y = get_grid_pos(mouse_pos, opponent_board_x, opponent_board_y)
                    
                    if 0 <= grid_x < BattleshipsGame.BOARD_SIZE and 0 <= grid_y < BattleshipsGame.BOARD_SIZE:
                        p.shoot(grid_x, grid_y)
        
        # The server handles shot processing, we just sync state
        
        redrawWindow(win, p, p2)

if __name__ == "__main__":
    main()
