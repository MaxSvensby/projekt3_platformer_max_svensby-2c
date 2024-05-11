import sys
import pygame

from scripts.utils import load_images  # Importing the load_images function from the utils module
from scripts.tilemap import Tilemap    # Importing the Tilemap class from the tilemap module



RENDER_SCALE = 2.0 # Constant for render scale


class Editor:  # Defining the Editor class
    def __init__(self): # Initializing the Editor class
        pygame.init() # Initializing the pygame module

        pygame.display.set_caption('editor') # Setting the caption for the pygame window
        self.screen = pygame.display.set_mode((640, 480)) # Setting the size of the window
        self.display = pygame.Surface((320, 240)) # Creating a display surface

        self.clock = pygame.time.Clock() # Creating a Clock object to control the frame rate

        # Dictionary containing image assets loaded from various directories
        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass_new'),
            'large_decor': load_images('tiles/large_decor'),
            'rocks': load_images('tiles/rocks'),
            'spikes': load_images('tiles/all_spikes/top_spikes'),
            'spikes_right': load_images('tiles/all_spikes/right_spikes'),
            'spikes_bot': load_images('tiles/all_spikes/bot_spikes'),
            'spikes_left': load_images('tiles/all_spikes/left_spikes'),
            'bushes': load_images('tiles/bushes'),
            'crystals': load_images('tiles/crystals'),
            'stone': load_images('tiles/stone_new'),
            'spawners': load_images('tiles/spawners'),
            'checkpoints': load_images('tiles/checkpoints'),
            'collectables': load_images('tiles/collectables'),
        }

        # List to track movement directions
        self.movement = [False, False, False, False]

        # Creating a Tilemap object with tile size 16
        self.tilemap = Tilemap(self, tile_size=16) 

        # Trying to load a map file, ignores FileNotFoundError
        try:
            self.tilemap.load('map.json')
        except FileNotFoundError:
            pass

        self.scroll = [0, 0] # List to track scrolling

        self.tile_list = list(self.assets) # List of tile types
        self.tile_group = 0 # Index of current tile group
        self.tile_variant = 0 # Index of current tile variant

        self.clicking = False  # Flag to track left mouse button clicks
        self.right_clicking = False  # Flag to track right mouse button clicks
        self.shift = False  # Flag to track if shift key is pressed
        self.ongrid = True  # Flag to track if placing tiles on grid

    def run(self): # Method to run the editor
        while True: # Main loop
            self.display.fill((0,0,0)) # Filling the display surface with black color

            # Updating scroll positions based on movement
            self.scroll[0] += (self.movement[1] - self.movement[0]) * 5
            self.scroll[1] += (self.movement[3] - self.movement[2]) * 5
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))  # Converting scroll positions to integers

            # Rendering the tilemap on the display surface
            self.tilemap.render(self.display, offset=render_scroll)

            # Copying the current tile image and setting alpha value for transparency
            current_tile_img = self.assets[self.tile_list[self.tile_group]][self.tile_variant].copy()
            current_tile_img.set_alpha(200)

            # Getting mouse position and scaling it
            mpos = pygame.mouse.get_pos()
            mpos = (mpos[0] / RENDER_SCALE, mpos[1] / RENDER_SCALE)
            # Calculating tile position
            tile_pos = (int((mpos[0] + self.scroll[0]) // self.tilemap.tile_size), int((mpos[1] + self.scroll[1]) // self.tilemap.tile_size))

            if self.ongrid: # If placing tiles on grid
                # Blitting current tile image on grid
                self.display.blit(current_tile_img, (tile_pos[0] * self.tilemap.tile_size - self.scroll[0], tile_pos[1] * self.tilemap.tile_size - self.scroll[1]))
            else:# If not placing tiles on grid
                # Blitting current tile image at mouse position
                self.display.blit(current_tile_img, mpos)

            if self.clicking and self.ongrid: # If left mouse button is clicked and placing tiles on grid
                # Adding tile to tilemap
                self.tilemap.tilemap[str(tile_pos[0]) + ';' + str(tile_pos[1])] = {'type': self.tile_list[self.tile_group], 'variant': self.tile_variant, 'pos': tile_pos}
            if self.right_clicking: # If right mouse button is clicked
                tile_loc = str(tile_pos[0]) + ';' + str(tile_pos[1]) # Getting tile position as string
                if tile_loc in self.tilemap.tilemap: # If tile position is in tilemap
                    del self.tilemap.tilemap[tile_loc] # Deleting tile from tilemap
                for tile in self.tilemap.offgrid_tiles.copy():
                    tile_img = self.assets[tile['type']][tile['variant']]
                    tile_r = pygame.Rect(tile['pos'][0] - self.scroll[0], tile['pos'][1] - self.scroll[1], tile_img.get_width(), tile_img.get_height())
                    if tile_r.collidepoint(mpos):
                        self.tilemap.offgrid_tiles.remove(tile)

            # Blitting current tile image at position (5,5)
            self.display.blit(current_tile_img, (5,5))


            for event in pygame.event.get(): # Handling events
                if event.type == pygame.QUIT: # If the window is closed
                    pygame.quit() # Quitting pygame
                    sys.exit() # Exiting the script

                if event.type == pygame.MOUSEBUTTONDOWN: # If a mouse button is pressed
                    if event.button == 1: # Left mouse button
                        self.clicking = True # Setting clicking flag to True
                        if not self.ongrid: # If not placing tiles on grid
                            # Appending tile information to offgrid_tiles
                            self.tilemap.offgrid_tiles.append({'type': self.tile_list[self.tile_group], 'variant': self.tile_variant, 'pos': (mpos[0] + self.scroll[0], mpos[1] + self.scroll[1])})
                    if event.button == 3: # Right mouse button
                        self.right_clicking = True # Setting right clicking flag to True
                    if self.shift: # If shift key is pressed
                        if event.button == 4: # Scroll up
                            self.tile_variant = (self.tile_variant - 1) % len(self.assets[self.tile_list[self.tile_group]])
                        if event.button == 5: # Scroll down
                            self.tile_variant = (self.tile_variant + 1) % len(self.assets[self.tile_list[self.tile_group]])
                    else: # If shift key is not pressed
                        if event.button == 4: # Scroll up
                            self.tile_group = (self.tile_group - 1) % len(self.tile_list)
                            self.tile_variant = 0
                        if event.button == 5: # Scroll down
                            self.tile_group = (self.tile_group + 1) % len(self.tile_list)
                            self.tile_variant = 0
                if event.type == pygame.MOUSEBUTTONUP: # If a mouse button is released
                    if event.button == 1: # Left mouse button
                        self.clicking = False # Setting clicking flag to False
                    if event.button == 3: # Right mouse button
                        self.right_clicking = False # Setting right clicking flag to False

                # If a movement key is pressed then set that direction to true in the array
                # Rest is basic keybinds
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        self.movement[0] = True
                    if event.key == pygame.K_d:
                        self.movement[1] = True
                    if event.key == pygame.K_w or event.key == pygame.K_SPACE:
                        self.movement[2] = True
                    if event.key == pygame.K_s:
                        self.movement[3] = True
                    if event.key == pygame.K_g:
                        self.ongrid = not self.ongrid
                    if event.key == pygame.K_t:
                        self.tilemap.autotile()
                    if event.key == pygame.K_o:
                        self.tilemap.save('map.json')
                    if event.key == pygame.K_LSHIFT:
                        self.shift = True
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a:
                        self.movement[0] = False
                    if event.key == pygame.K_d:
                        self.movement[1] = False
                    if event.key == pygame.K_w or event.key == pygame.K_SPACE:
                        self.movement[2] = False
                    if event.key == pygame.K_s:
                        self.movement[3] = False
                    if event.key == pygame.K_LSHIFT:
                        self.shift = False

            # Scaling and blitting the display surface onto the screen
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0,0))
            pygame.display.update()
            self.clock.tick(60)

Editor().run() # Creating an instance of Editor class and running it