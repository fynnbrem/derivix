import logging
import os
from multiprocessing import Pool
from pathlib import Path
from threading import Thread
from typing import Optional, Iterable, Callable

import sympy.core.symbol
from PySide6.QtCore import QThreadPool, QRunnable, Signal, QObject, QTimer, QMetaObject
from PySide6.QtGui import Qt, QIcon
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QLineEdit, QGridLayout, QPushButton, QLabel
from sympy import Mul
from sympy.core import symbol
from sympy.parsing.latex import parse_latex

from derivix.deriver import latex_to_svg, Formula, derive_by_symbols, as_gaussian_uncertainty
from derivix.gui_elements.abstracts import WidgetControl
from derivix.gui_elements.cards import CardData
from derivix.gui_elements.formula_display import FormulaDisplay
from derivix.gui_elements.prefabs import LabelWithLine
from derivix.gui_elements.transfer_widget import TransferWidget, Filter
from data import ToolIcons, OtherImages
from derivix.utils import MutableBool
from derivix.utils.env import TEMP_PATH
from derivix.utils.math_util import CONSTANTS
from derivix.utils.workers import ExceptionWorkerSignals, ExceptionWorker, emit_exception, raise_exc


class MainWindow(QMainWindow, WidgetControl):
    def __init__(self):
        super().__init__()

        wid = QWidget()
        self.setCentralWidget(wid)
        wid.setLayout(QGridLayout())

        self.init_widget()

    def enqueue(self, func: Callable[[], None]):
        QMetaObject.invokeMethod(self, func, Qt.ConnectionType.QueuedConnection)

    def init_content(self):

        self.formula_input = QLineEdit()
        self.derive_button = QPushButton()
        self.input_formula = FormulaDisplay(show_copy=False)
        self.adv_formula = FormulaDisplay()

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
        layout.addWidget(self.input_formula, layout.rowCount(), 1, 1, -1)

        layout.addWidget(LabelWithLine(
            "<h3>Symbols</h3>", pixmap=ToolIcons.var_x.get_pixmap()),
            layout.rowCount(), 1, 1, -1
        )
        layout.addWidget(self.symbol_manager, layout.rowCount(), 1, 1, -1)

        layout.addWidget(LabelWithLine(
            "<h3>Error Formula</h3>", pixmap=ToolIcons.var_delta_c.get_pixmap()),
            layout.rowCount(), 1, 1, -1
        )
        layout.addWidget(self.adv_formula, layout.rowCount(), 1, 1, -1)

        layout.addWidget(LabelWithLine(
            "<h3>Partial Derivations</h3>", pixmap=ToolIcons.var_delta_v.get_pixmap()),
            layout.rowCount(), 1, 1, -1
        )

    def init_style(self):
        self.setWindowTitle("derivix")
        self.setWindowIcon(QIcon(OtherImages.app_icon.get_path_string()))

    def init_values(self):
        self.formula_input.setPlaceholderText("Enter your formula")
        self.derive_button.setText("Derive")

    def init_control(self):
        self.derive_button.clicked.connect(self.gen_adv_formula)

        self.thread_pool = QThreadPool()
        self.worker: Optional[ImageWorker] = None
        self.image_timer = QTimer()
        self.image_timer.setInterval(1000)
        self.image_timer.setSingleShot(True)

        def queue_render():
            self.clear_base_formula()
            if self.formula_input.text().strip() == "":
                self.input_formula.standby_mode()
                self.image_timer.stop()
            else:
                logging.debug(f"Queueing render")
                self.input_formula.loading_mode()
                # ↑ Even if a render did not start already, start loading mode as the display is outdated.
                # Only when a render finishes, it will return to display mode.
                self.image_timer.start()

        def start_render():
            logging.debug("Starting render")
            if self.worker is not None:
                self.worker.terminate()

            latex = self.formula_input.text()
            self.worker = ImageWorker([latex])

            self.worker.signals.finished.connect(lambda svgs, *, l=latex: push_formula(svgs[0], l))
            self.worker.signals.error.connect(self.input_formula.error_mode)
            self.thread_pool.start(self.worker)

        def push_formula(svg_file: Path, latex: str):
            formula = Formula(svg_file=svg_file, formula=parse_latex(latex), latex=latex)
            self.push_base_formula(formula)

        self.image_timer.timeout.connect(start_render)
        self.formula_input.textChanged.connect(queue_render)

    def clear_base_formula(self):
        for container in self.symbol_manager.containers.values():
            container.remove_all()

    def push_base_formula(self, formula: Formula):
        self.formula = formula
        self.input_formula.display_mode(formula.svg_file, formula.latex)
        cards = create_cards_from_symbols(formula.formula.free_symbols)
        for card in cards:
            self.symbol_manager.containers[card.filter].add_card(card)

    def gen_adv_formula(self):
        self.adv_formula.loading_mode()

        cards = list(self.symbol_manager.containers[Filter.Include].cards)
        symbols = [c.symbol for c in cards]

        worker = DeriveWorker(self.formula.formula, symbols)
        worker.signals.error.connect(raise_exc)

        def finish(*, w=worker):
            derived_formulas = [sympy.latex(f) for f in w.derived_formulas]
            self.render_adv_formula(w.gaussian_formula, derived_formulas)

        worker.signals.finished.connect(finish)

        self.thread_pool.start(worker)

    def render_adv_formula(self, gaussian_formula: str, derived_formulas: Iterable[str]):
        """Renders the formulas produced by `gen_adv_formula`"""
        worker = ImageWorker([gaussian_formula])
        worker.signals.error.connect(raise_exc)

        def finish(svg_files: tuple[Path]):
            self.adv_formula.display_mode(svg_files[0], gaussian_formula)

        worker.signals.finished.connect(finish)

        self.thread_pool.start(worker)





    @property
    def layout_(self) -> QGridLayout:
        return self.centralWidget().layout()


class DeriveWorkerSignals(ExceptionWorkerSignals):
    finished = Signal()


class DeriveWorker(ExceptionWorker):
    def __init__(self, formula: Mul, symbols: Iterable[symbol]):
        super().__init__()
        self.signals = DeriveWorkerSignals()

        self.formula = formula
        self.symbols = symbols

    @emit_exception
    def run(self) -> None:
        self.derived_formulas = derive_by_symbols(self.formula, self.symbols)
        self.gaussian_formula = as_gaussian_uncertainty(self.derived_formulas)
        self.signals.finished.emit()


class ImageWorkerSignals(ExceptionWorkerSignals):
    finished = Signal(tuple)


class ImageWorker(ExceptionWorker):
    def __init__(self, formulas: list[str]):
        super().__init__()
        self.signals = ImageWorkerSignals()
        self.formulas = formulas
        self._force_terminate = False

    @emit_exception
    def run(self) -> None:
        svg_files = [latex_to_svg(formula, TEMP_PATH) for formula in self.formulas]
        # ↑ Could be upgraded to use multiprocessing, but right now this causes issues with matlab.
        if not self._force_terminate:
            self.signals.finished.emit(tuple(svg_files))

    def terminate(self):
        self._force_terminate = True


def create_cards_from_symbols(symbols: set[sympy.core.symbol.Symbol]) -> list[CardData]:
    cards = list()
    for symbol in symbols:
        try:
            value = CONSTANTS[symbol.name]
        except KeyError:
            value = None
        card = CardData(symbol, Filter.Include)
        card.primary.v = value
        card.secondary.v = None
        cards.append(card)
    return cards


if __name__ == '__main__':
    app = QApplication()

    win = MainWindow()
    win.show()
    app.exec()
