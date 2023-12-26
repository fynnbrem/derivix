import logging
from itertools import chain
from pathlib import Path
from typing import Optional

import sympy.core.symbol
from PySide6.QtCore import QThreadPool, QRunnable, Signal, QObject, QTimer
from PySide6.QtGui import Qt, QIcon
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QLineEdit, QGridLayout, QPushButton, QLabel
from sympy import Mul
from sympy.parsing.latex import parse_latex

from deriver import latex_to_svg, Formula, derive_by_symbols, as_gaussian_uncertainty
from gui_elements.abstracts import WidgetControl
from gui_elements.cards import CardData
from gui_elements.formula_display import FormulaDisplay
from gui_elements.prefabs import LabelWithLine
from gui_elements.transfer_widget import TransferWidget, Filter
from res import ToolIcons
from utils import MutableBool
from utils.math_util import CONSTANTS

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
        self.input_formula = FormulaDisplay(show_copy=False)
        self.error_formula = FormulaDisplay()

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
        layout.addWidget(self.error_formula, layout.rowCount(), 1, 1, -1)

        layout.addWidget(LabelWithLine(
            "<h3>Partial Derivations</h3>", pixmap=ToolIcons.var_delta_v.get_pixmap()),
            layout.rowCount(), 1, 1, -1
        )

    def init_style(self):
        self.setWindowTitle("derivix")
        self.setWindowIcon(QIcon(str(Path() / "res" / "images" / "icon.png")))

    def init_values(self):
        self.formula_input.setPlaceholderText("Enter your formula")
        self.derive_button.setText("Derive")

    def init_control(self):
        self.derive_button.clicked.connect(self.start_derivation)

        self.thread_pool = QThreadPool()
        self.worker: Optional[ImageWorker] = None
        self.image_timer = QTimer()
        self.image_timer.setInterval(1000)
        self.image_timer.setSingleShot(True)

        def queue_render():
            self.clear_primary_formula()
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
            self.worker = ImageWorker(self.formula_input.text())
            self.worker.signals.finished.connect(self.push_primary_formula)
            self.worker.signals.error.connect(self.input_formula.error_mode)
            self.thread_pool.start(self.worker)

        self.image_timer.timeout.connect(start_render)
        self.formula_input.textChanged.connect(queue_render)

    def clear_primary_formula(self):
        for container in self.symbol_manager.containers.values():
            container.remove_all()

    def push_primary_formula(self, formula: Formula):
        self.formula = formula
        self.input_formula.display_mode(formula.svg_file, formula.latex)
        cards = create_cards_from_symbols(formula.formula.free_symbols)
        for card in cards:
            self.symbol_manager.containers[card.filter].add_card(card)
    def start_derivation(self):
        cards = list(self.symbol_manager.containers[Filter.Include].cards)
        derived_formulas = derive_by_symbols(self.formula.formula, [c.symbol for c in cards])
        gaussian_formula = as_gaussian_uncertainty(derived_formulas)
        svg_file = latex_to_svg(gaussian_formula)
        self.error_formula.display_mode(svg_file, gaussian_formula)



    @property
    def layout_(self) -> QGridLayout:
        return self.centralWidget().layout()




class DeriveWorkerSignals(QObject):
    finished = Signal(Formula)
    error = Signal(Exception)

class DeriveWorker(QRunnable):
    def __init__(self, formula: Mul, variables: set[sympy.Symbol]):
        super().__init__()
        self.signals = DeriveWorkerSignals()
        self.formula = formula
        self.variables = variables
        self._force_terminate = MutableBool(False)

    def run(self) -> None:
        try:
            svg_file = latex_to_svg(self.formula, self._force_terminate)
            formula = parse_latex(self.formula)
            formula_data = Formula(svg_file=svg_file, formula=formula, latex=self.formula)
            if not self._force_terminate.state:
                self.signals.finished.emit(formula_data)
        except Exception as err:
            self.signals.error.emit(err)

    def terminate(self):
        self._force_terminate.state = True


class ImageWorkerSignals(QObject):
    finished = Signal(Formula)
    error = Signal(Exception)


class ImageWorker(QRunnable):
    def __init__(self, formula: str):
        super().__init__()
        self.signals = ImageWorkerSignals()
        self.formula = formula
        self._force_terminate = MutableBool(False)

    def run(self) -> None:
        try:
            svg_file = latex_to_svg(self.formula, self._force_terminate)
            formula = parse_latex(self.formula)
            formula_data = Formula(svg_file=svg_file, formula=formula, latex=self.formula)
            if not self._force_terminate.state:
                self.signals.finished.emit(formula_data)
        except Exception as err:
            self.signals.error.emit(err)

    def terminate(self):
        self._force_terminate.state = True

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
    win = MainWindow()
    win.show()
    app.exec()
