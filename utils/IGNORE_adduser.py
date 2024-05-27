async def add(bot, member, choomah_coins=0, xp=0, level=0, logs=None):
    """
    helper function to add a member into the database
    :param bot:
    :param member:
    :param choomah_coins:
    :param xp:
    :param level:
    :param logs:
    :return:
    """
    if logs is None:
        logs = []

    await bot.db.insert_one({
        "uid": member.id,
        "choomah_coins": choomah_coins,
        "xp": xp,
        "level": level,
        "logs": logs
    })
