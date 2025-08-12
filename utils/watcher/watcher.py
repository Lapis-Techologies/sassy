from typing import TYPE_CHECKING
from time import time
from asyncio import sleep

from pymongo.results import InsertOneResult

if TYPE_CHECKING:
    from main import Sassy


class Watcher:
    def __init__(self, bot: "Sassy", database_name: str, callback):
        self.bot = bot
        self.database = self.bot.database[database_name]
        self.callback = callback

    async def watch_all_events(self) -> None:
        future_events = self.database.find({
            "finished": {
                "$ne": True
            }
        })

        async for event in future_events:
            self.watch_event(event)

    def watch_event(self, event: dict | InsertOneResult):
        if isinstance(event, InsertOneResult):
            self.bot.loop.create_task(self._watch_inserted_event(event.inserted_id))
            return

        finished = event["finished"]

        if finished:
            return

        self.bot.loop.create_task(
            self.finish_event(event)
        )

    async def finish_event(self, event: dict | InsertOneResult):
        if isinstance(event, InsertOneResult):
            event = await self.database.find_one({"_id": event.inserted_id})

        await sleep(self._time_left(event["end_date"]))
        await self.callback(self.bot, event)
        await self.database.update_one(
            {"_id": event["_id"]}, {"$set": {"finished": True}}
        )

    async def _watch_inserted_event(self, document_id):
        event = await self.database.find_one({"_id": document_id})
        if event and not event["finished"]:
            self.bot.loop.create_task(self.finish_event(event))

    def _time_left(self, end_date) -> int:
        return max(0, end_date - time())
