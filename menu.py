import pygame
import math

# Colors
COLOR_BG = (8, 12, 24)           # Darker navy background
COLOR_BG_GRADIENT = (15, 23, 42)  # Lighter navy
COLOR_PANEL = (30, 41, 59)
COLOR_PANEL_GLOW = (59, 130, 246, 30)  # Blue glow
COLOR_TEXT = (226, 232, 240)
COLOR_TEXT_BRIGHT = (255, 255, 255)
COLOR_HOVER = (94, 234, 212)      # Cyan for hover
COLOR_BUTTON = (59, 130, 246)     # Accent blue
COLOR_BUTTON_HOVER = (99, 102, 241)  # Indigo
COLOR_SELECTED = (94, 234, 212)   # Cyan for selected mode
COLOR_ACCENT = (239, 68, 68)     # Red accent

class Menu:
    def __init__(self, width=900, height=520):
        self.width = width
        self.height = height
        self.win = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Battleships - Menu")
        
        self.selected_mode = 0  # 0 or 1 for the two game modes
        self.font_title = None
        self.font_large = None
        self.font_normal = None
        self.font_small = None
        self.init_fonts()
        
        self.time = 0  # For animations
        self.pulse_offset = 0
    
    def init_fonts(self):
        pygame.font.init()
        self.font_title = pygame.font.Font(None, 72)
        self.font_large = pygame.font.Font(None, 48)
        self.font_normal = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
    
    def draw_gradient_background(self, surface):
        """Draw gradient background"""
        for y in range(self.height):
            ratio = y / self.height
            r = int(COLOR_BG[0] * (1 - ratio) + COLOR_BG_GRADIENT[0] * ratio)
            g = int(COLOR_BG[1] * (1 - ratio) + COLOR_BG_GRADIENT[1] * ratio)
            b = int(COLOR_BG[2] * (1 - ratio) + COLOR_BG_GRADIENT[2] * ratio)
            pygame.draw.line(surface, (r, g, b), (0, y), (self.width, y))
    
    def draw_glow_effect(self, surface, rect, color, intensity=5):
        """Draw glow effect around rectangle"""
        for i in range(intensity):
            glow_rect = pygame.Rect(
                rect.x - i * 2, rect.y - i * 2,
                rect.width + i * 4, rect.height + i * 4
            )
            # Use lighter color for glow
            glow_color = tuple(min(255, c + i * 10) for c in color[:3])
            pygame.draw.rect(surface, glow_color, glow_rect, width=1, border_radius=12 + i)
    
    def draw_label(self, surface, text, pos, size=32, color=COLOR_TEXT, shadow=True):
        if size == 72:
            font = self.font_title
        elif size == 48:
            font = self.font_large
        elif size == 24:
            font = self.font_small
        else:
            font = self.font_normal
        
        if shadow:
            shadow_surf = font.render(text, True, (0, 0, 0))
            surface.blit(shadow_surf, (pos[0] + 2, pos[1] + 2))
        
        text_surf = font.render(text, True, color)
        surface.blit(text_surf, pos)
    
    def draw_button(self, surface, text, rect, hover=False, pulse=False):
        # Glow effect on hover
        if hover:
            glow_color = COLOR_BUTTON_HOVER
            for i in range(4):
                glow_rect = pygame.Rect(
                    rect.x - i * 2, rect.y - i * 2,
                    rect.width + i * 4, rect.height + i * 4
                )
                # Create lighter glow color
                light_color = tuple(min(255, c + (4-i) * 15) for c in glow_color[:3])
                pygame.draw.rect(surface, light_color, glow_rect, width=1, border_radius=12)
        
        # Pulse animation
        if pulse:
            pulse_size = int(math.sin(self.time * 0.1) * 3)
            rect = pygame.Rect(
                rect.x - pulse_size, rect.y - pulse_size,
                rect.width + pulse_size * 2, rect.height + pulse_size * 2
            )
        
        color = COLOR_BUTTON_HOVER if hover else COLOR_BUTTON
        pygame.draw.rect(surface, color, rect, border_radius=12)
        
        # Inner highlight
        highlight = pygame.Rect(rect.x + 2, rect.y + 2, rect.width - 4, rect.height // 2)
        highlight_color = tuple(min(255, c + 30) for c in color[:3])
        pygame.draw.rect(surface, highlight_color, highlight, border_radius=10)
        
        # Border
        border_color = COLOR_HOVER if hover else COLOR_TEXT
        pygame.draw.rect(surface, border_color, rect, width=3, border_radius=12)
        
        # Text with shadow
        text_surf = self.font_normal.render(text, True, COLOR_TEXT_BRIGHT)
        text_rect = text_surf.get_rect(center=rect.center)
        shadow_surf = self.font_normal.render(text, True, (0, 0, 0))
        surface.blit(shadow_surf, (text_rect.x + 2, text_rect.y + 2))
        surface.blit(text_surf, text_rect)
    
    def draw_mode_button(self, surface, text, rect, selected=False, hover=False):
        # Glow effect
        if selected or hover:
            glow_color = COLOR_SELECTED if selected else COLOR_HOVER
            for i in range(5):
                glow_rect = pygame.Rect(
                    rect.x - i, rect.y - i,
                    rect.width + i * 2, rect.height + i * 2
                )
                # Create lighter glow
                light_glow = tuple(min(255, c + (5-i) * 10) for c in glow_color[:3])
                pygame.draw.rect(surface, light_glow, glow_rect, width=1, border_radius=10)
        
        if selected:
            color = COLOR_SELECTED
            border_color = COLOR_SELECTED
            border_width = 4
        elif hover:
            color = COLOR_PANEL
            border_color = COLOR_HOVER
            border_width = 3
        else:
            color = COLOR_PANEL
            border_color = COLOR_TEXT
            border_width = 2
        
        # Background with gradient effect
        pygame.draw.rect(surface, color, rect, border_radius=10)
        
        # Inner highlight
        if selected:
            highlight = pygame.Rect(rect.x + 3, rect.y + 3, rect.width - 6, rect.height // 2)
            highlight_color = tuple(min(255, c + 40) for c in COLOR_SELECTED[:3])
            pygame.draw.rect(surface, highlight_color, highlight, border_radius=8)
        
        # Border
        pygame.draw.rect(surface, border_color, rect, width=border_width, border_radius=10)
        
        # Icon/indicator for selected
        if selected:
            indicator = pygame.Rect(rect.right - 25, rect.y + 10, 15, 15)
            pygame.draw.circle(surface, COLOR_SELECTED, indicator.center, 7)
            pygame.draw.circle(surface, COLOR_TEXT_BRIGHT, indicator.center, 4)
        
        # Text
        text_surf = self.font_normal.render(text, True, COLOR_TEXT_BRIGHT if selected else COLOR_TEXT)
        text_rect = text_surf.get_rect(center=rect.center)
        shadow_surf = self.font_normal.render(text, True, (0, 0, 0))
        surface.blit(shadow_surf, (text_rect.x + 1, text_rect.y + 1))
        surface.blit(text_surf, text_rect)
    
    def draw_particles(self, surface):
        """Draw animated particles in background"""
        particle_count = 15
        for i in range(particle_count):
            x = (self.time * 8 + i * 60) % (self.width + 100) - 50
            y = self.height // 2 + math.sin(self.time * 0.05 + i) * 80
            size = 2 + math.sin(self.time * 0.1 + i) * 1.5
            # Vary brightness
            brightness = int(100 + math.sin(self.time * 0.15 + i) * 100)
            color = tuple(min(255, c * brightness // 200) for c in COLOR_BUTTON[:3])
            pygame.draw.circle(surface, color, (int(x), int(y)), int(size))
    
    def run(self):
        run = True
        clock = pygame.time.Clock()
        
        # Button positions
        start_button = pygame.Rect(self.width // 2 - 140, self.height // 2 - 35, 280, 70)
        
        start_hover = False
        
        while run:
            clock.tick(60)
            self.time += 1
            mouse_pos = pygame.mouse.get_pos()
            
            # Check hover states
            start_hover = start_button.collidepoint(mouse_pos)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None, None
                
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if start_button.collidepoint(mouse_pos):
                        return self.selected_mode, True  # Return mode and start flag
            
            # Draw everything
            self.draw_gradient_background(self.win)
            
            # Background particles
            self.draw_particles(self.win)
            
            # Title with glow effect
            title_text = "BATTLESHIPS"
            title_surf = self.font_title.render(title_text, True, COLOR_TEXT_BRIGHT)
            title_rect = title_surf.get_rect(center=(self.width // 2, 120))
            
            # Title glow
            for i in range(6):
                glow_intensity = 30 - i * 4
                glow_color = tuple(min(255, c + glow_intensity) for c in COLOR_BUTTON[:3])
                glow_surf = self.font_title.render(title_text, True, glow_color)
                glow_rect = glow_surf.get_rect(center=(self.width // 2 + i, 120 + i))
                self.win.blit(glow_surf, glow_rect)
            
            # Title shadow
            shadow_surf = self.font_title.render(title_text, True, (0, 0, 0))
            shadow_rect = shadow_surf.get_rect(center=(self.width // 2 + 3, 123))
            self.win.blit(shadow_surf, shadow_rect)
            
            # Title
            self.win.blit(title_surf, title_rect)
            
            # Start button with pulse
            pulse = start_hover
            self.draw_button(self.win, "START GAME", start_button, hover=start_hover, pulse=pulse)
            
            pygame.display.update()
        
        return None, None
