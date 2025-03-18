import pygame
pygame.init()

pygame.display.set_mode((300, 100))
pygame.display.set_caption("Task 2")
pygame.mixer.init()
songs = ["song1.mp3", "song2.mp3", "song3.mp3"]
index = 0

pygame.mixer.music.load(songs[index])
pygame.mixer.music.play()

def toggle_play_pause():
    if pygame.mixer.music.get_busy(): 
        pygame.mixer.music.pause()   
    else:
        pygame.mixer.music.unpause()   

def next_song():
    global index
    index = (index + 1) % len(songs)
    pygame.mixer.music.load(songs[index])
    pygame.mixer.music.play()

def previous_song():
    global index
    index = (index - 1) % len(songs)
    pygame.mixer.music.load(songs[index])
    pygame.mixer.music.play()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:  
                toggle_play_pause()
            elif event.key == pygame.K_RIGHT:  
                next_song()
            elif event.key == pygame.K_LEFT:  
                previous_song()
            elif event.key == pygame.K_q:  
                running = False

pygame.quit()