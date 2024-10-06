import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from kink import di
import uvicorn

from player.src.application.break_observer import BreakObserver
from player.src.application.events.handle import EventHandler
from player.src.application.interfaces.events import EventsConsumer
from player.src.application.playing_manager import PlayingManager
from player.src.bootstrap import bootstrap_di
from player.src.config import get_logger
from player.src.infrastructure.messaging.types import PlaylistEventsConsumer

logger = get_logger(__name__)


async def consume_events(
    events_consumer: EventsConsumer, event_handler: EventHandler
) -> None:
    logger.info("Started consuming and handling events")
    while True:
        events = await events_consumer.consume(1)
        for event in events:
            event_handler.handle_event(event)
        await asyncio.sleep(0.1)


def main_tasks() -> list[asyncio.Task]:
    playing_manager = di[PlayingManager]
    break_observer = di[BreakObserver]
    playlist_events_consumer = di[PlaylistEventsConsumer]
    event_handler = di[EventHandler]

    mp_task = asyncio.create_task(playing_manager.manage_playing())
    ucb_task = asyncio.create_task(break_observer.update_current_break())
    ce_task = asyncio.create_task(
        consume_events(playlist_events_consumer, event_handler)
    )
    return [mp_task, ucb_task, ce_task]


@asynccontextmanager
async def lifespan(app: FastAPI):
    tasks = main_tasks()

    yield

    logger.info("Handling stop")

    statuses_done = []
    while True:
        for task in tasks:
            statuses_done.clear()
            if task.done():
                statuses_done.append(True)
                continue
            task.cancel()
            statuses_done.append(False)
        if not all(statuses_done):
            await asyncio.sleep(0.1)
        else:
            break
    logger.debug("The very end of the lifespan")


app = FastAPI(lifespan=lifespan)

if __name__ == "__main__":
    bootstrap_di()
    uvicorn.run("app:app", host="localhost", port=5000)
