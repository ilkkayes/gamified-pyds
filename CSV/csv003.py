# Import packages
import numpy as np
import random as rnd
import pygame

# Import pygame.locals names to namespace
from pygame.locals import (
    RLEACCEL,
    KEYDOWN,
    K_ESCAPE,
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
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

    # Initialize counters for village and cave tiles
    village_set = 0
    cave_set = 0

    looping = True
    while looping:
        # Randomize village and cave location on the terrain array
        village_x = rnd.randint(0, width-1)
        village_y = rnd.randint(0, height-1)
        cave_x = rnd.randint(0, width-1)
        cave_y = rnd.randint(0, height-1)

        # Add village/cave to the terrain if the position is grass (for village) and mountain (for cave), and no village/cave has been added
        if terrain[village_x][village_y] == 0 and village_set == 0:
            terrain[village_x][village_y] = 3
            village_set = 1 
        if terrain[cave_x][cave_y] == 2 and cave_set == 0:
            terrain[cave_x][cave_y] = 4
            cave_set = 1
        if village_set == 1 and cave_set == 1:
            looping = False

    # Return randomly generated terrain as NumPy array
    return terrain

terrain = gen_terrain(20, 20)

# Generate player character location randomly
def gen_player_coord(terrain_arr):
    # Player coordinates are in separate NumPy array with the same size as terrain array
    player_coord_arr = np.zeros((np.shape(terrain_arr)[0], np.shape(terrain_arr)[1]), dtype=int)

    # Loop until suitable player location has been generated
    looping = True
    while looping:
        player_x = rnd.randint(0, np.shape(terrain_arr)[0]-1)
        player_y = rnd.randint(0, np.shape(terrain_arr)[1]-1)
        # Add player to generated location if the terrain tile is grass
        if terrain_arr[player_x][player_y] == 0:
            player_coord_arr[player_x][player_y] = 1
            looping = False

    # Stack terrain array and player location array so that both can be accessed within the same 3-dimensional array
    terrain_player_arr = np.stack((terrain, player_coord_arr))

    return terrain_player_arr

terrain_player = gen_player_coord(terrain)

# Initialize pygame
pygame.init()

# Initiate pygame clock for framerate control
clock = pygame.time.Clock()

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

# Create custom class for player sprite
class Player(pygame.sprite.Sprite):
    def __init__(self):
        self.surf = pygame.image.load('CSV/player.png').convert()
        # Set player.png background color as transparent
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surf.get_rect()

    # Update player location on player coordinate array in the 3-dimensional array
    def update(self, key_pressed):
        # Players current location is derived from the player sprites current x and y pixel coordinates        
        curr_x = int(self.rect.x/20)
        curr_y = int(self.rect.y/20)

        # Check for screen edges and impassable terrain (water, mountain) before updating location
        if key_pressed[K_UP]:
            if curr_y > 0:
                if terrain_player[0][curr_y-1][curr_x] not in (1, 2):
                    terrain_player[1][curr_y][curr_x] = 0
                    terrain_player[1][curr_y-1][curr_x] = 1
        if key_pressed[K_DOWN]:
            if curr_y < 19:
                if terrain_player[0][curr_y+1][curr_x] not in (1, 2):
                    terrain_player[1][curr_y][curr_x] = 0
                    terrain_player[1][curr_y+1][curr_x] = 1
        if key_pressed[K_LEFT]:
            if curr_x > 0:
                if terrain_player[0][curr_y][curr_x-1] not in (1, 2):
                    terrain_player[1][curr_y][curr_x] = 0
                    terrain_player[1][curr_y][curr_x-1] = 1
        if key_pressed[K_RIGHT]:
            if curr_x < 19:
                if terrain_player[0][curr_y][curr_x+1] not in (1, 2):
                    terrain_player[1][curr_y][curr_x] = 0
                    terrain_player[1][curr_y][curr_x+1] = 1

# Load the different terrain tiles as Tiles-class
grass = Tiles('CSV/grass.png')
water = Tiles('CSV/water.png')
mountain = Tiles('CSV/mountain.png')
village = Tiles('CSV/village.png')
cave = Tiles('CSV/cave.png')

# Initiate player class
player = Player()

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
            elif terrain[i][j] == 3:
                village.rect.x = j * 20
                village.rect.y = i * 20
                land.blit(village.surf, village.rect)
            elif terrain[i][j] == 4:
                cave.rect.x = j * 20
                cave.rect.y = i * 20
                land.blit(cave.surf, cave.rect)                
    return

draw_terrain()

# Check where player coordinate array has the value of 1, and then use that array position to draw the player sprite to the land surface
def draw_player(terrain_player_arr): 
    for i in range(np.shape(terrain_player_arr)[1]):
        for j in range(np.shape(terrain_player_arr)[2]):
            if terrain_player_arr[1][i][j] == 1: 
                player.rect.x = j * 20
                player.rect.y = i * 20
                land.blit(player.surf, player.rect)
    return

draw_player(terrain_player)

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
                terrain_player = gen_player_coord(terrain)
                draw_terrain()
                draw_player(terrain_player)

            # Save the current terrain to .csv file
            elif event.key == K_s:
                np.savetxt('CSV/rnd_terrain.csv', terrain, fmt='%d', delimiter=',')

        elif event.type == QUIT:
            running = False

    # Check which key was pressed, update player position if direction key was pressed, and draw terrain and player again
    key_pressed = pygame.key.get_pressed()
    player.update(key_pressed)
    draw_terrain()
    draw_player(terrain_player)

    # Draw black screen and blit the land surface to it
    screen.fill((0, 0, 0))
    screen.blit(land, (0, 0))

    # Slow down framerate
    clock.tick(15)

    # Draw screen
    pygame.display.flip()
