import socket
import asyncore
import random
import pickle
import time


def handle_message(message, outgoing, minionmap):
    #FUNCTION RETURNS UPDATE MESSAGE
    remove = []
    #update position/world if game event is pos update
    if message[0] == 'position update':
        playerid = message[1]
        x = message[2]
        y = message[3]
        health = message[4]

        minionmap[playerid].x = x
        minionmap[playerid].y = y
        minionmap[playerid].health = health
        message[0] = 'player locations'

    #player has quit, tell everyone to remove him
    if message[0] == 'disconnect':
        print(f"player {message[1]} has disconnected")
        del minionmap[message[1]]
        message[0] == 'remove player'

    #['class update', playerid, player.Class]
    if message[0] == 'class update':
        playerid = message[1]
        minionmap[playerid].Class = message[2]


    for i in outgoing:
        update = [message[0]]

        for key, value in minionmap.items():
            update.append([value.ownerid, value.x, value.y, value.Class, value.health])

        try:
            i.send(pickle.dumps(update))
        except Exception:
            remove.append(i)
            continue

        for r in remove:
            outgoing.remove(r)
    return minionmap
