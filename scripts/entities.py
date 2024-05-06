import pygame
import random
import math

from scripts.particle import Particle
from scripts.spark import Spark

class PhysicsEntity:
    def __init__(self, game, e_type, pos, size):
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.velocity = [0, 0]
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}

        self.action = ''
        self.anim_offset = (0, 0)
        self.flip = False
        self.set_action('idle')

        self.last_movement = [0, 0]

    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.type + '/' + self.action].copy()

    def update(self, tilemap, movement=(0, 0)):
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}

        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])

        self.pos[0] += frame_movement[0]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left
                    self.collisions['right'] = True
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right
                    self.collisions['left'] = True
                self.pos[0] = entity_rect.x

        self.pos[1] += frame_movement[1]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.collisions['down'] = True
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self.collisions['up'] = True
                self.pos[1] = entity_rect.y

        ## Image facing right 
        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0:
            self.flip = True

        self.last_movement = movement

        self.velocity[1] = min(5, self.velocity[1] + 0.1)

        if self.collisions['down'] or self.collisions['up']:
            self.velocity[1] = 0

        self.animation.update()

    def render(self, surf, offset=(0, 0)):
        ## Used with animation to flip image
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False),
                  (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[1]))


class LivingEntity(PhysicsEntity):
    def __init__(self, game, e_type, pos, size, health):
        super().__init__(game, e_type, pos, size)
        self.health = health
        self.max_health = health

    def take_damage(self, damage):
        self.health -= damage
        if self.health < 0:
            self.health = 0  # Ensure health does not go negative
        print(f"{self.type} took {damage} damage, {self.health} HP left.")

    def reset_health(self):
        self.health = self.max_health

    def is_hurt(self):
        if self.health < self.max_health and self.health != 0:
            return True

    def is_dead(self):
        if self.health == 0:
            return True

class Enemy(LivingEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'enemy', pos, size, 4)

        self.walking = 0
        self.is_hit = False
        self.flicker_count = 0

    def update(self, tilemap, movement=(0, 0)):

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
                distance = (self.game.player.pos[0] - self.pos[0], self.game.player.pos[1] - self.pos[1])
                if (abs(distance[1]) < 32):
                    if (self.flip and distance[0] < 0):
                        self.game.sfx['shoot_projectile'].play()
                        self.game.projectiles.append([[self.rect().centerx - 7, self.rect().centery], -1.5, 0])
                        for i in range(4):
                            self.game.sparks.append(Spark(self.game.projectiles[-1][0], random.random() - 0.5 + math.pi,
                                                          2 + random.random()))
                    if (not self.flip and distance[0] > 0):
                        self.game.sfx['shoot_projectile'].play()
                        self.game.projectiles.append([[self.rect().centerx + 7, self.rect().centery], 1.5, 0])
                        for i in range(4):
                            self.game.sparks.append(
                                Spark(self.game.projectiles[-1][0], random.random() - 0.5, 2 + random.random()))
        elif random.random() < 0.01:
            self.walking = random.randint(30, 120)

        super().update(tilemap, movement=movement)

        if movement[0] != 0:
            self.set_action('run')
        else:
            self.set_action('idle')

    def render(self, surf, offset=(0, 0)):
        if self.is_hit:
            self.render_damage(surf, offset, (255, 0, 0), (255, 255, 255))
            self.flicker_count += 1
            if self.flicker_count >= 10:
                self.is_hit = False
                self.flicker_count = 0
        else:
            super().render(surf, offset=offset)

        if self.flip:
            surf.blit(pygame.transform.flip(self.game.assets['gun'], True, False), (
                self.rect().centerx - 6 - self.game.assets['gun'].get_width() - offset[0],
                self.rect().centery - 2 - offset[1]))
        else:
            surf.blit(self.game.assets['gun'],
                      (self.rect().centerx + 6 - offset[0], self.rect().centery - 2 - offset[1]))

    def render_damage(self, surf, offset, color1, color2):
        enemy_sprite = self.animation.img().copy()
        if self.flicker_count % 2 == 0:
            enemy_sprite.fill(color1, special_flags=pygame.BLEND_RGB_MULT)
        else:
            enemy_sprite.fill(color2, special_flags=pygame.BLEND_RGB_MULT)
        surf.blit(enemy_sprite, (self.pos[0] - offset[0], self.pos[1] - offset[1]))


class Chicken(LivingEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'chicken', pos, size, 1)
        self.walking = 0
        self.is_hit = False

    def update(self, tilemap, movement=(0, 0)):

        if self.walking:
            if tilemap.solid_check((self.rect().centerx + (-7 if self.flip else 7), self.pos[1] + 23)):
                if (self.collisions['right'] or self.collisions['left']):
                    self.flip = not self.flip
                else:
                    movement = (movement[0] - 1.75 if self.flip else 1.75, movement[1])
            else:
                self.flip = not self.flip
            self.walking = max(0, self.walking - 1)
            if not self.walking:
                distance = (self.game.player.pos[0] - self.pos[0], self.game.player.pos[1] - self.pos[1])
                if (abs(distance[1]) < 32):
                    if (self.flip and distance[0] < 0):
                        self.game.sfx['shoot_egg'].play()
                        self.game.eggs.append([[self.rect().centerx - 7, self.rect().centery], -1.5, 0])
                        for i in range(4):
                            self.game.sparks.append(
                                Spark(self.game.eggs[-1][0], random.random() - 0.5 + math.pi, 2 + random.random()))
                    if (not self.flip and distance[0] > 0):
                        self.game.sfx['shoot_egg'].play()
                        self.game.eggs.append([[self.rect().centerx + 7, self.rect().centery], 1.5, 0])
                        for i in range(4):
                            self.game.sparks.append(
                                Spark(self.game.eggs[-1][0], random.random() - 0.5, 2 + random.random()))
        elif random.random() < 0.01:
            self.walking = random.randint(30, 120)

        super().update(tilemap, movement=movement)

        if movement[0] != 0:
            self.set_action('run')
        else:
            self.set_action('idle')

    def render(self, surf, offset=(0, 0)):
        if self.is_hit:
            self.render_damage(surf, offset, (255, 0, 0))
        else:
            super().render(surf, offset=offset)

    def render_damage(self, surf, offset, color):
        enemy_sprite = self.animation.img().copy()
        enemy_sprite.fill(color, special_flags=pygame.BLEND_RGB_MULT)
        surf.blit(enemy_sprite, (self.pos[0] - offset[0], self.pos[1] - offset[1]))

class Player(LivingEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'player', pos, size, 3)
        self.initial_position = list(pos)

        self.air_time = 0
        self.jumps = 0
        self.total_jumps = 0  # increments with each collected

        self.dash_active = False
        self.dash_count = 0
        self.dash_cooldown = 5500  # cooldown in milliseconds
        self.dash_speed = 5
        self.dash_duration = 10  # frames the dash will last
        self.dash_timestamps = [-self.dash_count]  # tracks cooldown
        self.dash_frame_count = 0

        self.player_movement_speed = 2.5

        self.invuln = False
        self.invuln_duration = 120
        self.invuln_timer = 0

        self.attacking = False
        self.attack_frame = 0
        self.attack_cooldown = 240  # cooldown in frames (0.5 seconds at 60 FPS)
        self.last_attack_time = -self.attack_cooldown  # ensure attack is available at start
        self.attack_duration = 110  # Duration the attack lasts in frames (0.25 seconds at 60 FPS)

        self.has_jump_powerup = False

        self.has_fireball_powerup = False
        self.fireball_count = 0  # Fireballs per cooldown
        self.fireball_shots_available = 0  # Shots available to be fired immediately (Don't Change)
        self.fireball_cooldown = 2000  # 2 seconds between shots
        self.last_fireball_time = -self.fireball_cooldown

        self.shooting = False
        self.shoot_cooldown = 240  # cooldown in frames (0.5 seconds at 60 FPS)
        self.last_shoot_time = -self.shoot_cooldown  # ensure attack is available at start
        self.shoot_duration = 110

        self.knockback_velocity = [0, 0]
        self.knockback_frames = 0

        self.blink_timer = 0
        self.blink_duration = 50000 # Milliseconds
        self.blink_state = True

    def update(self, tilemap, movement=(0, 0)):
        movement = (movement[0] * self.player_movement_speed, movement[1])
        super().update(tilemap, movement=movement)

        if self.is_invulnerable():
            self.invuln_timer -= 1
            if self.invuln_timer <= 0:
                self.invuln = False

        # Manage attack duration
        if self.attacking and pygame.time.get_ticks() - self.last_attack_time > self.attack_duration:
            self.reset_attack()

        self.air_time += 1

        if self.air_time > 120:
            if not self.game.dead:
                self.game.sfx['player_hurt'].play()
                self.game.screenshake = max(16, self.game.screenshake)
            self.health = 0

        if self.collisions['down']:
            self.air_time = 0
            ## Change to increase available jumps for testing
            self.jumps = self.total_jumps

        if self.air_time > 4:
            self.set_action('jump')
        elif movement[0] != 0:
            self.set_action('run')
        else:
            self.set_action('idle')

        if self.knockback_frames > 0:
            self.pos[0] += self.knockback_velocity[0]
            self.pos[1] += self.knockback_velocity[1]
            # Gradually reduce knockback impact
            self.knockback_velocity[0] *= 0.8
            self.knockback_velocity[1] *= 0.8
            self.knockback_frames -= 1

        ### Swing effects to emulate air moving around sword
        if self.attacking:
            if self.flip:
                hitbox_offset_x = -5
            else:
                hitbox_offset_x = 20
            hitbox_offset_y = -15
            player_rect = self.rect()
            sword_rect = pygame.Rect(player_rect.x + hitbox_offset_x, player_rect.y + hitbox_offset_y,
                                     player_rect.width, player_rect.height)
            if self.flip:
                pvelocity = [0.15 * random.random(), 0]
                self.game.particles.append(
                    Particle(self.game, 'swingleft', sword_rect, velocity=pvelocity, frame=random.randint(0, 7)))
            else:
                pvelocity = [-0.15 * random.random(), 0]
                self.game.particles.append(
                    Particle(self.game, 'swingright', sword_rect, velocity=pvelocity, frame=random.randint(0, 7)))

        current_time = pygame.time.get_ticks()
        if (current_time - self.last_fireball_time) > self.fireball_cooldown:
            self.fireball_shots_available = self.fireball_count

        if self.shooting and self.has_fireball_powerup:
            self.game.sfx['shoot_fireball'].play()
            if self.flip:
                self.game.fireballs.append([[self.rect().centerx, self.rect().centery], -1.5, 0])
            if not self.flip:
                self.game.fireballs.append([[self.rect().centerx, self.rect().centery], 1.5, 0])
            if pygame.time.get_ticks() - self.last_shoot_time > self.shoot_duration:
                self.reset_fireball()

        if self.dash_active:
            self.game.sfx['dash'].play()
            self.handle_dash_collision()
            for i in range(20):
                angle = random.random() * math.pi * 2
                speed = random.random() * 0.5 + 0.5
                pvelocity = [math.cos(angle) * speed, math.sin(angle) * speed]
                self.game.particles.append(Particle(self.game, 'particle', self.rect().center, velocity=pvelocity, frame=random.randint(0, 7)))

            self.dash_frame_count -= 1
            if self.dash_frame_count <= 0:
                self.dash_active = False
                self.velocity[0] = 0  # Reset the horizontal velocity when dash ends

            # Remaining update logic
        super().update(tilemap, movement=(self.velocity[0], movement[1]))

    def render(self, surf, offset=(0, 0)):
        
        if self.invuln and self.invuln_timer % 10 < 5 and self.health != self.max_health:
            return
        super().render(surf, offset=offset)

        if not self.attacking:
            if self.flip:
                surf.blit(pygame.transform.flip(self.game.assets['sword'], True, False), (
                    self.rect().centerx + 28 - self.game.assets['sword'].get_width() - offset[0],
                    self.rect().centery + 2 - self.game.assets['sword'].get_height() - offset[1]))
            else:
                surf.blit(self.game.assets['sword'], (self.rect().centerx - 28 - offset[0],
                                                      self.rect().centery + 2 - self.game.assets['sword'].get_height() -
                                                      offset[1]))
        elif self.attacking:
            if self.flip:
                surf.blit(pygame.transform.flip(self.game.assets['sword_frame2'], True, False), (
                    self.rect().centerx + 25 - self.game.assets['sword_frame2'].get_width() - offset[0],
                    self.rect().centery + 5 - self.game.assets['sword_frame2'].get_height() - offset[1]))
            else:
                surf.blit(self.game.assets['sword_frame2'], (self.rect().centerx - 25 - offset[0],
                                                             self.rect().centery + 5 - self.game.assets[
                                                                 'sword_frame2'].get_height() - offset[1]))

    def jump(self):
        if self.jumps > 0:
            self.game.sfx['jump'].play()
            self.velocity[1] = -3
            self.jumps -= 1
            self.air_time = 5

    def attack(self):
        current_time = pygame.time.get_ticks()
        if not self.attacking and current_time - self.last_attack_time >= self.attack_cooldown:
            self.attacking = True
            self.last_attack_time = current_time
            direction = -1.5 if self.flip else 1.5
            self.game.sword_projectiles.append([[self.rect().centerx, self.rect().centery], direction, 0])

    def reset_attack(self):
        self.attacking = False

    def shoot_fireball(self):
        if self.fireball_shots_available > 0:
            self.fireball_shots_available -= 1
            self.last_fireball_time = pygame.time.get_ticks()
            direction = -1.5 if self.flip else 1.5
            self.game.fireballs.append([[self.rect().centerx, self.rect().centery], direction, 0])
            self.game.sfx['shoot_fireball'].play()

    def reset_fireball(self):
        self.shooting = False

    def take_damage(self, damage):
        if not self.invuln:
            super().take_damage(damage)
            self.invuln = True
            self.invuln_timer = self.invuln_duration

    def is_invulnerable(self):
        if self.invuln:
            return True

    def give_fireball_powerup(self):
        self.fireball_count += 1
        self.fireball_shots_available = self.fireball_count  # Immediately allow more shots

    def give_jump_powerup(self):
        print("player has jump ability")
        self.total_jumps += 1
        self.jumps = self.total_jumps
        self.has_jump_powerup = True

    def give_wallslide_powerup(self):
        pass

    def give_dash_powerup(self):
        self.dash_count += 1
        self.dash_timestamps.append(-self.dash_cooldown)

    def dash(self):
        current_time = pygame.time.get_ticks()
        available_dash = next((i for i, t in enumerate(self.dash_timestamps) if current_time - t >= self.dash_cooldown),
                              None)

        if available_dash is not None:
            self.dash_active = True
            self.dash_frame_count = self.dash_duration
            dash_direction = 1 if not self.flip else -1
            self.velocity[0] = self.dash_speed * dash_direction
            self.invuln = True
            self.invuln_timer = self.dash_duration  # Invulnerability lasts only as long as the dash
            self.dash_timestamps[available_dash] = current_time

            self.flip = dash_direction == -1

    def handle_dash_collision(self):
        bounce_back_speed = -self.velocity[0] * .8

        for enemy in self.game.enemies:
            if self.rect().colliderect(enemy.rect()):
                self.game.sfx['dash_hit'].play()
                self.game.sfx['enemy_hurt'].play()
                enemy.take_damage(enemy.max_health)
                for i in range(30):
                        angle = random.random() * math.pi * 2
                        speed = random.random() * 5
                        self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
                        self.game.particles.append(Particle(self.game, 'particle', self.rect().center,

                                                        velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                  math.sin(angle + math.pi) * speed * 0.5],
                                                        frame=random.randint(0, 7)))
                self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random()))
                self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random()))
                self.game.screenshake = max(16, self.game.screenshake)
                self.velocity[0] = -self.velocity[0]
                if enemy.is_dead():
                    continue  # Skip the bounce back if the enemy is dead
                self.velocity[0] = -self.velocity[0]

        for chicken in self.game.chickens:
            if self.rect().colliderect(chicken.rect()):
                self.game.sfx['dash_hit'].play()
                self.game.sfx['chicken_hurt'].play()
                chicken.take_damage(chicken.max_health)
                for i in range(30):
                        angle = random.random() * math.pi * 2
                        speed = random.random() * 5
                        self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
                        self.game.particles.append(Particle(self.game, 'particle', self.rect().center,
                                                        velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                  math.sin(angle + math.pi) * speed * 0.5],
                                                        frame=random.randint(0, 7)))
                self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random()))
                self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random()))
                self.game.screenshake = max(16, self.game.screenshake)
                self.velocity[0] = -self.velocity[0]
                if chicken.is_dead():
                    continue
                self.velocity[0] = -self.velocity[0]

        for ufo in self.game.ufos:
            if self.rect().colliderect(ufo.rect()):
                self.game.sfx['dash_hit'].play()
                self.game.sfx['ufo_hurt'].play()
                ufo.take_damage(ufo.max_health)
                for i in range(30):
                        angle = random.random() * math.pi * 2
                        speed = random.random() * 5
                        self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
                        self.game.particles.append(Particle(self.game, 'particle', self.rect().center,
                                                        velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                  math.sin(angle + math.pi) * speed * 0.5],
                                                        frame=random.randint(0, 7)))
                self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random()))
                self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random()))
                self.game.screenshake = max(16, self.game.screenshake)
                self.velocity[0] = -self.velocity[0]
                if ufo.is_dead():
                    continue
                self.velocity[0] = -self.velocity[0]

        for wall_of_flesh in self.game.walls_of_flesh:
            if self.rect().colliderect(wall_of_flesh.hitbox):
                self.game.sfx['dash_hit'].play()
                self.game.sfx['wall_hurt'].play()
                wall_of_flesh.take_damage(wall_of_flesh.max_health / 10)
                self.velocity[0] = -self.velocity[0] * 2
                for i in range(30):
                        angle = random.random() * math.pi * 2
                        speed = random.random() * 5
                        self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
                        self.game.particles.append(Particle(self.game, 'particle', self.rect().center,

                                                        velocity=[math.cos(angle + math.pi) * speed * 0.5,
                                                                  math.sin(angle + math.pi) * speed * 0.5],
                                                        frame=random.randint(0, 7)))
                self.game.sparks.append(Spark(self.rect().center, 0, 5 + random.random()))
                self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random()))
                self.game.screenshake = max(16, self.game.screenshake)
                self.velocity[0] = -self.velocity[0]
                if wall_of_flesh.is_dead():
                    self.game.sfx['wall_dead'].play()
                    continue
                self.velocity[0] = -self.velocity[0] * 2

        self.dash_frame_count -= 1
        if self.dash_frame_count <= 0:
            self.dash_active = False
            self.velocity[0] = 0
            self.invuln = False
        else:
            self.flip = bounce_back_speed < 0

    def reset_health(self):
        if self.max_health > 3:
            self.max_health = 3
        self.health = self.max_health

    def reset_position(self, position):
        self.pos = list(position)
        self.air_time = 0

    def give_health_powerup(self):
        if self.health < self.max_health:
            self.health += 1
        ## self.max_health == 4 can be changed to anything for bonus hp if full hp
        elif self.max_health == 4 and self.health == self.max_health:
            pass
        else:
            self.max_health += 1
            self.health = self.max_health
            
    def reset_powerups(self):
        self.has_fireball_powerup = False
        self.fireball_count = 0

        self.has_jump_powerup = False
        self.total_jumps = 0
        self.jumps = 0

        self.dash_active = False
        self.dash_frame_count = 0
        self.dash_count = 0
        self.dash_timestamps = [-self.dash_cooldown] * self.dash_count

        self.invuln = False

    def apply_knockback(self, force, duration):
        self.knockback_velocity = [force[0], force[1]]
        self.knockback_frames = duration

    def draw_health(self):
        blink = False
        if self.health == 1:
            self.blink_timer += pygame.time.get_ticks()  # Update timer
            if self.blink_timer >= self.blink_duration:
                self.blink_timer -= self.blink_duration
                self.blink_state = not self.blink_state  # Toggle blink state
            blink = self.blink_state

        for i in range(self.max_health):
            # x, y properties for hearts
            x = 8 + i * (self.game.assets['full_heart'].get_width() + 5)
            y = 10

            if i < self.health:
                if blink:
                    self.game.display.blit(self.game.assets['empty_heart'], (x, y))  # Filled heart for current health
                else:
                    self.game.display.blit(self.game.assets['full_heart'], (x, y))  # Empty heart for lost health
            else:
                self.game.display.blit(self.game.assets['empty_heart'], (x, y))  # Empty heart for lost health

class JumpPowerUp(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'jump_powerup', pos, size)
        self.set_action('idle')
        self.bounce_timer = 0
        self.initial_y = pos[1]

    def update(self, tilemap, movement=(0, 0)):
        self.bounce_timer += 0.1
        bounce_offset = math.sin(self.bounce_timer) * 2
        self.pos[1] = self.initial_y + bounce_offset

        super().update(tilemap, movement=movement)
        self.set_action('idle')

class FireballPowerUp(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'fireball_powerup', pos, size)
        self.set_action('idle')
        self.bounce_timer = 0
        self.initial_y = pos[1]

    def update(self, tilemap, movement=(0, 0)):
        self.bounce_timer += 0.1
        bounce_offset = math.sin(self.bounce_timer) * 2
        self.pos[1] = self.initial_y + bounce_offset

        super().update(tilemap, movement=movement)
        self.set_action('idle')

    def render(self, surf, offset=(0, 0)):
        super().render(surf, offset=offset)

class DashPowerUp(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'dash_powerup', pos, size)
        self.set_action('idle')  # Assuming an idle animation exists for powerups
        self.bounce_timer = 0
        self.initial_y = pos[1]

    def update(self, tilemap, movement=(0, 0)):
        self.bounce_timer += 0.1
        bounce_offset = math.sin(self.bounce_timer) * 2
        self.pos[1] = self.initial_y + bounce_offset

        super().update(tilemap, movement=movement)
        self.set_action('idle')

    def render(self, surf, offset=(0, 0)):
        super().render(surf, offset=offset)

class HealthRestorePowerUp(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'health_restore_powerup', pos, size)
        self.set_action('idle')
        self.bounce_timer = 0
        self.initial_y = pos[1]

    def update(self, tilemap, movement=(0, 0)):
        super().update(tilemap, movement)
        self.bounce_timer += 0.1
        bounce_offset = math.sin(self.bounce_timer) * 2
        self.pos[1] = self.initial_y + bounce_offset

    def render(self, surf, offset=(0, 0)):
        super().render(surf, offset=offset)

class Ufo(LivingEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'ufo', pos, size, 3)
        self.hover_speed = 0.5
        self.attack_speed = 3
        self.retreat_speed = 2
        self.hover_height = 75
        self.state = "hovering"  # "hovering", "attacking", "retreating"
        self.attack_timer = 0
        self.attack_cooldown = 2000  # ms before UFO can attack again
        self.retreat_timer = 0
        self.retreat_cooldown = 3000  # ms the UFO spends in retreating
        self.retreat_direction_change_timer = 0
        self.hit_dur = 30
        self.hit_timer = 0
        self.is_hit = False
        self.set_action('idle')

    def update(self, player):
        player = self.game.player
        player_pos = self.game.player.pos
        current_time = pygame.time.get_ticks()

        distance_to_player = math.hypot(player_pos[0] - self.pos[0], player_pos[1] - self.pos[1])
        angle_to_player = math.atan2(player_pos[1] - self.pos[1], player_pos[0] - self.pos[0])

        if self.state == "hovering" and distance_to_player <= 300:
            self.state = "attacking"
        elif self.state == "attacking" and (distance_to_player > 500 or self.retreat_timer > current_time):
            self.state = "retreating"
            self.retreat_timer = current_time + self.retreat_cooldown
            self.retreat_direction_change_timer = 0
        elif self.state == "retreating" and current_time > self.retreat_timer:
            self.state = "hovering"

        if self.state == "hovering":
            self.hover(player_pos, angle_to_player, distance_to_player)
        elif self.state == "attacking" and not player.is_invulnerable():
            self.attack(player_pos, angle_to_player)
        elif self.state == "retreating":
            self.retreat(player_pos, angle_to_player, current_time)

        self.flip = self.velocity[0] < 0

    def hover(self, player_pos, angle_to_player, distance_to_player):
        self.set_action('idle')
        self.pos[1] += math.sin(pygame.time.get_ticks() / 1000.0) * 2  # Simulate floating

    def attack(self, player_pos, angle_to_player):
        self.set_action('idle')
        self.velocity[0] = math.cos(angle_to_player) * self.attack_speed
        self.velocity[1] = math.sin(angle_to_player) * self.attack_speed
        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]

    def retreat(self, player_pos, angle_to_player, current_time):
        self.set_action('idle')
        if self.retreat_direction_change_timer <= current_time:
            # Randomly choose a new direction to retreat to
            retreat_angle = random.uniform(0, 2 * math.pi)
            self.velocity[0] = math.cos(retreat_angle) * self.retreat_speed
            self.velocity[1] = math.sin(retreat_angle) * self.retreat_speed
            # Set the next direction change time
            self.retreat_direction_change_timer = current_time + random.randint(500, 1500)
        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]

    def render(self, surf, offset=(0, 0), zoom_level=1.0):
        super().render(surf, offset)

class WallOfFlesh(LivingEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'wall_of_flesh', pos, size, 30)
        self.velocity = [.5, 0]  # Constantly move left
        self.hitbox = pygame.Rect(self.pos[0], self.pos[1], 32, 500)  # Setting the hitbox dimensions
        self.walking = 0
        self.is_hit = False
        self.flicker_count = 0
        
    def update(self, tilemap):

        # Move left constantly
        self.pos[0] += self.velocity[0]
        self.pos[0] += self.velocity[0]
        self.hitbox.x = self.pos[0]  # Update hitbox position X
        self.hitbox.y = self.pos[1]  # Update hitbox position Y
        
    def render(self, surf, offset):
        if self.is_hit:
            self.render_damage(surf, offset, (255, 0, 0), (255, 255, 255))
            self.flicker_count += 1
            if self.flicker_count >= 10:
                self.is_hit = False
                self.flicker_count = 0
        else:
            super().render(surf, offset=offset)

    def render_damage(self, surf, offset, color1, color2):
        enemy_sprite = self.animation.img().copy()
        if self.flicker_count % 2 == 0:
            enemy_sprite.fill(color1, special_flags=pygame.BLEND_RGB_MULT)
        else:
            enemy_sprite.fill(color2, special_flags=pygame.BLEND_RGB_MULT)
        surf.blit(enemy_sprite, (self.pos[0] - offset[0], self.pos[1] - offset[1]))