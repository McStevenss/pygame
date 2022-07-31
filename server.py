import socket
import asyncore
import random
import pickle
import time
from server_utils import handle_message

BUFFERSIZE = 512

global outgoing
outgoing = []

class Minion:
  def __init__(self, ownerid, health= 100):
    self.x = 50
    self.y = 50
    self.ownerid = ownerid
    self.Class = 0
    self.health = health

global minionmap
minionmap = {}

def updateWorld(message):
  global minionmap
  global outgoing
  arr = pickle.loads(message)

  playerid = arr[1]
  if playerid == 0: return

  updated_minionmap = handle_message(arr, outgoing ,minionmap)

  minionmap = updated_minionmap


class MainServer(asyncore.dispatcher):
  def __init__(self, port):
    asyncore.dispatcher.__init__(self)
    self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
    self.bind(('', port))
    self.listen(10)
  def handle_accept(self):
    conn, addr = self.accept()
    print('Connection address:' + addr[0] + " " + str(addr[1]))
    outgoing.append(conn)
    playerid = random.randint(1000, 1000000)
    playerminion = Minion(playerid)
    minionmap[playerid] = playerminion
    conn.send(pickle.dumps(['id update', playerid]))
    SecondaryServer(conn)

class SecondaryServer(asyncore.dispatcher_with_send):
  def handle_read(self):
    recievedData = self.recv(BUFFERSIZE)
    if recievedData:
      #update the game with data
      updateWorld(recievedData)
    else: self.close()

MainServer(4321)
print("Server Started...")
asyncore.loop()