import os
import sys


def main():

    if "--light" in sys.argv:
        os.environ["QT_QPA_PLATFORM"] = "windows:darkmode=0"
    elif "--dark" in sys.argv:
        os.environ["QT_QPA_PLATFORM"] = "windows:darkmode=1"

    if "--dev" in sys.argv:
        from papyrus_pal.main import dev

        dev()
    else:
        from papyrus_pal.main import prod

        prod()


if __name__ == "__main__":
    main()
