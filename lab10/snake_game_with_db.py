import pygame
import sys
import random
import snake_game_db  # Import our module for working with the DB

# Pygame Initialization
pygame.init()

#  Constants
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Fonts
FONT_SCORE = pygame.font.SysFont('Arial', 25)
FONT_MSG = pygame.font.SysFont('Arial', 40)
FONT_INFO = pygame.font.SysFont('Arial', 18)

#  Screen and Clock Setup 
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Snake with Database')
clock = pygame.time.Clock()

#  Global Variables for DB 
db_conn = None
db_cursor = None
current_user_id = None

#  Game Functions 

def draw_grid():
    """Draw grid (for debugging, can be disabled)"""
    for x in range(0, SCREEN_WIDTH, GRID_SIZE):
        pygame.draw.line(screen, (50, 50, 50), (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, (50, 50, 50), (0, y), (SCREEN_WIDTH, y))

def draw_object(obj_pos, color):
    """Draw object (snake segment or food)"""
    rect = pygame.Rect(obj_pos[0] * GRID_SIZE, obj_pos[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
    pygame.draw.rect(screen, color, rect)
    # Add border for better visibility
    pygame.draw.rect(screen, BLACK, rect, 1)

def place_food(snake_body):
    """Place food in a random position not occupied by the snake"""
    while True:
        food_pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        if food_pos not in snake_body:
            return food_pos

def draw_text(text, font, color, surface, x, y, center=False):
    """Convenient function for drawing text"""
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    if center:
        textrect.center = (x, y)
    else:
        textrect.topleft = (x, y)
    surface.blit(textobj, textrect)
    return textrect  # Return rect for possible positioning of other elements

#  Main Game Function 
def game_loop(start_level):
    global db_conn, db_cursor, current_user_id  # Use global variables

    # Initial snake parameters
    snake_pos = (GRID_WIDTH // 2, GRID_HEIGHT // 2)
    snake_body = [snake_pos]
    snake_direction = RIGHT
    change_to = snake_direction  # Buffer for direction change

    # Initial game parameters
    food_pos = place_food(snake_body)
    score = 0
    level = start_level
    # Speed depends on level (example)
    speed = 7 + level
    paused = False
    game_over = False

    while True:  # Main game loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"  # Signal for full exit
            if event.type == pygame.KEYDOWN:
                if not game_over:  # Controls work only if the game is not over
                    if event.key == pygame.K_UP and snake_direction != DOWN:
                        change_to = UP
                    elif event.key == pygame.K_DOWN and snake_direction != UP:
                        change_to = DOWN
                    elif event.key == pygame.K_LEFT and snake_direction != RIGHT:
                        change_to = LEFT
                    elif event.key == pygame.K_RIGHT and snake_direction != LEFT:
                        change_to = RIGHT
                    elif event.key == pygame.K_p:  # Pause/Save
                        paused = not paused
                        if paused:
                            print("Game paused. Saving state...")
                            if db_cursor and current_user_id is not None:
                                # Save current score and level
                                snake_game_db.save_game_state(db_cursor, current_user_id, score, level)
                            else:
                                print("Saving not available (DB or user error).")
                        else:
                            print("Game resumed.")
                if event.key == pygame.K_q:  # Quit game with 'Q'
                    return "quit"
                if game_over and event.key == pygame.K_r:  # Restart after Game Over
                    return "restart"
        # If the game is paused, skip updates and draw message
        if paused:
            screen.fill(BLACK)
            draw_text("PAUSE (Saved)", FONT_MSG, YELLOW, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30, center=True)
            draw_text("Press 'P' to continue", FONT_INFO, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20, center=True)
            draw_text("Press 'Q' to quit", FONT_INFO, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50, center=True)
            pygame.display.flip()
            clock.tick(15)  # Low tick rate for pause
            continue  # Go to next iteration of while loop

        # If the game is over
        if game_over:
            screen.fill(BLACK)
            draw_text("GAME OVER", FONT_MSG, RED, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50, center=True)
            score_rect = draw_text(f"Your score: {score}", FONT_SCORE, WHITE, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, center=True)
            draw_text("Press 'R' to restart", FONT_INFO, WHITE, screen, SCREEN_WIDTH // 2, score_rect.bottom + 20, center=True)
            draw_text("Press 'Q' to quit", FONT_INFO, WHITE, screen, SCREEN_WIDTH // 2, score_rect.bottom + 50, center=True)
            pygame.display.flip()
            clock.tick(15)
            continue  # Go to next iteration of while loop

        #  Game Logic (if not paused and not game over) 

        # Check for direction change (to prevent 180-degree turn)
        if change_to == UP and snake_direction != DOWN: snake_direction = UP
        if change_to == DOWN and snake_direction != UP: snake_direction = DOWN
        if change_to == LEFT and snake_direction != RIGHT: snake_direction = LEFT
        if change_to == RIGHT and snake_direction != LEFT: snake_direction = RIGHT

        # New head position
        new_head_pos = (snake_body[0][0] + snake_direction[0], snake_body[0][1] + snake_direction[1])

        # Check for collision with walls
        if (new_head_pos[0] < 0 or new_head_pos[0] >= GRID_WIDTH or
                new_head_pos[1] < 0 or new_head_pos[1] >= GRID_HEIGHT):
            game_over = True
            # Can save final score before Game Over
            if db_cursor and current_user_id is not None:
                print("Saving final state...")
                snake_game_db.save_game_state(db_cursor, current_user_id, score, level)
            continue  # Go to next iteration to display Game Over

        # Check for collision with body
        if new_head_pos in snake_body[1:]:  # Check with all except the new head
            game_over = True
            if db_cursor and current_user_id is not None:
                print("Saving final state...")
                snake_game_db.save_game_state(db_cursor, current_user_id, score, level)
            continue

        # Add new head
        snake_body.insert(0, new_head_pos)

        # Check for eating food
        if new_head_pos == food_pos:
            score += 10  # Increase score
            food_pos = place_food(snake_body)  # New food
            # Check for level up (e.g., every 50 points)
            if score > 0 and score % 50 == 0:
                level += 1
                speed += 1  # Increase speed
                print(f"Level up! Current level: {level}, Speed: {speed}")
        else:
            snake_body.pop()  # Remove tail if food not eaten

        #  Drawing 
        screen.fill(BLACK)  # Clear screen
        # draw_grid()  # Uncomment to draw grid

        # Draw snake
        for segment in snake_body:
            draw_object(segment, GREEN)
        # Highlight head
        draw_object(snake_body[0], (0, 200, 0))

        # Draw food
        draw_object(food_pos, RED)

        # Draw score and level
        draw_text(f"Score: {score}", FONT_SCORE, WHITE, screen, 5, 5)
        draw_text(f"Level: {level}", FONT_SCORE, WHITE, screen, SCREEN_WIDTH - 120, 5)
        draw_text("P-pause/save", FONT_INFO, YELLOW, screen, SCREEN_WIDTH // 2 - 50, 5)

        # Update screen
        pygame.display.flip()

        # Control speed
        clock.tick(speed)


#  Main Launch Block
if __name__ == "__main__":
    print("Starting 'Snake' game...")

    # 1. Database initialization
    print("Connecting to the database...")
    db_conn, db_cursor = snake_game_db.initialize_db()

    if not db_conn or not db_cursor:
        print("Critical error: Failed to connect to the database. The game cannot be started.")
        sys.exit()
    else:
        print("Database successfully initialized.")

    # 2. Get player name
    while True:
        player_name = input("Enter your player name: ").strip()
        if player_name:
            break
        else:
            print("Name cannot be empty.")

    # 3. Get user ID and starting level from DB
    print(f"Checking user '{player_name}' in the database...")
    current_user_id, start_level = snake_game_db.get_or_create_user(db_cursor, player_name)

    if current_user_id is None:
        print("Failed to get or create user in the database. The game will start from level 1 without saving.")
        start_level = 1  # Set default level
    else:
        print(f"Welcome, {player_name}! Starting from level {start_level}.")

    # 4. Start game loop
    while True:  # Loop to allow game restart
        game_result = game_loop(start_level)  # Start main game
        if game_result == "quit":
            break  # Exit restart loop if user wants to quit
        elif game_result == "restart":
            print("Restarting the game...")
            # On restart, level can be reset to 1 or use last saved
            # For simplicity, reset to 1
            start_level = 1
            continue  # Start new iteration of while loop, launching game_loop again

    # 5. Close DB connection before exit
    print("Exiting...")
    snake_game_db.close_db()
    pygame.quit()
    sys.exit()
