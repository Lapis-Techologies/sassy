import traceback
import pathlib
import discord
from time import time
from typing import TYPE_CHECKING
from discord.ext import commands
from discord import (
    app_commands,
    Interaction
)
from utils.dpaste import upload
from utils.log import log, Importancy, LogType, Field


if TYPE_CHECKING:
    from main import Sassy


class Error(commands.Cog):
    def __init__(self, bot: "Sassy"):
        self.bot = bot
        self._old_tree_error = None

    def cog_load(self):
        tree = self.bot.tree
        self._old_tree_error = tree.on_error
        tree.on_error = self.on_slash_error

    def cog_unload(self):
        tree = self.bot.tree
        tree.on_error = self._old_tree_error

    async def handle_error(
        self, interaction: Interaction, error: app_commands.AppCommandError
    ) -> tuple[str, str, str, str | None, str]:
        if interaction.command is None:
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

        command = interaction.command.name

        if isinstance(interaction.command, app_commands.ContextMenu):
            params = "None"
        else:
            try:
                params = ", ".join(
                    [
                        f"{param['name']}={param['value']}"
                        for param in interaction.data["options"]
                    ]
                )
            except Exception:
                params = "None"

        return file_name, line, command, params, tb

    async def command_not_found(self, interaction, _) -> None:
        await interaction.response.send_message("Command not found!")

    async def command_already_registered(self, _, __):
        pass

    async def check_failure(self, interaction, _) -> None:
        await interaction.response.send_message(
            "You do not have permission to use this command!"
        )

    async def command_on_cooldown(self, interaction, error) -> None:
        time_left = int(error.cooldown.get_retry_after())
        length = int(time()) + time_left
        formatted_time = f"<t:{length}:R>"

        await interaction.response.send_message(
            f"Command is on cooldown! (Ends {formatted_time})"
        )

    async def error_out(self, interaction, error) -> None:
        # TODO: Refactor actual logging into own function, allow for
        #  customizing button.
        file_name, line, command, params, tb = await self.handle_error(interaction, error)

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
                interaction,
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

        message = (f"I'm sorry mate, the choomahs are coming back,"
                   f" I can't do that right now. I've noted it down and will"
                   f" look into it. (Ran into error {type(error).__name__})")

        goto_url = discord.ui.Button(
            label="Traceback", style=discord.ButtonStyle.link, url=url
        )
        view = discord.ui.view.View()
        view.add_item(goto_url)
        await log(
            self.bot,
            interaction,
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

        await interaction.response.send_message(message, ephemeral=True)

    async def on_slash_error(
        self, interaction: Interaction, error: app_commands.AppCommandError
    ) -> None:  # noqa
        errors = {
            app_commands.CommandNotFound: self.command_not_found,
            app_commands.CommandOnCooldown: self.command_on_cooldown,
            app_commands.CheckFailure: self.check_failure,
            app_commands.CommandAlreadyRegistered: self.command_already_registered,
        }

        callback = errors.get(type(error), self.error_out)
        await callback(interaction, error)


async def setup(bot):
    await bot.add_cog(Error(bot))
