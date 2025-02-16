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


class SubTaskFailed(RuntimeError):
    pass


async def manage_playing_with_exc(playing_manager: PlayingManager) -> None:
    try:
        await playing_manager.manage_playing()
    except asyncio.CancelledError as err:
        logger.info("Handling CancelledError")
        playing_manager.handle_playing_immediate_stop()
        raise asyncio.CancelledError from err


async def update_current_break_with_exc(
    break_observer: BreakObserver, playing_manager: PlayingManager
) -> None:
    try:
        await break_observer.update_current_break()
    except asyncio.CancelledError as err:
        logger.info("Handling CancelledError")
        playing_manager.handle_playing_immediate_stop()
        raise asyncio.CancelledError from err


async def consume_events_with_exc(
    events_consumer: EventsConsumer, event_handler: EventHandler
) -> None:
    try:
        await consume_events(events_consumer, event_handler)
    except asyncio.CancelledError as err:
        logger.info("Handling CancelledError")
        raise asyncio.CancelledError from err


async def consume_events(
    events_consumer: EventsConsumer, event_handler: EventHandler
) -> None:
    logger.info("Started consuming and handling events")
    while True:
        events = await events_consumer.consume(1)
        for event in events:
            event_handler.handle_event(event)
        await asyncio.sleep(0.1)


async def main_tasks() -> None:
    playing_manager = di[PlayingManager]
    break_observer = di[BreakObserver]
    playlist_events_consumer = di[PlaylistEventsConsumer]
    event_handler = di[EventHandler]
    try:
        async with asyncio.TaskGroup() as tg:
            mp_task = tg.create_task(manage_playing_with_exc(playing_manager))
            ucb_task = tg.create_task(
                update_current_break_with_exc(break_observer, playing_manager)
            )
            ce_task = tg.create_task(
                consume_events_with_exc(playlist_events_consumer, event_handler)
            )
        tasks_results = [mp_task.result(), ucb_task.result(), ce_task.result()]
        print(f"{tasks_results=}")
    except* RuntimeError as ex:
        logger.error(f"Caught RuntimeError")
        logger.exception(ex)
        raise SubTaskFailed from ex
    except* Exception as ex:
        logger.error(f"Caught Exception")
        raise SubTaskFailed from ex
    except* BaseException as ex:
        logger.error(f"Caught BaseException")
        logger.exception(ex)
        raise SubTaskFailed from ex


@asynccontextmanager
async def lifespan(app: FastAPI):
    main_task = asyncio.create_task(main_tasks())
    try:
        await main_task
    except SubTaskFailed as ex:
        logger.error(f"Handling stop due to exception {ex=}")

    yield
    logger.info("Handling stop")

    # statuses_done = []
    # while True:
    #     for task in tasks:
    #         statuses_done.clear()
    #         if task.done():
    #             statuses_done.append(True)
    #             continue
    #         task.cancel()
    #         statuses_done.append(False)
    #     if not all(statuses_done):
    #         await asyncio.sleep(0.1)
    #     else:
    #         break
    logger.debug("The very end of the lifespan")


app = FastAPI(lifespan=lifespan)

if __name__ == "__main__":
    bootstrap_di()
    uvicorn.run("app:app", host="localhost", port=5000)
