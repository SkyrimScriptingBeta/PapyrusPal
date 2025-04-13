from dataclasses import dataclass, fields
from typing import Callable, Type, TypeVar

from PySide6.QtWidgets import QBoxLayout, QWidget

T = TypeVar("T", bound=QWidget)

Direction = QBoxLayout.Direction


def widget(
    name: str | None = None,
    classes: list[str] | None = None,
    layout: QBoxLayout.Direction | None = QBoxLayout.Direction.TopToBottom,
    add_widgets_to_layout: bool = True,
) -> Callable[[Type[T]], Type[T]]:
    def decorator(cls: Type[T]) -> Type[T]:
        def new_post_init(self: T) -> None:
            derived_from = cls.__bases__[0]
            derived_from.__init__(self)

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
            if layout is not None:
                the_layout = QBoxLayout(layout)
                self.setLayout(the_layout)
                if hasattr(
                    self, "_layout"
                ):  # TODO: check to verify it's callable (even check signature if possible)
                    self._layout(the_layout)
                if add_widgets_to_layout:
                    for field in fields(cls):  # type: ignore
                        if isinstance(field.type, type) and issubclass(
                            field.type, QWidget
                        ):
                            widget_instance = getattr(self, field.name)
                            if widget_instance is not None:
                                self.layout().addWidget(widget_instance)

        cls.__post_init__ = new_post_init  # type: ignore[attr-defined]

        # Make it a dataclass
        cls = dataclass(cls)

        return cls

    return decorator
