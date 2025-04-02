import pygame
import random
pygame.init()

WIDTH, HEIGHT = 600, 400 
GRID_SIZE = 20  
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# Food colors based on weight dictionary
FOOD_COLORS = {
    1: (255, 0, 0),    # Red for 1-point food
    2: (255, 165, 0),  # Orange for 2-point food
    3: (255, 255, 0)   # Yellow for 3-point food
}

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")

snake = [(100, 100), (80, 100), (60, 100)]  
snake_dir = (GRID_SIZE, 0)  

# Food properties
food = (0, 0)
food_weight = 1  # Default weight of food
food_spawn_time = pygame.time.get_ticks()  # Time when food was spawned
FOOD_LIFETIME = 20000  # 20 seconds in milliseconds

score = 0
level = 1
speed = 5 

def generate_food():
    global food_weight, food_spawn_time
    while True:
        x = random.randint(0, (WIDTH // GRID_SIZE) - 1) * GRID_SIZE
        y = random.randint(0, (HEIGHT // GRID_SIZE) - 1) * GRID_SIZE
        if (x, y) not in snake:
            food_weight = random.choice([1, 2, 3])  # Assign random weight (1, 2, or 3 points)
            food_spawn_time = pygame.time.get_ticks()  # Reset spawn time
            return (x, y)

food = generate_food()

running = True
clock = pygame.time.Clock()
while running:
    screen.fill(BLACK)
    
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
    
    new_head = (snake[0][0] + snake_dir[0], snake[0][1] + snake_dir[1])
    
    if new_head[0] < 0 or new_head[0] >= WIDTH or new_head[1] < 0 or new_head[1] >= HEIGHT or new_head in snake:
        running = False 
    
    snake.insert(0, new_head)
    
    if new_head == food:
        score += food_weight 
        food = generate_food() 
        if score % 3 == 0:
            level += 1
            speed += 1 
    else:
        snake.pop()  
    
    # Check if food has expired
    if pygame.time.get_ticks() - food_spawn_time > FOOD_LIFETIME:
        food = generate_food() # New food is generated 
    
    for segment in snake:
        pygame.draw.rect(screen, GREEN, (*segment, GRID_SIZE, GRID_SIZE))
    
    # Draw food with color based on its weight
    pygame.draw.rect(screen, FOOD_COLORS[food_weight], (*food, GRID_SIZE, GRID_SIZE))
    
    font = pygame.font.SysFont(None, 24)
    score_text = font.render(f"Score: {score}  Level: {level}", True, WHITE)
    screen.blit(score_text, (10, 10))
    
    pygame.display.flip()
    clock.tick(speed) 

pygame.quit()
