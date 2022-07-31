import pygame, sys
from pygame.locals import *
import pickle
import select
import socket

WIDTH = 900
HEIGHT = 700
PLAY_AREA_Y = 600
SPRITE_SIZE = 64
BUFFERSIZE = 2048

print("Please choose class: [0] Archer, [1] Knight, [2] Healer, [3] Mage")
player_class = input()
player_class = int(player_class)
classes = ["archer", "knight", "healer", "mage"]

print("You chose: ", classes[player_class])

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Gladiator Play')

clock = pygame.time.Clock()

serverAddr = '127.0.0.1'
if len(sys.argv) == 2:
  serverAddr = sys.argv[1]

archer_sprite = pygame.image.load('images\Archer\Archer.png')
knight_sprite = pygame.image.load('images\Knight\knight.png')
healer_sprite = pygame.image.load('images\Healer\Healer.png')
mage_sprite = pygame.image.load('images\Mage\Mage.png')
dead_sprite = pygame.image.load('images\Dead\Dead.png')


archer_sprite = pygame.transform.scale(archer_sprite, (64, 64))
knight_sprite = pygame.transform.scale(knight_sprite, (64, 64))
healer_sprite = pygame.transform.scale(healer_sprite, (64, 64))
mage_sprite = pygame.transform.scale(mage_sprite, (64, 64))
dead_sprite = pygame.transform.scale(dead_sprite, (64, 64))



#Create font for text
font = pygame.font.SysFont("verdana", 32)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((serverAddr, 4321))

playerid = 0

sprites = { 0: archer_sprite, 1: knight_sprite, 2: healer_sprite, 3: mage_sprite, 4: dead_sprite}

class Minion:
  def __init__(self, x, y, id, class_id, health):
    self.x = x
    self.y = y
    self.vx = 0
    self.vy = 0
    self.id = id
    self.health = health
    self.Class = class_id
    self.sprite = sprites[class_id]

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

      if self.id == 0:
        self.id = playerid
      
    if self.health < 0:
        self.health = 0
   
  def render(self):

      #Player sprite
      if self.health > 0:
        screen.blit(self.sprite, (self.x, self.y))
      else:
        self.sprite = sprites[4]
        screen.blit(self.sprite, (self.x, self.y))


      #Healthbar background
      pygame.draw.rect(screen, (0,0,0), pygame.Rect(self.x, self.y + SPRITE_SIZE + 5, 64, 10))
      #Healthbar
      pygame.draw.rect(screen, (255,0,0), pygame.Rect(self.x, self.y + SPRITE_SIZE + 5, self.health * 0.64, 10))


player = Minion(50, 50, 0, player_class, 100)

minions = []

#Create UI Rectangle
ui_class = font.render("Class: " + f"{classes[player.Class]}", True, (255,0,0))


ui_rect = pygame.Rect(0,600,WIDTH, HEIGHT-PLAY_AREA_Y)

#Game loop
while True:
  ins, outs, ex = select.select([s], [], [], 0)
  for inm in ins: 
    gameEvent = pickle.loads(inm.recv(BUFFERSIZE))

    if gameEvent[0] == 'id update':
      playerid = gameEvent[1]
      print("Your player id:", playerid)
      s.send(pickle.dumps(['class update', playerid, player.Class]))
    if gameEvent[0] == 'player locations':
      gameEvent.pop(0)
      minions = []
      for minion in gameEvent:
        if minion[0] != playerid:
          minions.append(Minion(minion[1], minion[2], minion[0], minion[3],minion[4]))

    if gameEvent[0] == 'remove player':
          del minions[gameEvent[1]]

    if gameEvent[0] == 'class update':
      gameEvent.pop(0)
      minions = []
      for minion in gameEvent:
        if minion[0] != playerid:
          minions.append(Minion(minion[1], minion[2], minion[0], minion[3],minion[4]))        

    
  for event in pygame.event.get():
    if event.type == QUIT:
      s.send(pickle.dumps(['disconnect', playerid]))
      pygame.quit()
      sys.exit()
    if event.type == KEYDOWN:
      if event.key == K_LEFT: player.vx = -10
      if event.key == K_RIGHT: player.vx = 10
      if event.key == K_UP: player.vy = -10
      if event.key == K_DOWN: player.vy = 10

    if event.type == KEYUP:
      if event.key == K_LEFT and player.vx == -10: player.vx = 0
      if event.key == K_RIGHT and player.vx == 10: player.vx = 0
      if event.key == K_UP and player.vy == -10: player.vy = 0
      if event.key == K_DOWN and player.vy == 10: player.vy = 0
      if event.key == K_q: player.health -= 10 


  clock.tick(60)
  screen.fill((194, 178, 128))

  #UI ELEMENTS
  pygame.draw.rect(screen, (50,50,50), ui_rect)
  ui_health = font.render("Health: " + f"{player.health}", True, (255,0,0))
  screen.blit(ui_health, (25,610))
  screen.blit(ui_class, (25,640))


  player.update()


  for minion in minions:
    minion.render()

  player.render()

  
  pygame.display.flip()

  ge = ['position update', playerid, player.x, player.y, player.health]
  s.send(pickle.dumps(ge))
s.close()
