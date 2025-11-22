from typing import TYPE_CHECKING
from io import BytesIO
from time import time
from asyncio import sleep
from discord.ext import commands
from discord import Message, File, Embed
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

        self.bumping_achievements: dict[dict[str, int | str]] = self.bot.config.get(
            "events", "bumping", "achievement"
        )

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
            await self._bump_achievement(message)
            await self._send_thank_you(message, bump_time)

            self.bot.loop.create_task(self._bump_task(message))
        except Exception as e:
            print(f"[handle_bump] ERROR: {e}")

    async def _bump_achievement(self, message: Message) -> None:
        bumper = await self.user_db.find_one(
            {"uid": message.interaction_metadata.user.id},
            {"bumps": 1, "achievements": 1},
        )
        bumps = bumper["bumps"]
        bumper_achievements = bumper.get("achievements", [])
        new_achievements = []

        sorted_achievements = sorted(
            self.bumping_achievements.items(), key=lambda x: x[1]["amount"]
        )

        for achievement_name, achievement_data in sorted_achievements:
            achievement_amount = achievement_data["amount"]

            if bumps < achievement_amount:
                break
            elif achievement_name in bumper_achievements:
                continue

            new_achievements.append((achievement_name, achievement_data))

        if not new_achievements:
            return
        await self.user_db.update_one(
            {"uid": message.interaction_metadata.user.id},
            {
                "$push": {
                    "achievements": {
                        "$each": [achievement[0] for achievement in new_achievements]
                    }
                }
            },
        )
        embeds = []
        files = []
        for new_achievement in new_achievements:
            name = new_achievement[0]
            data = new_achievement[1]
            with open(f"resources/achievement/bump/{name}.png", "rb") as f:
                files.append(File(f, filename=f"{name}.png"))
            ach_emb = Embed(
                title=name.title(),
                description=f"You earned new achievements, Mate that thing is like a 1 way ticket to the Astral planes, but it feels like you got 2. Nice you bumped the hangout **{data['amount']}** times!",
            )
            ach_emb.set_image(url=data["source"])
            embeds.append(ach_emb)

        await message.channel.send(
            message.interaction_metadata.user.mention, embeds=embeds
        )

    async def _bump_task(self, message: Message) -> None:
        try:
            bump_info = await self.meta.find_one({"id": "bump_tracker"})
            bump_time = float(bump_info["bump_time"])
            time_left = bump_time - time()

            if time_left > 0:
                await sleep(time_left)

            await message.channel.send(
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
            files=[self._get_gif(True)],
        )

    def _get_gif(self, yis: bool = False) -> File:
        if yis:
            with open("resources/oh-yis.gif", "rb") as f:
                return File(fp=BytesIO(f.read()), filename="oh-yis.gif")

        with open("./resources/you-fucken-druggah.gif", "rb") as f:
            return File(fp=BytesIO(f.read()), filename="you-fucken-druggah.gif")


async def setup(bot):
    await bot.add_cog(Bump(bot))
