import os
import sys
import asyncio
import pathlib
import discord
from subprocess import check_output
from discord import Activity
from discord.enums import ActivityType
from discord.ext import commands
from pymongo import AsyncMongoClient
from config import botconfig
from repl import REPL
from utils.tasks import poll_watcher


class Sassy(commands.Bot):
    """
    Sassy the Sasquatch discord bot!!!!
    """

    def __init__(
        self,
        bot_config,
        database,
        verbose: bool = False,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.database = database
        self.verbose = verbose
        self.IGNORE_COMMANDS = []
        self.config: botconfig.BotConfig = bot_config
        self.version = get_version()
        self.repl = REPL(self)
        self.remove_command("help")

    def reload_config(self) -> None:
        self.config.set_config("config.json")

    async def on_ready(self):
        await self.load_cogs()
        guild = self.get_guild(int(self.config.get("guild", "id")))
        if guild is None:
            print("Cannot find guild! Check your config file!")
            sys.exit(1)
        self.tree.copy_global_to(
            guild=guild
        )  # https://stackoverflow.com/a/75236448/19119462
        synced = len(await self.tree.sync(guild=guild))
        print(f"Synced {synced} commands!")

        if self.user is None:
            print("Unable to login in!")
            sys.exit(1)

        print(f"Logged in as {self.user.name} ({self.user.id})")

        await self._get_polls()

        await self.change_presence(
            status=None,
            activity=Activity(
                type=ActivityType.listening, name=f"Now Version {self.version}!"
            ),
        )

        print(f"Now version {self.version} 🎉")
        await self.loop.create_task(self.repl.run())

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

    async def _get_polls(self):
        try:
            polls_db = self.database["polls"]
            polls = polls_db.find({"finished": {"$ne": True}})
            async for poll in polls:
                poll_id = poll["id"]
                await poll_watcher.watch_poll(self, poll_id)
        except Exception as e:
            print(e)


def get_version() -> str:
    return str(check_output(["python", "bumper.py", "-q"]).strip(), encoding="utf-8")


async def main() -> None:
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
    )
    try:
        await bot.start(token)
    finally:
        await bot.close()


if __name__ == "__main__":
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    loop.run_until_complete(main())
    loop.close()

    sys.exit(0)
