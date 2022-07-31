import pygame, sys
from pygame.locals import *
from game_utils import Minion, Projectile, get_projectile_sprites
import pickle
import select
import socket

WIDTH = 900
HEIGHT = 700
PLAY_AREA_Y = 600
SPRITE_SIZE = 64
BUFFERSIZE = 2048
MOVEMENT_SPEED = 5

print("Please choose class: [0] Archer, [1] Knight, [2] Healer, [3] Mage")
player_class = input()
player_class = int(player_class)
classes = ["Archer", "Knight", "Healer", "Mage"]

print("You chose: ", classes[player_class])

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Gladiator Play')

clock = pygame.time.Clock()

serverAddr = '127.0.0.1'
if len(sys.argv) == 2:
  serverAddr = sys.argv[1]

#Create font for text
font = pygame.font.SysFont("verdana", 32)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((serverAddr, 4321))

playerid = 0
player = Minion(50, 50, 0, player_class, 100, screen)

minions = []

projectile_sprites = get_projectile_sprites()
projectiles = []

#Create static UI elements
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
      player = Minion(50, 50, playerid, player_class, 100, screen)
      s.send(pickle.dumps(['class update', playerid, player.Class]))

    if gameEvent[0] == 'player locations':
      gameEvent.pop(0)
      minions = []
      for minion in gameEvent:
        if minion[0] != playerid:
          minions.append(Minion(minion[1], minion[2], minion[0], minion[3],minion[4], screen))

    if gameEvent[0] == 'remove player':
          del minions[gameEvent[1]]

    if gameEvent[0] == 'class update':
      gameEvent.pop(0)
      minions = []
      for minion in gameEvent:
        if minion[0] != playerid:
          minions.append(Minion(minion[1], minion[2], minion[0], minion[3],minion[4], screen))        

    
  for event in pygame.event.get():
    if event.type == QUIT:
      s.send(pickle.dumps(['disconnect', playerid]))
      pygame.quit()
      sys.exit()
    if event.type == KEYDOWN:
      if event.key == K_LEFT: player.vx = -MOVEMENT_SPEED
      if event.key == K_RIGHT: player.vx = MOVEMENT_SPEED
      if event.key == K_UP: player.vy = -MOVEMENT_SPEED
      if event.key == K_DOWN: player.vy = MOVEMENT_SPEED
      if event.key == K_a:
        arrow = Projectile(player.x + (SPRITE_SIZE/2) ,player.y + (SPRITE_SIZE/2) , -10, 0, playerid, len(projectiles), screen)
        arrow.set_sprite(projectile_sprites[player_class])
        projectiles.append(arrow)
      if event.key == K_w:
        arrow = Projectile(player.x + (SPRITE_SIZE/2) ,player.y + (SPRITE_SIZE/2) , 0, -10, playerid, len(projectiles), screen)
        arrow.set_sprite(projectile_sprites[player_class])
        projectiles.append(arrow)
      if event.key == K_d:
        arrow = Projectile(player.x + (SPRITE_SIZE/2) ,player.y + (SPRITE_SIZE/2) , 10, 0, playerid, len(projectiles), screen)
        arrow.set_sprite(projectile_sprites[player_class])
        projectiles.append(arrow)
      if event.key == K_s:
        arrow = Projectile(player.x + (SPRITE_SIZE/2) ,player.y + (SPRITE_SIZE/2) , 0, 10, playerid, len(projectiles), screen)
        arrow.set_sprite(projectile_sprites[player_class])
        projectiles.append(arrow)
      if event.key == K_SPACE:
        for i in range(3):
          arrow = Projectile(player.x + (SPRITE_SIZE/2) ,player.y + (SPRITE_SIZE/2) , 10, -1.25 + i, playerid, len(projectiles), screen)
          arrow.set_sprite(projectile_sprites[player_class])
          projectiles.append(arrow)


    if event.type == KEYUP:
      if event.key == K_LEFT and player.vx == -MOVEMENT_SPEED: player.vx = 0
      if event.key == K_RIGHT and player.vx == MOVEMENT_SPEED: player.vx = 0
      if event.key == K_UP and player.vy == -MOVEMENT_SPEED: player.vy = 0
      if event.key == K_DOWN and player.vy == MOVEMENT_SPEED: player.vy = 0
      if event.key == K_q: player.health -= MOVEMENT_SPEED 


  clock.tick(60)
  screen.fill((194, 178, 128))

  #UI ELEMENTS
  pygame.draw.rect(screen, (50,50,50), ui_rect)
  if player.health > 0:
    ui_health = font.render("Health: " + f"{player.health}", True, (255,0,0))
  else:
    ui_health = font.render("You are dead!", True, (255,0,0))

  screen.blit(ui_health, (25,610))
  screen.blit(ui_class, (25,640))


  player.update()

  for projectile in projectiles:
    projectile.update()
    projectile.render()

  for minion in minions:
    minion.render()

  player.render()

  
  pygame.display.flip()

  ge = ['position update', playerid, player.x, player.y, player.health]
  s.send(pickle.dumps(ge))
s.close()
