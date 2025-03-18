import pygame
import datetime

pygame.init()

screen = pygame.display.set_mode((800, 800))
pygame.display.set_caption("Task 1")

clock_face = pygame.image.load('clock.png')  
right_hand = pygame.image.load('rightarm.png')
left_hand = pygame.image.load('leftarm.png')

clock_face = pygame.transform.scale(clock_face, (800, 800))
right_hand = pygame.transform.scale(right_hand, (400, 400))  
left_hand = pygame.transform.scale(left_hand, (150, 150))  

clock_center = (400, 400)

def rotate_image(image, angle, pivot):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center=pivot)
    return rotated_image, new_rect

fps_clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    now = datetime.datetime.now()
    minutes = now.minute
    seconds = now.second

    minute_angle = -(minutes * 6 + seconds * 0.1)  
    second_angle = -seconds * 6

    rotated_minute_hand, minute_rect = rotate_image(right_hand, minute_angle, clock_center)
    rotated_second_hand, second_rect = rotate_image(left_hand, second_angle, clock_center)

    screen.fill((255, 255, 255))  
    screen.blit(clock_face, (0, 0))  
    screen.blit(rotated_minute_hand, minute_rect.topleft)  
    screen.blit(rotated_second_hand, second_rect.topleft)  
    pygame.display.update()
    fps_clock.tick(60)  

pygame.quit()
