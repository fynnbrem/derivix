import tempfile
import uuid
from pathlib import Path
from typing import Callable, Optional

from sympy import diff
import sympy
import matplotlib.pyplot as plt
from matplotlib import rc
from io import BytesIO

from sympy.parsing.latex import parse_latex

from utils import MutableBool

TEMP = tempfile.TemporaryDirectory()
TEMP_PATH = Path(TEMP.name)


def get_derivations(formula: str):
    formula = parse_latex(formula)
    symbols = sorted(formula.free_symbols, key=lambda sym: sym.name)
    for sym in symbols:
        diff_formula = diff(formula, sym)
        print(f"f_d{sym}: {sympy.latex(diff_formula)}")


def latex_to_svg(formula, terminator: MutableBool = MutableBool(False)) -> Optional[Path]:
    rc('text', usetex=True)

    if terminator.state:
        return None
    fig = plt.figure(figsize=(0.01, 0.01))
    fig.text(0, 0, f"${formula}$", fontsize=72)
    file_name = str(uuid.uuid4()) + ".svg"
    file = TEMP_PATH / file_name
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
    latex_to_svg(t_formula)
