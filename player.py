import pygame
import random

class BattleshipsGame:
    BOARD_SIZE = 10
    CELL_SIZE = 30
    
    SHIPS = [5, 4, 3, 3, 2]  # Ship sizes
    
    def __init__(self, player_id):
        self.player_id = player_id
        self.own_board = [[0 for _ in range(self.BOARD_SIZE)] for _ in range(self.BOARD_SIZE)]
        self.opponent_board = [[0 for _ in range(self.BOARD_SIZE)] for _ in range(self.BOARD_SIZE)]
        self.ships = []  # List of ship positions [(x, y, length, horizontal), ...]
        self.shots_fired = []  # List of shots [(x, y), ...]
        self.hits = []  # List of hits [(x, y), ...]
        self.setup_complete = False
        self.game_over = False
        self.winner = None
        
        # Auto-place ships for now (can be changed to manual placement)
        if not self.setup_complete:
            self.auto_place_ships()
    
    def auto_place_ships(self):
        """Automatically place ships on the board"""
        self.ships = []
        for ship_size in self.SHIPS:
            placed = False
            attempts = 0
            while not placed and attempts < 100:
                horizontal = random.choice([True, False])
                if horizontal:
                    x = random.randint(0, self.BOARD_SIZE - ship_size)
                    y = random.randint(0, self.BOARD_SIZE - 1)
                else:
                    x = random.randint(0, self.BOARD_SIZE - 1)
                    y = random.randint(0, self.BOARD_SIZE - ship_size)
                
                # Check if position is valid (no overlap)
                valid = True
                for i in range(ship_size):
                    if horizontal:
                        check_x, check_y = x + i, y
                    else:
                        check_x, check_y = x, y + i
                    
                    # Check overlap with existing ships
                    for sx, sy, slen, shor in self.ships:
                        for j in range(slen):
                            if shor:
                                if sx + j == check_x and sy == check_y:
                                    valid = False
                                    break
                            else:
                                if sx == check_x and sy + j == check_y:
                                    valid = False
                                    break
                        if not valid:
                            break
                    
                    if not valid:
                        break
                
                if valid:
                    self.ships.append((x, y, ship_size, horizontal))
                    # Mark on board
                    for i in range(ship_size):
                        if horizontal:
                            self.own_board[y][x + i] = 1
                        else:
                            self.own_board[y + i][x] = 1
                    placed = True
                attempts += 1
        
        self.setup_complete = True
    
    def place_ship(self, x, y, length, horizontal):
        """Manually place a ship"""
        if x < 0 or y < 0:
            return False
        if horizontal and x + length > self.BOARD_SIZE:
            return False
        if not horizontal and y + length > self.BOARD_SIZE:
            return False
        
        # Check overlap
        for sx, sy, slen, shor in self.ships:
            for i in range(length):
                check_x = x + i if horizontal else x
                check_y = y if horizontal else y + i
                for j in range(slen):
                    ship_x = sx + j if shor else sx
                    ship_y = sy if shor else sy + j
                    if check_x == ship_x and check_y == ship_y:
                        return False
        
        self.ships.append((x, y, length, horizontal))
        for i in range(length):
            if horizontal:
                self.own_board[y][x + i] = 1
            else:
                self.own_board[y + i][x] = 1
        return True
    
    def shoot(self, x, y):
        """Shoot at opponent's board"""
        if (x, y) in self.shots_fired:
            return False  # Already shot here
        if x < 0 or x >= self.BOARD_SIZE or y < 0 or y >= self.BOARD_SIZE:
            return False
        
        self.shots_fired.append((x, y))
        return True
    
    def receive_shot(self, x, y):
        """Receive a shot from opponent"""
        if x < 0 or x >= self.BOARD_SIZE or y < 0 or y >= self.BOARD_SIZE:
            return False
        
        # Check if already shot
        if self.own_board[y][x] == 2 or self.own_board[y][x] == -1:
            return self.own_board[y][x] == 2  # Return True if hit, False if miss
        
        hit = self.own_board[y][x] == 1
        if hit:
            self.own_board[y][x] = 2  # Hit
            self.hits.append((x, y))
        else:
            self.own_board[y][x] = -1  # Miss
        
        # Check if all ships are sunk
        all_sunk = True
        for sx, sy, slen, shor in self.ships:
            ship_sunk = True
            for i in range(slen):
                check_x = sx + i if shor else sx
                check_y = sy if shor else sy + i
                if self.own_board[check_y][check_x] != 2:
                    ship_sunk = False
                    break
            if not ship_sunk:
                all_sunk = False
                break
        
        if all_sunk:
            self.game_over = True
        
        return hit
    
    def update_opponent_board(self, x, y, hit):
        """Update opponent board after shooting"""
        if hit:
            self.opponent_board[y][x] = 2  # Hit
        else:
            self.opponent_board[y][x] = -1  # Miss
    
    def draw(self, win, offset_x, offset_y, show_ships=True):
        """Draw the board"""
        # Draw grid
        for i in range(self.BOARD_SIZE + 1):
            # Vertical lines
            pygame.draw.line(win, (0, 0, 0), 
                           (offset_x + i * self.CELL_SIZE, offset_y),
                           (offset_x + i * self.CELL_SIZE, offset_y + self.BOARD_SIZE * self.CELL_SIZE), 1)
            # Horizontal lines
            pygame.draw.line(win, (0, 0, 0),
                           (offset_x, offset_y + i * self.CELL_SIZE),
                           (offset_x + self.BOARD_SIZE * self.CELL_SIZE, offset_y + i * self.CELL_SIZE), 1)
        
        # Draw cells
        for y in range(self.BOARD_SIZE):
            for x in range(self.BOARD_SIZE):
                cell_x = offset_x + x * self.CELL_SIZE + 1
                cell_y = offset_y + y * self.CELL_SIZE + 1
                cell_rect = pygame.Rect(cell_x, cell_y, self.CELL_SIZE - 2, self.CELL_SIZE - 2)
                
                if self.own_board[y][x] == 1 and show_ships:
                    # Ship (only show on own board)
                    pygame.draw.rect(win, (100, 100, 200), cell_rect)
                elif self.own_board[y][x] == 2:
                    # Hit
                    pygame.draw.rect(win, (200, 0, 0), cell_rect)
                    pygame.draw.circle(win, (255, 255, 255), 
                                     (cell_x + self.CELL_SIZE // 2, cell_y + self.CELL_SIZE // 2), 
                                     self.CELL_SIZE // 3)
                elif self.own_board[y][x] == -1:
                    # Miss
                    pygame.draw.circle(win, (150, 150, 150),
                                     (cell_x + self.CELL_SIZE // 2, cell_y + self.CELL_SIZE // 2),
                                     self.CELL_SIZE // 4)
        
        # Draw opponent board hits/misses
        if not show_ships:
            for y in range(self.BOARD_SIZE):
                for x in range(self.BOARD_SIZE):
                    cell_x = offset_x + x * self.CELL_SIZE + 1
                    cell_y = offset_y + y * self.CELL_SIZE + 1
                    
                    if self.opponent_board[y][x] == 2:
                        # Hit
                        pygame.draw.rect(win, (200, 0, 0), 
                                       pygame.Rect(cell_x, cell_y, self.CELL_SIZE - 2, self.CELL_SIZE - 2))
                        pygame.draw.circle(win, (255, 255, 255),
                                         (cell_x + self.CELL_SIZE // 2, cell_y + self.CELL_SIZE // 2),
                                         self.CELL_SIZE // 3)
                    elif self.opponent_board[y][x] == -1:
                        # Miss
                        pygame.draw.circle(win, (150, 150, 150),
                                         (cell_x + self.CELL_SIZE // 2, cell_y + self.CELL_SIZE // 2),
                                         self.CELL_SIZE // 4)
