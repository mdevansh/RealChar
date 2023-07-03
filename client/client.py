import io
import os
import sys
import asyncio
import websockets
from aioconsole import ainput  # for async input
from pydub import AudioSegment
from pydub.playback import play

async def send_message(websocket):
    print('You: ', end="", flush=True)
    while True:
        message = await ainput()  # Reading input
        await websocket.send(message)


async def receive_message(websocket):
    while True:
        response = await websocket.recv()
        if response == "type:audio":
            audio_response = await websocket.recv()
            audio_data = io.BytesIO(audio_response)
            audio = AudioSegment.from_mp3(audio_data)
            play(audio)
        else: # text data
            if response == '\n':
                print('\nYou: ', end="", flush=True)
            else:
                print(f"{response}", end="", flush=True)

async def start_client():
    uri = "ws://localhost:8000/ws/1"
    async with websockets.connect(uri) as websocket:
        receiver_task = asyncio.create_task(receive_message(websocket))
        sender_task = asyncio.create_task(send_message(websocket))
        done, pending = await asyncio.wait(
            [receiver_task, sender_task],
            return_when=asyncio.FIRST_COMPLETED,
        )

        for task in pending:
            task.cancel()

if __name__ == "__main__":
    try:
        asyncio.run(start_client())
    except KeyboardInterrupt:
        print("Client stopped by user")
