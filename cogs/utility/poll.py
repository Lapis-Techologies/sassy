from typing import TYPE_CHECKING
from uuid import uuid4
from discord import app_commands, Interaction, Embed
from discord.ext import commands
from utils.checks import db_check
from utils.tasks.poll_watcher import _watch_poll


if TYPE_CHECKING:
    from main import Sassy


class Poll(commands.Cog):
    def __init__(self, bot: "Sassy"):
        self.bot = bot
        self.polling_db = self.bot.database["polls"]
        self.emojis = None
        self.MAX_QUESTION_LEN = 200
        self.MAX_ANSWER_COUNT = 10
        self.MAX_ANSWER_LEN = 100

    @app_commands.command(name="poll", description="Make a poll")
    @app_commands.describe(
        minutes="How long the poll should last (in minutes).",
        question="The poll question to ask",
        answers="The answer choices, separated by commas",
    )
    @app_commands.checks.cooldown(
        1, 300, key=lambda i: (i.guild_id, i.user.id)
    )  # 1/5min
    @db_check()
    async def poll(self, interaction: Interaction, minutes: int, question: str, answers: str):
        await interaction.response.defer()
        poll_id = str(uuid4())
        try:
            question_clean = self._block_mentions(self._clean_question(question))
            answer_list = self._clean_answers(answers)
        except ValueError as e:
            await interaction.followup.send(f"❌ {str(e)}", ephemeral=True)
            return

        seconds = minutes * 60
        if seconds > 604800:  # 1 Week
            await interaction.followup.send("Sorry m8, Polls can only last up to 1 week.")
            return

        end_date = interaction.created_at.timestamp() + seconds

        await self.polling_db.insert_one(
            {
                "id": poll_id,
                "uid": interaction.user.id,
                "channel": interaction.channel_id,
                "question": question_clean,
                "answers": answer_list,
                "votes": [0] * len(answer_list),
                "end_date": end_date,
                "finished": False,  # Check for the bot to see if it has
                # finished it or not, see utils/tasks/poll_watcher.py
            }
        )

        embed = Embed(
            title="Brand New Poll", description=f"**{question_clean}**", color=0x3399FF
        )
        embed.set_footer(text=f"Poll ID | {poll_id}")

        for i, option in enumerate(answer_list):
            embed.add_field(name=f"Option {i + 1}", value=option)

        message = await interaction.followup.send(
            f"This poll ends <t:{int(end_date)}:R>", embed=embed, wait=True
        )

        if self.emojis is None:
            self.emojis = []
            for _, emoji_id in self.bot.config.get("commands", "poll").items():
                emoji = await self.bot.fetch_application_emoji(emoji_id)
                self.emojis.append(emoji)

        for i, _ in enumerate(answer_list):
            await message.add_reaction(self.emojis[i])

        await _watch_poll(self.bot, poll_id)

    def _clean_answers(self, raw: str) -> list[str]:
        split_answers = [a.strip() for a in raw.split(",")]
        unique_answers = list(dict.fromkeys(split_answers))

        if len(unique_answers) < 2:
            raise ValueError("You must provide at least 2 distinct answers.")
        if len(unique_answers) > self.MAX_ANSWER_COUNT:
            raise ValueError(f"You can provide up to {self.MAX_ANSWER_COUNT} answers.")

        for a in unique_answers:
            if len(a) > self.MAX_ANSWER_LEN:
                raise ValueError(
                    f"Each answer must be under {self.MAX_ANSWER_LEN} characters."
                )
            if "$" in a or "." in a:
                raise ValueError(
                    "Answers cannot contain '$' or '.' (MongoDB restriction)."
                )

        return unique_answers

    def _clean_question(self, q: str) -> str:
        q = q.strip()
        if len(q) > self.MAX_QUESTION_LEN:
            raise ValueError(
                f"Question must be under {self.MAX_QUESTION_LEN} characters."
            )
        if "$" in q or "." in q:
            raise ValueError(
                "Question cannot contain '$' or '.' (MongoDB restriction)."
            )
        return q

    @staticmethod
    def _block_mentions(text: str) -> str:
        return text.replace("@everyone", "[everyone]").replace("@here", "[here]")


async def setup(bot: "Sassy"):
    await bot.add_cog(Poll(bot))
