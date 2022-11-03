from pypresence import Presence
import time
client_id = "748670819156099073"
RPC = Presence(client_id)
RPC.connect()
RPC.update(state="Is Cool", details="Hangman", large_image="hangman-7-christmasified_v1")

while True:
    time.sleep(15)