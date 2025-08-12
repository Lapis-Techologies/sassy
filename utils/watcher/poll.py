from typing import TYPE_CHECKING
from discord import Embed


if TYPE_CHECKING:
    from main import Sassy


async def callback(bot: "Sassy", poll: dict):
    channel_id = poll["channel"]
    user_id = poll["uid"]
    question = poll["question"]
    final_votes = poll["votes"]
    options = poll["answers"]

    channel = await bot.fetch_channel(channel_id)
    user = await bot.fetch_user(user_id)

    biggest = (0, 0)
    for i, vote in enumerate(final_votes):
        if vote > biggest[1]:
            biggest = (i, vote)
    winner = options[biggest[0]]

    embed = Embed(title="Finished Poll", color=0x3399FF)
    embed.add_field(name="Question", value=f"**{question}**")
    embed.add_field(
        name="Winner", value=f"The winner is option **{biggest[0] + 1}**!"
    )

    for i, option in enumerate(options):
        if i == biggest[0]:
            embed.add_field(
                name=f"⭐ Option {i + 1} ⭐", value=f"**{winner}**", inline=False
            )
        else:
            embed.add_field(name=f"Option {i + 1}", value=option, inline=False)

    message = await channel.send(f"{user.mention} Your poll is over!", embed=embed)
    await message.add_reaction("🎉")
