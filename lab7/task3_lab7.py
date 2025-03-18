import pygame

pygame.init()
screen = pygame.display.set_mode((400, 400))
pygame.display.set_caption("Task 3")
radius = 25
x = 200
y = 200
color_ball = (255, 0, 0)
color = (255, 255, 255)
step = 20
running = True 

while running:
    screen.fill(color)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and y - radius - step >= 0:
                y -= step
            elif event.key == pygame.K_DOWN and y + radius + step <= 400:
                y += step
            elif event.key == pygame.K_LEFT and x - radius - step >= 0:
                x -= step
            elif event.key == pygame.K_RIGHT and x + radius + step <= 400: 
                x += step

    pygame.draw.circle(screen, color_ball, (x, y), radius)
    pygame.display.flip()

pygame.quit()