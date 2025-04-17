import os
import sys


def main():

    if "--light" in sys.argv:
        os.environ["QT_QPA_PLATFORM"] = "windows:darkmode=0"
    elif "--dark" in sys.argv:
        os.environ["QT_QPA_PLATFORM"] = "windows:darkmode=1"

    if "--dev" in sys.argv:
        from papyruspad.main import dev

        dev()
    else:
        from papyruspad.main import prod

        prod()


if __name__ == "__main__":
    main()
