import random
from typing import TYPE_CHECKING
from discord import app_commands, Interaction
from discord.ext import commands
from utils.adduser import add


if TYPE_CHECKING:
    from main import Sassy


class Hunt(commands.Cog):
    def __init__(self, bot: "Sassy"):
        self.bot = bot
    
    @app_commands.command(name="hunt", description="Go hunting with sassy on choomah island")
    @app_commands.checks.cooldown(1, 30, key=lambda i: (i.guild_id, i.user.id))
    async def hunt(self, inter: Interaction):
        await inter.response.defer()
        
        user = inter.user

        curs = await self.bot.user_db.find_one({"uid": user.id}, projection={"choomah_coins": 1})
        
        dice = random.randint(0, 2)

        if dice == 0:
            # Add
            offset = random.randint(1, 15)
            message = f"You goto choomah island and find {offset} choomah coins!"
        elif dice == 1:
            # Remove
            offset = random.randint(-15, -1)
            message = f"You goto choomah island and lose {abs(offset)} choomah coins!"
        else:
            # Nothing
            offset = 0
            message = "You found no coins!"

        if curs is None:
            new_bal = offset if offset >= 0 else 0
            await add(self.bot, user, choomah_coins=new_bal)
        else:
            new_bal = curs["choomah_coins"] + offset
            new_bal = new_bal if new_bal >= 0 else 0

            await self.bot.user_db.update_one({"uid": user.id}, {
                "$set": {
                    "choomah_coins": new_bal
                }
            })

        await inter.followup.send(f"{message} Your balance is now **{new_bal}**.")


async def setup(bot):
    await bot.add_cog(Hunt(bot))

