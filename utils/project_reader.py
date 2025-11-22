import pathlib
import os
from discord import Embed


class ProjectReader:
    def __init__(self, whitelisted: list[pathlib.Path], banned: list[str]):
        self.whitelisted = whitelisted
        self.banned = banned  # List of banned names for files

    def project_stats(self):
        root = pathlib.Path(os.getcwd())
        lines = 0
        files = 0
        directories = 0
        failed = 0
        size = 0
        longest_file = {}

        for path in self.whitelisted:
            path = pathlib.Path.joinpath(root, path)
            if path.is_file():
                files += 1
                try:
                    file_lines, file_size, new_longest_file = self._handle_file(
                        path, longest_file
                    )
                    if file_lines == -1:
                        failed += 1

                    lines += file_lines if file_lines != -1 else 0
                    size += file_size
                    if new_longest_file:
                        longest_file = new_longest_file
                except Exception as e:
                    print(f"Failed to process {path}: {e}")
                    failed += 1
                    continue
            elif path.is_dir():
                directories += 1
                dir_lines, dir_size, dir_files, dir_failed, new_longest_file = (
                    self._handle_directory(path, longest_file)
                )
                lines += dir_lines
                size += dir_size
                files += dir_files
                failed += dir_failed
                if new_longest_file:
                    longest_file = new_longest_file

        feet, miles = self._get_length(lines)

        embed = Embed(
            title="Project Stats",
            description="Some cool facts about me!",
            color=0x44FF99,
        )

        longest_file_name = list(longest_file.keys())[0] if longest_file else "None"
        longest_file_length = list(longest_file.values())[0] if longest_file else 0

        embed.add_field(name="Line Count", value=lines)
        embed.add_field(
            name="Average Line Count",
            value=round(lines / files, 1) if files > 0 else 0,
        )
        embed.add_field(name="File Count", value=files)
        embed.add_field(name="Directory Count", value=directories)
        embed.add_field(name="Files Read", value=files - failed)
        embed.add_field(name="Files Failed to Read", value=failed)
        embed.add_field(
            name="Longest File",
            value=f"{longest_file_name} with **{longest_file_length}** lines!"
            if longest_file
            else "No files processed",
        )
        embed.add_field(name="Total Size", value=self._format_size(size))
        embed.add_field(
            name="Total Length (Physically)",
            value=f"**{feet:.2f}** feet, **{miles:.2f}** miles!",
        )

        return embed

    def _handle_directory(self, path: pathlib.Path, longest_file: dict):
        dir_lines = 0
        dir_size = 0
        dir_files = 0
        dir_failed = 0
        for file in path.glob("*"):
            if file.name in self.banned:
                continue
            if file.is_file():
                dir_files += 1
                try:
                    file_lines, file_size, new_longest_file = self._handle_file(
                        file, longest_file
                    )
                    if file_lines == -1:
                        dir_failed += 1

                    dir_lines += file_lines if file_lines != -1 else 0
                    dir_size += file_size
                    if new_longest_file:
                        longest_file = new_longest_file
                except Exception as e:
                    print(f"Failed to process {file}: {e}")
                    dir_failed += 1
                    continue
            else:
                sub_lines, sub_size, sub_files, sub_failed, new_longest_file = (
                    self._handle_directory(file, longest_file)
                )
                dir_lines += sub_lines
                dir_size += sub_size
                dir_files += sub_files
                dir_failed += sub_failed
                if new_longest_file:
                    longest_file = new_longest_file
        return dir_lines, dir_size, dir_files, dir_failed, longest_file

    def _handle_file(self, path: pathlib.Path, longest_file: dict):
        file_lines, file_size = self._read_file(path)
        if not longest_file or list(longest_file.values())[0] < file_lines:
            return file_lines, file_size, {path.name: file_lines}
        return file_lines, file_size, None

    def _read_file(self, path: pathlib.Path):
        with open(path, "r", encoding="utf-8") as file:
            try:
                file_lines = len(file.readlines())
            except UnicodeDecodeError:
                file_lines = -1
            size = path.stat().st_size
        return file_lines, size

    def _format_size(self, size) -> str:
        kb = 1024
        mb = kb**2
        gb = kb**3
        return (
            f"{size:.2f} bytes"
            if size < kb
            else f"{size / kb:.2f} KB"
            if size < mb
            else f"{size / mb:.2f} MB"
            if size < gb
            else f"{size / gb:.2f} GB"
        )

    @staticmethod
    def _get_length(length):
        total_length_inches = length * 0.1667  # Based on Ubuntu Mono, 12-point font
        total_length_feet = total_length_inches / 12  # 12 inches per foot
        total_length_mile = total_length_feet / 5280  # 5280 feet per mile
        return total_length_feet, round(total_length_mile, 2)
