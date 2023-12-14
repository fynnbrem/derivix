from typing import Optional

from PySide6.QtCore import QThreadPool, QRunnable, Signal, QObject, QTimer
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QWidget, QLineEdit, QFrame, QGridLayout, QPushButton

from deriver import latex_to_svg
from utils import MutableBool

app = QApplication()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        wid = QWidget()
        self.setCentralWidget(wid)
        wid.setLayout(QGridLayout())

        self.content()
        self.place()
        self.style()
        self.preset()
        self.control()

    def content(self):
        self.formula_input = QLineEdit()
        self.derive_button = QPushButton()
        self.formula_display = QLabel()

    def place(self):
        self.layout_.addWidget(self.formula_input, 1, 1)
        self.layout_.addWidget(self.derive_button, 1, 2)
        self.layout_.addWidget(self.formula_display, 2, 1, 1, 2)

    def style(self):
        self.formula_display.setBaseSize(100, 100)
        self.formula_display.setFrameShape(QFrame.Shape.Box)

    def preset(self):
        self.formula_input.setPlaceholderText("Enter your formula")
        self.derive_button.setText("Derive")
        self.formula_display.setText("Your formula will be shown here")

    def control(self):
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
            self.worker.signals.finished.connect(self.safe_set_image)
            self.thread_pool.start(self.worker)

        self.image_timer.timeout.connect(start_render)
        self.formula_input.textChanged.connect(queue_render)


    def safe_set_image(self, svg: Optional[str]):
        if svg != "":
            self.set_image(svg)

    def set_image(self, svg: str):
        pix = QPixmap(svg)
        self.formula_display.setText("")
        self.formula_display.setPixmap(pix)



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
