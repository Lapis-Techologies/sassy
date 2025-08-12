from typing import TYPE_CHECKING
from time import time
from asyncio import sleep
from discord import Embed


if TYPE_CHECKING:
    from main import Sassy


async def watch_polls(bot: "Sassy"):
    try:
        polls_db = bot.database["polls"]
        polls = polls_db.find({"finished": {"$ne": True}})
    except Exception as e:
        print(e)

    async for poll in polls:
        try:
            poll_id = poll["id"]
            await _watch_poll(bot, poll_id)
        except Exception as e:
            print(e)


async def _watch_poll(bot: "Sassy", poll_id: str) -> None:
    polls_db = bot.database["polls"]
    poll = await polls_db.find_one({"id": poll_id})
    end_date = poll["end_date"]
    finished = poll["finished"]

    if finished:
        return

    now = time()
    time_left = end_date - now
    if time_left > 0:
        bot.loop.create_task(_finish_poll(bot, polls_db, poll_id, time_left))
    else:
        bot.loop.create_task(_finish_poll(bot, polls_db, poll_id, 0))


async def _finish_poll(bot: "Sassy", poll_db, poll_id: str, time_left) -> None:
    await sleep(time_left)
    await poll_db.update_one({"id": poll_id}, {"$set": {"finished": True}})
    poll = await poll_db.find_one({"id": poll_id})
    channel_id = poll["channel"]
    channel = await bot.fetch_channel(channel_id)
    user_id = poll["uid"]
    user = await bot.fetch_user(user_id)
    question = poll["question"]
    final_votes = poll["votes"]
    options = poll["answers"]

    biggest = (0, 0)
    for i, vote in enumerate(final_votes):
        if vote > biggest[1]:
            biggest = (i, vote)
    winner = options[biggest[0]]

    embed = Embed(title="Finished Poll", color=0x3399FF)
    embed.add_field(name="Question", value=f"**{question}**")
    embed.add_field(name="Winner", value=f"The winner is option **{biggest[0] + 1}**!")

    for i, option in enumerate(options):
        if i == biggest[0]:
            embed.add_field(
                name=f"⭐ Option {i + 1} ⭐", value=f"**{winner}**", inline=False
            )
        else:
            embed.add_field(name=f"Option {i + 1}", value=option, inline=False)

    message = await channel.send(f"{user.mention} Your poll is over!", embed=embed)
    await message.add_reaction("🎉")
