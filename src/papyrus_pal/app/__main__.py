################################################################
# Application must be created before importing any other modules
# which create QWidgets at import time.
from PySide6.QtGui import QPixmap
from papyrus_pal.app.application import Application

app = Application()
################################################################
# pylint: disable=wrong-import-position,ungrouped-imports
################################################################

from qt_helpers.fonts import load_fonts
from papyrus_pal.app.windows.main_window import AppMainWindow
from papyrus_pal.app.qrc_resources import qt_resource_data
from qt_helpers.run_app import run_app


QRC_DATA = qt_resource_data


def main(development_mode: bool = False) -> None:
    load_fonts()
    main_window = AppMainWindow()
    main_window.show()
    main_window.setWindowIcon(QPixmap(":/icon.ico"))
    run_app(
        app,
        development_mode=development_mode,
        main_scss_local_path="resources/styles/main.scss",
        styles_qss_local_path="resources/styles.qss",
        styles_qss_resource=":/styles.qss",
    )


def dev():
    main(development_mode=True)


def prod():
    main(development_mode=False)


if __name__ == "__main__":
    main()
