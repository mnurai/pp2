import pygame
import random

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 600, 400
GRID_SIZE = 20
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# Create screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")

# Snake initialization
snake = [(100, 100), (80, 100), (60, 100)]  # Initial snake position
snake_dir = (GRID_SIZE, 0)  # Initial movement direction
food = (0, 0)
score = 0
level = 1
speed = 5  # Slower initial speed

# Function to generate food in a valid position
def generate_food():
    while True:
        x = random.randint(0, (WIDTH // GRID_SIZE) - 1) * GRID_SIZE
        y = random.randint(0, (HEIGHT // GRID_SIZE) - 1) * GRID_SIZE
        if (x, y) not in snake:
            return (x, y)

food = generate_food()

# Game loop
running = True
clock = pygame.time.Clock()
while running:
    screen.fill(BLACK)
    
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and snake_dir != (0, GRID_SIZE):
                snake_dir = (0, -GRID_SIZE)
            elif event.key == pygame.K_DOWN and snake_dir != (0, -GRID_SIZE):
                snake_dir = (0, GRID_SIZE)
            elif event.key == pygame.K_LEFT and snake_dir != (GRID_SIZE, 0):
                snake_dir = (-GRID_SIZE, 0)
            elif event.key == pygame.K_RIGHT and snake_dir != (-GRID_SIZE, 0):
                snake_dir = (GRID_SIZE, 0)
    
    # Move snake
    new_head = (snake[0][0] + snake_dir[0], snake[0][1] + snake_dir[1])
    
    # Check for wall collision
    if new_head[0] < 0 or new_head[0] >= WIDTH or new_head[1] < 0 or new_head[1] >= HEIGHT or new_head in snake:
        running = False  # End game on collision
    
    # Add new head
    snake.insert(0, new_head)
    
    # Check if snake eats food
    if new_head == food:
        score += 1
        food = generate_food()
        # Level up every 3 points
        if score % 3 == 0:
            level += 1
            speed += 1 
    else:
        snake.pop()  # Remove last segment if no food eaten
    
    # Draw snake
    for segment in snake:
        pygame.draw.rect(screen, GREEN, (*segment, GRID_SIZE, GRID_SIZE))
    
    # Draw food
    pygame.draw.rect(screen, RED, (*food, GRID_SIZE, GRID_SIZE))
    
    # Display score and level
    font = pygame.font.SysFont(None, 24)
    score_text = font.render(f"Score: {score}  Level: {level}", True, WHITE)
    screen.blit(score_text, (10, 10))
    
    pygame.display.flip()
    clock.tick(speed)  # Control game speed

pygame.quit()
