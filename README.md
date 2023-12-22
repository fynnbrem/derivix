![](https://github.com/fynnbrem/derivix/blob/master/res/images/banner.png?raw=True)

# Introduction
A small programm to help with generating and handling complex formulas for gaussian uncertainty.

All that is required is the root formula.
The partial derivations and the resulting formula for gaussian uncertainty will be automatically determined.

# Features
- Input your formula in LaTeX format
- Easy copy & paste the determined formula in LaTeX format
- Actual rendered view of all formulas
- View every partial derivation individually if needed
- Calculate an actual value by inputting the values for the variables

# Attribution
- The mathematical processing heavily relies on the great work of [SymPy](https://www.sympy.org/en/index.html)
- The rendering is done by [matplotlib](https://matplotlib.org)
- The user interface is written in Qt with the [PySide6](https://wiki.qt.io/Qt_for_Python) framework


# Notes
- Requires a LaTeX distribution on your local machine to run
    - Check out [MiKTeX](https://miktex.org) for a dynamic, minimal distribution
