import os
import pathlib
import json
import discord
from discord.ext import commands
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient


class Sassy(commands.Bot):
    """
    Sassy the Sasquatch discord bot!!!!
    """
    def __init__(self, config: json, user_db, economy_db, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = config
        self.user_db = user_db
        self.economy_db = economy_db
        self.remove_command("help")
        self.version = "1.6"  # TODO: Add Bot Debug Command
        # TODO: Add load, unload, and refresh command

    async def on_ready(self):
        await self.process_config(self.config)
        await self.load_cogs()

        synced = len(await self.tree.sync())
        print(f"Synced {synced} commands!")

    async def process_config(self, config: json):
        guild = config.get("guild")
        xp = config.get("xp")
        self.config = {}

        if guild is None:
            raise KeyError("You need to provide a guild in the config.json file!")
        elif xp is None:
            raise KeyError("You need to provide an xp field in the config.json file!")

        guild_id = guild.get("id")
        guild_roles = guild.get("roles")
        guild_channels = guild.get("channels")
        rewards = xp["rewards"]

        if guild_id is None:
            raise KeyError("You need to provide a guild id in the config.json file!")
        elif guild_roles is None:
            raise KeyError("You need to provide guild roles in the config.json file!")
        elif guild_channels is None:
            raise KeyError("You need to provide guild channels in the config.json file!")
        elif rewards is None:
            raise KeyError("You need to provide xp rewards in the config.json file!")

        self.config["guild"] = self.get_guild(guild_id)
        self.config["channels"] = {}
        self.config["roles"] = {}
        self.config["xp"] = {"rewards": {}}

        for level, reward in rewards.items():
            self.config["xp"]["rewards"][level] = self.config["guild"].get_role(reward)

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
                if item.name.startswith("IGNORE_"):
                    continue
                await self._process_folder(item, f"{path_start}.{item.name}")
            elif item.is_file() and item.suffix == ".py":
                if item.name.split('.')[0].startswith("IGNORE_"):
                    continue
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
    mongo = os.getenv("mongo")

    mongo = AsyncIOMotorClient(mongo)
    collection_name = os.getenv("db") + f"-{branch}"
    db = mongo[collection_name]
    user_db = db["user"]
    economy_db = db["economy"]

    bot = Sassy(command_prefix=config["prefix"], intents=intents, config=config, user_db=user_db, economy_db=economy_db)
    bot.run(os.getenv("TOKEN"))


if __name__ == '__main__':
    main()
