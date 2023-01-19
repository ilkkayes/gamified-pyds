# Import packages
import numpy as np
import random as rnd
import pygame

# Import pygame.locals names to namespace
from pygame.locals import (
    KEYDOWN,
    K_ESCAPE,
    K_g,
    K_s,
    QUIT
)

# Screen dimension variables for easier usage
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Generate random terrain
def gen_terrain(width, height):
    # Generate template terrain filled with zeroes
    terrain = np.zeros((width, height), dtype=int)
    terrain_area = width * height

    # Initialize tracking of number of water or mountain tiles
    water_tiles = 0
    mountain_tiles = 0

    # Create first seeds of water and mountain areas
    for i in range(3):
        x_water = rnd.randint(0, width-1)
        y_water = rnd.randint(0, height-1)
        x_mountain = rnd.randint(0, width-1)
        y_mountain = rnd.randint(0, height-1)
        terrain[x_water][y_water] = 1
        terrain[x_mountain][y_mountain] = 2            

    # Expand seed tiles to neighbouring tiles with a probability of 1/3
    # Total amount of water or mountain tiles is limited to 1/3 of the terrain area
    # Iterate from top-left to bottom-right
    for j in range(width):
        for k in range(height):
            for l in (j-1, j, j+1):
                for m in (k-1, k, k+1):
                    if l >= 0 and l <= width-1 and m >= 0 and m <= height-1:
                        if terrain[j][k] == 1 and water_tiles <= terrain_area/3:
                            prob = rnd.randint(0, 2)
                            if prob == 2:
                                terrain[l][m] = 1
                                water_tiles += 1
                        elif terrain[j][k] == 2 and mountain_tiles <= terrain_area/3:
                            prob = rnd.randint(0, 2)
                            if prob == 2:
                                terrain[l][m] = 2
                                mountain_tiles += 1

    # Iterate from bottom-right to top-left
    for j in reversed(range(width)):
        for k in reversed(range(height)):
            for l in (j-1, j, j+1):
                for m in (k-1, k, k+1):
                    if l >= 0 and l <= width-1 and m >= 0 and m <= height-1:
                        if terrain[j][k] == 1 and water_tiles <= terrain_area/3:
                            prob = rnd.randint(0, 2)
                            if prob == 2:
                                terrain[l][m] = 1
                                water_tiles += 1
                        elif terrain[j][k] == 2 and mountain_tiles <= terrain_area/3:
                            prob = rnd.randint(0, 2)
                            if prob == 2:
                                terrain[l][m] = 2
                                mountain_tiles += 1                            

    # Return randomly generated terrain as Numpy array
    return terrain

terrain = gen_terrain(20, 20)

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
# Modified this step to be a custom function, so updating the terrain is easier later
def draw_terrain(): 
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
    return

draw_terrain()

# Main loop
running = True
while running:
    # Check for exit conditions and user interaction
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False

            # Generate new random terrain and blit it to land surface
            elif event.key == K_g:
                terrain = gen_terrain(20, 20)
                draw_terrain()

            # Save the current terrain to .csv file
            elif event.key == K_s:
                np.savetxt('CSV/rnd_terrain.csv', terrain, fmt='%d', delimiter=',')

        elif event.type == QUIT:
            running = False

    # Draw black screen and blit the land surface to it
    screen.fill((0, 0, 0))
    screen.blit(land, (0, 0))

    # Draw screen
    pygame.display.flip()
