import pathlib
import os
import tracemalloc
import time


class ProjectReader:
    def __init__(self, path: str | None = None, banned: tuple[str, ...] = tuple()) -> None:
        """
        A simple class to read a project's files and calculate some statistics.
        :param path: Base path to start reading files from. Default is current working directory.
        :param banned: Banned directories/files to ignore.
        """
        self.lines = 0
        self.total = 0
        self.files = 0
        self.failed = 0
        self.size = 0
        self.directories = 0
        self._kb = 1024
        self._mb = 1024 ** 2
        self._gb = 1024 ** 3
        self.path = pathlib.Path(os.getcwd()) if path is None else pathlib.Path(path)
        self.banned = banned

    def project_stats(self) -> None:
        """
        Print the project statistics.
        :return: None
        """
        lines, files, failed, size = self._process_project()

        self.lines = lines
        self.files = files
        self.failed = failed
        self.size = size

        print("-" * 50)
        print(f"Reading files in '{self.path}':")
        print(f"Total lines: {lines} (~{lines//(files - failed)} lines per file)")
        print(f"Total files: {files} (Failed {failed} files)")
        print(f"Total directories: {self.directories}")
        print(f"Total files read: {files - failed}")
        print(f"Total size: {self._format_size()}")
        print("-" * 50)

    def _format_size(self) -> str:
        """
        Format the size of the project.
        :return: str
        """
        return (
            f"{self.size:.2f} bytes" if self.size < self._kb else
            f"{self.size / self._kb:.2f} KB" if self.size < self._mb else
            f"{self.size / self._mb:.2f} MB" if self.size < self._gb else
            f"{self.size / self._gb:.2f} GB"
        )

    def _process_project(self) -> tuple[int, int, int, float]:
        """
        Process the project files.
        :return: None
        """
        if self.path.is_file():
            raise NotADirectoryError("Path must be a directory.")

        return self._process_folder(self.path)

    def _process_folder(self, folder: pathlib.Path) -> tuple[int, int, int, float]:
        """
        Process a folder.
        :param folder: pathlib.Path
        :return: None
        """
        lines = 0
        files = 0
        failed = 0
        size = 0

        try:
            for item in folder.iterdir():
                if item.name in self.banned:
                    continue
                elif item.is_dir():
                    self.directories += 1
                    l, f, e, s = self._process_folder(item)
                    lines += l
                    files += f
                    failed += e
                    size += s
                elif item.is_file():
                    try:
                        with open(item, 'r') as f:
                            files += 1
                            lines += len(f.readlines())
                            size += item.stat().st_size
                    except Exception:   # noqa
                        failed += 1
                else:
                    continue
        except PermissionError:
            pass

        return lines, files, failed, size


# https://stackoverflow.com/questions/552744/how-do-i-profile-memory-usage-in-python
def display_top(snapshot, key_type='lineno'):
    snapshot = snapshot.filter_traces((
        tracemalloc.Filter(False, "<frozen importlib._bootstrap>"),
        tracemalloc.Filter(False, "<unknown>"),
    ))
    top_stats = snapshot.statistics(key_type)

    total = sum(stat.size for stat in top_stats)
    print("Total allocated size: %.1f KiB" % (total / 1024))


def main(debug: bool, path: str | None = None) -> None:
    """
    Main function.
    :return: None
    """

    if debug:
        tracemalloc.start()
        start = time.time()

    banned = (
        'venv',
        '.idea',
        '__pycache__',
        os.path.basename(__file__),
        # Add more here
    )

    reader = ProjectReader(banned=banned, path=path or os.getcwd())
    reader.project_stats()

    if debug:
        snap = tracemalloc.take_snapshot()

        display_top(snap)
        print(f"Time taken: {time.time() - start:.2f} seconds")


if __name__ == '__main__':
    debug = False
    path = None
    main(debug, path)
