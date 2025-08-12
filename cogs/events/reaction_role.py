import discord
from typing import TYPE_CHECKING
from discord.ext import commands
from discord import RawReactionActionEvent



if TYPE_CHECKING:
    from main import Sassy


class ReactionRole(commands.Cog):
    def __init__(self, bot: "Sassy"):
        self.bot = bot

    async def handle_reaction_event(self, payload: RawReactionActionEvent) -> None:
        guild = self.bot.get_guild(payload.guild_id)
        member = await guild.fetch_member(payload.user_id)

        if member.bot:
            return

        guild_id = payload.guild_id

        if guild_id is None:
            return  # Ignore DMs

        reaction_message_id = int(
            self.bot.config.get("guild", "roles", "reactions", "message")
        )
        if payload.message_id == reaction_message_id:
            await self.handle_reaction_roles(payload, guild_id)
            return

    async def handle_reaction_roles(self, payload: RawReactionActionEvent, guild_id):
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

        if payload.event_type == "REACTION_REMOVE":
            if role not in member.roles:
                return
        else:
            if role in member.roles:
                return

        await member.remove_roles(
            role
        ) if payload.event_type == "REACTION_REMOVE" else await member.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_add(
        self, payload: discord.RawReactionActionEvent
    ) -> None:
        await self.handle_reaction_event(payload)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(
        self, payload: discord.RawReactionActionEvent
    ) -> None:
        await self.handle_reaction_event(payload)


async def setup(bot):
    await bot.add_cog(ReactionRole(bot))
