from discord import Embed


async def log(bot, interaction, action, reason=None, fields=None):
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
        "warn",
        "rwarn",
        "mute",
        "unmute",
        "ban",
        "unban",
        "kick"
    )

    if action in moderation_actions:
        invoker = interaction.user
        embed.add_field(name="Moderator", value=f"{invoker.mention} (`{invoker.id}`)", inline=False)

        if action not in ("unmute", "rwarn"):
            embed.add_field(name="Reason", value=f"```{reason}```", inline=False)

    for field in fields:
        name = field["name"]
        value = field["value"]
        inline = field["inline"]

        embed.add_field(name=name, value=value, inline=inline)

    await bot.config["channels"]["logs"].send(embed=embed)
