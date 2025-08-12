from typing import TYPE_CHECKING
from io import BytesIO
from time import time
from asyncio import sleep
from discord.ext import commands
from discord import Message, File, Embed, TextChannel
from cogs.xp.IGNORE_score import calculate_score


if TYPE_CHECKING:
    from main import Sassy


class Bump(commands.Cog):
    def __init__(self, bot: "Sassy"):
        self.bot = bot
        self.meta = self.bot.database["meta"]
        self.user_db = self.bot.database["user"]

        self.level_multiplier = float(self.bot.config.get("xp", "multipliers", "level"))
        self.choomah_coin_multiplier = float(
            self.bot.config.get("xp", "multipliers", "choomah_coins")
        )
        self.bumps_multiplier = float(self.bot.config.get("xp", "multipliers", "bumps"))

        self.bump_bot_id = int(self.bot.config.get("guild", "channels", "bump", "bot"))

    @commands.Cog.listener()
    async def on_message(self, message: Message) -> None:
        if message.interaction_metadata and (message.author.id == self.bump_bot_id):
            await self.handle_bump(message)

    async def handle_bump(self, message: Message) -> None:
        try:
            if not await self._is_valid_bump_message(message):
                return

            await self.user_db.update_one(
                {"uid": message.interaction_metadata.user.id}, {"$inc": {"bumps": 1}}
            )

            bump_time = await self._store_next_bump_time()

            await self._send_thank_you(message, bump_time)

            self.bot.loop.create_task(self._bump_task(message.channel, message))
        except Exception as e:
            print(f"[handle_bump] ERROR: {e}")

    async def _bump_task(self, channel: TextChannel, message: Message) -> None:
        try:
            bump_info = await self.meta.find_one({"id": "bump_tracker"})
            bump_time = float(bump_info["bump_time"])
            time_left = bump_time - time()

            if time_left > 0:
                await sleep(time_left)

            await channel.send(
                f"{message.interaction_metadata.user.mention} Time to bump you fucken druggah",
                files=[self._get_gif()],
            )
        except Exception as e:
            print(f"[Bump Task Error] {e}")

    async def _is_valid_bump_message(self, message: Message) -> bool:
        await sleep(1)  # Let embed load
        channel = message.channel

        expected_channel = self.bot.config.get("guild", "channels", "bump", "id")
        if channel.id != expected_channel:
            return False

        if not message.embeds or len(message.embeds) != 1:
            return False

        embed = message.embeds[0]
        if not embed.description or "Bump done!" not in embed.description:
            return False

        return True

    async def _store_next_bump_time(self) -> float:
        bump_time = time() + (10 if self.bot.config.get("database", "dev") else 7200)
        await self.meta.update_one(
            {"id": "bump_tracker"}, {"$set": {"bump_time": bump_time}}, upsert=True
        )
        return bump_time

    async def _send_thank_you(self, message: Message, bump_time: float) -> None:
        timestamp_one = f"<t:{int(bump_time)}:f>"
        timestamp_relative = f"<t:{int(bump_time)}:R>"

        uid = message.interaction_metadata.user.id
        user_data = await self.user_db.find_one({"uid": uid})
        bumps = user_data["bumps"]
        coins = user_data["choomah_coins"]
        level = user_data["level"]

        score = calculate_score(
            level,
            coins,
            bumps,
            self.level_multiplier,
            self.choomah_coin_multiplier,
            self.bumps_multiplier,
        )

        embed = Embed(
            title="Thanks For Bumping!", description="Fuk yeh mate", color=0x33FF99
        )
        embed.add_field(name="Bumps", value=f"You have bumped **{bumps}** times!")
        embed.add_field(
            name="Score",
            value=f"You have a new score of **{score}**! Use /leaderboard to see your ranking!",
        )

        await message.channel.send(
            f"I will remind you to bump again {message.interaction_metadata.user.mention} at {timestamp_one} ({timestamp_relative}).",
            embed=embed,
            files=[self._get_gif()],
        )

    def _get_gif(self) -> File:
        with open("./resources/you-fucken-druggah.gif", "rb") as f:
            return File(fp=BytesIO(f.read()), filename="you-fucken-druggah.gif")


async def setup(bot):
    await bot.add_cog(Bump(bot))
