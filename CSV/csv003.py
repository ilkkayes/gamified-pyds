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

# Import deque container
from collections import deque

# Screen and map dimension variables for easier usage
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 400
MAP_WIDTH = 20
MAP_HEIGHT = 20

# Generate random terrain
def gen_terrain():
    # Generate template terrain filled with zeroes
    terrain = np.zeros((MAP_HEIGHT, MAP_WIDTH), dtype=int)
    terrain_area = MAP_WIDTH * MAP_HEIGHT

    # Initialize tracking of number of water or mountain tiles, and if village/cave has been placed
    water_tiles = 0
    mountain_tiles = 0
    village_set = False
    cave_set = False

    # Create random seed tiles for water and mountain areas (number of seeds scaled according to total map area)
    for i in range(round(terrain_area/133)):
        x_water = rnd.randint(0, MAP_WIDTH-1)
        y_water = rnd.randint(0, MAP_HEIGHT-1)
        x_mountain = rnd.randint(0, MAP_WIDTH-1)
        y_mountain = rnd.randint(0, MAP_HEIGHT-1)
        terrain[y_water][x_water] = 1
        terrain[y_mountain][x_mountain] = 2            

    # Expand seed tiles to neighbouring tiles with a probability of 1/3
    # Total amount of water or mountain tiles is limited to 1/3 of the terrain area
    map_full = False
    while map_full == False:
        # Get coordinates of all water/mountain tiles, and generate array of neighboring tile coordinates
        for j in np.argwhere(terrain > 0):
            neighbors = [(j[0]-1, j[1]), (j[0], j[1]-1), (j[0]+1, j[1]), (j[0], j[1]+1)]

            # Iterate through neighbors and place water/mountain tile at 1/3 change
            for k in neighbors:
                if k[0] >= 0 and k[0] <= MAP_HEIGHT-1 and k[1] >= 0 and k[1] <= MAP_WIDTH-1:
                    prob = rnd.randint(0, 2)
                    if prob == 2:
                        terrain[k[0]][k[1]] = terrain[j[0]][j[1]]
                        if terrain[j[0]][j[1]] == 1:
                            water_tiles += 1
                        elif terrain[j[0]][j[1]] == 2:
                            mountain_tiles += 1

        if water_tiles >= round(terrain_area/3) and mountain_tiles >= round(terrain_area/3):
            map_full = True

    # Place village and cave at random location
    looping = True
    while looping:
        # Randomize village and cave location on the terrain array, and retain coordinate of succesful placement
        if village_set == False:
            village_x = rnd.randint(0, MAP_WIDTH-1)
            village_y = rnd.randint(0, MAP_HEIGHT-1)
        if cave_set == False:
            cave_x = rnd.randint(0, MAP_WIDTH-1)
            cave_y = rnd.randint(0, MAP_HEIGHT-1)

        # Add village/cave to the terrain if the position is grass (for village) and mountain (for cave), and no village/cave has been added
        if terrain[village_y][village_x] == 0 and village_set == False:
            terrain[village_y][village_x] = 3
            village_set = True 
        if terrain[cave_y][cave_x] == 2 and cave_set == False:
            terrain[cave_y][cave_x] = 4
            cave_set = True
        if village_set == True and cave_set == True:
            looping = False

    # Return randomly generated terrain as NumPy array, and village/cave coordinates for path checking
    return terrain, village_x, village_y, cave_x, cave_y

terrain, village_x, village_y, cave_x, cave_y = gen_terrain()

# Initialize pygame
pygame.init()

# Initiate pygame clock for framerate control
clock = pygame.time.Clock()

# Define main display surface and land surface
# Land surface is where the terrain is drawn based on the terrain array
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
land = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

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
village = Tiles('CSV/village.png')
cave = Tiles('CSV/cave.png')

# Create custom class for player sprite
class Player(pygame.sprite.Sprite):
    def __init__(self):
        self.surf = pygame.image.load('CSV/player.png').convert()
        # Set player.png background color as transparent
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surf.get_rect()

    # Update player location on player coordinate array in the 3-dimensional array
    def update(self, key_pressed):
        # Get players current location from terrain_player array
        curr_x = np.argwhere(terrain_player[1] == 1)[0][1]
        curr_y = np.argwhere(terrain_player[1] == 1)[0][0]

        # Check for screen edges and impassable terrain (water, mountain) before updating location
        if key_pressed[K_UP]:
            if curr_y > 0:
                if terrain_player[0][curr_y-1][curr_x] not in (1, 2):
                    terrain_player[1][curr_y][curr_x] = 0
                    terrain_player[1][curr_y-1][curr_x] = 1
        if key_pressed[K_DOWN]:
            if curr_y < MAP_HEIGHT-1:
                if terrain_player[0][curr_y+1][curr_x] not in (1, 2):
                    terrain_player[1][curr_y][curr_x] = 0
                    terrain_player[1][curr_y+1][curr_x] = 1
        if key_pressed[K_LEFT]:
            if curr_x > 0:
                if terrain_player[0][curr_y][curr_x-1] not in (1, 2):
                    terrain_player[1][curr_y][curr_x] = 0
                    terrain_player[1][curr_y][curr_x-1] = 1
        if key_pressed[K_RIGHT]:
            if curr_x < MAP_WIDTH-1:
                if terrain_player[0][curr_y][curr_x+1] not in (1, 2):
                    terrain_player[1][curr_y][curr_x] = 0
                    terrain_player[1][curr_y][curr_x+1] = 1

# Initiate player class
player = Player()

# Generate player character location randomly
def gen_player_coord():
    # Player coordinates are in separate NumPy array with the same size as terrain array
    player_coord_arr = np.zeros((MAP_HEIGHT, MAP_WIDTH), dtype=int)

    # Loop until suitable player location has been generated
    looping = True
    while looping:
        player_x = rnd.randint(0, MAP_WIDTH-1)
        player_y = rnd.randint(0, MAP_HEIGHT-1)
        # Add player to generated location if the terrain tile is grass
        if terrain[player_y][player_x] == 0:
            player_coord_arr[player_y][player_x] = 1
            looping = False

    # Stack terrain array and player location array so that both can be accessed within the same 3-dimensional array
    terrain_player_arr = np.stack((terrain, player_coord_arr))

    return terrain_player_arr

# Create function Breadth-First Search algorithm for checking if there is any path between start and goal coordinate
def bfs(start, goal):
    # Add start location to queue and to set of visited coordinates
    queue = deque([start])
    visited = set()
    visited.add(start)

    # Get next location from left of queue, and check if it is the goal location
    while queue:
        current_node = queue.popleft() if queue else None
        if current_node == goal:
            return True

        # Check all neighboring tiles that are within the map, are not water or mountain tiles, and are not yet visited
        # Add these to queue (to check at the beginning of loop) and to set of visited tiles 
        neighbors = [(current_node[0], current_node[1]-1), (current_node[0]-1, current_node[1]), (current_node[0], current_node[1]+1), (current_node[0]+1, current_node[1])]
        for i in neighbors:
            if i[1] >= 0 and i[1] <= MAP_HEIGHT-1 and i[0] >= 0 and i[0] <= MAP_WIDTH-1 and terrain[i[1]][i[0]] not in (1, 2) and i not in visited:
                visited.add(i)
                queue.append(i)

    return False

terrain_player = gen_player_coord()

# Check with BFS algorithm if there is any path, in the initial map, from player location to the village and cave
# If not, then regenerate the terrain and player location until paths exist
if bfs((np.argwhere(terrain_player[1]==1)[0][1], np.argwhere(terrain_player[1]==1)[0][0]), (village_x, village_y)) == False or bfs((np.argwhere(terrain_player[1]==1)[0][1], np.argwhere(terrain_player[1]==1)[0][0]), (cave_x, cave_y)) == False:
    nopaths = True
    while nopaths:
        terrain, village_x, village_y, cave_x, cave_y = gen_terrain()
        terrain_player = gen_player_coord()
        if bfs((np.argwhere(terrain_player[1]==1)[0][1], np.argwhere(terrain_player[1]==1)[0][0]), (village_x, village_y)) == True and bfs((np.argwhere(terrain_player[1]==1)[0][1], np.argwhere(terrain_player[1]==1)[0][0]), (cave_x, cave_y)) == True:
            nopaths = False

# Iterate through all the elements of the terrain array, assign drawing coordinate in pixels (size of tile sprite * array coordinate), then draw the correct tile (based on array value of the terrain layout) to the land surface
# Modified this step to be a custom function, so updating the terrain is easier later
def draw_terrain(): 
    for i in range(MAP_HEIGHT):
        for j in range(MAP_WIDTH):
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

# Check where player coordinate array has the value of 1, and then use that array position to draw the player sprite to the land surface
def draw_player(): 
    player.rect.x = np.argwhere(terrain_player[1] == 1)[0][1] * 20
    player.rect.y = np.argwhere(terrain_player[1] == 1)[0][0] * 20
    land.blit(player.surf, player.rect)
    return

# Draw initial map and player
draw_terrain()
draw_player()

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
                # Check with BFS algorithm if any path exists between player location and the village and the cave
                # If not, generate new map and player location
                nopaths = True
                while nopaths:
                    terrain, village_x, village_y, cave_x, cave_y = gen_terrain()
                    terrain_player = gen_player_coord()
                    if (
                            bfs((np.argwhere(terrain_player[1]==1)[0][1], np.argwhere(terrain_player[1]==1)[0][0]), (village_x, village_y)) == True and
                            bfs((np.argwhere(terrain_player[1]==1)[0][1], np.argwhere(terrain_player[1]==1)[0][0]), (cave_x, cave_y)) == True
                        ):
                        nopaths = False

                draw_terrain()
                draw_player()

            # Save the current terrain to .csv file
            elif event.key == K_s:
                np.savetxt('CSV/rnd_terrain.csv', terrain, fmt='%d', delimiter=',')

            # Update player location when arrow keys are pressed
            key_pressed = pygame.key.get_pressed()
            player.update(key_pressed)

        elif event.type == QUIT:
            running = False

    draw_terrain()
    draw_player()

    # Draw black screen and blit the land surface to it
    screen.fill((0, 0, 0))
    screen.blit(land, (0, 0))

    # Slow down framerate
    clock.tick(15)

    # Draw screen
    pygame.display.flip()