import asyncio
from pathlib import Path

from domain.types import Seconds
from infrastructure.real_player import MiniaudioPlayer


async def play():
    player = MiniaudioPlayer()
    player.load_file(Path("file_example_MP3_700KB.mp3"))
    playing_task = asyncio.create_task(
        player.play(Seconds(7), lambda: print("Playing ended"))
    )
    await asyncio.sleep(5)
    player.stop()
    print("Early stop works!")
    await playing_task


if __name__ == "__main__":
    asyncio.run(play())
