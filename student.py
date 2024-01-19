# Students:
# Bárbara Nóbrega Galiza - 105937
# Pedro Daniel Fidalgo de Pinho - 109986

import asyncio
import getpass
import json
import os

import websockets

from ai import *
from path_to_enemies import *

async def agent_loop(server_address="localhost:8000", agent_name="student"):
    async with websockets.connect(f"ws://{server_address}/player") as websocket:
        # Receive information about static game properties
        await websocket.send(json.dumps({"cmd": "join", "name": agent_name}))

        level = 1
        map = json.loads(await websocket.recv()).get("map")
        dug_dir = Direction.EAST

        while True:
            enemies = []
            key = ""
            try:
                state = json.loads(
                    await websocket.recv()
                )  # receive game update, this must be called timely or game will get out of sync with the server
                if state.get("level") != level:
                    level = state.get("level")
                    map = state.get("map")

                if state.get("enemies") is not None and len(state.get("enemies")) != 0:
                    # storing all enemies
                    for each in state.get("enemies"):
                        enemies.append(each)
                    digdug = state.get("digdug")
                    target_enemy, target_neighbors = enemy_prio(digdug, enemies)
                    rocks = state.get("rocks")
                    step = state.get("step")
                    key = get_key(map, digdug, target_enemy, target_neighbors, dug_dir, rocks, step, len(enemies))
                    
                    if update_digdug_dir(key) != None:
                        dug_dir = update_digdug_dir(key)
                        update_map(key, map, digdug)
                else:
                    key = " "
                    
                await websocket.send(
                    json.dumps({"cmd": "key", "key": key})
                )  # send key command to server
            except websockets.exceptions.ConnectionClosedOK:
                print("Server has cleanly disconnected us")
                return
            

# DO NOT CHANGE THE LINES BELLOW
# You can change the default values using the command line, example:
# $ NAME='arrumador' python3 client.py
loop = asyncio.get_event_loop()
SERVER = os.environ.get("SERVER", "localhost")
PORT = os.environ.get("PORT", "8000")
NAME = os.environ.get("NAME", getpass.getuser())
loop.run_until_complete(agent_loop(f"{SERVER}:{PORT}", NAME))
