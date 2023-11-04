import pygame
import sys

pygame.init()
screen = pygame.display.set_mode((500, 100))

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            pass
    

    pygame.display.flip()