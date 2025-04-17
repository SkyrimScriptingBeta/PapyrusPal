from PySide6.QtWidgets import QApplication


class Application(QApplication):
    def __init__(self, *args: list[str], **kwargs: dict[str, object]) -> None:
        super().__init__(*args, *kwargs)  # type: ignore[no-untyped-call]
        self.setApplicationName("Papyrus Pad")
        self.setApplicationDisplayName("Papyrus Pad")
