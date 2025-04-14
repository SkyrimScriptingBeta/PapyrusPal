from PySide6.QtGui import QFontDatabase


def load_fonts():
    # Generated using BASH script (found in [root]/resources/qt/font-names.sh)
    custom_font_names = ["FiraCode", "FiraCodeiScript"]

    for font_name in custom_font_names:
        print(f"Loading {font_name}")
        QFontDatabase.addApplicationFont(f":/fonts/{font_name}.ttf")
