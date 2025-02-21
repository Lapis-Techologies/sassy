from functools import wraps
from typing import TYPE_CHECKING
from discord import Interaction
from discord.app_commands import check
from utils.adduser import add


if TYPE_CHECKING:
    from main import Sassy


def db_check():
    def decorator(func):
        async def predicate(interaction: Interaction) -> bool:
            user = interaction.user
            bot: "Sassy" = interaction.client

            # Check if user exists in the database
            curs = await bot.user_db.find_one({"uid": user.id}, projection={"uid": 1})
            if curs is None:
                await add(bot, user)

            return True

        @wraps(func)
        @check(predicate)
        async def wrapped(interaction: Interaction, *args, **kwargs):
            await func(interaction, *args, **kwargs)

        return wrapped
    return decorator


def is_dev():
    def decorator(func):
        async def predicate(interaction: Interaction) -> bool:
            user = interaction.user
            bot: "Sassy" = interaction.client
            guild = interaction.guild
            dev = guild.get_role(bot.config.get("guild", "roles", "dev"))

            if dev is None:
                return False

            return dev in user.roles

        @wraps(func)
        @check(predicate)
        async def wrapped(interaction: Interaction, *args, **kwargs):
            # Call the original command function
            await func(interaction, *args, **kwargs)

        return wrapped
    return decorator


def is_admin():
    def decorator(func):
        async def predicate(interaction: Interaction) -> bool:
            user = interaction.user
            bot: "Sassy" = interaction.client
            guild = interaction.guild
            admin = guild.get_role(bot.config.get("guild", "roles", "admin"))

            if admin is None:
                return False

            return admin in user.roles

        @wraps(func)
        @check(predicate)
        async def wrapped(interaction: Interaction, *args, **kwargs):
            # Call the original command function
            await func(interaction, *args, **kwargs)

        return wrapped
    return decorator


def in_server():
    def decorator(func):
        async def predicate(interaction: Interaction) -> bool:
            return interaction.guild is None
    
        @wraps(func)
        @check(predicate)
        async def wrapped(interaction: Interaction, *args, **kwargs):
            await func(interaction, *args, **kwargs)
        
        return wrapped
    return decorator
