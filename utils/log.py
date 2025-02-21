from typing import TYPE_CHECKING, List
from enum import Enum, StrEnum
from discord import Embed, TextChannel, Interaction, ui


if TYPE_CHECKING:
    from main import Sassy


class Importancy(Enum):
    LOW = 0
    MEDIUM = 1
    HIGH = 2


class LogType(StrEnum):
    WARN = "warn"
    REMOVE_WARN = "rwarn"
    MUTE = "mute"
    UNMUTE = "unmute"
    BAN = "ban"
    UNBAN = "unban"
    KICK = "kick"
    ERROR = "error"
    JOIN = "join"
    DATABASE_ADD = "database add"
    MESSAGE_EDIT = "message edit"
    MESSAGE_DELETE = "message delete"


async def log(bot: "Sassy", interaction: Interaction | None, action: LogType, reason: str | None = None, fields: List | None = None, importancy: Importancy = Importancy.MEDIUM, view: ui.view.View | None = None):
    """
    Helper function to add logs to the log channel
    :param bot:
    :param interaction:
    :param action:
    :param reason:
    :param fields:
    :return:
    """
    if fields is None:
        fields = []

    embed = Embed(title=f"Log - {action.title()}")

    moderation_actions = (
        LogType.BAN,
        LogType.UNBAN,
        LogType.KICK,
        LogType.MUTE,
        LogType.UNMUTE,
        LogType.WARN,
        LogType.REMOVE_WARN
    )

    colors = {
        Importancy.LOW: 0x00FF00,
        Importancy.MEDIUM: 0xFFD700,
        Importancy.HIGH: 0xFF0000
    }

    embed.color = colors[importancy]
    
    if importancy == Importancy.HIGH:
        role_id = bot.config.get("guild", "roles", "dev")
        content = f"<@&{role_id}>" if role_id is not None else f"<@{bot.owner_id}>"
    else:
        content = ""

    if action in moderation_actions:
        # interaction should never be None in this case
        invoker = interaction.user
        embed.add_field(name="Moderator", value=f"{invoker.mention} (`{invoker.id}`)", inline=False)

        if action not in (LogType.UNMUTE, LogType.REMOVE_WARN):
            embed.add_field(name="Reason", value=f"```{reason}```", inline=False)

    for field in fields:
        name = field["name"]
        value = field["value"]
        inline = field["inline"]

        embed.add_field(name=name, value=value, inline=inline)

    logs = bot.get_channel(bot.config.get("guild", "channels", "logs"))

    if logs is None or not isinstance(logs, TextChannel):
        return

    await logs.send(content, embed=embed, view=view)
