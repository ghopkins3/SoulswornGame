import os
import sys
import math
import random
import pygame
import webbrowser

from scripts.utils import load_image, load_images, Animation
from scripts.entities import Player, Enemy, Chicken, JumpPowerUp, FireballPowerUp, Ufo, WallOfFlesh, DashPowerUp, HealthRestorePowerUp
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds
from scripts.particle import Particle
from scripts.spark import Spark

class Game:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption('Soulsworn')
        self.screen = pygame.display.set_mode((1920, 1080))
        self.display = pygame.Surface((960, 540), pygame.SRCALPHA)
        self.display_2 = pygame.Surface((960, 540))

        self.clock = pygame.time.Clock()

        ## displays for around 3 seconds when first jump powerup is collected
        self.jump_tooltip_timer = 0
        self.jump_tooltip_duration = 120
        self.attack_tooltip_timer = 0
        self.attack_tooltip_duration = 120
        self.fireball_tooltip_timer = 0
        self.fireball_tooltip_duration = 120
        self.dash_tooltip_timer = 0
        self.dash_tooltip_duration = 120

        self.movement = [False, False]
        self.pause_menu_open = False
        self.win_screen_active = False

        # Alleviates scope errors:
        self.plus_rect = pygame.Rect(0, 0, 0, 0)
        self.minus_rect = pygame.Rect(0, 0, 0, 0)
        self.back_rect = pygame.Rect(0, 0, 0, 0)
        self.resume_rect = pygame.Rect(0, 0, 0, 0)
        self.restart_rect = pygame.Rect(0, 0, 0, 0)
        self.feedback_rect = pygame.Rect(0, 0, 0, 0)
        self.quit_rect = pygame.Rect(0, 0, 0, 0)

        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'stone': load_images('tiles/stone'),
            'background': load_image('background.png'),
            'main_menu_bg': load_image('main_menu.png'),
            'control_menu': load_image('controls_popup.png'),
            'pause_popup': load_image('pause_popup.png'),
            'jump_tooltip': load_image('jump_tooltip.png'),
            'attack_tooltip': load_image('attack_tooltip.png'),
            'fireball_tooltip': load_image('fireball_tooltip.png'),
            'dash_tooltip': load_image('dash_tooltip.png'),
            'clouds': load_images('clouds'),

            ## Loads animation images
            'player/idle': Animation(load_images('entities/player/idle'), img_dur=6),
            'player/run': Animation(load_images('entities/player/run'), img_dur=7),
            'player/jump': Animation(load_images('entities/player/jump')),

            ## Loads particle effects
            'particle/leaf': Animation(load_images('particles/leaf'), img_dur=20, loop=False),
            'particle/particle': Animation(load_images('particles/particle'), img_dur=6, loop=False),
            'particle/swingright': Animation(load_images('particles/swingright'), img_dur=2, loop=False),
            'particle/swingleft': Animation(load_images('particles/swingleft'), img_dur=6, loop=False),

            ## Loads enemy
            'enemy/idle': Animation(load_images('entities/enemy/idle'), img_dur=6),
            'enemy/run': Animation(load_images('entities/enemy/run'), img_dur=4),

            ## Load chickens
            'chicken/idle': Animation(load_images('entities/chicken/idle'), img_dur=6),
            'chicken/run': Animation(load_images('entities/chicken/run'), img_dur=4),

            ## Load ufos
            'ufo/idle': Animation(load_images('entities/ufo/idle'), img_dur=6),
            'ufo/run': Animation(load_images('entities/ufo/run'), img_dur=6),
            'ufo/hover': Animation(load_images('entities/ufo/hover'), img_dur=6),
            'ufo/attacking': Animation(load_images('entities/ufo/attacking'), img_dur=6),

            ## Load Wall of Flesh
            'wall_of_flesh/idle': Animation(load_images('entities/wall_of_flesh/idle'), img_dur=6),

            ## Loads gun for enemies and projectiles for guns
            'gun': load_image('gun.png'),
            'projectile': load_image('projectile.png'),
            'egg': load_image('egg.png'),

            ## Load fireball for player
            'fireball': load_image('fireball.png'),

            ## Load sword for players
            'sword': load_image('big_sword.png'),
            'sword_frame2': load_image('big_sword_final.png'),

            ## Load powerups
            'jump_powerup/idle': Animation(load_images('entities/jump_powerup/idle')),
            'fireball_powerup/idle': Animation(load_images('entities/fireball_powerup/idle'), img_dur=6, loop=True),
            'dash_powerup/idle': Animation(load_images('entities/dash_powerup/idle')),
            'health_restore_powerup/idle': Animation(load_images('entities/health_restore_powerup/idle')),

            ## Load hearts for HP
            'full_heart': load_image('full_heart.png'),
            'empty_heart': load_image('empty_heart.png'),
        }

        self.sfx = {
            'ui_select': pygame.mixer.Sound('data/sfx/ui_select.wav'),
            'open_pause_menu': pygame.mixer.Sound('data/sfx/open_pause_menu.wav'),

            'jump': pygame.mixer.Sound('data/sfx/jump.wav'),
            'dash': pygame.mixer.Sound('data/sfx/dash.wav'),
            'sword_hit_flesh': pygame.mixer.Sound('data/sfx/sword_hit_flesh.wav'),
            'sword_hit_metal': pygame.mixer.Sound('data/sfx/sword_hit_metal.wav'),
            'sword_hit_tile': pygame.mixer.Sound('data/sfx/sword_hit_tile.wav'),
            'dash_hit': pygame.mixer.Sound('data/sfx/dash_hit.wav'),
            'shoot_fireball': pygame.mixer.Sound('data/sfx/shoot_fireball.wav'),
            'get_powerup': pygame.mixer.Sound('data/sfx/get_powerup.wav'),
            'player_hurt': pygame.mixer.Sound('data/sfx/player_hurt.wav'),
            'player_dead': pygame.mixer.Sound('data/sfx/player_dead.wav'),

            'shoot_projectile': pygame.mixer.Sound('data/sfx/shoot_projectile.wav'),
            'shoot_egg': pygame.mixer.Sound('data/sfx/shoot_egg.wav'),
            'ufo_attack': pygame.mixer.Sound('data/sfx/ufo_attack.wav'),
            'fireball_hit': pygame.mixer.Sound('data/sfx/fireball_hit.wav'),
            'egg_hit': pygame.mixer.Sound('data/sfx/egg_hit.wav'),
            'projectile_hit': pygame.mixer.Sound('data/sfx/projectile_hit.wav'),

            'chicken_hurt': pygame.mixer.Sound('data/sfx/chicken_hurt.wav'),
            'enemy_hurt': pygame.mixer.Sound('data/sfx/enemy_hurt.wav'),
            'enemy_dead': pygame.mixer.Sound('data/sfx/enemy_dead.wav'),
            'ufo_hurt': pygame.mixer.Sound('data/sfx/ufo_hurt.wav'),
            'wall_hurt': pygame.mixer.Sound('data/sfx/wall_hurt.wav'),
            'wall_dead': pygame.mixer.Sound('data/sfx/wall_dead.wav'),

            'chicken_ambience': pygame.mixer.Sound('data/sfx/chicken_ambience.wav'),
            'ambience': pygame.mixer.Sound('data/sfx/ambience.wav'),

            'beat_level': pygame.mixer.Sound('data/sfx/beat_level.wav'),
            'beat_game': pygame.mixer.Sound('data/sfx/beat_game.wav'),
        }

        self.sfx['ui_select'].set_volume(0.15)
        self.sfx['open_pause_menu'].set_volume(0.2)

        self.sfx['jump'].set_volume(0.05)
        self.sfx['dash'].set_volume(0.05)
        self.sfx['shoot_fireball'].set_volume(0.075)
        self.sfx['sword_hit_flesh'].set_volume(0.15)
        self.sfx['sword_hit_metal'].set_volume(0.035)
        self.sfx['sword_hit_tile'].set_volume(0.35)
        self.sfx['dash_hit'].set_volume(0.035)
        self.sfx['player_hurt'].set_volume(0.3)
        self.sfx['player_dead'].set_volume(0.2)
        self.sfx['get_powerup'].set_volume(0.03)

        self.sfx['shoot_projectile'].set_volume(0.5)
        self.sfx['shoot_egg'].set_volume(0.35)
        self.sfx['fireball_hit'].set_volume(0.085)
        self.sfx['egg_hit'].set_volume(0.085)
        self.sfx['projectile_hit'].set_volume(0.5)
        self.sfx['ufo_attack'].set_volume(0.5)

        self.sfx['chicken_hurt'].set_volume(0.12)
        self.sfx['enemy_hurt'].set_volume(0.3)
        self.sfx['enemy_dead'].set_volume(0.5)
        self.sfx['ufo_hurt'].set_volume(0.025)
        self.sfx['wall_hurt'].set_volume(0.15)
        self.sfx['wall_dead'].set_volume(0.35)

        self.sfx['chicken_ambience'].set_volume(0.05)
        self.sfx['ambience'].set_volume(0.04)

        self.sfx['beat_level'].set_volume(0.2)
        self.sfx['beat_game'].set_volume(0.2)

        self.master_volume = 0.15
        self.update_music_volume()

        self.clouds = Clouds(self.assets['clouds'], count=24)
        self.tilemap = Tilemap(self, tile_size=16)
        self.player = Player(self, (50, 50), (16, 16))
        self.screenshake = 0


    def load_level(self, map_id):
        map_path = 'data/maps/' + str(map_id) + '.json'
        self.tilemap.load(map_path)

        if self.level != 7:
            pygame.mixer.music.load('data/8-bit_music_brisk.wav')
            pygame.mixer.music.set_volume(0.08)
            pygame.mixer.music.play(-1)
        elif self.level == 7:
            pygame.mixer.music.load('data/8-bit_music_fast.wav')
            pygame.mixer.music.set_volume(0.08)
            pygame.mixer.music.play(-1)

        self.player.reset_powerups()

        if self.player.flip == True:
            self.player.flip = False

        if self.level == 0:
            self.attack_tooltip_timer = self.attack_tooltip_duration
        elif self.level == 1:
            self.player.total_jumps = 2
            self.player.give_dash_powerup()
            self.player.give_dash_powerup()
        elif self.level == 2:
            self.player.total_jumps = 2
        elif self.level == 3:
            self.player.total_jumps = 3
            self.player.give_dash_powerup()
        elif self.level == 4:
            self.player.total_jumps = 11
            self.player.give_dash_powerup()
            self.player.fireball_count = 1
        elif self.level == 5:
            self.player.total_jumps = 14
            self.player.give_dash_powerup()
            self.player.fireball_count = 2
        elif self.level == 6:
            self.player.total_jumps = 18
            self.player.give_dash_powerup()
            self.player.fireball_count = 2
        elif self.level == 7:
            self.player.total_jumps = 18
            self.player.give_dash_powerup()
            self.player.give_dash_powerup()
            self.player.fireball_count = 2

        self.leaf_spawners = []
        for tree in self.tilemap.extract([('large_decor', 2)], keep=True):
            self.leaf_spawners.append(pygame.Rect(4 + tree['pos'][0], 4 + tree['pos'][1], 23, 13))

        self.enemies = []
        self.chickens = []
        self.ufos = []
        self.walls_of_flesh = []
        self.enemies_remaining = 0

        self.jump_powerups = []
        self.fireball_powerups = []
        self.dash_powerups = []
        self.health_restore_powerups = []

        for spawner in self.tilemap.extract(
                [('spawners', 0), ('spawners', 1), ('spawners', 2), ('spawners', 3), ('spawners', 4),
                ('spawners', 5), ('spawners', 6), ('spawners', 7), ('spawners', 8), ('spawners', 9)]):
            if spawner['variant'] == 0:
                self.player.pos = spawner['pos']
                self.player.air_time = 0
            if spawner['variant'] == 1:
                self.enemies.append(Enemy(self, spawner['pos'], (16, 16)))
            if spawner['variant'] == 2:
                self.chickens.append(Chicken(self, spawner['pos'], (16, 16)))
            if spawner['variant'] == 4:
                self.fireball_powerups.append(FireballPowerUp(self, spawner['pos'], (16, 16)))
            if spawner['variant'] == 5:
                self.jump_powerups.append(JumpPowerUp(self, spawner['pos'], (16, 16)))
            if spawner['variant'] == 6:
                self.ufos.append(Ufo(self, spawner['pos'], (16, 16)))
            if spawner['variant'] == 7:
                self.walls_of_flesh.append(WallOfFlesh(self, spawner['pos'], (500, 32)))
            if spawner['variant'] == 8:
                self.dash_powerups.append(DashPowerUp(self, spawner['pos'], (16, 16)))
            if spawner['variant'] == 9:
                self.health_restore_powerups.append(HealthRestorePowerUp(self, spawner['pos'], (16, 16)))

        self.projectiles = []
        self.fireballs = []
        self.sword_projectiles = []
        self.eggs = []
        self.particles = []
        self.sparks = []

        self.scroll = [0, 0]
        self.dead = 0
        self.transition = -30

    def start_game(self):
        self.running = True

        self.sfx['ambience'].play(-1)
        self.sfx['chicken_ambience'].play(-1)

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and not self.pause_menu_open:
                        self.player.jump()
                    if event.key == pygame.K_a and not self.pause_menu_open:
                        self.movement[0] = True
                    if event.key == pygame.K_d and not self.pause_menu_open:
                        self.movement[1] = True
                    if event.key == pygame.K_f and self.player.dash_count > 0 and not self.pause_menu_open:
                        self.player.dash()
                    if event.key == pygame.K_c and not self.pause_menu_open:
                        self.player.shoot_fireball()
                    if event.key == pygame.K_ESCAPE:
                        self.sfx['open_pause_menu'].play()
                        self.pause_menu_open = not self.pause_menu_open
                    if event.key == pygame.K_o:
                        pygame.quit()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a:
                        self.movement[0] = False
                    if event.key == pygame.K_d:
                        self.movement[1] = False
                if event.type == pygame.MOUSEBUTTONDOWN and not self.pause_menu_open:
                    if event.button == 1:
                        self.player.attack()
                if self.pause_menu_open and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.handle_menu_click(pygame.mouse.get_pos())

            if not self.pause_menu_open:
                self.update_game()
            else:
                self.render_pause_menu()

            self.display_2.blit(self.display, (0, 0))

            screenshake_offset = (random.random() * self.screenshake - self.screenshake / 2,
                                  random.random() * self.screenshake - self.screenshake / 2)
            self.screen.blit(pygame.transform.scale(self.display_2, self.screen.get_size()), screenshake_offset)
            pygame.display.update()
            self.clock.tick(60)

    def update_game(self):
        self.display.fill((0, 0, 0, 0))
        self.display_2.blit(self.assets['background'], (0, 0))

        self.screenshake = max(0, self.screenshake - 1)

        self.enemies_remaining = len(self.enemies) + len(self.chickens) + len(self.ufos) + len(self.walls_of_flesh)

        if self.enemies_remaining == 0:
            self.transition += 1
            if self.transition == 10 and self.level == 1:
                self.render_win_screen()
            if self.transition > 30:
                if self.level != 1:
                    self.sfx['beat_level'].play()
                self.level = min(self.level + 1, len(os.listdir('data/maps')) - 1)
                self.load_level(self.level)
        if self.transition < 0:
            self.transition += 1

        if self.player.health == 0:
            self.dead += 1
            if self.dead == 10:
                self.sfx['player_dead'].play()
            if self.dead >= 10:
                self.transition = min(30, self.transition + 1)
            if self.dead > 40:
                self.player.reset_health()
                self.load_level(self.level)

        self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 30
        self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) / 30
        render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

        for rect in self.leaf_spawners:
            if random.random() * 49999 < rect.width * rect.height:
                pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height)
                self.particles.append(Particle(self, 'leaf', pos, velocity=[-0.1, 0.3], frame=random.randint(0, 20)))

        self.clouds.update()
        self.clouds.render(self.display_2, offset=render_scroll)

        self.tilemap.render(self.display, offset=render_scroll)

        for enemy in self.enemies.copy():
            enemy.update(self.tilemap, (0, 0))
            enemy.render(self.display, offset=render_scroll)
            if enemy.is_dead():
                self.enemies.remove(enemy)

        for chicken in self.chickens.copy():
            chicken.update(self.tilemap, (0, 0))
            chicken.render(self.display, offset=render_scroll)
            if chicken.is_dead():
                self.chickens.remove(chicken)

        for wall_of_flesh in self.walls_of_flesh.copy():
            wall_of_flesh.update(self.tilemap)
            wall_of_flesh.render(self.display, offset=render_scroll)
            if wall_of_flesh.is_dead():
                self.walls_of_flesh.remove(wall_of_flesh)

            if self.player.rect().colliderect(wall_of_flesh.hitbox):
                if not self.player.is_invulnerable():
                    self.player.take_damage(2)
                    self.sfx['player_hurt'].play()
                    # This uses UFO velocity to calculate knockback
                if not self.tilemap.has_tiles_above(self.player.rect().topleft) and self.player.health >= 2:
                    knockback_force = [math.copysign(2, wall_of_flesh.velocity[0]) * 25, -2]
                    self.player.apply_knockback(knockback_force, duration=10)

        for ufo in self.ufos.copy():
            ufo.update(self.player)
            ufo.render(self.display, offset=render_scroll)
            if ufo.is_dead():
                self.ufos.remove(ufo)

            # Check collision between player and UFO
            if self.player.rect().colliderect(ufo.rect()):
                if not self.player.is_invulnerable():
                    self.player.take_damage(1)
                    self.sfx['ufo_attack'].play()
                    if not self.tilemap.has_tiles_above(self.player.rect().topleft) and self.player.health >= 1:
                        knockback_direction = -1 if ufo.rect().centerx < self.player.rect().centerx else  1
                        knockback_force = [knockback_direction * 5, -2]
                        self.player.apply_knockback(knockback_force, duration=10)
                    # Trigger UFO retreat
                    ufo.state = 'retreating'
                    ufo.retreat_timer = pygame.time.get_ticks() + ufo.retreat_cooldown

        for fireball_powerup in self.fireball_powerups.copy():
            fireball_powerup.update(self.tilemap, (0, 0))
            fireball_powerup.render(self.display, offset=render_scroll)
            if self.player.rect().colliderect(fireball_powerup.rect()):
                self.sfx['get_powerup'].play()
                self.player.give_fireball_powerup()
                self.fireball_powerups.remove(fireball_powerup)
                if self.player.fireball_count == 1:
                    self.fireball_tooltip_timer = self.fireball_tooltip_duration

        for jump_powerup in self.jump_powerups.copy():
            jump_powerup.update(self.tilemap, (0, 0))
            jump_powerup.render(self.display, offset=render_scroll)
            if self.player.rect().colliderect(jump_powerup.rect()):
                self.sfx['get_powerup'].play()
                self.player.give_jump_powerup()
                self.jump_powerups.remove(jump_powerup)
                if self.player.total_jumps == 1:
                    self.jump_tooltip_timer = self.jump_tooltip_duration

        ## Tooltips rendered 
        if self.jump_tooltip_timer > 0:
            self.render_jump_tooltip()
            self.jump_tooltip_timer -= 1

        if self.attack_tooltip_timer > 0:
            self.render_attack_tooltip()
            self.attack_tooltip_timer -= 1

        if self.fireball_tooltip_timer > 0:
            self.render_fireball_tooltip()
            self.fireball_tooltip_timer -= 1

        if self.dash_tooltip_timer > 0:
            self.render_dash_tooltip()
            self.dash_tooltip_timer -= 1

        for dash_powerup in self.dash_powerups.copy():
            dash_powerup.update(self.tilemap, (0, 0))
            dash_powerup.render(self.display, offset=render_scroll)
            if self.player.rect().colliderect(dash_powerup.rect()):
                self.sfx['get_powerup'].play()
                self.player.give_dash_powerup()
                self.dash_powerups.remove(dash_powerup)
                if self.player.dash_count == 1:
                    self.dash_tooltip_timer = self.dash_tooltip_duration
        
        for health_restore_powerup in self.health_restore_powerups.copy():
            health_restore_powerup.update(self.tilemap, (0, 0))
            health_restore_powerup.render(self.display, offset=render_scroll)
            if self.player.rect().colliderect(health_restore_powerup.rect()):
                self.sfx['get_powerup'].play()
                self.player.give_health_powerup()
                self.health_restore_powerups.remove(health_restore_powerup)

        if not self.player.health == 0:
            self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
            self.player.render(self.display, offset=render_scroll)

            ## [[(x, y)], direction, timer]
            ## basic enemy projectiles
            for projectile in self.projectiles.copy():
                projectile[0][0] += projectile[1]
                projectile[2] += 1
                img = self.assets['projectile']
                self.display.blit(img, (projectile[0][0] - img.get_width() / 2 - render_scroll[0],
                                        projectile[0][1] - img.get_height() / 2 - render_scroll[1]))
                if self.tilemap.solid_check(projectile[0]):
                    self.sfx['projectile_hit'].play()
                    self.projectiles.remove(projectile)
                    for i in range(4):
                        self.sparks.append(
                            Spark(projectile[0], random.random() - 0.5 + (math.pi if projectile[1] > 0 else 0),
                                  2 + random.random()))
                elif projectile[2] > 720:
                    self.projectiles.remove(projectile)
                else:
                    if self.player.rect().collidepoint(projectile[0]):
                        if not self.player.is_invulnerable():
                            self.projectiles.remove(projectile)
                            self.player.take_damage(1)
                            self.sfx['projectile_hit'].play()
                            self.sfx['player_hurt'].play()
                            self.screenshake = max(16, self.screenshake)
                            for i in range(30):
                                angle = random.random() * math.pi * 2
                                speed = random.random() * 5
                                self.sparks.append(Spark(self.player.rect().center, angle, 2 + random.random()))
                                self.particles.append(Particle(self, 'particle', self.player.rect().center,
                                                               velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                         math.sin(angle + math.pi) * speed * 0.5],
                                                               frame=random.randint(0, 7)))

            ## Fireball projectiles for player
            for fireball in self.fireballs.copy():
                fireball[0][0] += fireball[1] * 2.5
                fireball[2] += 1
                img = self.assets['fireball']
                if fireball[1] > 0:
                    img = pygame.transform.flip(img, True, False)
                self.display.blit(img, (fireball[0][0] - img.get_width() / 2 - render_scroll[0],
                                        fireball[0][1] - img.get_height() / 2 - render_scroll[1]))
                if self.tilemap.solid_check(fireball[0]):
                    self.sfx['fireball_hit'].play()
                    self.fireballs.remove(fireball)
                    for i in range(4):
                        self.sparks.append(
                            Spark(fireball[0], random.random() - 0.5 + (math.pi if fireball[1] > 0 else 0),
                                  2 + random.random()))
                elif fireball[2] > 360:
                    self.fireballs.remove(fireball)
                else:
                    for enemy in self.enemies:
                        if enemy.rect().collidepoint(fireball[0]):
                            if fireball in self.fireballs:  # Check if fireball is still in the list before trying to remove it
                                self.sfx['fireball_hit'].play()
                                self.fireballs.remove(fireball)
                            enemy.take_damage(enemy.max_health / 2)
                            enemy.is_hit = True
                            if not enemy.is_dead():
                                self.sfx['enemy_hurt'].play()
                                for i in range(4):
                                    self.sparks.append(
                                        Spark(fireball[0], random.random() - 0.5 + (math.pi if fireball[1] > 0 else 0),
                                        2 + random.random()))
                            else:
                                self.sfx['enemy_dead'].play()
                                self.screenshake = max(16, self.screenshake)
                                for i in range(30):
                                    angle = random.random() * math.pi * 2
                                    speed = random.random() * 5
                                    self.sparks.append(Spark(enemy.rect().center, angle, 2 + random.random()))
                                    self.particles.append(Particle(self, 'particle', enemy.rect().center,
                                                                velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                            math.sin(angle + math.pi) * speed * 0.5],
                                                                frame=random.randint(0, 7)))
                    for chicken in self.chickens:
                        if chicken.rect().collidepoint(fireball[0]):
                            if fireball in self.fireballs:  # Check if fireball is still in the list before trying to remove it
                                self.sfx['chicken_hurt'].play()
                                self.sfx['fireball_hit'].play()
                                self.fireballs.remove(fireball)
                            chicken.take_damage(chicken.max_health)
                            self.screenshake = max(16, self.screenshake)
                            for i in range(30):
                                angle = random.random() * math.pi * 2
                                speed = random.random() * 5
                                self.sparks.append(Spark(chicken.rect().center, angle, 2 + random.random()))
                                self.particles.append(Particle(self, 'particle', chicken.rect().center,
                                                               velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                         math.sin(angle + math.pi) * speed * 0.5],
                                                               frame=random.randint(0, 7)))
                    for ufo in self.ufos:
                        if ufo.rect().collidepoint(fireball[0]):
                            if fireball in self.fireballs:  # Check if fireball is still in the list before trying to remove it
                                self.sfx['fireball_hit'].play()
                                self.sfx['ufo_hurt'].play()
                                self.fireballs.remove(fireball)
                            ufo.take_damage(ufo.max_health)
                            self.screenshake = max(16, self.screenshake)
                            for i in range(30):
                                angle = random.random() * math.pi * 2
                                speed = random.random() * 5
                                self.sparks.append(Spark(ufo.rect().center, angle, 2 + random.random()))
                                self.particles.append(Particle(self, 'particle', ufo.rect().center,
                                                               velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                         math.sin(angle + math.pi) * speed * 0.5],
                                                               frame=random.randint(0, 7)))
                    for wall_of_flesh in self.walls_of_flesh:
                        if wall_of_flesh.hitbox.collidepoint(fireball[0]):
                            if fireball in self.fireballs:  # Check if sword_projectile is still in the list before trying to remove it
                                self.sfx['fireball_hit'].play()
                                self.fireballs.remove(fireball)
                            wall_of_flesh.take_damage(wall_of_flesh.max_health / 10)
                            wall_of_flesh.is_hit = True
                            if not wall_of_flesh.is_dead():
                                self.sfx['wall_hurt'].play()
                                for i in range(4):
                                    self.sparks.append(
                                        Spark(fireball[0], random.random() - 0.5 + (math.pi if fireball[1] > 0 else 0),
                                        2 + random.random()))
                            else:
                                self.sfx['wall_dead'].play()
                                self.screenshake = max(16, self.screenshake)
                                for i in range(30):
                                    angle = random.random() * math.pi * 2
                                    speed = random.random() * 5
                                    self.sparks.append(Spark(wall_of_flesh.hitbox.center, angle, 2 + random.random()))
                                    self.particles.append(Particle(self, 'particle', wall_of_flesh.hitbox.center,
                                                                velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                         math.sin(angle + math.pi) * speed * 0.5],
                                                                frame=random.randint(0, 7)))
            for sword_projectile in self.sword_projectiles.copy():
                sword_projectile[0][0] += sword_projectile[1] * 8
                sword_projectile[2] += 1
                if self.tilemap.solid_check(sword_projectile[0]):
                    self.sfx['sword_hit_tile'].play()
                    self.sword_projectiles.remove(sword_projectile)
                    for i in range(4):
                        self.sparks.append(
                            Spark(sword_projectile[0], random.random() - 0.5 + (math.pi if sword_projectile[1] > 0 else 0),
                                  2 + random.random()))
                elif sword_projectile[2] > 3:
                    self.sword_projectiles.remove(sword_projectile)
                else:
                    for enemy in self.enemies:
                        if enemy.rect().collidepoint(sword_projectile[0]):
                            if sword_projectile in self.sword_projectiles:  # Check if sword_projectile is still in the list before trying to remove it
                                self.sfx['sword_hit_flesh'].play()
                                self.sfx['enemy_hurt'].play()
                                self.sword_projectiles.remove(sword_projectile)
                            enemy.take_damage(enemy.max_health / 2)
                            enemy.is_hit = True
                            if not enemy.is_dead():
                                for i in range(4):
                                    self.sparks.append(
                                        Spark(sword_projectile[0], random.random() - 0.5 + (math.pi if sword_projectile[1] > 0 else 0),
                                        2 + random.random()))
                            else:
                                self.sfx['enemy_dead'].play()
                                self.screenshake = max(16, self.screenshake)
                                for i in range(30):
                                    angle = random.random() * math.pi * 2
                                    speed = random.random() * 5
                                    self.sparks.append(Spark(enemy.rect().center, angle, 2 + random.random()))
                                    self.particles.append(Particle(self, 'particle', enemy.rect().center,
                                                               velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                         math.sin(angle + math.pi) * speed * 0.5],
                                                               frame=random.randint(0, 7)))
                    for chicken in self.chickens:
                        if chicken.rect().collidepoint(sword_projectile[0]):
                            if sword_projectile in self.sword_projectiles:  # Check if sword_projectile is still in the list before trying to remove it
                                self.sfx['chicken_hurt'].play()
                                self.sfx['sword_hit_flesh'].play()
                                self.sword_projectiles.remove(sword_projectile)
                            chicken.take_damage(chicken.max_health)
                            self.screenshake = max(16, self.screenshake)
                            for i in range(30):
                                angle = random.random() * math.pi * 2
                                speed = random.random() * 5
                                self.sparks.append(Spark(chicken.rect().center, angle, 2 + random.random()))
                                self.particles.append(Particle(self, 'particle', chicken.rect().center,
                                                               velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                         math.sin(angle + math.pi) * speed * 0.5],
                                                               frame=random.randint(0, 7)))
                    for ufo in self.ufos:
                        if ufo.rect().collidepoint(sword_projectile[0]):
                            if sword_projectile in self.sword_projectiles:  # Check if sword_projectile is still in the list before trying to remove it
                                self.sfx['sword_hit_metal'].play()
                                self.sfx['ufo_hurt'].play()
                                self.sword_projectiles.remove(sword_projectile)
                            ufo.take_damage(ufo.max_health)
                            self.screenshake = max(16, self.screenshake)
                            for i in range(30):
                                angle = random.random() * math.pi * 2
                                speed = random.random() * 5
                                self.sparks.append(Spark(ufo.rect().center, angle, 2 + random.random()))
                                self.particles.append(Particle(self, 'particle', ufo.rect().center,
                                                               velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                         math.sin(angle + math.pi) * speed * 0.5],
                                                               frame=random.randint(0, 7)))
                    for wall_of_flesh in self.walls_of_flesh:
                        if wall_of_flesh.hitbox.collidepoint(sword_projectile[0]):
                            if sword_projectile in self.sword_projectiles:  # Check if sword_projectile is still in the list before trying to remove it
                                self.sfx['sword_hit_flesh'].play()
                                self.sword_projectiles.remove(sword_projectile)
                            wall_of_flesh.take_damage(wall_of_flesh.max_health / 10)
                            wall_of_flesh.is_hit = True
                            if not wall_of_flesh.is_dead():
                                self.sfx['wall_hurt'].play()
                                for i in range(4):
                                    self.sparks.append(
                                        Spark(sword_projectile[0], random.random() - 0.5 + (math.pi if sword_projectile[1] > 0 else 0),
                                        2 + random.random()))
                            else:
                                self.sfx['wall_dead'].play()
                                self.screenshake = max(16, self.screenshake)
                                for i in range(30):
                                    angle = random.random() * math.pi * 2
                                    speed = random.random() * 5
                                    self.sparks.append(Spark(wall_of_flesh.hitbox.center, angle, 2 + random.random()))
                                    self.particles.append(Particle(self, 'particle', wall_of_flesh.hitbox.center,
                                                                velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                         math.sin(angle + math.pi) * speed * 0.5],
                                                                frame=random.randint(0, 7)))
                                
            ## [[(x, y)], direction, timer]
            ## chicken egg projectiles
            for egg in self.eggs.copy():
                egg[0][0] += egg[1]
                egg[2] += 1
                img = self.assets['egg']
                self.display.blit(img, (egg[0][0] - img.get_width() / 2 - render_scroll[0],
                                        egg[0][1] - img.get_height() / 2 - render_scroll[1]))
                if self.tilemap.solid_check(egg[0]):
                    self.sfx['egg_hit'].play()
                    self.eggs.remove(egg)
                    for i in range(4):
                        self.sparks.append(
                            Spark(egg[0], random.random() - 0.5 + (math.pi if egg[1] > 0 else 0), 2 + random.random()))
                elif egg[2] > 720:
                    self.eggs.remove(egg)
                else:
                    if self.player.rect().collidepoint(egg[0]):
                        if not self.player.is_invulnerable():
                            self.sfx['egg_hit'].play()
                            self.sfx['player_hurt'].play()
                            self.eggs.remove(egg)
                            self.player.take_damage(1)
                            self.screenshake = max(16, self.screenshake)
                            for i in range(30):
                                angle = random.random() * math.pi * 2
                                speed = random.random() * 5
                                self.sparks.append(Spark(self.player.rect().center, angle, 2 + random.random()))
                                self.particles.append(Particle(self, 'particle', self.player.rect().center,
                                                               velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                         math.sin(angle + math.pi) * speed * 0.5],
                                                               frame=random.randint(0, 7)))

        for spark in self.sparks.copy():
            kill = spark.update()
            spark.render(self.display, offset=render_scroll)
            if kill:
                self.sparks.remove(spark)

        display_mask = pygame.mask.from_surface(self.display)
        display_sillhouette = display_mask.to_surface(setcolor=(0, 0, 0, 180), unsetcolor=(0, 0, 0, 0))
        for offset in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            self.display_2.blit(display_sillhouette, offset)

        for particle in self.particles.copy():
            kill = particle.update()
            particle.render(self.display, offset=render_scroll)
            if particle.type == 'leaf':
                particle.pos[0] += math.sin(particle.animation.frame * 0.035) * 0.3
            if kill:
                self.particles.remove(particle)

        if self.transition:
            transition_surf = pygame.Surface(self.display.get_size())
            pygame.draw.circle(transition_surf, (255, 255, 255),
                               (self.display.get_width() // 2, self.display.get_height() // 2),
                               (30 - abs(self.transition)) * 8)
            transition_surf.set_colorkey((255, 255, 255))
            self.display.blit(transition_surf, (0, 0))

        self.player.draw_health()
        self.render_pause_popup()
        self.render_enemies_remaining()

        if self.pause_menu_open:
            self.render_pause_menu()

    def reset_game(self):
        self.pause_menu_open = False
        self.win_screen_active = False
        self.level = 0
        self.player.reset_health()
        self.load_level(self.level)
        self.start_game()

    def update_music_volume(self):
        pygame.mixer.music.set_volume(self.master_volume)

    def increase_volume(self):
        self.master_volume = min(1.0, self.master_volume + 0.05)
        self.update_music_volume()

    def decrease_volume(self):
        self.master_volume = max(0.0, self.master_volume - 0.05)
        self.update_music_volume()

    def render_pause_menu(self):

        font = pygame.font.Font('data/fonts/alagard.ttf', 36)

        resume_text = font.render('Resume', True, pygame.Color('white'))
        restart_text = font.render('Restart', True, pygame.Color('white'))
        controls_text = font.render('Controls', True, pygame.Color('white'))
        feedback_text = font.render('Submit Feedback', True, pygame.Color('white'))
        quit_text = font.render('Quit To Main Menu', True, pygame.Color('white'))

        resume_rect = resume_text.get_rect(center=(480, 200))
        restart_rect = restart_text.get_rect(center=(480, 250))
        controls_rect = controls_text.get_rect(center=(480, 300))
        feedback_rect = feedback_text.get_rect(center=(480, 350))
        quit_rect = quit_text.get_rect(center=(480, 400))

        mx, my = pygame.mouse.get_pos()
        scale_x, scale_y = self.screen.get_width() / self.display.get_width(), self.screen.get_height() / self.display.get_height()
        mouse_pos = (mx / scale_x, my / scale_y)

        # Highlight if hovered
        if resume_rect.collidepoint(mouse_pos):
            pygame.draw.rect(self.display, (255, 0, 0), resume_rect.inflate(20, 10), 2)
        else:
            pygame.draw.rect(self.display, (255, 255, 255), resume_rect.inflate(20, 10), 2)

        if restart_rect.collidepoint(mouse_pos):
            pygame.draw.rect(self.display, (255, 0, 0), restart_rect.inflate(20, 10), 2)
        else:
            pygame.draw.rect(self.display, (255, 255, 255), restart_rect.inflate(20, 10), 2)

        if controls_rect.collidepoint(mouse_pos):
            pygame.draw.rect(self.display, (255, 0, 0), controls_rect.inflate(20, 10), 2)
        else:
            pygame.draw.rect(self.display, (255, 255, 255), controls_rect.inflate(20, 10), 2)

        if feedback_rect.collidepoint(mouse_pos):
            pygame.draw.rect(self.display, (255, 0, 0), feedback_rect.inflate(20, 10), 2)
        else:
            pygame.draw.rect(self.display, (255, 255, 255), feedback_rect.inflate(20, 10), 2)    

        if quit_rect.collidepoint(mouse_pos):
            pygame.draw.rect(self.display, (255, 0, 0), quit_rect.inflate(20, 10), 2)
        else:
            pygame.draw.rect(self.display, (255, 255, 255), quit_rect.inflate(20, 10), 2)

        self.display.blit(resume_text, resume_rect)
        self.display.blit(restart_text, restart_rect)
        self.display.blit(controls_text, controls_rect)
        self.display.blit(feedback_text, feedback_rect)
        self.display.blit(quit_text, quit_rect)

        self.resume_rect = resume_rect.inflate(20, 10)
        self.restart_rect = restart_rect.inflate(20, 10)
        self.controls_rect = controls_rect.inflate(20, 10)
        self.feedback_rect = feedback_rect.inflate(20, 10)
        self.quit_rect = quit_rect.inflate(20, 10)

    def render_options_menu(self):
        self.screen.fill((0, 0, 0))

        font = pygame.font.Font('data/fonts/alagard.ttf', 36)

        # Volume controls
        volume_text = font.render(f'Music: {int(self.master_volume * 100)}%', True, pygame.Color('white'))
        volume_rect = volume_text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 - 100))
        plus_text = font.render('+', True, pygame.Color('white'))
        minus_text = font.render('-', True, pygame.Color('white'))
        plus_rect = plus_text.get_rect(center=(self.screen.get_width() // 2 + 120, self.screen.get_height() // 2 - 100))
        minus_rect = minus_text.get_rect(
            center=(self.screen.get_width() // 2 - 120, self.screen.get_height() // 2 - 100))

        back_text = font.render('Back', True, pygame.Color('white'))
        back_rect = back_text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 + 100))

        pygame.draw.rect(self.screen, (255, 255, 255), back_rect.inflate(20, 10), 2)
        pygame.draw.rect(self.screen, (255, 255, 255), plus_rect.inflate(20, 10), 2)
        pygame.draw.rect(self.screen, (255, 255, 255), minus_rect.inflate(20, 10), 2)
        self.screen.blit(back_text, back_rect)
        self.screen.blit(plus_text, plus_rect)
        self.screen.blit(minus_text, minus_rect)
        self.screen.blit(volume_text, volume_rect)

        self.plus_rect = plus_text.get_rect(
            center=(self.screen.get_width() // 2 + 100, self.screen.get_height() // 2 - 100))
        self.minus_rect = minus_text.get_rect(
            center=(self.screen.get_width() // 2 - 100, self.screen.get_height() // 2 - 100))
        self.back_rect = back_text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 + 100))

        self.back_rect = back_rect.inflate(20, 10)
        self.plus_rect = plus_rect.inflate(20, 10)
        self.minus_rect = minus_rect.inflate(20, 10)

    def handle_menu_click(self, mouse_pos):
        scale_x, scale_y = self.screen.get_width() / self.display.get_width(), self.screen.get_height() / self.display.get_height()
        scaled_mouse_pos = (mouse_pos[0] / scale_x, mouse_pos[1] / scale_y)

        if self.resume_rect.collidepoint(scaled_mouse_pos):
            self.sfx['ui_select'].play()
            self.pause_menu_open = not self.pause_menu_open
        if self.restart_rect.collidepoint(scaled_mouse_pos):
            self.sfx['ui_select'].play()
            self.reset_game()
        if self.controls_rect.collidepoint(scaled_mouse_pos):
            self.sfx['ui_select'].play()
            self.render_controls_menu()
        if self.feedback_rect.collidepoint(scaled_mouse_pos):
            self.sfx['ui_select'].play()
            feedback_url = 'https://mail.google.com/mail/?view=cm&fs=1&to=cbohannon4@murraystate.edu,ghopkins3@murraystate.edu,ahead5@murraystate.edu'
            webbrowser.open_new(feedback_url)
        if self.quit_rect.collidepoint(scaled_mouse_pos):
            self.sfx['ui_select'].play()
            self.running = False
            pygame.mixer.stop()
            self.main_menu()
    
        if self.plus_rect.collidepoint(scaled_mouse_pos):
            self.increase_volume()
            self.sfx['ui_select'].play()
        elif self.minus_rect.collidepoint(scaled_mouse_pos):
            self.decrease_volume()
            self.sfx['ui_select'].play()
        elif self.back_rect.collidepoint(scaled_mouse_pos):
            self.pause_menu_open = False
            self.sfx['ui_select'].play()

    def render_controls_menu(self):
        self.display.blit(self.assets['control_menu'], (40, 100))
    
    def render_enemies_remaining(self):
        font = pygame.font.Font('data/fonts/alagard.ttf', 24)
        enemies_remaining_text = font.render(f'Enemies Remaining: {int(self.enemies_remaining)}', True, pygame.Color('white'))
        self.display.blit(enemies_remaining_text, (350, 25))

    def render_pause_popup(self):
        self.display.blit(self.assets['pause_popup'], (750, 15))

    def render_jump_tooltip(self):
        self.display.blit(self.assets['jump_tooltip'], (480, 180))

    def render_attack_tooltip(self):
        self.display.blit(self.assets['attack_tooltip'], (480, 180))
    
    def render_fireball_tooltip(self):
        self.display.blit(self.assets['fireball_tooltip'], (480, 180))

    def render_dash_tooltip(self):
        self.display.blit(self.assets['dash_tooltip'], (480, 180))

    def render_win_screen(self):
        pygame.mixer.stop()
        self.sfx['beat_game'].play()
        self.win_screen_active = True
        font = pygame.font.Font('data/fonts/alagard.ttf', 72)
        win_text = font.render('You Win, Congratulations!', True, pygame.Color('white'))
        restart_text = font.render('Restart', True, pygame.Color('white'))
        quit_text = font.render('Back to Menu', True, pygame.Color('white'))

        center_x = self.screen.get_width() // 2
        center_y = self.screen.get_height() // 2
        win_text_rect = win_text.get_rect(center=(center_x, center_y - 100))
        restart_text_rect = restart_text.get_rect(center=(center_x, center_y))
        quit_text_rect = quit_text.get_rect(center=(center_x, center_y + 100))

        while self.win_screen_active:
            self.screen.fill((0, 0, 0))
            self.screen.blit(win_text, win_text_rect.topleft)
            self.screen.blit(restart_text, restart_text_rect.topleft)
            self.screen.blit(quit_text, quit_text_rect.topleft)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        mouse_x, mouse_y = event.pos
                        if restart_text_rect.collidepoint(mouse_x, mouse_y):
                            self.sfx['ui_select'].play()
                            self.reset_game()
                            return
                        elif quit_text_rect.collidepoint(mouse_x, mouse_y):
                            self.sfx['ui_select'].play()
                            self.main_menu()
        pygame.display.update()

    def main_menu(self):
        in_options_menu = False  # State to track which menu to display
        self.win_screen_active = False

        pygame.mixer.music.load('data/Of_Knights_and_Kings.wav')
        pygame.mixer.music.set_volume(0.04)
        pygame.mixer.music.play(-1)
        self.running = False

        font = pygame.font.Font(None, 36)

        new_game_text = font.render('', True, pygame.Color('black'))
        load_game_text = font.render('', True, pygame.Color('black'))
        feedback_text = font.render('', True, pygame.Color('black'))
        options_text = font.render('', True, pygame.Color('black'))
        quit_text = font.render('', True, pygame.Color('black'))

        new_game_pos = (705, 430)
        load_game_pos = (705, 512)
        feedback_pos = (705, 599)
        options_pos = (705, 682)
        quit_pos = (978, 682)

        large_button_width = 520
        large_button_height = 60
        small_button_width = 250
        small_button_height = 60

        self.new_game_rect = pygame.Rect(new_game_pos, (large_button_width, large_button_height))
        self.load_game_rect = pygame.Rect(load_game_pos, (large_button_width, large_button_height))
        self.feedback_rect = pygame.Rect(feedback_pos, (large_button_width, large_button_height))
        self.options_rect = pygame.Rect(options_pos, (small_button_width, small_button_height))
        self.quit_rect = pygame.Rect(quit_pos, (small_button_width, small_button_height))

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.sfx['ui_select'].play()
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    print("main menu clicked: ", mouse_pos)
                    if in_options_menu:
                        if self.back_rect.collidepoint(mouse_pos):
                            self.sfx['ui_select'].play()
                            in_options_menu = False
                        if self.plus_rect.collidepoint(mouse_pos):
                            self.increase_volume()
                            self.sfx['ui_select'].play()
                        if self.minus_rect.collidepoint(mouse_pos):
                            self.decrease_volume()
                            self.sfx['ui_select'].play()
                    else:
                        if self.new_game_rect.collidepoint(mouse_pos):
                            self.sfx['ui_select'].play()
                            self.reset_game()
                            print("start game clicked")
                        elif self.load_game_rect.collidepoint(mouse_pos):
                            self.sfx['ui_select'].play()
                            if self.pause_menu_open:
                                self.start_game()
                            else: 
                                pass
                            print("load game clicked")
                        elif self.options_rect.collidepoint(mouse_pos):
                            self.sfx['ui_select'].play()
                            in_options_menu = True
                        elif self.feedback_rect.collidepoint(mouse_pos):
                            self.sfx['ui_select'].play()
                            print("feedback button")
                            feedback_url = 'https://mail.google.com/mail/?view=cm&fs=1&to=cbohannon4@murraystate.edu,ghopkins3@murraystate.edu,ahead5@murraystate.edu'
                            webbrowser.open_new(feedback_url)
                        elif self.quit_rect.collidepoint(mouse_pos):
                            self.sfx['ui_select'].play()
                            pygame.quit()
                            sys.exit()

            if in_options_menu:
                self.render_options_menu()
            else:
                self.screen.fill((0, 0, 0, 0))
                self.screen.blit(self.assets['main_menu_bg'], (0, 0))
                self.screen.blit(new_game_text, self.new_game_rect.topleft)
                self.screen.blit(load_game_text, self.load_game_rect.topleft)
                self.screen.blit(feedback_text, self.feedback_rect.topleft)
                self.screen.blit(options_text, self.options_rect.topleft)
                self.screen.blit(quit_text, self.quit_rect.topleft)
                
                self.clouds.update()
                self.clouds.render(self.screen)

            pygame.display.flip()
            self.clock.tick(60)

Game().main_menu()