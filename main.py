import os
import pathlib
import json
import discord
from discord.ext import commands
from motor.motor_asyncio import AsyncIOMotorClient


class Sassy(commands.Bot):
    """
    Sassy the Sasquatch discord bot!!!!
    """
    def __init__(self, config: dict, user_db, economy_db, starboard_db,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = config
        self.user_db = user_db
        self.economy_db = economy_db
        self.starboard_db = starboard_db
        self.remove_command("help")
        self.version = "1.6.7"

    async def on_ready(self):
        await self.process_config(self.config)
        await self.load_cogs()

        synced = len(await self.tree.sync())
        print(f"Synced {synced} commands!")
    
    async def verify_keys(self, guild_id, guild_roles, guild_channels, rewards):
        checks = {
            0: {
                "failed": False,
                "message": "guild id"
            },
            1: {
                "failed": False,
                "message": "guild roles"
            },
            2: {
                "failed": False,
                "message": "guild channels"
            },
            3: {
                "failed": False,
                "message": "xp rewards"
            }
        }
        message = "You need to provide a %s in the config.json file!"

        if guild_id is None:
            checks[0]["failed"] = True
        elif guild_roles is None:
            checks[1]["failed"] = True
        elif guild_channels is None:
            checks[2]["failed"] = True
        elif rewards is None:
            checks[3]["failed"] = True
        
        needed = []
        
        for _, results in checks.items():
            failed = results["failed"]
            if failed:
                needed.append(results["message"])
        
        if len(needed) != 0:
            raise KeyError(message % ', '.join(needed))
    
    async def verify_guild(self, guild, xp):
        if guild is None:
            raise KeyError("You need to provide a guild in the config.json file!")
        elif xp is None:
            raise KeyError("You need to provide an xp field in the config.json file!")

    async def verify_config(self, rewards, guild_roles, guild_channels):
        if self.config["guild"] == None:
            raise commands.GuildNotFound(f"Could not find guild with id {self.config["guild"]}")

        for level, reward in rewards.items():
            self.config["xp"]["rewards"][level] = self.config["guild"].get_role(reward)

        for role in guild_roles:
            self.config["roles"][role] = self.config["guild"].get_role(guild_roles[role])

        for channel in guild_channels:
            self.config["channels"][channel] = self.config["guild"].get_channel(guild_channels[channel])

    async def process_config(self, config: dict):
        guild = config.get("guild")
        xp = config.get("xp")
        self.config = {}

        await self.verify_guild(guild, xp)

        guild_id = guild.get("id", None)
        guild_roles = guild.get("roles", None)
        guild_channels = guild.get("channels", None)
        rewards = xp.get("rewards", None)

        await self.verify_keys(guild_id, guild_roles, guild_channels, rewards)

        self.config["guild"] = self.get_guild(guild_id)
        self.config["channels"] = {}
        self.config["roles"] = {}
        self.config["xp"] = {"rewards": {}}

        await self.verify_config(rewards, guild_roles, guild_channels)

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
                if item.name.startswith("IGNORE_"):
                    continue
                
                module = f"{path_start}.{item.stem}"
                try:
                    await self.load_extension(module)
                    print(f"Loaded {module}")
                except Exception as e:
                    print(f"Failed to load {module} with error: {e}")


def load_config():
    with open("config.json", "r") as f:
        config = json.load(f)

    intents = discord.Intents.all()

    is_dev = config["database"]["dev"]
    branch = "dev" if is_dev else "prod"
    url = config["database"]["url"]

    mongo = AsyncIOMotorClient(url)
    collection_name = config["database"]["name"] + f"-{branch}"
    db = mongo[collection_name]
    user_db = db["user"]
    economy_db = db["economy"]
    starboard_db = db["starboard"]

    token = config["bot"]["token"]

    return {
        "token": token,
        "user_db": user_db,
        "economy_db": economy_db,
        "starboard_db": starboard_db,
        "config": config,
        "intents": intents,
        "prefix": config["bot"]["prefix"]
    }

def main() -> None:
    config = load_config()

    TOKEN = config["token"]
    
    prefix = config["prefix"]
    user_db = config["user_db"]
    economy_db = config["economy_db"]
    starboard_db = config["starboard_db"]
    intents = config["intents"]
    config = config["config"]

    bot = Sassy(command_prefix=prefix, intents=intents, config=config, user_db=user_db, economy_db=economy_db, starboard_db=starboard_db)
    bot.run(TOKEN)


if __name__ == '__main__':
    main()
