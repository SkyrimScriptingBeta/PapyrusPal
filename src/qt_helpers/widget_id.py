from typing import TypeVar

from PySide6.QtWidgets import QWidget

T = TypeVar("T", bound=QWidget)


def widget_id(
    _widget: T, name: str | None = None, classes: str | list[str] | None = None
) -> T:
    if name:
        _widget.setObjectName(name)

    klasses: list[str] = []
    if classes:
        if isinstance(classes, str):
            klasses.append(classes)
        else:
            klasses.extend(classes)
    if klasses:
        _widget.setProperty("class", f"|{'|'.join(klasses)}|")

    return _widget
