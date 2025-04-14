import os
import re
from dataclasses import dataclass
from re import Match

import sass
from PySide6.QtCore import QFileSystemWatcher
from PySide6.QtWidgets import QApplication

from qt_helpers.files import write_file


@dataclass
class StylesheetWatcher:
    app: QApplication
    main_scss_path: str
    out_qss_path: str
    _qss_watcher: QFileSystemWatcher = QFileSystemWatcher()
    _main_scss_folder_path: str = ""

    def __post_init__(self):
        self._main_scss_folder_path = os.path.dirname(self.main_scss_path)
        self._qss_watcher.fileChanged.connect(self._on_file_change)
        self._qss_watcher.directoryChanged.connect(self._on_file_change)
        self._update_watched_files()
        self._on_file_change()

    def _update_watched_files(self):
        print(f"Updating watched files in {self._main_scss_folder_path}")

        # Remove all paths; we'll re-add the current directory contents
        for path in self._qss_watcher.files() + self._qss_watcher.directories():
            self._qss_watcher.removePath(path)

        # Add the directory itself to watch for new files or directories
        self._qss_watcher.addPath(self._main_scss_folder_path)

        # Add all files in the directory to the watcher
        for filename in os.listdir(self._main_scss_folder_path):
            full_path = os.path.join(self._main_scss_folder_path, filename)
            if os.path.isfile(full_path):
                self._qss_watcher.addPath(full_path)

    def _on_file_change(self):
        print(f"Rebuilding {self.out_qss_path}")
        qss = self._rebuild_qss()
        write_file(self.out_qss_path, qss)
        self.app.setStyleSheet(qss)

    def _rebuild_qss(self) -> str:
        def attribute_name_replacer(match: Match[str]) -> str:
            content = match.group(1).replace("data-", "").replace("-", "_")
            return f"[{content}="

        qss_output: str = sass.compile(
            filename=self.main_scss_path, include_paths=[self._main_scss_folder_path]
        )
        qss_output = re.sub(r"\[([^\]]+)=", attribute_name_replacer, qss_output)
        qss_output = f"/* Generated File - DO NOT EDIT */\n\n{qss_output}"

        return qss_output


stylesheet_watcher: StylesheetWatcher | None = None


def watch_qss(app: QApplication, main_scss: str, out_qss: str) -> None:
    print(f"Watching {main_scss} and writing to {out_qss}")

    if not os.path.exists(main_scss):
        raise FileNotFoundError(
            f"Could not find file {main_scss}. Current directory: {os.getcwd()}"
        )

    global stylesheet_watcher
    stylesheet_watcher = StylesheetWatcher(app, main_scss, out_qss)
