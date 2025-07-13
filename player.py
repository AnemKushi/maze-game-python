import pygame
import sys
import random

pygame.init()

WIDTH, HEIGHT = 800, 700
BLACK = (0, 0, 0)
RED = (255, 0, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Automata Maze Runner")

player_image = pygame.image.load("img/player.png")
player_image = pygame.transform.scale(player_image, (40, 40))
background_image = pygame.image.load("img/background.jpg")
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
bomb_image = pygame.image.load("img/bomb.png")
bomb_image = pygame.transform.scale(bomb_image, (50, 50))
blastimage = [pygame.image.load("img/blast0.png")]

cell_size = 50
maze_width = WIDTH // cell_size
maze_height = HEIGHT // cell_size
wall_color = (66, 58, 58)
exit_color = (0, 255, 0)

def generate_maze(width, height):
    maze = [[" " for _ in range(width)] for _ in range(height)]

    for x in range(width):
        maze[0][x] = "*"
        maze[height - 1][x] = "*"
    for y in range(height):
        maze[y][0] = "*"
        maze[y][width - 1] = "*"

    for y in range(0, height - 1, 2):
        for x in range(0, width - 1, 2):
            maze[y][x] = "*"

    start_point = (1, 1)
    end_point = (height - 2, width - 2)

    bomb_locations = []
    while len(bomb_locations) < 15:  
        x = random.randint(1, width - 2)
        y = random.randint(1, height - 2)

        if (x, y) != start_point and (x, y) != end_point and not in_line_of_sight(start_point, end_point, (x, y)):
            bomb_locations.append((x, y))
            maze[y][x] = "B"

    maze[1][1] = " "
    maze[height - 2][width - 2] = "E"

    return maze

def in_line_of_sight(start, end, point):
    x1, y1 = start
    x2, y2 = end
    x, y = point

    if (x - x1) * (y2 - y1) == (y - y1) * (x2 - x1):
        return True
    return False

maze = generate_maze(maze_width, maze_height)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_image
        self.rect = self.image.get_rect(topleft=(cell_size, cell_size))

    def update(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

def draw_maze():
    for y, row in enumerate(maze):
        for x, cell in enumerate(row):
            if cell == "*":
                pygame.draw.rect(screen, wall_color, (x * cell_size, y * cell_size, cell_size, cell_size))
            elif cell == "E":
                pygame.draw.rect(screen, exit_color, (x * cell_size, y * cell_size, cell_size, cell_size))
            elif cell == "B":
                screen.blit(bomb_image, (x * cell_size, y * cell_size))


def animate_blast():
    blast_duration = 600 
    start_time = pygame.time.get_ticks()

    blast_image_width, blast_image_height = blastimage[0].get_size()  

    while pygame.time.get_ticks() - start_time < blast_duration:
        for blast_image in blastimage:
            center_x = WIDTH // 2 - blast_image_width // 2  
            center_y = HEIGHT // 2 - blast_image_height // 2  
            screen.blit(blast_image, (center_x, center_y))  
            pygame.display.flip()

start_message = pygame.font.Font(None, 72).render("Press any key to start", True, BLACK)
game_over_message = pygame.font.Font(None, 72).render("Game Over", True, RED)
game_over_rect = game_over_message.get_rect(center=(WIDTH // 2, HEIGHT // 2))

player = Player()
all_sprites = pygame.sprite.Group(player)
clock = pygame.time.Clock()

game_started = False
game_over = False

running = True
while running:
    screen.blit(background_image, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if not game_started:
                game_started = True
            elif game_over:
                if event.key == pygame.K_RETURN:  
                    game_over = False
                    game_started = False
                    player.rect.topleft = (cell_size, cell_size)  

    if not game_started:
        screen.blit(start_message, (WIDTH // 2 - start_message.get_width() // 2, HEIGHT // 2 - start_message.get_height() // 2))
        pygame.display.flip()
        continue

    keys = pygame.key.get_pressed()
    dx, dy = 0, 0
    if keys[pygame.K_LEFT]:
        dx = -5
    if keys[pygame.K_RIGHT]:
        dx = 5
    if keys[pygame.K_UP]:
        dy = -5
    if keys[pygame.K_DOWN]:
        dy = 5

    player.update(dx, dy)

    for y, row in enumerate(maze):
        for x, cell in enumerate(row):
            if cell == "*" or cell == "B":
                if player.rect.colliderect(pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size)):
                    if cell == "B":
                        animate_blast()
                        player.rect.topleft = (cell_size, cell_size)
                    else:
                        player.rect.x -= dx
                        player.rect.y -= dy
            if cell == "E" and player.rect.colliderect(pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size)):
                game_over = True

    draw_maze()
    all_sprites.draw(screen)

    if game_over:
        screen.blit(game_over_message, game_over_rect)

    pygame.display.flip()
    clock.tick(30)

pygame.quit()