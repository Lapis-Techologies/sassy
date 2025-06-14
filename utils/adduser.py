from .log import log, LogType


async def add(bot, member, choomah_coins=0, xp=0, level=0, last_message=0, logs=None):
    """
    helper function to add a member into the database
    """
    if logs is None:
        logs = []

    await bot.user_db.insert_one(
        {
            "uid": member.id,
            "choomah_coins": choomah_coins,
            "xp": xp,
            "level": level,
            "logs": logs,
            "last_message": last_message,
        }
    )

    await log(
        bot,
        None,
        LogType.DATABASE_ADD,
        fields=[
            {"name": "User", "value": member.name},
            {"name": "ID", "value": member.id},
            {"name": "Mention", "value": member.mention},
        ],
    )
