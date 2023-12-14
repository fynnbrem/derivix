from typing import Optional

from PySide6.QtCore import QThreadPool, QRunnable, Signal, QObject, QTimer
from PySide6.QtGui import QPixmap, Qt
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QWidget, QLineEdit, QFrame, QGridLayout, QPushButton, \
    QBoxLayout

from deriver import latex_to_svg
from gui_elements.abstracts import WidgetControl
from gui_elements.animations import JumpyDots
from utils import MutableBool

app = QApplication()


class FormulaDisplay(QLabel, WidgetControl):
    loading_animation_base = lambda: JumpyDots(3, 8, Qt.GlobalColor.darkGray)
    loading_animation: Optional[JumpyDots]

    def __init__(self):
        super().__init__()
        self.setLayout(QBoxLayout(QBoxLayout.Direction.TopToBottom))
        self.layout_.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.init_widget()
        self.loading_mode()

    def init_content(self):
        self.loading_animation = None

    def init_style(self):
        self.setFrameShape(QFrame.Shape.Box)
        self.setMinimumSize(100, 60)

    def init_values(self):
        self.setText("Your formula will be shown here")

    @property
    def layout_(self) -> QBoxLayout:
        return self.layout()

    def loading_mode(self):
        self.clear()
        self.setText("")
        self.loading_animation = self.__class__.loading_animation_base()
        self.layout_.addWidget(self.loading_animation)

    def formula_mode(self, svg: Optional[str]):
        self.clear()
        if svg == "" or svg is None:
            return
        pix = QPixmap(svg)
        self.setPixmap(pix)
        self.setFixedSize(pix.size())

    def clear(self):
        self.setText("")
        if self.loading_animation is not None:
            self.loading_animation.hide()
            self.loading_animation.destroy()


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
        self.layout_.addWidget(self.formula_input, 1, 1)
        self.layout_.addWidget(self.derive_button, 1, 2)
        self.layout_.addWidget(self.formula_display, 2, 1, 1, 2)

    def init_style(self):
        ...

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
            print(f"Queueing render.")
            self.image_timer.start()

        def start_render():
            print(f"Starting render.")
            if self.worker is not None:
                self.worker.terminate()
            self.worker = ImageWorker(self.formula_input.text())
            self.worker.signals.finished.connect(self.set_image)
            self.thread_pool.start(self.worker)

        self.image_timer.timeout.connect(start_render)
        self.formula_input.textChanged.connect(queue_render)

    def set_image(self, svg: Optional[str]):
        self.formula_display.formula_mode(svg)

    @property
    def layout_(self) -> QGridLayout:
        return self.centralWidget().layout()


class WorkerSignals(QObject):
    finished = Signal(str)
    error = Signal(str)


class ImageWorker(QRunnable):
    def __init__(self, formula: str):
        super().__init__()
        self.signals = WorkerSignals()
        self.formula = formula
        self._force_terminate = MutableBool(False)

    def run(self) -> None:
        svg_file = latex_to_svg(self.formula, self._force_terminate)
        if svg_file is not None and not self._force_terminate.state:
            signal = str(svg_file)
        else:
            signal = ""

        self.signals.finished.emit(str(signal))

    def terminate(self):
        self._force_terminate.state = True


if __name__ == '__main__':
    win = MainWindow()
    win.show()
    app.exec()
