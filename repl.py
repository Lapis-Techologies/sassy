from typing import TYPE_CHECKING
from asyncio import to_thread


if TYPE_CHECKING:
    from main import Sassy


class REPL:
    def __init__(self, bot: "Sassy") -> None:
        self.bot = bot
        self.running = False

    def help(self) -> None:
        print("help - Shows this message")
        print("refresh - Refreshes the config")
        print("shutdown - Safely Shutdown the bot")

    def refresh(self) -> None:
        old_keys = set(self.bot.config.config.keys())
        self.bot.config.set_config("config.json")
        new_keys = set(self.bot.config.config.keys())

        additions = new_keys - old_keys
        subtractions = old_keys - new_keys

        print("Config Refreshed!")
        print(f"{len(additions)} new additions!")
        print(f"{len(subtractions)} new subtractions!")

    def reset(self) -> None:
        self.running = False

    async def ainput(self, string: str) -> str:
        return await to_thread(input, string)

    async def run(self) -> None:
        self.running = True
        should_send_welcome = True

        while self.running:
            if should_send_welcome:
                print("Welcome to Sassy's Terminal! Use `help` to learn the commands.")
                should_send_welcome = False
            command = await self.ainput("Admin> ")

            if command == "help":
                self.help()
            elif command == "refresh":
                self.refresh()
            elif command == "shutdown":
                await self.bot.close()
                self.reset()
