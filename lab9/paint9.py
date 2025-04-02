import pygame
import pygame.gfxdraw 

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    
    radius = 15
    mode = 'pen'
    color = (0, 0, 255)  
    points = [] 
    start_pos = None 
    
    while True:
        pressed = pygame.key.get_pressed()
        alt_held = pressed[pygame.K_LALT] or pressed[pygame.K_RALT]
        ctrl_held = pressed[pygame.K_LCTRL] or pressed[pygame.K_RCTRL]
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w and ctrl_held:
                    return
                if event.key == pygame.K_F4 and alt_held:
                    return
                if event.key == pygame.K_ESCAPE:
                    return
                
                # Shape modes
                if event.key == pygame.K_p:
                    mode = 'pen'
                elif event.key == pygame.K_r:
                    mode = 'rectangle'
                elif event.key == pygame.K_c:
                    mode = 'circle'
                elif event.key == pygame.K_s:
                    mode = 'square'# Added
                elif event.key == pygame.K_t:
                    mode = 'right_triangle' # Added
                elif event.key == pygame.K_e:
                    mode = 'equilateral_triangle'#Added
                elif event.key == pygame.K_h:
                    mode = 'rhombus' #Added
                elif event.key == pygame.K_x:
                    mode = 'eraser'
                
                elif event.key == pygame.K_1:
                    color = (255, 0, 0)  
                elif event.key == pygame.K_2:
                    color = (0, 255, 0)  
                elif event.key == pygame.K_3:
                    color = (0, 0, 255)  
                elif event.key == pygame.K_4:
                    color = (255, 255, 0)  
            
                elif event.key == pygame.K_UP:
                    radius = min(200, radius + 1)
                elif event.key == pygame.K_DOWN:
                    radius = max(1, radius - 1)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    start_pos = event.pos
                    if mode in ['pen', 'eraser']:
                        points = [start_pos]
                
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    end_pos = event.pos
                    if mode == 'rectangle':
                        pygame.draw.rect(screen, color, pygame.Rect(start_pos, (end_pos[0] - start_pos[0], end_pos[1] - start_pos[1])), 2)
                    elif mode == 'circle':
                        center = ((start_pos[0] + end_pos[0]) // 2, (start_pos[1] + end_pos[1]) // 2)
                        radius = max(abs(end_pos[0] - start_pos[0]), abs(end_pos[1] - start_pos[1])) // 2
                        pygame.draw.circle(screen, color, center, radius, 2)
                    elif mode == 'square': # new
                        side = min(abs(end_pos[0] - start_pos[0]), abs(end_pos[1] - start_pos[1])) 
                        # smallest difference between the x and y coordinates
                        pygame.draw.rect(screen, color, pygame.Rect(start_pos, (side, side)), 2)
                    elif mode == 'right_triangle': # new
                        pygame.draw.polygon(screen, color, [start_pos, (start_pos[0], end_pos[1]), (end_pos[0], end_pos[1])], 2)
                    elif mode == 'equilateral_triangle': # new
                        height = abs(end_pos[1] - start_pos[1])
                        width = height * 1.732 / 2  # 1.732 is sqrt(3)
                        pygame.draw.polygon(screen, color, [start_pos, (start_pos[0] - width, end_pos[1]), (start_pos[0] + width, end_pos[1])], 2)
                    elif mode == 'rhombus': # new
                        dx = abs(end_pos[0] - start_pos[0])
                        dy = abs(end_pos[1] - start_pos[1])
                        pygame.draw.polygon(screen, color, [start_pos, (start_pos[0] + dx, start_pos[1] + dy), (start_pos[0], start_pos[1] + 2*dy), (start_pos[0] - dx, start_pos[1] + dy)], 2)
                    start_pos = None
            
            if event.type == pygame.MOUSEMOTION:
                if mode == 'pen' and start_pos:
                    points.append(event.pos)
                elif mode == 'eraser' and start_pos:
                    points.append(event.pos)
        
        if mode == 'pen' and len(points) > 1:
            drawLineBetween(screen, points[-2], points[-1], radius, color)
        elif mode == 'eraser' and len(points) > 1:
            drawLineBetween(screen, points[-2], points[-1], radius, (0, 0, 0))
        
        pygame.display.flip()
        clock.tick(60)

def drawLineBetween(screen, start, end, width, color):
    dx = start[0] - end[0]
    dy = start[1] - end[1]
    iterations = max(abs(dx), abs(dy))
    
    for i in range(iterations):
        progress = 1.0 * i / iterations
        aprogress = 1 - progress
        x = int(aprogress * start[0] + progress * end[0])
        y = int(aprogress * start[1] + progress * end[1])
        pygame.draw.circle(screen, color, (x, y), width)

main()
