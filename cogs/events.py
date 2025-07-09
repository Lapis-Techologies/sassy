import traceback
import pathlib
import discord
from re import compile
from io import BytesIO
from time import time
from typing import TYPE_CHECKING
from asyncio import sleep
from discord.ext import commands
from discord import (
    app_commands,
    Interaction,
    RawMemberRemoveEvent,
    RawMessageUpdateEvent,
    RawReactionActionEvent,
    Message,
)
from utils.dpaste import upload
from utils.adduser import add
from utils.log import log, Importancy, LogType, Field


if TYPE_CHECKING:
    from main import Sassy


class Events(commands.Cog):
    def __init__(self, bot: "Sassy"):
        self.bot = bot
        self._old_tree_error = None
        self.uuid4_regex = compile(
            r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
        )  # UUID4
        self.polling_db = self.bot.database["polls"]
        self.user_db = self.bot.database["user"]
        bdir = pathlib.Path("./bumping")
        bdir.mkdir(exist_ok=True)
        self.bump_file = bdir / "bump.txt"
        with open(self.bump_file, "w") as bump_file:
            bump_file.write("")

    def cog_load(self):
        tree = self.bot.tree
        self._old_tree_error = tree.on_error
        tree.on_error = self.on_slash_error

    def cog_unload(self):
        tree = self.bot.tree
        tree.on_error = self._old_tree_error

    async def handle_error(
        self, inter: Interaction, error: app_commands.AppCommandError
    ) -> tuple[str, str, str, str | None, str]:
        if inter.command is None:
            raise Exception("interaction cannot be found!")

        error = getattr(error, "original", error)
        tb = "".join(
            traceback.format_exception(type(error), error, error.__traceback__)
        )
        final_tb = tb.split("File")[-1]
        sections = final_tb.split(",")
        file_dir = sections[0].strip().replace('"', "")

        file_name = pathlib.Path(file_dir).name
        line = sections[1].strip().split(" ")[1]

        command = inter.command.name

        if isinstance(inter.command, app_commands.ContextMenu):
            params = "None"
        else:
            try:
                params = ", ".join(
                    [
                        f"{param['name']}={param['value']}"
                        for param in inter.data["options"]
                    ]
                )
            except Exception:
                params = "None"

        return file_name, line, command, params, tb

    async def command_not_found(self, inter, _) -> None:
        await inter.response.send_message("Command not found!")

    async def check_failure(self, inter, _) -> None:
        await inter.response.send_message(
            "You do not have permission to use this command!"
        )

    async def command_on_cooldown(self, inter, error) -> None:
        time_left = int(error.cooldown.get_retry_after())
        length = int(time()) + time_left
        formatted_time = f"<t:{length}:R>"

        await inter.response.send_message(
            f"Command is on cooldown! (Ends {formatted_time})"
        )

    async def error_out(self, inter, error) -> None:
        file_name, line, command, params, tb = await self.handle_error(inter, error)

        if command == "fail":
            goto_url = discord.ui.Button(
                label="Traceback",
                style=discord.ButtonStyle.link,
                disabled=True,
                url="https://discord.com/invite/HxFxPF3n25",
            )
            view = discord.ui.view.View()
            view.add_item(goto_url)
            await log(
                self.bot,
                inter,
                LogType.ERROR,
                None,
                [
                    Field(
                        "Error",
                        f"```File: {file_name}\nLine: {line}\nCommand: {command}\nParameters: {params}```",
                        False,
                    )
                ],
                Importancy.LOW,
                view,
            )
            return

        url = await upload(tb)

        message = f"I'm sorry mate, the choomahs are coming back, I can't do that right now. I've noted it down and will look into it. (Ran into error {type(error).__name__})"

        goto_url = discord.ui.Button(
            label="Traceback", style=discord.ButtonStyle.link, url=url
        )
        view = discord.ui.view.View()
        view.add_item(goto_url)
        await log(
            self.bot,
            inter,
            LogType.ERROR,
            None,
            [
                Field(
                    "Error",
                    f"```File: {file_name}\nLine: {line}\nCommand: {command}\nParameters: {params}```",
                    False,
                )
            ],
            Importancy.HIGH,
            view,
        )

        await inter.response.send_message(message, ephemeral=True)

    async def on_slash_error(
        self, inter: Interaction, error: app_commands.AppCommandError
    ) -> None:  # noqa
        errors = {
            app_commands.CommandNotFound: self.command_not_found,
            app_commands.CommandOnCooldown: self.command_on_cooldown,
            app_commands.CheckFailure: self.check_failure,
        }

        callback = errors.get(type(error), self.error_out)
        await callback(inter, error)

    async def handle_bump(self, message: discord.Message) -> None:
        await sleep(1)  # Allow the embed to load...
        channel = message.channel

        bump_channel = self.bot.config.get("guild", "channels", "bump", "id")
        if channel.id != bump_channel:
            return
        elif not message.embeds or len(message.embeds) != 1:
            return

        embed = message.embeds[0]
        if "Bump done!" not in embed.description:
            return

        with open("./resources/oh-yis.gif", "rb") as gif:
            gif = discord.File(fp=BytesIO(gif.read()), filename="oh-yis.gif")

        await channel.send(
            f"Thanks for bumping {message.interaction_metadata.user.mention}, I'll remind you to bump again in 2 hours!",
            files=[gif],
        )

        with open(self.bump_file, "w") as bump_file:
            bump_time = time() + 5 if self.bot.config.get("database", "dev") else 7200
            bump_file.write(str(bump_time))

        await self.user_db.update_one(
            {"uid": message.interaction_metadata.user.id}, {"$inc": {"bumps": 1}}
        )
        await self.bot.loop.create_task(self.bump_task(channel, message))

    async def bump_task(self, channel, message) -> None:
        # Check for file instead of database, saves the extra DB operation and is simpler
        with open(self.bump_file, "r") as bump_file:
            bump_time = float(bump_file.read())
            now = time()
            time_left = bump_time - now

            if time_left <= 0:
                with open("./resources/you-fucken-druggah.gif", "rb") as gif:
                    file = discord.File(
                        fp=BytesIO(gif.read()), filename="you-fucken-druggah.gif"
                    )
                    await channel.send(
                        f"{message.interaction_metadata.user.mention} Time to bump you fucken druggah",
                        files=[file],
                    )
            else:
                await sleep(time_left)
                with open("./resources/you-fucken-druggah.gif", "rb") as gif:
                    file = discord.File(
                        fp=BytesIO(gif.read()), filename="you-fucken-druggah.gif"
                    )
                    await channel.send(
                        f"{message.interaction_metadata.user.mention} Time to bump you fucken druggah",
                        files=[file],
                    )

    async def handle_reaction_event(self, payload: RawReactionActionEvent) -> None:
        guild = self.bot.get_guild(payload.guild_id)
        member = await guild.fetch_member(payload.user_id)

        if member.bot:
            return

        guild_id = payload.guild_id

        if guild_id is None:
            return  # Ignore DMs

        reaction_message_id = int(
            self.bot.config.get("guild", "roles", "reactions", "message")
        )
        if payload.message_id == reaction_message_id:
            await self.handle_reaction_roles(payload, guild_id)
            return

        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        if message.embeds:
            await self.handle_poll_reaction(payload, message)
            return

    async def handle_poll_reaction(
        self, payload: RawReactionActionEvent, message: Message
    ):
        embed = message.embeds[0]
        footer = embed.footer.text
        parts = footer.split(" | ")
        if len(parts) != 2:
            return
        uuid = parts[1].strip()

        if not self.uuid4_regex.match(uuid):
            return

        poll = await self.polling_db.find_one({"id": uuid})
        if poll is None:
            return

        end_date = int(poll["end_date"])
        finished = poll["finished"]
        current_time = time()
        if (current_time > end_date) or finished:
            return

        emoji_id = payload.emoji.id

        emojis = {
            int(emoji_id): idx
            for idx, (_, emoji_id) in enumerate(
                self.bot.config.get("commands", "poll").items()
            )
        }
        selected_option = emojis.get(emoji_id)

        if selected_option is None or selected_option >= len(poll["votes"]):
            return

        if payload.event_type == "REACTION_REMOVE":
            await self.polling_db.update_one(
                {"id": uuid}, {"$inc": {f"votes.{selected_option}": -1}}
            )
        else:
            await self.polling_db.update_one(
                {"id": uuid}, {"$inc": {f"votes.{selected_option}": 1}}
            )

    async def handle_reaction_roles(self, payload: RawReactionActionEvent, guild_id):
        emoji: str = str(payload.emoji.id) if payload.emoji.id else payload.emoji.name
        roles = self.bot.config.get("guild", "roles", "reactions")
        role_id = roles.get(emoji, None)

        if role_id is None:
            return

        guild = self.bot.get_guild(guild_id)
        if guild is None:
            return

        role = guild.get_role(role_id)
        if role is None:
            return  # Role not found

        try:
            member = await guild.fetch_member(payload.user_id)
        except discord.NotFound:
            return  # Member not in guild

        if payload.event_type == "REACTION_REMOVE":
            if role not in member.roles:
                return
        else:
            if role in member.roles:
                return

        await member.remove_roles(
            role
        ) if payload.event_type == "REACTION_REMOVE" else await member.add_roles(role)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        welcome_channel = self.bot.get_channel(
            self.bot.config.get("guild", "channels", "welcome")
        )

        if welcome_channel is None or not isinstance(
            welcome_channel, discord.TextChannel
        ):
            await add(bot=self.bot, member=member)
            return

        await welcome_channel.send(
            f"{member.mention} Whats goin on mate? You're druggo #{member.guild.member_count}, fuckin skits mate"
        )

        await add(bot=self.bot, member=member)
        await log(
            self.bot,
            None,
            LogType.JOIN,
            fields=[
                Field("User", member.name),
                Field("ID", member.id),
                Field("Mention", member.mention),
            ],
        )

    @commands.Cog.listener()
    async def on_raw_member_remove(self, payload: RawMemberRemoveEvent):
        welcome_channel = self.bot.get_channel(
            self.bot.config.get("guild", "channels", "welcome")
        )

        if welcome_channel is None or not isinstance(
            welcome_channel, discord.TextChannel
        ):
            await log(
                self.bot,
                None,
                LogType.ERROR,
                importancy=Importancy.HIGH,
                fields=[Field("Error", "Failed to get welcome channel!")],
            )

        server = self.bot.get_guild(payload.guild_id)
        await welcome_channel.send(
            f"**{payload.user.name}** left the server, they probably ate a trippa snippa. {server.member_count} druggos left"
        )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.interaction_metadata:
            if message.author.id == int(
                self.bot.config.get("guild", "channels", "bump", "bot")
            ):
                await self.handle_bump(message)

    @commands.Cog.listener()
    async def on_raw_message_edit(self, payload: RawMessageUpdateEvent) -> None:
        before = payload.cached_message
        after = payload.message
        if before is None:
            before = "UNABLE TO CACHE MESSAGE"
        if after.author.bot:
            return
        # Ignore discord content servers
        elif before.content == after.content:
            return

        await log(
            self.bot,
            None,
            LogType.MESSAGE_EDIT,
            fields=[
                Field("User", f"{after.author.mention}", False),
                Field(
                    "Before",
                    f"```{before.content}```" if before.content else "_ _",  # Nothing
                    False,
                ),
                Field("After", f"```{after.content}```", False),
                Field("Jump Link", after.jump_url, False),
            ],
        )

    @commands.Cog.listener()
    async def on_raw_message_delete(
        self, payload: discord.RawMessageDeleteEvent
    ) -> None:
        if payload.cached_message.author.bot:
            return
        elif isinstance(
            payload.cached_message.channel, (discord.DMChannel, discord.GroupChannel)
        ):
            return

        await log(
            self.bot,
            None,
            LogType.MESSAGE_DELETE,
            fields=[
                Field(
                    "User",
                    f"{payload.cached_message.author.mention} (`{payload.cached_message.author.id}`)",
                    False,
                ),
                Field(
                    "Content",
                    f"```{payload.cached_message.content}```"
                    if payload.cached_message.content
                    else "!!No Content.!!",
                    False,
                ),
                Field("Channel", payload.cached_message.channel.jump_url, False),
            ],
        )

    @commands.Cog.listener()
    async def on_raw_reaction_add(
        self, payload: discord.RawReactionActionEvent
    ) -> None:
        await self.handle_reaction_event(payload)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(
        self, payload: discord.RawReactionActionEvent
    ) -> None:
        await self.handle_reaction_event(payload)


async def setup(bot):
    await bot.add_cog(Events(bot))
