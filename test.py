import asyncio
import websockets


async def echo(websocket):
    async for message in websocket:
        await websocket.send(f'Got your msg its: {message}')


async def main():
    async with websockets.serve(echo, "localhost", 5000):
        await asyncio.Future()  # run forever

asyncio.run(main())
