import pygame
import sys
import random

# --- Configuration & Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BLOCK_SIZE = 20
FPS = 15  # Controls game speed

# Colors (Cyberpunk Palette)
COLOR_BG = (10, 10, 20)          # Dark Blue/Black
COLOR_GRID = (30, 30, 50)        # Faint Grid Lines
COLOR_SNAKE = (0, 255, 255)      # Cyan Neon
COLOR_SNAKE_GLOW = (0, 200, 200) # Slightly darker cyan for glow
COLOR_FOOD = (255, 0, 128)       # Hot Pink Neon
COLOR_FOOD_GLOW = (200, 0, 100)  # Darker pink
COLOR_TEXT = (255, 255, 255)     # White
COLOR_ACCENT = (255, 255, 0)     # Yellow for UI accents

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Cyber Snake")
clock = pygame.time.Clock()

# Fonts (Using system fonts to ensure compatibility)
try:
    FONT_MAIN = pygame.font.SysFont("consolas", 30)
    FONT_TITLE = pygame.font.SysFont("impact", 70)
    FONT_SMALL = pygame.font.SysFont("consolas", 20)
except:
    FONT_MAIN = pygame.font.SysFont("arial", 30)
    FONT_TITLE = pygame.font.SysFont("arial", 70, bold=True)
    FONT_SMALL = pygame.font.SysFont("arial", 20)

# --- Helper Functions ---

def draw_glow_rect(surface, color, rect, glow_color):
    """Draws a rectangle with a 'glow' effect by drawing a larger, transparent rect behind it."""
    # Create a surface for the glow (handling transparency)
    glow_surf = pygame.Surface((rect.width + 10, rect.height + 10), pygame.SRCALPHA)
    
    # Calculate alpha based on color intensity or fixed
    r, g, b = glow_color
    pygame.draw.rect(glow_surf, (r, g, b, 100), glow_surf.get_rect(), border_radius=5)
    
    # Blit glow centered on the target position
    surface.blit(glow_surf, (rect.x - 5, rect.y - 5))
    
    # Draw the main solid rectangle
    pygame.draw.rect(surface, color, rect, border_radius=3)
    
    # Draw a faint white center for "brightness"
    center_rect = rect.inflate(-10, -10)
    pygame.draw.rect(surface, (255, 255, 255), center_rect, border_radius=1)

def draw_grid():
    """Draws a retro-wave style grid background."""
    for x in range(0, SCREEN_WIDTH, BLOCK_SIZE):
        pygame.draw.line(screen, COLOR_GRID, (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, BLOCK_SIZE):
        pygame.draw.line(screen, COLOR_GRID, (0, y), (SCREEN_WIDTH, y))

def draw_scanlines():
    """Draws horizontal scanlines for a monitor effect."""
    for y in range(0, SCREEN_HEIGHT, 4):
        pygame.draw.line(screen, (0, 0, 0), (0, y), (SCREEN_WIDTH, y))

def draw_text_centered(text, font, color, y_offset=0, shadow=True):
    """Draws text centered on the screen with an optional shadow."""
    if shadow:
        shadow_surf = font.render(text, True, (0, 0, 0))
        shadow_rect = shadow_surf.get_rect(center=(SCREEN_WIDTH // 2 + 3, SCREEN_HEIGHT // 2 + y_offset + 3))
        screen.blit(shadow_surf, shadow_rect)
        
        # Neon glow for text
        glow_surf = font.render(text, True, COLOR_FOOD)
        glow_rect = glow_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + y_offset))
        screen.blit(glow_surf, (glow_rect.x - 1, glow_rect.y))
        screen.blit(glow_surf, (glow_rect.x + 1, glow_rect.y))

    text_surf = font.render(text, True, color)
    text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + y_offset))
    screen.blit(text_surf, text_rect)

# --- Main Game Classes ---

class Snake:
    def __init__(self):
        self.reset()

    def reset(self):
        self.body = [
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
            (SCREEN_WIDTH // 2 - BLOCK_SIZE, SCREEN_HEIGHT // 2),
            (SCREEN_WIDTH // 2 - (2 * BLOCK_SIZE), SCREEN_HEIGHT // 2)
        ]
        self.direction = (BLOCK_SIZE, 0) # Moving Right
        self.new_direction = self.direction
        self.grow = False

    def update(self):
        # Update direction
        self.direction = self.new_direction

        # Calculate new head position
        head_x, head_y = self.body[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)

        # Check Wall Collision
        if (new_head[0] < 0 or new_head[0] >= SCREEN_WIDTH or
            new_head[1] < 0 or new_head[1] >= SCREEN_HEIGHT):
            return False # Game Over

        # Check Self Collision
        if new_head in self.body:
            return False # Game Over

        # Move Snake
        self.body.insert(0, new_head)
        if not self.grow:
            self.body.pop()
        else:
            self.grow = False
        
        return True # Game continues

    def draw(self):
        for segment in self.body:
            rect = pygame.Rect(segment[0], segment[1], BLOCK_SIZE - 2, BLOCK_SIZE - 2)
            draw_glow_rect(screen, COLOR_SNAKE, rect, COLOR_SNAKE_GLOW)

    def change_direction(self, direction):
        # Prevent 180-degree turns
        if (direction[0] * -1, direction[1] * -1) != self.direction:
            self.new_direction = direction

class Food:
    def __init__(self):
        self.position = (0, 0)
        self.spawn()

    def spawn(self):
        x = random.randint(0, (SCREEN_WIDTH // BLOCK_SIZE) - 1) * BLOCK_SIZE
        y = random.randint(0, (SCREEN_HEIGHT // BLOCK_SIZE) - 1) * BLOCK_SIZE
        self.position = (x, y)

    def draw(self):
        rect = pygame.Rect(self.position[0], self.position[1], BLOCK_SIZE - 2, BLOCK_SIZE - 2)
        draw_glow_rect(screen, COLOR_FOOD, rect, COLOR_FOOD_GLOW)

# --- Main Logic ---

def main():
    snake = Snake()
    food = Food()
    
    # States: MENU, PLAYING, GAMEOVER
    state = "MENU"
    score = 0
    
    while True:
        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if state == "MENU":
                    if event.key == pygame.K_RETURN:
                        state = "PLAYING"
                        snake.reset()
                        score = 0
                        food.spawn()
                    elif event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()

                elif state == "PLAYING":
                    if event.key == pygame.K_UP:
                        snake.change_direction((0, -BLOCK_SIZE))
                    elif event.key == pygame.K_DOWN:
                        snake.change_direction((0, BLOCK_SIZE))
                    elif event.key == pygame.K_LEFT:
                        snake.change_direction((-BLOCK_SIZE, 0))
                    elif event.key == pygame.K_RIGHT:
                        snake.change_direction((BLOCK_SIZE, 0))
                    elif event.key == pygame.K_ESCAPE:
                        state = "MENU" # Pause/Back to menu
                
                elif state == "GAMEOVER":
                    if event.key == pygame.K_r:
                        state = "PLAYING"
                        snake.reset()
                        score = 0
                        food.spawn()
                    elif event.key == pygame.K_q:
                        state = "MENU"

        # Game Logic Update
        if state == "PLAYING":
            if not snake.update():
                state = "GAMEOVER"
            
            # Check Food Collision
            if snake.body[0] == food.position:
                snake.grow = True
                score += 1
                food.spawn()
                # Ensure food doesn't spawn inside snake
                while food.position in snake.body:
                    food.spawn()

        # --- Rendering ---
        screen.fill(COLOR_BG)
        draw_grid()

        if state == "MENU":
            # Draw Title Screen
            draw_text_centered("CYBER SNAKE", FONT_TITLE, COLOR_SNAKE, -100)
            draw_text_centered("PROTOCOL: CONSUME", FONT_MAIN, COLOR_ACCENT, -30)
            
            # Blinking "Press Enter"
            if pygame.time.get_ticks() % 1000 < 500:
                draw_text_centered("PRESS [ENTER] TO START", FONT_MAIN, COLOR_TEXT, 50)
            
            draw_text_centered("PRESS [Q] TO QUIT", FONT_SMALL, (150, 150, 150), 100)

        elif state == "PLAYING":
            snake.draw()
            food.draw()
            
            # UI: Score
            score_text = FONT_MAIN.render(f"DATA: {score} MB", True, COLOR_TEXT)
            screen.blit(score_text, (10, 10))

        elif state == "GAMEOVER":
            # Draw elements in background but dimmed (optional)
            snake.draw() 
            food.draw()
            
            # Overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
            draw_text_centered("SYSTEM FAILURE", FONT_TITLE, (255, 50, 50), -50)
            draw_text_centered(f"DATA COLLECTED: {score} MB", FONT_MAIN, COLOR_SNAKE, 20)
            draw_text_centered("PRESS [R] TO REBOOT", FONT_MAIN, COLOR_TEXT, 70)
            draw_text_centered("PRESS [Q] FOR MENU", FONT_SMALL, (150, 150, 150), 110)

        # Apply scanlines over everything for retro feel
        draw_scanlines()

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
