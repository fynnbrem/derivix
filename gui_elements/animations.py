import math
from typing import Generator, TypeVar

from PySide6.QtCore import QTimer, QRect
from PySide6.QtGui import QColor, Qt, QBrush, QPainter
from PySide6.QtWidgets import QFrame, QWidget


class JumpyDots(QWidget):
    """A widget that contains dots that sequentially jump.

    :param count:
        The count of dots.
    :param diameter:
        The diameter of each dot. All other values (e.g. jump height and widget size) will be scaled proportionately.
    :param color:
        The color of the dots.


    :cvar default_diameter:
        The default diameter for the dots.
    :cvar default_spacing:
        The default spacing between dots applied at the default diameter.
    :cvar default_jump_height:
        The default jump height of the dots applied at the default diameter.
    """
    default_diameter = 20
    default_spacing = 30
    default_jump_height = 40

    def __init__(self, count: int = 3, diameter: int = default_diameter, color: QColor = Qt.GlobalColor.black):
        super().__init__()
        # region: Determine the scale based on the desired `diameter` and set the accordingly scaled values.
        self._scale = diameter / self.default_diameter
        self.diameter = round(self.default_diameter * self._scale)
        self.spacing = round(self.default_spacing * self._scale)
        self.jump_height = round(self.default_jump_height * self._scale)
        # endregion

        self.coords = tuple(
            (c * self.spacing, self.jump_height)
            for c
            in range(count)
        )
        self.coords_generator = jump(self.coords, self.jump_height, 4)

        self.animation_timer = QTimer()
        self.animation_timer.setInterval(20)
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_timer.start()

        # region: Set the size of the widget.
        x_size = self.diameter + self.spacing * (count - 1)
        # ↑ The radiuses of the first and last dot plus the spacing caused by all dots.
        y_size = self.diameter + self.jump_height
        # ↑ The diameter of a dot plus its maximum jump height.
        # endregion
        self.brush = QBrush(color)
        self.setFixedSize(x_size, y_size)

    def update_animation(self):
        """Gets the next set of coordinates for the dots and updates the widget."""
        self.coords = next(self.coords_generator)
        self.update()

    def paintEvent(self, event):
        """Draw all the dots, based on `self.coords`."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(self.brush)
        painter.setPen(Qt.GlobalColor.transparent)

        for x, y in self.coords:
            painter.drawEllipse(
                QRect(x, y, self.diameter, self.diameter)
            )
        painter.end()


def jump(start_coords: tuple[tuple[int, int], ...], jump_height: int, steepness: int) \
        -> Generator[tuple[tuple[int, int], ...], None, None]:
    """Infinitely yields modified coordinates so the corresponding objects appears to be jumping in sequence.

    :param jump_height:
        The height of the jump.
    :param steepness:
        The coordinates will form a hill, and this variable controls that hill's steepness.
    """
    base_coords = list(start_coords)
    offset = 0
    curve = list(hill(60, 1 / 3))  # Those numbers were tested to look nice.
    while True:
        coords = [
            (x, y - int(jump_height * curve[(int(index * steepness) - offset) % len(curve)]))
            for index, (x, y)
            in enumerate(base_coords)
        ]  # `offset` must be subtracted so the wave goes from left to right
        offset = (offset + 1) % len(curve)
        yield tuple(coords)


def hill(step_size: int, flat_share: float) -> Generator[float, None, None]:
    """Generates a curve with values in [0;1].
    The curve starts flat and then has a hill in the shape of sin**2.

    :param step_size:
        Sets the total length of this curve (The length of the resulting generator).
    :param flat_share:
        Sets the share of the `step_size` that is flat. The hill will be stretched accordingly.
    """
    flat_range = int(flat_share * step_size)
    hill_range = step_size - flat_range
    for _ in range(flat_range):
        yield 0
    for index in range(hill_range):
        yield (1 + math.cos(2 * math.pi * (index / hill_range) + math.pi)) / 2


if __name__ == '__main__':
    import sys
    from PySide6.QtWidgets import QMainWindow, QApplication

    app = QApplication(sys.argv)
    win = QMainWindow()
    jumpy_dots = JumpyDots(100, 10, QColor(55, 55, 55))
    win.setCentralWidget(jumpy_dots)
    win.show()
    sys.exit(app.exec())
