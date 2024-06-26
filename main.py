import os
import asyncio
import pathlib
import discord
from discord.ext import commands
from motor.motor_asyncio import AsyncIOMotorClient
from utils import configloader


__VERSION__ = "1.7.2"

class Sassy(commands.Bot):
    """
    Sassy the Sasquatch discord bot!!!!
    """
    def __init__(self, bot_config, user_db, economy_db, starboard_db,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_db = user_db
        self.economy_db = economy_db
        self.starboard_db = starboard_db
        self.version = __VERSION__
        
        # normally this wouldnt be something we would want public, but in this case we will use it to help manage config accessing
        self.config: configloader.BotConfig = bot_config
        self.remove_command("help")

    async def on_ready(self):
        await self.load_cogs()

        print(await self.config.config)

        synced = len(await self.tree.sync())
        print(f"Synced {synced} commands!")
        
        print(f"Logged in as {self.user.name} ({self.user.id})") if self.user else None

    async def load_cogs(self):
        if not os.path.exists("./cogs"):
            raise OSError("You need a cogs folder!")

        cogs = pathlib.Path(os.path.join(os.getcwd(), "cogs"))

        if cogs.is_file():
            raise OSError("'cogs' should be a folder/directory, not a file!")

        print(f"{"=" * 10} COGS {"=" * 10}")
        await self._process_folder(cogs, 'cogs')
        print("=" * 26)

    async def _process_folder(self, path: pathlib.Path, path_start: str):
        banned = (
            '__pycache__'
        )

        for item in path.iterdir():
            if item.name in banned:
                continue
            
            if item.name.startswith("IGNORE_"):
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


async def main() -> None:
    bot_config = configloader.BotConfig()
    await bot_config.set_config("config.json")

    intents = discord.Intents.all()
    token = await bot_config.get("bot", "token")
    prefix = await bot_config.get("bot", "prefix")
    
    is_dev = await bot_config.get("database", "dev")
    branch = "dev" if is_dev else "prod"

    url = await bot_config.get("database", "url")
    name = await bot_config.get("database", "name")

    mongo_client = AsyncIOMotorClient(url)
    collection_name = f"{name}-{branch}"
    database = mongo_client[collection_name]
    user_db = database["user"]
    economy_db = database["economy"]
    starboard_db = database["starboard"]

    bot = Sassy(command_prefix=prefix, intents=intents, bot_config=bot_config, user_db=user_db, economy_db=economy_db, starboard_db=starboard_db)
    await bot.start(token)
    await bot.close()


if __name__ == '__main__':
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    loop.run_until_complete(main())