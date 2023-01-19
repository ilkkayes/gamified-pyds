# Import packages
import numpy as np
import pygame

# Import pygame.locals names to namespace
from pygame.locals import (
    KEYDOWN,
    K_ESCAPE,
    QUIT
)

# Screen dimension variables for easier usage
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Read the terrain layout from a .csv file as numpy array
terrain = np.genfromtxt('CSV/terrain01.csv', delimiter=',', dtype=int)

# Initialize pygame
pygame.init()

# Define main display surface and land surface
# Land surface is where the terrain is drawn based on the terrain array
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
land = pygame.Surface((400, 400))

# Create custom class for terrain tiles from pygame.sprite.Sprite class
# Contains graphic used for surface and assigns rect object to the class
class Tiles(pygame.sprite.Sprite):
    def __init__(self, filename):
        self.surf = pygame.image.load(filename).convert()
        self.rect = self.surf.get_rect()

# Load the different terrain tiles as Tiles-class
grass = Tiles('CSV/grass.png')
water = Tiles('CSV/water.png')
mountain = Tiles('CSV/mountain.png')

# Iterate through all the elements of the terrain array, assign drawing coordinate in pixels (size of tile sprite * array coordinate), then draw the correct tile (based on array value of the terrain layout) to the land surface 
for i in range(np.shape(terrain)[0]):
    for j in range(np.shape(terrain)[1]):
        if terrain[i][j] == 0:
            grass.rect.x = j * 20
            grass.rect.y = i * 20
            land.blit(grass.surf, grass.rect)
        elif terrain[i][j] == 1:
            water.rect.x = j * 20
            water.rect.y = i * 20
            land.blit(water.surf, water.rect)
        elif terrain[i][j] == 2:
            mountain.rect.x = j * 20
            mountain.rect.y = i * 20
            land.blit(mountain.surf, mountain.rect)

# Main loop
running = True
while running:
    # Exit conditions (Escape key pressed or window closed)
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False
        elif event.type == QUIT:
            running = False

    # Draw black screen and blit the land surface to it
    screen.fill((0, 0, 0))
    screen.blit(land, (0, 0))

    # Draw screen
    pygame.display.flip()
