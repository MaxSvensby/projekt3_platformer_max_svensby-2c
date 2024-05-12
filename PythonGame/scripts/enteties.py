import math
import random

import pygame

from scripts.particle import Particle
from scripts.spark import Spark

class PhysicsEntity:
    # Initialize a physics entity with game reference, type, position, and size
    def __init__(self, game, e_type, pos, size):
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.velocity = [0, 0] # Initial velocity
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False} # Collision flags

        self.action = '' # Current action (animation)
        self.anim_offset = (-3, -3) # Animation offset
        self.flip = False # Flip flag for animation
        self.set_action('idle') # Set initial action

        self.last_movement = [0, 0] # Last movement direction

    def rect(self):
        # Returns a pygame.Rect object representing entity's position and size
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
    
    def set_action(self, action):
        # Set action (animation) if it's different from the current one
        if action != self.action:
            self.action = action
            # Copy animation from game assets
            self.animation = self.game.assets[self.type + '/' + self.action].copy()

    def update(self, tilemap, movement=(0, 0)):
        # Update collisions dictionary
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}

        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])

        # Horizontal collisions
        self.pos[0] += frame_movement[0]
        entity_rect = self.rect()
        for index, types in enumerate(tilemap.physics_rects_around(self.pos)):
            for rect in types:
                if entity_rect.colliderect(rect):
                    if frame_movement[0] > 0:
                        entity_rect.right = rect.left
                        self.collisions['right'] = True
                        if index == 2 and self.type == 'player':
                            # Player collision with a certain type, increment dead count
                            self.game.dead += 1
                    if frame_movement[0] < 0:
                        entity_rect.left = rect.right
                        self.collisions['left'] = True
                        if index == 2 and self.type == 'player':
                            # Player collision with a certain type, increment dead count
                            self.game.dead += 1
                    self.pos[0] = entity_rect.x
        
        # Handle checkpoints collision
        entity_rect = self.rect()
        for tile in tilemap.tiles_around(self.pos):
            if tile['type'] == 'checkpoints' and tile['variant'] == 0:
                rect = pygame.Rect(tile['pos'][0] * tilemap.tile_size, tile['pos'][1] * tilemap.tile_size, tilemap.tile_size, tilemap.tile_size)
                if entity_rect.colliderect(rect):
                    # Update checkpoint states
                    tile_loc = str(tile['pos'][0]) + str(';') + str(tile['pos'][1])
                    del tilemap.tilemap[tile_loc]
                    tilemap.tilemap[tile_loc] = {'type': 'checkpoints', 'variant': 1, 'pos': tile['pos']}
                    if self.game.checkpoint_claimed != [0, 0] and self.game.checkpoint_claimed != tile['pos']:
                        del tilemap.tilemap[str(self.game.checkpoint_claimed[0]) + str(';') + str(self.game.checkpoint_claimed[1])]
                        tilemap.tilemap[str(self.game.checkpoint_claimed[0]) + str(';') + str(self.game.checkpoint_claimed[1])] = {'type': 'checkpoints', 'variant': 0, 'pos': self.game.checkpoint_claimed}
                        self.game.checkpoint_claimed = tile['pos']
                    else:
                        self.game.checkpoint_claimed = tile['pos']

        # Handle collectibles collision
        entity_rect = self.rect()
        for collectable in self.game.collectables:
            if entity_rect.colliderect(collectable):
                for particle in self.game.particles.copy():
                    if particle.pos == [collectable.x, collectable.y]:
                        self.game.particles.remove(particle)
                        self.game.collectables.remove(collectable)
                        is_collectable_aquired = False
                        for rect in self.game.collectables_aquired:
                            if rect == collectable:
                                is_collectable_aquired = True
                        if not is_collectable_aquired:
                            self.game.collectables_aquired += [collectable]

        # Vertical collisions
        self.pos[1] += frame_movement[1]
        entity_rect = self.rect()
        for index, types in enumerate(tilemap.physics_rects_around(self.pos)):
            for rect in types:
                if entity_rect.colliderect(rect):
                    if frame_movement[1] > 0:
                        entity_rect.bottom = rect.top
                        self.collisions['down'] = True
                        if index == 1 and self.type == 'player':
                            # Player collision with a certain type, increment dead count
                            self.game.dead += 1
                    if frame_movement[1] < 0:
                        entity_rect.top = rect.bottom
                        self.collisions['up'] = True
                        if index == 1 and self.type == 'player':
                            # Player collision with a certain type, increment dead count
                            self.game.dead += 1
                    self.pos[1] = entity_rect.y

        # Update flip flag based on movement direction
        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0:
            self.flip = True

        self.last_movement = movement

        # Apply gravity
        self.velocity[1] = min(5, self.velocity[1] + 0.1)

        # Stop vertical velocity if colliding with floor or ceiling
        if self.collisions['down'] or self.collisions['up']:
            self.velocity[1] = 0

        # Update animation
        self.animation.update()

    def render(self, surf, offset=(0, 0)):
        # Render entity on provided surface
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False), (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[1]))


class Enemy(PhysicsEntity):
    # Initialize an enemy entity
    def __init__(self, game, pos, size):
        super().__init__(game, 'enemy', pos, size)

        # Walking state
        self.walking = 0

    def update(self, tilemap, movement=(0, 0)):
        # Update enemy behavior
        if self.walking:
            if tilemap.solid_check((self.rect().centerx + (-7 if self.flip else 7), self.pos[1] + 23)):
                if (self.collisions['right'] or self.collisions['left']):
                    self.flip = not self.flip
                else:
                    movement = (movement[0] - 0.5 if self.flip else 0.5, movement[1])
            else:
                self.flip = not self.flip
            self.walking = max(0, self.walking - 1)
            if not self.walking:
                dis = (self.game.player.pos[0] - self.pos[0], self.game.player.pos[1] - self.pos[1])
                if (abs(dis[1]) < 16):
                    # Shoot projectile towards player
                    if (self.flip and dis[0] < 0):
                        self.game.sfx['shoot'].play()
                        self.game.projectiles.append([[self.rect().centerx - 7, self.rect().centery], -1.5, 0])
                        for i in range(4):
                            self.game.sparks.append(Spark(self.game.projectiles[-1][0], random.random() - 0.5 + math.pi, 2 + random.random()))
                    if (not self.flip and dis[0] > 0):
                        self.game.sfx['shoot'].play()
                        self.game.projectiles.append([[self.rect().centerx + 7, self.rect().centery], 1.5, 0])
                        for i in range(4):
                            self.game.sparks.append(Spark(self.game.projectiles[-1][0], random.random() - 0.5, 2 + random.random()))
                        
        elif random.random() < 0.01:
            self.walking = random.randint(30, 120)

        super().update(tilemap, movement=movement)

        # Set animation based on movement
        if movement[0] != 0:
            self.set_action('run')
        else:
            self.set_action('idle')

        # Handle player dash collision
        if abs(self.game.player.dashing) >= 50:
            if self.rect().colliderect(self.game.player.rect()):
                # Trigger effects on collision
                self.game.screenshake = max(16, self.game.screenshake)
                self.game.sfx['hit'].play()
                for i in range(30):
                    angle = random.random() * math.pi * 2
                    speed = random.random() * 5
                    self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
                    self.game.particles.append(Particle(self.game, 'particle', self.rect().center, velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))
                self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random()))
                self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random()))
                return True

    def render(self, surf, offset=(0,0)):
        # Render enemy and its weapon on provided surface
        super().render(surf, offset=offset)

        if self.flip:
            # Render weapon flipped
            surf.blit(pygame.transform.flip(self.game.assets['gun'], True, False), (self.rect().centerx - 4 - self.game.assets['gun'].get_width() - offset[0], self.rect().centery - offset[1]))
        else:
            # Render weapon
            surf.blit(self.game.assets['gun'], (self.rect().centerx + 4 - offset[0], self.rect().centery - offset[1]))


class Player(PhysicsEntity):
    # Initialize a player entity
    def __init__(self, game, pos, size):
        super().__init__(game, 'player', pos, size)
        self.air_time = 0 # Time spent in the air
        self.jumps = 1 # Remaining jumps
        self.wall_slide = False # Wall sliding state
        self.dashing = 0 # Dash state

    # Update player behavior
    def update(self, tilemap, movement=(0, 0)):
        super().update(tilemap, movement=movement)

        self.air_time += 1

        # Handle falling out of bounds
        if self.air_time > 120 and not self.wall_slide and self.pos[1] > 600: # change 600 to y value for player to fall to his death
            if not self.game.dead:
                self.game.screenshake = max(16, self.game.screenshake)
            self.game.dead += 1

        # Reset jumps if grounded
        if self.collisions['down']:
            self.air_time = 0
            self.jumps = 1

        # Handle wall sliding
        self.wall_slide = False
        if (self.collisions['right'] or self.collisions['left']) and self.air_time > 4:
            # Check if wall sliding is possible
            # Set animation to wall slide
            self.wall_slide = True
            self.velocity[1] = min(self.velocity[1], 0.5)
            if self.collisions['right']:
                self.flip = False
            else:
                self.flip = True
            self.set_action('wall_slide')

        # Set animation based on state
        if not self.wall_slide:
            if self.air_time > 4:
                self.set_action('jump')
            elif movement[0] != 0:
                self.set_action('run')
            else:
                self.set_action('idle')

        # Handle player dash
        if abs(self.dashing) in {60, 50}:
            # Emit particles during dash
            for i in range(20):
                angle = random.random() * math.pi * 2
                speed = random.random() * 0.5 + 0.5
                pvelocity = [math.cos(angle) * speed, math.sin(angle) * speed]
                self.game.particles.append(Particle(self.game, 'particle', self.rect().center, velocity=pvelocity, frame=random.randint(0, 7)))
        if self.dashing > 0:
            self.dashing = max(0, self.dashing - 1)
        if self.dashing < 0:
            self.dashing = min(0, self.dashing + 1)
        if abs(self.dashing) > 50:
            # Apply dash velocity and emit particles
            self.velocity[0] = abs(self.dashing) / self.dashing * 8
            if abs(self.dashing) == 51:
                self.velocity[0] *= 0.1
            pvelocity = [abs(self.dashing) / self.dashing * random.random() * 3, 0]
            self.game.particles.append(Particle(self.game, 'particle', self.rect().center, velocity=pvelocity, frame=random.randint(0, 7)))
        
        # Slow down horizontal movement
        if self.velocity[0] > 0:
            self.velocity[0] = max(self.velocity[0] - 0.05, 0) # origanally -0.1
        else:
            self.velocity[0] = min(self.velocity[0] + 0.05, 0) # origanally +0.1

    # Render the player, mostly from the physicsentety renderer
    def render(self, surf, offset=(0, 0)):
        if abs(self.dashing) <= 50:
            super().render(surf, offset=offset)

    # Jump method, called when player jumps
    def jump(self):
        if self.wall_slide:
            # walljump in one direction, give velocity, airtime, give more jumps, return True if he jumped
            if self.flip and self.last_movement[0] < 0:
                self.velocity[0] = 2.5
                self.velocity[1] = -2.5
                self.air_time = 5
                self.jumps = 2         # origanally remove this row
                self.jumps = max(0, self.jumps - 1)  # -1 to remove double jump off walls
                return True
            # walljump in another direction, give velocity, airtime, give more jumps, return True if he jumped
            elif not self.flip and self.last_movement[0] > 0:
                self.velocity[0] = -2.5
                self.velocity[1] = -2.5
                self.air_time = 5
                self.jumps = 2         # origanally remove this row
                self.jumps = max(0, self.jumps - 1)  # -1 to remove double jump off walls
                return True

        # regular jump, give velocity, remove jumps, give airtime, return True if he jumped
        elif self.jumps:
            self.velocity[1] = -3
            self.jumps -= 1
            self.air_time = 5
            return True
        
    # Dash method for the player, play audio, set dashing to value in right direction
    def dash(self):
        if not self.dashing:
            self.game.sfx['dash'].play()
            if self.flip:
                self.dashing = -60
            else:
                self.dashing = 60