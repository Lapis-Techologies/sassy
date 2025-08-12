from typing import TYPE_CHECKING
from random import choices
from discord import Embed

if TYPE_CHECKING:
    from main import Sassy


async def callback(bot: "Sassy", giveaway: dict):
    channel_id = giveaway["channel"]
    message_id = giveaway["message"]
    user_id = giveaway["creator"]
    prize = giveaway["prize"]
    winners = giveaway["winners"]

    channel = await bot.fetch_channel(channel_id)
    message = await channel.fetch_message(message_id)
    user = await bot.fetch_user(user_id)

    embed = Embed(title="Finished Giveaway", color=0x3399FF)
    embed.add_field(name="Prize", value=f"**{prize}**")

    users = [user async for user in message.reactions[0].users()]
    chosen_winners = choices(users, k=winners)

    message_text = [f"{user.mention} Your giveaway is over!"]
    for winner in chosen_winners:
        message_text.append(f"{winner.mention} You have been selected as a "
                       f"winner!")

    message = await channel.send("\n".join(message_text),
                                 embed=embed)
    await message.add_reaction("🎉")
