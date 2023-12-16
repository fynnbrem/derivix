import logging
from pathlib import Path
from typing import Optional, Literal

from PySide6.QtCore import QThreadPool, QRunnable, Signal, QObject, QTimer
from PySide6.QtGui import QPixmap, Qt, QIcon
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QWidget, QLineEdit, QFrame, QGridLayout, QPushButton, \
    QBoxLayout

from deriver import latex_to_svg
from gui_elements.abstracts import WidgetControl
from gui_elements.animations import JumpyDots
from utils import MutableBool

app = QApplication()


class FormulaDisplay(QLabel, WidgetControl):
    default_height = 60
    default_width = 240
    loading_animation_base = lambda: JumpyDots(3, 8, Qt.GlobalColor.darkGray)
    loading_animation: Optional[JumpyDots]
    mode: Literal["s", "l", "d", "e"]

    def __init__(self):
        super().__init__()
        self.setLayout(QBoxLayout(QBoxLayout.Direction.TopToBottom))
        self.layout_.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.init_widget()
        self.standby_mode()

    def init_positions(self):
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def init_content(self):
        self.loading_animation = None

    def init_style(self):
        self.setFrameShape(QFrame.Shape.Box)
        self.setMinimumWidth(self.default_width)  # The height is set by the individual modes.

    @property
    def layout_(self) -> QBoxLayout:
        return self.layout()

    def loading_mode(self):
        # ↓ Prevent resetting the loading animation if it is already running.
        if self.mode == "l":
            return
        self.mode = "l"
        self.clear()
        self.loading_animation = self.__class__.loading_animation_base()
        self.layout_.addWidget(self.loading_animation)

    def display_mode(self, svg: Optional[str]):
        self.mode = "d"
        self.clear()
        if svg == "" or svg is None:
            return
        pix = QPixmap(svg)
        self.setPixmap(pix)
        self.setFixedHeight(int(pix.height() * 1.1))

    def standby_mode(self):
        self.mode = "s"
        self.clear()
        self.setText("Your formula will be shown here")

    def error_mode(self, err: Exception):
        self.clear()
        self.mode = "e"
        error_text = str(err)
        if isinstance(err, RuntimeError):
            text = "Unable to parse formula:\n"
            if "Undefined control sequence" in error_text:
                text += "Undefined control sequence in formula."
            else:
                text += "Unknown error."
                logging.error(err)
        else:
            text = f"An unexpected error occurred during parsing:\n{type(err)}"
            logging.error(err)

        self.setText(text)

    def clear(self):
        self.setText("")
        self.setFixedHeight(self.default_height)
        if self.loading_animation is not None:
            self.loading_animation.deleteLater()
            self.loading_animation = None
        self.setPixmap(QPixmap())


class MainWindow(QMainWindow, WidgetControl):
    def __init__(self):
        super().__init__()

        wid = QWidget()
        self.setCentralWidget(wid)
        wid.setLayout(QGridLayout())

        self.init_widget()

    def init_content(self):
        self.formula_input = QLineEdit()
        self.derive_button = QPushButton()
        self.formula_display = FormulaDisplay()

    def init_positions(self):
        self.layout_.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.layout_.addWidget(self.formula_input, 1, 1)
        self.layout_.addWidget(self.derive_button, 1, 2)
        self.layout_.addWidget(self.formula_display, 2, 1, 1, 2)

    def init_style(self):
        self.setWindowTitle("derivix")
        self.setWindowIcon(QIcon(str(Path() / "res" / "images" / "icon.png")))

    def init_values(self):
        self.formula_input.setPlaceholderText("Enter your formula")
        self.derive_button.setText("Derive")

    def init_control(self):
        self.thread_pool = QThreadPool()
        self.worker: Optional[ImageWorker] = None
        self.image_timer = QTimer()
        self.image_timer.setInterval(1000)
        self.image_timer.setSingleShot(True)

        def queue_render():

            if self.formula_input.text().strip() == "":
                self.formula_display.standby_mode()
                self.image_timer.stop()
            else:
                logging.debug(f"Queueing render")
                self.formula_display.loading_mode()
                # ↑ Even if a render did not start already, start loading mode as the display is outdated.
                # Only when a render finishes, it will return to display mode.
                self.image_timer.start()

        def start_render():
            logging.debug("Starting render")
            if self.worker is not None:
                self.worker.terminate()
            self.worker = ImageWorker(self.formula_input.text())
            self.worker.signals.finished.connect(self.set_image)
            self.worker.signals.error.connect(self.formula_display.error_mode)
            self.thread_pool.start(self.worker)

        self.image_timer.timeout.connect(start_render)
        self.formula_input.textChanged.connect(queue_render)

    def set_image(self, svg: Optional[str]):
        self.formula_display.display_mode(svg)

    @property
    def layout_(self) -> QGridLayout:
        return self.centralWidget().layout()


class WorkerSignals(QObject):
    finished = Signal(str)
    error = Signal(Exception)


class ImageWorker(QRunnable):
    def __init__(self, formula: str):
        super().__init__()
        self.signals = WorkerSignals()
        self.formula = formula
        self._force_terminate = MutableBool(False)

    def run(self) -> None:
        try:
            svg_file = latex_to_svg(self.formula, self._force_terminate)
            if svg_file is not None and not self._force_terminate.state:
                signal = str(svg_file)
            else:
                signal = ""

            self.signals.finished.emit(str(signal))
        except Exception as err:
            self.signals.error.emit(err)

    def terminate(self):
        self._force_terminate.state = True


if __name__ == '__main__':
    win = MainWindow()
    win.show()
    app.exec()
