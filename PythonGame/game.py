import os
import sys
import math
import random
from ast import literal_eval

import pygame

from scripts.utils import load_image, load_images, Animation, circle_surf
from scripts.enteties import PhysicsEntity, Player, Enemy
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds
from scripts.particle import Particle
from scripts.spark import Spark
from scripts.button import Button

#finish-line needs to get powered by killing enemies, to then finish a level

class Game: 
    def __init__(self):
        pygame.init()

        pygame.display.set_caption('Ninja game')
        self.screen = pygame.display.set_mode((960, 720)) #640, 480
        self.display = pygame.Surface((320, 240), pygame.SRCALPHA)
        self.display_2 = pygame.Surface((320, 240))
        self.display_menu = pygame.Surface((320, 240))

        self.clock = pygame.time.Clock()

        self.fullscreen = False
        self.main_menu_music_playing = False
        self.timer = [0,0,0]

        if open("external_data.txt", "r").readline(-1):
            self.best_time = open("external_data.txt", "r").readline(-1)
            self.best_time = literal_eval(self.best_time)
            open("external_data.txt", "r").close()
        else:
            self.best_time = [0,0,0]

        self.movement = [False, False]
        self.checkpoint_claimed = [0, 0]
        self.collectables_aquired = []

        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass_new'),
            'large_decor': load_images('tiles/large_decor'),
            'rocks': load_images('tiles/rocks'),
            'bushes': load_images('tiles/bushes'),
            'crystals': load_images('tiles/crystals'),
            'spikes': load_images('tiles/all_spikes/top_spikes'),
            'spikes_right': load_images('tiles/all_spikes/right_spikes'),
            'spikes_bot': load_images('tiles/all_spikes/bot_spikes'),
            'spikes_left': load_images('tiles/all_spikes/left_spikes'),
            'stone': load_images('tiles/stone_new'),
            'checkpoints': load_images('tiles/checkpoints'),
            'player': load_image('entities/player.png'),
            'background': load_image('2.png'),
            'clouds': load_images('clouds'),
            'enemy/idle': Animation(load_images('entities/enemy/idle'), img_dur=6),
            'enemy/run': Animation(load_images('entities/enemy/run'), img_dur=4),
            'player/idle': Animation(load_images('entities/new_player/idle'), img_dur=6),
            'player/run': Animation(load_images('entities/new_player/run'), img_dur=4),
            'player/jump': Animation(load_images('entities/new_player/jump')),
            'player/slide': Animation(load_images('entities/new_player/slide')),
            'player/wall_slide': Animation(load_images('entities/new_player/wall_slide')),
            'particle/leaf': Animation(load_images('particles/leaf'), img_dur=20, loop=False),
            'particle/particle': Animation(load_images('particles/particle'), img_dur=6, loop=False),
            'particle/particle_rain': Animation(load_images('particles/particle'), img_dur=200, loop=False),
            'particle/collectables': Animation(load_images('tiles/collectables'), img_dur=40, loop=True),
            'gun': load_image('gun.png'),
            'projectile': load_image('projectile.png'),
        }

        self.buttons = {
            'start': load_image('buttons/start_btn.png'),
            'exit': load_image('buttons/exit_btn.png'),
            '1': load_image('buttons/button1.png'),
            'play': load_image('buttons/play.png'),
            'logo': load_image('buttons/logo.png'),
            'test': load_image('buttons/test.png'),
            'play1': load_image('buttons/play1.png'),
            'play1_hov': load_image('buttons/play1_hov.png'),
        }

        self.sfx = {
            'jump': pygame.mixer.Sound('data/sfx/jump.wav'),
            'dash': pygame.mixer.Sound('data/sfx/dash.wav'),
            'hit': pygame.mixer.Sound('data/sfx/hit.wav'),
            'shoot': pygame.mixer.Sound('data/sfx/shoot.wav'),
            'ambience': pygame.mixer.Sound('data/sfx/ambience.wav'),
        }

        self.sfx['ambience'].set_volume(0.2)
        self.sfx['shoot'].set_volume(0.4)
        self.sfx['hit'].set_volume(0.8)
        self.sfx['dash'].set_volume(0.3)
        self.sfx['jump'].set_volume(0.7)

        self.clouds = Clouds(self.assets['clouds'], count=16)

        self.player = Player(self, (50,50), (8,15))

        self.tilemap = Tilemap(self, tile_size=16)

        self.level = 0
        self.load_level(self.level)

    def main_menu(self):

        if not self.main_menu_music_playing:
            pygame.mixer.music.load('data/main_menu_music.wav')
            pygame.mixer.music.set_volume(0.2)
            pygame.mixer.music.play(-1, 0, 4000)
            self.main_menu_music_playing = True

        logo = Button((self.screen.get_width() / 2) - (self.buttons['logo'].get_width() // (2 / 10)), 50, self.buttons['logo'], self.buttons['logo'], 10)
        play_button = Button((self.screen.get_width() / 2) - (self.buttons['play1'].get_width() // (2 / 5)), 250, self.buttons['play1'], self.buttons['play1_hov'], 5)
        play1_button = Button((self.screen.get_width() / 2) - (self.buttons['play1'].get_width() // (2 / 5)), 400, self.buttons['play1'], self.buttons['play1_hov'], 5)
        play2_button = Button((self.screen.get_width() / 2) - (self.buttons['play1'].get_width() // (2 / 5)), 550, self.buttons['play1'], self.buttons['play1_hov'], 5)

        run = True
        while run:
            self.display_menu.blit(self.assets['background'], (0,0))
            self.clouds.update()
            self.clouds.render(self.display_menu, (0,0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.screen.blit(pygame.transform.scale(self.display_menu, self.screen.get_size()), (0,0))

            if play_button.draw(play_button.hover(), self.screen):
                run = False
                self.play_menu()

            play1_button.draw(play1_button.hover(), self.screen)

            play2_button.draw(play2_button.hover(), self.screen)

            logo.draw(logo.hover(), self.screen)

            pygame.display.update()
            self.clock.tick(60)

    def play_menu(self):

        button_1 = Button(50, 50, self.buttons['1'], self.buttons['1'], 5)

        run = True
        while run:
            self.display_menu.blit(self.assets['background'], (0,0))
            self.clouds.update()
            self.clouds.render(self.display_menu, (0,0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        run = False
                        self.main_menu()

            self.screen.blit(pygame.transform.scale(self.display_menu, self.screen.get_size()), (0,0))

            if button_1.draw(button_1.hover(), self.screen):
                run = False
                self.level = 0
                self.load_level(self.level)
                self.run()

            pygame.display.update()
            self.clock.tick(60)


    def load_level(self, map_id):
        self.tilemap.load('data/maps/' + str(map_id) + '.json')

        self.leaf_spawners = []
        for tree in self.tilemap.extract([('bushes', 1), ('bushes', 0)], keep=True):
            self.leaf_spawners.append(pygame.Rect(2 + tree['pos'][0], 4 + tree['pos'][1], 22, 18))

        self.collectables = []
        for collectable in self.tilemap.extract([('collectables', 0)]):
            self.collectables.append(pygame.Rect(collectable['pos'][0], collectable['pos'][1], 13, 13)) # change pos to topleft of the image not the whole picture

        self.enemies = []
        for spawner in self.tilemap.extract([('spawners', 0), ('spawners', 1)]):
            if spawner['type'] == 'spawners' and spawner['variant'] == 0 and self.checkpoint_claimed == [0, 0]:
                self.player.pos = spawner['pos']
                self.player.air_time = 0
            elif spawner['type'] == 'spawners' and spawner['variant'] == 1:
                self.enemies.append(Enemy(self, spawner['pos'], (8, 15)))

        #print(self.tilemap.tilemap)
        self.current_mapsize = [0, 0, 0, 0]
        for tile in self.tilemap.tilemap:
            if int(tile.split(';')[0]) < self.current_mapsize[0]:
                self.current_mapsize[0] = int(tile.split(';')[0])
            elif int(tile.split(';')[0]) > self.current_mapsize[1]:
                self.current_mapsize[1] = int(tile.split(';')[0])

            if int(tile.split(';')[1]) < self.current_mapsize[2]:
                self.current_mapsize[2] = int(tile.split(';')[1])
            elif int(tile.split(';')[1]) > self.current_mapsize[3]:
                self.current_mapsize[3] = int(tile.split(';')[1])

        # Arrays that temporarily store things, which are bound to get removed
        self.projectiles = []
        self.particles = []
        self.glowing_particles = []
        self.sparks = []

        self.scroll = [0, 0]
        self.dead = 0
        self.underwater = False  # adds a cool underwaterlooking effect when is set to True
        self.transition = -30

        for rect in self.collectables:
                self.particles.append(Particle(self, 'collectables', (rect.x, rect.y)))

        for checkpoint in self.tilemap.extract([('checkpoints', 0)], keep=True):
            if checkpoint['type'] == 'checkpoints' and checkpoint['variant'] == 0 and self.checkpoint_claimed != [0, 0]: # variant 1 is the second look of the checkpoint where it has been claimed
                if (checkpoint['pos'][0] // self.tilemap.tile_size) == self.checkpoint_claimed[0] and (checkpoint['pos'][1] // self.tilemap.tile_size) == self.checkpoint_claimed[1]:
                    self.scroll = [checkpoint['pos'][0], checkpoint['pos'][1]]
                    self.player.pos = checkpoint['pos']
                    self.player.air_time = 0

        self.screenshake = 0
        print(self.collectables_aquired)

    def run(self):

        # menu code or just call run method when i press play button, so instead of running Game().run() i run Game().menu()

        pygame.mixer.music.fadeout(500)

        pygame.mixer.music.load('data/music.wav')
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1, 0, 2000)
        self.main_menu_music_playing = False

        self.sfx['ambience'].play(-1)

        run = True
        while run:
            self.display.fill((0,0,0,0))
            self.display_2.blit(self.assets['background'], (0, 0))

            self.screenshake = max(0, self.screenshake - 1)

            if not len(self.enemies):
                if self.timer[0] < self.best_time[0]:
                    file = open("external_data.txt", "w")
                    file.write(str(self.timer))
                    file.close()
                elif self.timer[0] == self.best_time[0] and self.timer[1] < self.best_time[1]:
                    file = open("external_data.txt", "w")
                    file.write(str(self.timer))
                    file.close()
                elif self.timer[0] == self.best_time[0] and self.timer[1] == self.best_time[1] and self.timer[2] < self.best_time[2]:
                    file = open("external_data.txt", "w")
                    file.write(str(self.timer))
                    file.close()

                if open("external_data.txt", "r").readline(-1):
                    self.best_time = open("external_data.txt", "r").readline(-1)
                    self.best_time = literal_eval(self.best_time)
                    open("external_data.txt", "r").close()
                else:
                    self.best_time = [0,0,0]

                self.timer = [0,0,0]
                
                self.transition += 1
                if self.transition > 30:
                    self.checkpoint_claimed = [0,0]
                    self.level = min(self.level + 1, len(os.listdir('data/maps')) - 1)
                    self.load_level(self.level)
            if self.transition < 0:
                self.transition += 1

            if self.dead:
                self.dead += 1
                if self.dead >= 10:
                    self.transition = min(30, self.transition + 1)
                if self.dead > 40:
                    self.player.velocity[0] = 0
                    self.player.velocity[1] = 0
                    self.load_level(self.level)

            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 30
            self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) / 30
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            # random.random() is a number between 0 and 1
            for rect in self.leaf_spawners:
                if random.random() * 49999 < rect.width * rect.height:
                    pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height)
                    self.particles.append(Particle(self, 'leaf', pos, velocity=[-0.1, 0.3], frame=random.randint(0, 20)))

            self.clouds.update()
            self.clouds.render(self.display_2, offset=render_scroll)

            self.tilemap.render(self.display, offset=render_scroll)

            for enemy in self.enemies.copy():
                kill = enemy.update(self.tilemap, (0,0))
                enemy.render(self.display, offset=render_scroll)
                if kill:
                    self.enemies.remove(enemy)

            if not self.dead:
                self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
                self.player.render(self.display, offset=render_scroll)

            # [[x, y], direction , timer]
            for projectile in self.projectiles.copy():
                projectile[0][0] += projectile[1]
                projectile[2] += 1
                img = self.assets['projectile']
                self.display.blit(img, (projectile[0][0] - img.get_width() / 2 - render_scroll[0], projectile[0][1] - img.get_height() / 2 - render_scroll[1]))
                if self.tilemap.solid_check(projectile[0]):
                    self.projectiles.remove(projectile)
                    for i in range(4):
                        self.sparks.append(Spark(projectile[0], random.random() - 0.5 + (math.pi if projectile[1] > 0 else 0), 2 + random.random()))
                elif projectile[2] > 360:
                    self.projectiles.remove(projectile)
                elif abs(self.player.dashing) < 50:
                    if self.player.rect().collidepoint(projectile[0]):
                        self.projectiles.remove(projectile)
                        self.dead += 1
                        self.sfx['hit'].play()
                        self.screenshake = max(16, self.screenshake)
                        for i in range(30):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.sparks.append(Spark(self.player.rect().center, angle, 2 + random.random()))
                            self.particles.append(Particle(self, 'particle', self.player.rect().center, velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))

            for spark in self.sparks.copy():
                kill = spark.update()
                spark.render(self.display, offset=render_scroll)
                if kill:
                    self.sparks.remove(spark)

            display_mask = pygame.mask.from_surface(self.display)
            display_sillhouette = display_mask.to_surface(setcolor=(0,0,0,180), unsetcolor=(0,0,0,0))
            if not self.underwater:
                for offset in [(-1,0), (1,0), (0,-1), (0,1)]:
                    self.display_2.blit(display_sillhouette, offset)
            else:
                self.display_2.blit(display_sillhouette, offset)

            #self.particles.append(Particle(self, 'particle_rain', (self.player.pos[0] + random.randint(-400, 400), self.player.pos[1] - 200), velocity=[0, 1], frame=0))


            for index, particle in enumerate(self.particles.copy()):
                kill = particle.update()
                if particle.type != 'collectables':
                    particle.render(self.display, offset=render_scroll)
                else:
                    particle.render(self.display, offset=render_scroll, gem=True)

                if particle.type == 'leaf':
                    particle.pos[0] += math.sin(particle.animation.frame * 0.035) * 0.3
                if kill:
                    self.particles.remove(particle)
                if particle.type == 'particle_rain':
                    pass
                    #radius = (particle.animation.frame / particle.animation.img_duration) * 2
                    #self.display.blit(circle_surf(radius, (200,20,20)), ((particle.pos[0] - render_scroll[0] - radius), (particle.pos[1] - render_scroll[1] - radius)), special_flags=pygame.BLEND_RGB_ADD)


            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.player.dash()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        self.movement[0] = True
                    if event.key == pygame.K_d:
                        self.movement[1] = True
                    if event.key == pygame.K_w or event.key == pygame.K_SPACE:
                        if self.player.jump():
                            self.sfx['jump'].play()
                    if event.key == pygame.K_p:
                        self.player.dash()
                    if event.key == pygame.K_u:
                        self.underwater = not self.underwater
                    if event.key == pygame.K_f:
                        self.fullscreen = not self.fullscreen
                        if self.fullscreen:
                            self.screen = pygame.display.set_mode((960, 720), pygame.FULLSCREEN)
                        else:
                            self.screen = pygame.display.set_mode((960, 720))
                    if event.key == pygame.K_ESCAPE:
                        run = False
                        self.sfx['ambience'].stop()
                        pygame.mixer.music.stop()
                        self.main_menu()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a:
                        self.movement[0] = False
                    if event.key == pygame.K_d:
                        self.movement[1] = False

            if self.transition:
                transition_surf = pygame.Surface(self.display.get_size()) # change 30 to change the radius of the circle
                pygame.draw.circle(transition_surf, (255, 255, 255), (self.display.get_width() // 2, self.display.get_height() // 2), (30 - abs(self.transition)) * 8) # change 3rd argument to change the place the circle is being drawn at
                transition_surf.set_colorkey((255, 255, 255))
                self.display.blit(transition_surf, (0, 0))

            if not self.underwater:
                self.display_2.blit(self.display, (0,0))

            
            if len(self.glowing_particles) < 50:
                self.glowing_particles.append([[
                    random.randint(self.current_mapsize[0] * self.tilemap.tile_size, self.current_mapsize[1] * self.tilemap.tile_size)
                    , random.randint(self.current_mapsize[2] * self.tilemap.tile_size - render_scroll[1], self.current_mapsize[3] * self.tilemap.tile_size - render_scroll[1])
                    ], [random.randint(-2, 2) / 10, random.randint(-2, 2) / 10], random.randint(2, 2)])
            elif random.randint(1, 20) == 20:
                self.glowing_particles.append([[
                    random.randint(self.current_mapsize[0] * self.tilemap.tile_size, self.current_mapsize[1] * self.tilemap.tile_size)
                    , random.randint(self.current_mapsize[2] * self.tilemap.tile_size - render_scroll[1], self.current_mapsize[3] * self.tilemap.tile_size - render_scroll[1])
                    ], [random.randint(-2, 2) / 10, random.randint(-2, 2) / 10], random.randint(2, 2)])

            for particle in self.glowing_particles:
                particle[0][0] += particle[1][0]
                particle[0][1] += particle[1][1]
                particle[2] -= 0.001
                #particle[1][1] += 0.1

                self.display_2.blit(circle_surf(particle[2], (150,150,150)), ((int(particle[0][0] - render_scroll[0] - particle[2])), (int(particle[0][1] - render_scroll[1] - particle[2]))), special_flags=pygame.BLEND_RGB_ADD)
                #pygame.draw.circle(self.display_2, (255,255,255, 0.3), [int(particle[0][0] - render_scroll[0]), int(particle[0][1] - render_scroll[1])], int(particle[2]))

                for x in range(2, 10):
                    radius = particle[2] * x
                    self.display_2.blit(circle_surf(radius, (2,2,2)), ((int(particle[0][0] - render_scroll[0] - radius)), (int(particle[0][1] - render_scroll[1] - radius))), special_flags=pygame.BLEND_RGB_ADD)

                if particle[2] <= 0:
                    self.glowing_particles.remove(particle)
                if (particle[0][0] - render_scroll[0]) < (self.player.pos[0] - render_scroll[0] - 300) or (particle[0][0] - render_scroll[0]) > (self.player.pos[0] - render_scroll[0] + 300) or particle[0][1] < (self.player.pos[1] - render_scroll[1] - 300) or particle[0][1] > (self.player.pos[1] - render_scroll[1] + 300):
                    self.glowing_particles.remove(particle)

            screenshake_offset = (random.random() * self.screenshake - self.screenshake / 2, random.random() * self.screenshake - self.screenshake / 2)
            self.screen.blit(pygame.transform.scale(self.display_2, self.screen.get_size()), screenshake_offset)

            self.timer_font = pygame.font.SysFont('Times New Roman', 50)
            self.timer_render = self.timer_font.render((str(self.timer[0]) if self.timer[0] >= 10 else '0' + str(self.timer[0])) + ':' + (str(self.timer[1]) if self.timer[1] >= 10 else '0' + str(self.timer[1])) + ':' + str(int(self.timer[2])), True, (255,255,255))
            self.best_time_font = pygame.font.SysFont('Times New Roman', 20)
            self.best_time_render = self.best_time_font.render('Best: ' + (str(self.best_time[0]) if self.best_time[0] >= 10 else '0' + str(self.best_time[0])) + ':' + (str(self.best_time[1]) if self.best_time[1] >= 10 else '0' + str(self.best_time[1])) + ':' + (str(int(self.best_time[2])) if self.best_time[2] >= 10 else '0' + str(self.best_time[2])), True, (255,255,255))
            self.screen.blit(self.timer_render, (20, 20))
            self.screen.blit(self.best_time_render, (20, 70))

            self.timer[2] += (5/3)
            if int(self.timer[2]) == 100:
                self.timer[1] += 1
                self.timer[2] = 0
            elif self.timer[1] == 60:
                self.timer[0] += 1
                self.timer[1] = 0

            pygame.display.update()
            self.clock.tick(60)

Game().main_menu()