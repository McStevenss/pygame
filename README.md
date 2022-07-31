A Very Basic Python Multiplayer game prototype.

Currently allows players to :
- Choose class.
- Connect to server
- Run around server with other players
- Ability to sync actions such as dying, health, class to other players

Developed for Python 3.5.2 using pygame.

start the server by running

`py server.py`

then in a separate terminal start the client with

`py game.py`

foreign clients can join by specifying your ipaddress eg:

`py game.py 192.10.1.50`
