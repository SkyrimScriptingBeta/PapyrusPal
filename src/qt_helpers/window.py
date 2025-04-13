from dataclasses import dataclass
from typing import Callable, Type, TypeVar

from PySide6.QtWidgets import QBoxLayout, QMainWindow, QWidget

T = TypeVar("T", bound=QMainWindow)

Direction = QBoxLayout.Direction


def window(
    name: str | None = None,
    classes: list[str] | None = None,
) -> Callable[[Type[T]], Type[T]]:
    def decorator(cls: Type[T]) -> Type[T]:
        def new_post_init(self: T) -> None:
            derived_from = cls.__bases__[0]
            derived_from.__init__(self)  # type: ignore

            # Misc initializations
            if hasattr(self, "_init") and callable(self._init):
                self._init()

            # Setup widgets
            if hasattr(self, "_setup") and callable(self._setup):
                self._setup()

            # Setup styles
            if hasattr(self, "_styles") and callable(self._styles):
                self._styles()

            # Setup events
            if hasattr(self, "_events") and callable(self._events):
                self._events()

            # Connect signals
            if hasattr(self, "_signals") and callable(self._signals):
                self._signals()

            # Apply additional configurations
            if name:
                self.setObjectName(name)
            if classes:
                self.setProperty("class", f"|{'|'.join(classes)}|")

            # Set central widget
            if hasattr(self, "central_widget") and isinstance(
                self.central_widget, QWidget
            ):
                self.setCentralWidget(self.central_widget)

        cls.__post_init__ = new_post_init  # type: ignore[attr-defined]

        # Make it a dataclass
        cls = dataclass(cls)

        return cls

    return decorator
