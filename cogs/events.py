import traceback
import pathlib
import discord
from time import time
from typing import TYPE_CHECKING
from asyncio import sleep
from discord.ext import commands
from discord import app_commands, Interaction
from utils.dpaste import upload
from utils.adduser import add
from utils.log import log, Importancy, LogType


if TYPE_CHECKING:
    from main import Sassy


class Events(commands.Cog):
    def __init__(self, bot: "Sassy"):
        self.bot = bot
        self._old_tree_error = None

    def cog_load(self):
        tree = self.bot.tree
        self._old_tree_error = tree.on_error
        tree.on_error = self.on_slash_error

    def cog_unload(self):
        tree = self.bot.tree
        tree.on_error = self._old_tree_error

    async def handle_error(self, inter: Interaction, error: app_commands.AppCommandError) -> tuple[str, str, str, str | None, str]:
        if inter.command is None:
            raise Exception("interaction cannot be found!")

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
            try:
                params = ', '.join([f"{param['name']}={param['value']}" for param in inter.data["options"]])
            except Exception:
                params = "None"

        return file_name, line, command, params, tb

    async def on_slash_error(self, inter: Interaction, error: app_commands.AppCommandError) -> None:    # noqa
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
            url = await upload(tb)

            message = f"I'm sorry mate, the choomahs are coming back, I can't do that right now. I've noted it down and will look into it. (Ran into error {type(error).__name__})"

            goto_url = discord.ui.Button(label="Traceback", style=discord.ButtonStyle.link, url=url)
            view = discord.ui.view.View()
            view.add_item(goto_url)
            await log(self.bot, inter, LogType.ERROR, None, [
                {
                    "name": "Error",
                    "value": f"```File: {file_name}\nLine: {line}\nCommand: {command}\nParameters: {params}```",
                    "inline": False
                },
            ],
                      Importancy.HIGH,
                      view)

            await inter.response.send_message(message, ephemeral=True)

    async def handle_bump(self, message: discord.Message) -> None:
        await sleep(0.5)  # Allow the embed to load...
        channel = message.channel

        bump_channel = int(self.bot.config.get("guild", "channels", "bump"))

        if channel.id != bump_channel:
            return
        elif not message.embeds or len(message.embeds) != 1:
            return

        embed = message.embeds[0]

        if "Bump done!" in embed.description:
            await sleep(7200)  # 2 Hours
            await channel.send(f"{message.interaction_metadata.user.mention} Time to bump you fucken druggah")
            await channel.send("https://media1.tenor.com/m/rUUFSwPj-FMAAAAC/tbls-sassy.gif")

    async def handle_reaction_event(self, payload: discord.RawReactionActionEvent, remove: bool = False) -> None:
        guild_id = payload.guild_id

        if guild_id is None:
            return  # Ignore DMs

        reaction_message_id = int(self.bot.config.get("guild", "roles", "reactions", "message"))
        if payload.message_id != reaction_message_id:
            return

        emoji: str = str(payload.emoji.id) if payload.emoji.id else payload.emoji.name
        roles = self.bot.config.get("guild", "roles", "reactions")
        role_id = roles.get(emoji, None)

        if role_id is None:
            return

        guild = self.bot.get_guild(guild_id)
        if guild is None:
            return

        role = guild.get_role(role_id)
        if role is None:
            return  # Role not found

        try:
            member = await guild.fetch_member(payload.user_id)
        except discord.NotFound:
            return  # Member not in guild

        if remove:
            if role not in member.roles:
                return
        else:
            if role in member.roles:
                return

        await member.remove_roles(role) if remove else await member.add_roles(role)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        welcome_channel = self.bot.get_channel(self.bot.config.get("guild", "channels", "welcome"))

        if welcome_channel is None or not isinstance(welcome_channel, discord.TextChannel):
            await add(bot=self.bot, member=member)
            return

        await welcome_channel.send(f"{member.mention} Whats goin on mate? You're druggo #{len(member.guild.members)}, fuckin skits mate")

        await add(bot=self.bot, member=member)
        await log(self.bot, None, LogType.JOIN, fields=[
            {"name": "User", "value": member.name},
            {"name": "ID", "value": member.id},
            {"name": "Mention", "value": member.mention}
        ])

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.id == int(self.bot.config.get("guild", "channels", "bump", "bot")):
            await self.handle_bump(message)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message) -> None:
        if before.author.bot:
            return

        await log(self.bot, None, LogType.MESSAGE_EDIT, fields=[
            {"name": "User", "value": f"{before.author.mention} (`{before.author.id}`)", "inline": False},
            {"name": "Before", "value": f"```{before.content}```", "inline": False},
            {"name": "After", "value": f"```{after.content}```", "inline": False},
            {"name": "Jump Link", "value": after.jump_url, "inline": False}
        ])

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message) -> None:
        if message.author.bot:
            return

        if isinstance(message.channel, (discord.DMChannel, discord.GroupChannel)):
            return

        await log(self.bot, None, LogType.MESSAGE_DELETE, fields=[
            {"name": "User", "value": f"{message.author.mention} (`{message.author.id}`)", "inline": False},
            {"name": "Content", "value": f"```{message.content}```", "inline": False},
            {"name": "Channel", "value": f"{message.jump_url}", "inline": False},
        ])

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent) -> None:
        await self.handle_reaction_event(payload, False)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent) -> None:
        await self.handle_reaction_event(payload, True)


async def setup(bot):
    await bot.add_cog(Events(bot))
