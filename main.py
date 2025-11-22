import os
import sys
import asyncio
import pathlib
import discord
from time import time
from datetime import datetime
from subprocess import check_output
from discord import Activity, Embed
from discord.enums import ActivityType
from discord.ext import commands
from pymongo import AsyncMongoClient
from config import botconfig
from schedules.schedule import Schedule
from schedules.callbacks.poll import callback as poll_callback
from schedules.callbacks.giveaway import callback as giveaway_callback


class Sassy(commands.Bot):
    """
    Sassy the Sasquatch discord bot!!!!
    """

    def __init__(
        self,
        bot_config,
        database,
        startup_time: int,
        verbose: bool = False,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.database = database
        self.verbose = verbose
        self.IGNORE_COMMANDS = []
        self.guild = None
        self.config: botconfig.BotConfig = bot_config
        self.version = get_version()
        self.remove_command("help")
        self._booted = False
        self.startup_time = startup_time
        self.giveaway_watcher = Schedule(self, "giveaways", giveaway_callback)
        self.poll_watcher = Schedule(self, "polls", poll_callback)

    def reload_config(self) -> None:
        self.config.set_config("config.json")

    async def on_connect(self):
        tasks = [
            {"Poll Catchup": self.poll_watcher.watch_all_events},
            {"Giveaway Catchup": self.giveaway_watcher.watch_all_events},
        ]

        print(f"Running {len(tasks)} Task(s)")
        for task in tasks:
            for task_name, task_function in task.items():
                print(f"  > Running {task_name}")
                await task_function()

        await self.load_cogs()
        guild_id = int(self.config.get("guild", "id"))
        guild = self.get_guild(guild_id)

        if guild is None:
            await asyncio.sleep(1)
            guild = self.get_guild(guild_id)
        if guild is None:
            print("Cannot find guild! Check your config file!")
            return

        self.guild = guild

        self.tree.copy_global_to(guild=guild)
        synced = len(await self.tree.sync(guild=guild))
        print(f"Synced {synced} commands!")

    async def on_ready(self):
        # Prevent double syncing
        # https://github.com/Rapptz/discord.py/discussions/7884
        if self._booted:
            return
        self._booted = True

        if self.user is None:
            print("Unable to login in!")
            sys.exit(1)

        print(f"Logged in as {self.user.name} ({self.user.id})")

        await self.change_presence(
            status=None,
            activity=Activity(
                type=ActivityType.listening, name=f"Now Version {self.version}!"
            ),
        )
        finish_time = time()
        elapsed = finish_time - self.startup_time
        print(f"Launched in {elapsed:.2f} seconds.")
        print(f"Now version {self.version} 🎉")
        await self.ping_server()

    async def load_cogs(self):
        if not pathlib.Path.exists(pathlib.Path("./cogs")):
            raise OSError("You need a cogs folder!")

        cogs = pathlib.Path(os.getcwd()).joinpath("cogs")

        if cogs.is_file():
            raise OSError("'cogs' should be a folder/directory, not a file!")

        print(f"{'=' * 10} COGS {'=' * 10}")
        await self._process_folder(cogs, "cogs")
        print("=" * 26)

    async def _process_folder(self, path: pathlib.Path, path_start: str):
        banned = "__pycache__"

        for item in path.iterdir():
            if item.name in banned:
                continue
            elif item.name.startswith("IGNORE_"):
                continue
            elif item.is_dir():
                if item.stem == "dev" and not bool(self.config.get("database", "dev")):
                    continue
                await self._process_folder(item, f"{path_start}.{item.name}")
            elif item.is_file() and item.suffix == ".py":
                if item.name in self.IGNORE_COMMANDS:
                    continue

                module = f"{path_start}.{item.stem}"

                try:
                    await self.load_extension(module)
                    print(f"Loaded {module}")
                except Exception as e:
                    print(
                        f"Failed to load {module} with error: {e}"
                    ) if self.verbose else None

    async def ping_server(self) -> None:
        log_id = int(self.config.get("guild", "channels", "logs"))
        log_channel = await self.fetch_channel(log_id)
        epoch = int(time())
        embed = Embed(title="Launch", description=f"Launched at <t:{epoch}:F>.")
        embed.add_field(name="Information", value=f"Commands: `{len(self.tree.get_commands(guild=None, type=None))}`\nID: `{self.user.id}`\nUsers: `{self.guild.member_count}`\nOwner: `{self.guild.owner}`")
        await log_channel.send(embed=embed)


def get_version() -> str:
    return str(
        check_output(["python", "devtools/bumper.py", "-q"]).strip(), encoding="utf-8"
    )


async def main(start_time) -> None:
    bot_config = botconfig.BotConfig()
    bot_config.set_config("config.json")

    intents = discord.Intents.all()
    token = bot_config.get("bot", "token")
    prefix = bot_config.get("bot", "prefix")

    is_dev = bot_config.get("database", "dev")
    branch = "dev" if is_dev else "prod"

    url = bot_config.get("database", "url")
    name = bot_config.get("database", "name")

    mongo_client = AsyncMongoClient(url)
    collection_name = f"{name}-{branch}"
    database = mongo_client[collection_name]

    args = sys.argv

    verbose = args[-1] in ("-v", "--verbose")

    bot = Sassy(
        command_prefix=prefix,
        intents=intents,
        bot_config=bot_config,
        database=database,
        verbose=verbose,
        startup_time=start_time,
    )
    try:
        await bot.start(token)
    finally:
        await bot.close()


def _calculate_time(start: float, end: float) -> tuple[float, float, float]:
    elapsed = end - start
    minutes, seconds = divmod(elapsed, 60)
    hours, minutes = divmod(minutes, 60)
    return seconds, minutes, hours


if __name__ == "__main__":
    start_time = time()
    loop = None
    try:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        loop.run_until_complete(main(start_time))
    except KeyboardInterrupt:
        end_time = time()
        seconds, minutes, hours = _calculate_time(start_time, end_time)
        print(f"Goodbye, ran for {hours:.0f} hours, {minutes:.0f} minutes and {seconds:.2f} seconds.")
    finally:
        if loop is None:
            sys.exit(1)

        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()

    sys.exit(0)
