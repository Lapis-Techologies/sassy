from typing import TYPE_CHECKING
from random import randint
from time import time
from utils.adduser import add
from discord import Message, Member, Embed
from discord.ext.commands import Cog


if TYPE_CHECKING:
    from main import Sassy


class XPHandler(Cog):
    def __init__(self, bot: "Sassy"):
        self.bot = bot
        self.user_db = self.bot.database["user"]
        self.rewards = sorted(
            [
                (int(level), role)
                for level, role in self.bot.config.get("xp", "rewards").items()
            ],
            key=lambda x: x[0],
        )

    @staticmethod
    def calculate_xp(level: int) -> int:
        return (100 + (level - 1) * 50) * 2

    @staticmethod
    def calculate_progress(current_xp: int, xp_needed: int) -> int:
        return min(10, int(1 + (current_xp * 10) / xp_needed))

    @staticmethod
    def make_bar(progress: int) -> str:
        bar = "ERROR CALCULATING PROGRESS"
        if progress == 10:
            bar = "🟩" * 10
        elif progress == 9:
            bar = "🟩" * 9 + "🟨"
        elif progress <= 8:
            bar = "🟩" * (progress - 1) + "🟨🟨" + "🟥" * ((10 - progress) - 1)

        return bar

    @staticmethod
    def cooldown(last_message_time: int | float) -> tuple[bool, float]:
        current_time = time()
        if current_time - last_message_time < 8:
            return True, last_message_time
        else:
            return False, current_time

    def add_xp(self, xp: int, level: int) -> tuple[int, int]:
        xp_needed = self.calculate_xp(level)

        new_xp = xp + randint(5, 12)

        if new_xp >= xp_needed:
            left_over = new_xp - xp_needed
            level += 1

            return left_over, level
        return new_xp, level

    async def try_level_up(
        self,
        level: int,
        level_new: int,
        xp: int,
        xp_new: int,
        message: Message,
        last_message_time: float,
    ) -> None:
        if level_new > level:
            xp_needed = self.calculate_xp(level_new)
            progress = self.calculate_progress(xp_new, xp_needed)

            await self.update_member(message.author, xp, level_new, last_message_time)

            bar = self.make_bar(progress)

            embed = Embed(
                title="Level Up!",
                description=f"Congratulations you fuckin druggo, you're level __**{level_new}**__!",
                color=message.author.color or 0x92A0FF,
            )
            embed.add_field(
                name="Xp Progress",
                value=f"**{xp_new}** ▶ {bar} ◀ **{xp_needed}**",
            )
            embed.set_footer(text="yeeeeebrah")

            await message.channel.send(message.author.mention, embed=embed)

    async def update_member(
        self, member: Member, xp: int, level_new: int, last_message_time: float
    ) -> None:
        await self.user_db.update_one(
            {"uid": member.id},
            {"$set": {"xp": xp, "level": level_new, "last_message": last_message_time}},
        )

        roles_to_add = [
            role
            for level, role in self.rewards
            if level <= level_new and role not in member.roles
        ]

        if roles_to_add:
            await member.add_roles(*roles_to_add)

    @Cog.listener()
    async def on_message(self, message: Message):
        if message.author.bot:
            return

        curs = await self.user_db.find_one(
            {"uid": message.author.id},
            projection={"xp": 1, "level": 1, "last_message": 1},
        )

        if curs is None and message.guild.id == self.bot.config.get("guild", "id"):
            await add(self.bot, message.author)
            return

        last_message = curs["last_message"]

        should_wait, last_message_time = self.cooldown(last_message)

        if should_wait:
            return

        xp = curs["xp"]
        level = curs["level"]

        xp_new, level_new = self.add_xp(xp, level)

        await self.user_db.update_one(
            {"uid": message.author.id},
            {
                "$set": {
                    "xp": xp_new,
                    "level": level_new,
                    "last_message": last_message_time,
                }
            },
        )

        await self.try_level_up(
            level, level_new, xp, xp_new, message, last_message_time
        )


async def setup(bot):
    await bot.add_cog(XPHandler(bot))
