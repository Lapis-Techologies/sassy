import os
import pathlib
import json
import discord
from discord.ext import commands
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase


class Sassy(commands.Bot):
    """
    Sassy the Sasquatch discord bot!!!!
    """
    def __init__(self, config: json, db, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = config
        self.db: AsyncIOMotorDatabase = db
        self.remove_command("help")

    async def on_ready(self):
        await self.process_config(self.config)
        await self.load_cogs()

        synced = len(await self.tree.sync())
        print(f"Synced {synced} commands!")

    async def process_config(self, config: json):
        guild = config.get("guild")
        self.config = {}

        if guild is None:
            raise KeyError("You need to provide a guild in the config.json file!")

        guild_id = guild.get("id")
        guild_roles = guild.get("roles")
        guild_channels = guild.get("channels")

        if guild_id is None:
            raise KeyError("You need to provide a guild id in the config.json file!")
        elif guild_roles is None:
            raise KeyError("You need to provide guild roles in the config.json file!")
        elif guild_channels is None:
            raise KeyError("You need to provide guild channels in the config.json file!")

        self.config["guild"] = self.get_guild(guild_id)
        self.config["channels"] = {}
        self.config["roles"] = {}

        for role in guild_roles:
            self.config["roles"][role] = self.config["guild"].get_role(guild_roles[role])

        for channel in guild_channels:
            self.config["channels"][channel] = self.config["guild"].get_channel(guild_channels[channel])

    async def load_cogs(self):
        if not os.path.exists("./cogs"):
            raise OSError("You need a cogs folder!")

        cogs = pathlib.Path(os.path.join(os.getcwd(), "cogs"))

        if cogs.is_file():
            raise OSError("'cogs' should be a folder/directory, not a file!")

        await self._process_folder(cogs, 'cogs')

    async def _process_folder(self, path: pathlib.Path, path_start: str):
        banned = (
            '__pycache__'
        )

        for item in path.iterdir():
            if item.name in banned:
                continue

            if item.is_dir():
                await self._process_folder(item, f"{path_start}.{item.name}")
            elif item.is_file() and item.suffix == ".py":
                module = f"{path_start}.{item.stem}"
                try:
                    await self.load_extension(module)
                    print(f"Loaded {module}")
                except Exception as e:
                    print(f"Failed to load {module} with error: {e}")


def main() -> None:
    load_dotenv()

    with open("config.json", "r") as f:
        config = json.load(f)

    intents = discord.Intents.all()

    is_dev = os.getenv("DEV")
    branch = "dev" if is_dev else "prod"

    mongo = AsyncIOMotorClient(os.getenv("mongo"))
    db = mongo[os.getenv("db")]
    collection = db[branch]

    bot = Sassy(command_prefix=config["prefix"], intents=intents, config=config, db=collection)
    bot.run(os.getenv("TOKEN"))


if __name__ == '__main__':
    main()
