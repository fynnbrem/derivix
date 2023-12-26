import logging
import tempfile
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Iterable

import matplotlib.pyplot as plt
import sympy
from matplotlib import rc
from sympy import diff, Mul, latex, Symbol
from sympy.parsing.latex import parse_latex

from utils import MutableBool

logging.basicConfig(level=logging.INFO)
TEMP = tempfile.TemporaryDirectory()
TEMP_PATH = Path(TEMP.name)
logging.info(f"Created temporary folder at: `{TEMP_PATH}`")


@dataclass
class Formula():
    formula: sympy.core.mul.Mul
    latex: str
    svg_file: Path


def get_derivations(formula: str):
    formula = parse_latex(formula)
    symbols = sorted(formula.free_symbols, key=lambda sym: sym.name)
    for sym in symbols:
        diff_formula = diff(formula, sym)
        print(f"f_d{sym}: {sympy.latex(diff_formula)}")


def get_symbols(formula: str):
    formula = parse_latex(formula)
    symbols = sorted(formula.free_symbols, key=lambda sym: sym.name)

    return symbols


def as_gaussian_uncertainty(formulas: dict[Symbol, Mul]) -> str:
    """Concatenates all formulas to a single formula expressing them all as component of gaussian uncertainty.

    This just concatenates them according to gauss, the derivation to get the corresponding
    formulas must be done beforehand.

    `formulas` is expected to be a dict where for each formula, the key is the symbol it was partially derived by.
    If `formulas` is empty, the resulting formula will be "0".
    """
    latex_formulas = list()
    if len(formulas) != 0:
        for symbol, formula in formulas.items():
            # region: Format each formula:
            # 1. Add the corresponding delta factor
            # 2. Put it in brackets
            # 3. Square it
            formula = latex(formula) + rf"\cdot \Delta {symbol.name}"
            formula = r"\left(" + formula + r"\right)^2"
            latex_formulas.append(formula)
            # endregion
        formula_body = (" + ".join(latex_formulas))
        formula_body = r"\sqrt{" + formula_body + "}"
    else:
        formula_body = "0"

    full_formula = r"\Delta f =  " + formula_body
    return full_formula


def derive_by_symbols(formula: Mul, symbols: Iterable[Symbol]) -> dict[Symbol, Mul]:
    derivations = dict()
    for symbol in symbols:
        derivations[symbol] = diff(formula, symbol)
    return derivations


def latex_to_svg(formula, terminator: MutableBool = MutableBool(False)) -> Optional[Path]:
    rc('text', usetex=True)

    if terminator.state:
        return None
    fig = plt.figure(figsize=(0.01, 0.01))
    fig.text(0, 0, f"${formula}$", fontsize=72)
    file = TEMP_PATH / (str(uuid.uuid4()) + ".svg")
    if terminator.state:
        plt.close(fig)
        return None

    fig.savefig(file, format="svg", transparent=True, bbox_inches='tight', pad_inches=0.1)
    plt.close(fig)
    if terminator.state:
        return None

    return file


if __name__ == '__main__':
    t_formula = r"x^2 \cdot \frac{e y}{z \cdot \pi \cdot \cos(v) cos(x)}"
    get_derivations(t_formula)
    # latex_to_svg(t_formula)
    print(get_symbols("w a d e d x d i"))
