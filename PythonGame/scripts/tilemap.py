import json

import pygame

# The rulebook for when the blocks should autotile
AUTOTILE_MAP = {
    tuple(sorted([(1, 0), (0, 1)])): 0, 
    tuple(sorted([(1, 0), (0, 1), (-1, 0)])): 1, 
    tuple(sorted([(-1, 0), (0, 1)])): 2, 
    tuple(sorted([(-1, 0), (0, -1), (0, 1)])): 3, 
    tuple(sorted([(-1, 0), (0, -1)])): 4, 
    tuple(sorted([(-1, 0), (0, -1), (1, 0)])): 5, 
    tuple(sorted([(1, 0), (0, -1)])): 6, 
    tuple(sorted([(1, 0), (0, -1), (0, 1)])): 7, 
    tuple(sorted([(1, 0), (-1, 0), (0, 1), (0, -1)])): 8, 
}


# Other constants, which blocks does what, which blocks is neighbours
NEIGHBOR_OFFSETS = [(-1 , 0), (-1, -1), (0, -1), (1, -1), (1, 0), (0, 0), (-1, 1), (0, 1), (1, 1)]
PHYSICS_TILES = {'grass', 'stone'}
TOP_KILLABLE_OBJECT = {'spikes', 'spikes_bot'}
RIGHT_KILLABLE_OBJECT = {'spikes_right', 'spikes_left'}
CHECKPOINTS = {'checkpoints'}
AUTOTILE_TYPES = {'grass', 'stone'}

# Tilemap class
class Tilemap:
    # Initialize tilemap variabels
    def __init__(self, game, tile_size=16):
        self.game = game
        self.tile_size = tile_size
        self.tilemap = {}
        self.offgrid_tiles = []

    # Extract a block from the tilemap, in offgridtiles or on grid, returns the extract, can keep or remove the extracted element
    def extract(self, id_pairs, keep=False):
        matches = []
        for tile in self.offgrid_tiles.copy():
            if (tile['type'], tile['variant']) in id_pairs:
                matches.append(tile.copy())
                if not keep:
                    self.offgrid_tiles.remove(tile)

        for loc in self.tilemap:
            tile = self.tilemap[loc]
            if (tile['type'], tile['variant']) in id_pairs:
                matches.append(tile.copy())
                matches[-1]['pos'] = matches[-1]['pos'].copy()
                matches[-1]['pos'][0] *= self.tile_size
                matches[-1]['pos'][1] *= self.tile_size
                if not keep:
                    del self.tilemap[loc]

        return matches

    # See which tiles are around a block 
    def tiles_around(self, pos):
        tiles = []
        tile_loc = (int(pos[0] // self.tile_size), int(pos[1] // self.tile_size))
        for offset in NEIGHBOR_OFFSETS:
            check_loc = str(tile_loc[0] + offset[0]) + ';' + str(tile_loc[1] + offset[1])
            if check_loc in self.tilemap:
                tiles.append(self.tilemap[check_loc])
        return tiles
    
    # Saves the tilemap json file
    def save(self, path):
        f = open(path, 'w')
        json.dump({'tilemap': self.tilemap, 'tile_size': self.tile_size, 'offgrid': self.offgrid_tiles}, f)
        f.close()

    # Loades the tilemap json file and sets the data
    def load(self, path):
        f = open(path, 'r')
        map_data = json.load(f)
        f.close()

        self.tilemap = map_data['tilemap']
        self.tile_size = map_data['tile_size']
        self.offgrid_tiles = map_data['offgrid']

    # Check if a block is a physics block, can be collided with
    def solid_check(self, pos):
        tile_loc = str(int(pos[0] // self.tile_size)) + ';' + str(int(pos[1] // self.tile_size))
        if tile_loc in self.tilemap:
            if self.tilemap[tile_loc]['type'] in PHYSICS_TILES:
                return self.tilemap[tile_loc]
    
    # Checks which physics blocks are around the player, checks for which type it is, returns type
    def physics_rects_around(self, pos):
        rects = []
        vertical_kill_rects = []
        horizontal_kill_rects = []
        checkpoints = []
        for tile in self.tiles_around(pos):
            if tile['type'] in PHYSICS_TILES:
                rects.append(pygame.Rect(tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size, self.tile_size, self.tile_size))
            if tile['type'] in TOP_KILLABLE_OBJECT:
                vertical_kill_rects.append(pygame.Rect(tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size, self.tile_size, self.tile_size))
            if tile['type'] in RIGHT_KILLABLE_OBJECT:
                horizontal_kill_rects.append(pygame.Rect(tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size, self.tile_size, self.tile_size))
            if tile['type'] in CHECKPOINTS:
                checkpoints.append(pygame.Rect(tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size, self.tile_size, self.tile_size))
        return [rects, vertical_kill_rects, horizontal_kill_rects]
    
    # Autotiles the placed blocks, with the autotilemap
    def autotile(self):
        for loc in self.tilemap:
            tile = self.tilemap[loc]
            neighbours = set()
            for shift in [(1, 0),(-1, 0), (0, -1), (0, 1)]:
                check_loc = str(tile['pos'][0] + shift[0]) + ';' + str(tile['pos'][1] + shift[1])
                if check_loc in self.tilemap:
                    if self.tilemap[check_loc]['type'] == tile['type']:
                        neighbours.add(shift)
            neighbours = tuple(sorted(neighbours))
            if (tile['type'] in AUTOTILE_TYPES) and (neighbours in AUTOTILE_MAP):
                tile['variant'] = AUTOTILE_MAP[neighbours]


    # Renders all the blocks in the tilemap to the screen
    def render(self, surf, offset=(0, 0)):

        for tile in self.offgrid_tiles:
            surf.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] - offset[0], tile['pos'][1] - offset[1]))

        for x in range(offset[0] // self.tile_size, (offset[0] + surf.get_width()) // self.tile_size + 1):
            for y in range(offset[1] // self.tile_size, (offset[1] + surf.get_height()) // self.tile_size + 1):
                loc = str(x) + ';' + str(y)
                if loc in self.tilemap:
                    tile = self.tilemap[loc]
                    surf.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] * self.tile_size - offset[0], tile['pos'][1] * self.tile_size - offset[1]))
