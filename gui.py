import logging
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QThreadPool, QRunnable, Signal, QObject, QTimer
from PySide6.QtGui import Qt, QIcon
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QLineEdit, QGridLayout, QPushButton, QLabel

from deriver import latex_to_svg
from gui_elements.abstracts import WidgetControl
from gui_elements.formula_display import FormulaDisplay
from gui_elements.prefabs import LabelWithLine
from gui_elements.transfer_widget import TransferWidget
from res import ToolIcons
from utils import MutableBool

app = QApplication()


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
        self.formula_display = FormulaDisplay(show_copy=False)

        self.symbol_manager = TransferWidget()

    def init_positions(self):
        layout = self.layout_
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        layout.addWidget(LabelWithLine(
            "<h3>Formula</h3>", pixmap=ToolIcons.var_f.get_pixmap()),
            layout.rowCount(), 1, 1, -1
        )

        layout.addWidget(QLabel("f ="), layout.rowCount(), 1)
        layout.addWidget(self.formula_input, layout.rowCount() - 1, 2)
        layout.addWidget(self.derive_button, layout.rowCount() - 1, 3)
        layout.addWidget(self.formula_display, layout.rowCount(), 1, 1, -1)

        layout.addWidget(LabelWithLine(
            "<h3>Symbols</h3>", pixmap=ToolIcons.var_x.get_pixmap()),
            layout.rowCount(), 1, 1, -1
        )
        layout.addWidget(self.symbol_manager, layout.rowCount(), 1, 1, -1)
        layout.addWidget(LabelWithLine(
            "<h3>Error Formula</h3>", pixmap=ToolIcons.var_c_delta.get_pixmap()),
            layout.rowCount(), 1, 1, -1
        )

        layout.addWidget(LabelWithLine(
            "<h3>Partial Derivations</h3>", pixmap=ToolIcons.var_v_delta.get_pixmap()),
            layout.rowCount(), 1, 1, -1
        )

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
            self.worker.signals.finished.connect(lambda p: self.set_image(*p))
            self.worker.signals.error.connect(self.formula_display.error_mode)
            self.thread_pool.start(self.worker)

        self.image_timer.timeout.connect(start_render)
        self.formula_input.textChanged.connect(queue_render)

    def set_image(self, svg: Optional[str], formula: Optional[str]):
        self.formula_display.display_mode(svg, formula)

    @property
    def layout_(self) -> QGridLayout:
        return self.centralWidget().layout()


class WorkerSignals(QObject):
    finished = Signal(tuple)
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

            self.signals.finished.emit((signal, self.formula))
        except Exception as err:
            self.signals.error.emit(err)

    def terminate(self):
        self._force_terminate.state = True


if __name__ == '__main__':
    win = MainWindow()
    win.show()
    app.exec()
