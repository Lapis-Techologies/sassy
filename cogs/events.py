import traceback
import pathlib
import discord
from time import time
from random import randint
from typing import TYPE_CHECKING
from discord.abc import PrivateChannel
from discord.utils import get
from discord.ext import commands
from discord import CategoryChannel, ForumChannel, RawReactionActionEvent, app_commands, Interaction, Embed
from utils.adduser import add
from utils.log import log


if TYPE_CHECKING:
    from main import Sassy


class Events(commands.Cog):
    def __init__(self, bot: "Sassy"):
        self.bot = bot
        self._old_tree_error = None
    
    async def handle_xp(self, message: discord.Message):
        curs = await self.bot.user_db.find_one({"uid": message.author.id}, projection={"xp": 1, "level": 1, "last_message": 1})

        if curs is None:
            await add(self.bot, message.author)
            
        if not isinstance(message.author, discord.Member):
            return

        last_message = curs["last_message"]

        if time() > last_message:
            last_message = time() + 8   # +8 seconds
        else:
            return

        xp = curs["xp"]
        xp += randint(5, 12)

        level = curs["level"]
        xp_needed = (100 + (level - 1) * 50) * 2

        if xp >= xp_needed:
            level += 1
            xp -= xp_needed
            xp_needed = (100 + (level - 1) * 50) * 2

            progress = min(10, int(1 + (xp * 10) / xp_needed))

            bar = "ERROR CALCULATING PROGRESS"
            if progress == 10:
                bar = "🟩" * 10
            elif progress == 9:
                bar = "🟩" * 9 + "🟨"
            elif progress <= 8:
                bar = "🟩" * progress + "🟨" + "🟥" * ((10 - progress) - 1)

            embed = Embed(title="Level Up!", description=f"Holy shit mate you leveled up to level **{level}**",
                          color=0x00FF00)

            embed.add_field(name="XP Progress", value=f"**{xp}** > {bar} < **{xp_needed}**")

            await message.channel.send(f"{message.author.mention}", embed=embed)

            for lvl, reward in self.bot.config["xp"]["rewards"].items():
                if level == int(lvl):
                    # User has earned a new reward!
                    await message.author.add_roles(reward)

        await self.bot.user_db.update_one({"uid": message.author.id}, {
            "$set": {
                "xp": xp,
                "level": level,
                "last_message": last_message
            }
        })

    async def handle_error(self, inter: Interaction, error: app_commands.AppCommandError) -> tuple[str, str, str, str | None, str]:
        if inter.command is None:
            raise Exception("")
        error = getattr(error, "original", error)
        tb = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
        final_tb = tb.split("File")[-1]
        sections = final_tb.split(",")
        file_dir = sections[0].strip().replace('"', '')

        file_name = pathlib.Path(file_dir).name
        line = sections[1].strip().split(' ')[1]

        command = inter.command.name

        if isinstance(inter.command, app_commands.ContextMenu):
            params = "None"
        else:
            params = ', '.join([f"{param['name']}={param['value']}" for param in inter.data["options"]])
        
        return file_name, line, command, params, tb

    def cog_load(self):
        tree = self.bot.tree
        self._old_tree_error = tree.on_error
        tree.on_error = self.on_slash_error

    def cog_unload(self):
        tree = self.bot.tree
        tree.on_error = self._old_tree_error

    async def on_slash_error(self, inter: Interaction, error: app_commands.AppCommandError):    # noqa
        if isinstance(error, app_commands.CommandNotFound):
            await inter.response.send_message("Command not found!")

        elif isinstance(error, app_commands.CommandOnCooldown):
            time_left = int(error.cooldown.get_retry_after())
            length = int(time()) + time_left
            formatted_time = f"<t:{length}:R>"

            await inter.response.send_message(f"Command is on cooldown! (Ends {formatted_time})")

        elif isinstance(error, app_commands.CheckFailure):
            await inter.response.send_message("You do not have permission to use this command!")
        else:
            file_name, line, command, params, tb = await self.handle_error(inter, error)

            message = f"Uhh I may be high but I think I ran into an error.\n```File: {file_name}\nLine: {line}\nCommand: {command}\nParameters: {params}\n\n{tb}```"

            await inter.response.send_message(message, ephemeral=True)
    
    async def process_starboard(self, starboard, message, embed):
        curs = await self.bot.starboard_db.find_one({"uid": message.id}, projection={"uid": 1, "saved_message": 1})

        if curs is None:
            sent_message = await self.bot.config["channels"]["starboard"].send(embed=embed, files=[await at.to_file() for at in message.attachments])
            starboard["saved_message"] = sent_message.id

            await self.bot.starboard_db.insert_one(starboard)
        else:
            sent_message = await self.bot.config["channels"]["starboard"].fetch_message(curs["saved_message"])
            if sent_message is None:
                return
            
            await sent_message.edit(embed=embed)
            await self.bot.starboard_db.update_one({"uid": message.id}, {"$set": starboard})

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        await self.bot.config["channels"]["welcome"].send(f"{member.mention} Whats goin on mate? You're druggo #{len(member.guild.members)}, fuckin skits mate")

        await add(bot=self.bot, member=member)
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        
        await self.handle_xp(message)


    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.author.bot:
            return

        await log(self.bot, None, "edit", fields=[
            {"name": "User", "value": f"{before.author.mention} (`{before.author.id}`)", "inline": False},
            {"name": "Before", "value": f"```{before.content}```", "inline": False},
            {"name": "After", "value": f"```{after.content}```", "inline": False},
            {"name": "Jump Link", "value": after.jump_url, "inline": False}
        ])

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.author.bot:
            return

        if isinstance(message.channel, (discord.DMChannel, discord.GroupChannel)):
            return

        await log(self.bot, None, "delete", fields=[
            {"name": "User", "value": f"{message.author.mention} (`{message.author.id}`)", "inline": False},
            {"name": "Content", "value": f"```{message.content}```", "inline": False},
            {"name": "Channel", "value": f"{message.jump_url}", "inline": False},
        ])
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: RawReactionActionEvent):
        if payload.emoji.name != "⭐":
            return
        
        channel = self.bot.get_channel(payload.channel_id)
        if isinstance(channel, (ForumChannel, CategoryChannel, PrivateChannel)):
            return
        elif channel is None:
            return

        message = await channel.fetch_message(payload.message_id)
        if message is None:
            return
        
        reaction = get(message.reactions, emoji=payload.emoji.name)
        if reaction is None:
            return
        
        curs = await self.bot.user_db.find_one({"uid": message.author.id}, projection={"uid": 1})

        if curs is None:
            await add(self.bot, message.author)
        
        starboard = {
            "uid": message.id,
            "channel": channel.id,
            "author": message.author.id,
            "message": {
                "id": message.id,
                "content": message.content,
                "attachments": [
                    attachment.url for attachment in message.attachments
                ],
                "reactions": reaction.count
            }
        }

        if message.author.avatar is None:
            return

        embed = Embed(title=message.author.display_name, description=message.content)
        embed.add_field(name="Jump", value=message.jump_url)
        embed.set_thumbnail(url=message.author.avatar.url or message.author.default_avatar.url)
        embed.set_footer(text=f"{"⭐" * reaction.count if reaction.count < 8 else f"⭐x{reaction.count}"}")

        await self.process_starboard(starboard, message, embed)



async def setup(bot):
    await bot.add_cog(Events(bot))
