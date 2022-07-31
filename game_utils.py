from turtle import right
import pygame, sys
from pygame.locals import *
import pickle
import select
import socket


WIDTH = 900
HEIGHT = 700
PLAY_AREA_Y = 600
SPRITE_SIZE = 64

archer_sprite = pygame.image.load('images\Archer\Archer.png')
knight_sprite = pygame.image.load('images\Knight\knight.png')
healer_sprite = pygame.image.load('images\Healer\Healer.png')
mage_sprite = pygame.image.load('images\Mage\Mage.png')
dead_sprite = pygame.image.load('images\Dead\Dead.png')


arrow_sprite = pygame.image.load('images\Projectiles\Arrow.png')
fireball_sprite = pygame.image.load('images\Projectiles\Fireball.png')
healing_ray_sprite = pygame.image.load('images\Projectiles\Healing_Ray.png')
sword_sprite = pygame.image.load('images\Projectiles\Sword.png')



archer_sprite = pygame.transform.scale(archer_sprite, (64, 64))
knight_sprite = pygame.transform.scale(knight_sprite, (64, 64))
healer_sprite = pygame.transform.scale(healer_sprite, (64, 64))
mage_sprite = pygame.transform.scale(mage_sprite, (64, 64))
dead_sprite = pygame.transform.scale(dead_sprite, (64, 64))

sprites = { 0: archer_sprite, 1: knight_sprite, 2: healer_sprite, 3: mage_sprite, 4: dead_sprite}

projectile_sprites = {0: arrow_sprite, 1: sword_sprite , 2: healing_ray_sprite, 3: fireball_sprite}



class Minion:
  def __init__(self, x, y, id, class_id, health, screen):
    self.x = x
    self.y = y
    self.vx = 0
    self.vy = 0
    self.id = id
    self.health = health
    self.Class = class_id
    self.sprite = sprites[class_id]
    self.screen = screen

  def update(self):
    if self.health > 0:
      self.x += self.vx
      self.y += self.vy

      if self.x > WIDTH - SPRITE_SIZE:
        self.x = WIDTH - SPRITE_SIZE
      if self.x < 0:
        self.x = 0
      if self.y > PLAY_AREA_Y - SPRITE_SIZE:
        self.y = PLAY_AREA_Y - SPRITE_SIZE
      if self.y < 0:
        self.y = 0
      
    if self.health < 0:
        self.health = 0

  def render(self):

      #Player sprite
      if self.health > 0:
        self.screen.blit(self.sprite, (self.x, self.y))
      else:
        self.sprite = sprites[4]
        self.screen.blit(self.sprite, (self.x, self.y))


      #Healthbar background
      pygame.draw.rect(self.screen, (0,0,0), pygame.Rect(self.x, self.y + SPRITE_SIZE + 5, 64, 10))
      #Healthbar
      pygame.draw.rect(self.screen, (255,0,0), pygame.Rect(self.x, self.y + SPRITE_SIZE + 5, self.health * 0.64, 10))

def get_projectile_sprites():
    return projectile_sprites

class Projectile:
    def __init__(self, x, y, vx, vy, ownerid, projectile_id ,screen):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.ownerid = ownerid
        self.sprite = 0
        self.screen = screen
        self.id = projectile_id

    def generate_projectile_direction(self, sprite):
        left = sprite
        right = pygame.transform.flip(sprite, True, False)


        up = pygame.transform.rotate(sprite, -90)
        down = pygame.transform.rotate(sprite, 90)

        if self.vx > 0: return right
        if self.vx < 0: return left

        if self.vy > 0: return down
        if self.vy < 0: return up

    def set_sprite(self, sprite):
        directional_sprite = self.generate_projectile_direction(sprite)
        self.sprite = directional_sprite

    def update(self):
        self.x += self.vx
        self.y += self.vy

    def render(self):
        if not self.sprite == 0:
            self.screen.blit(self.sprite, (self.x, self.y))
