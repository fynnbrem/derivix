![Product Banner](https://github.com/fynnbrem/derivix/blob/master/data/images/banner.png)

# Introduction
![Sample of formula generation (light mode)](https://github.com/fynnbrem/derivix/blob/master/data/images/introduction-light.png#gh-light-mode-only)
![Sample of formula generation (dark mode)](https://github.com/fynnbrem/derivix/blob/master/data/images/introduction-dark.png#gh-dark-mode-only)

_derivix_ is a small programm to help with generating and handling complex formulas for gaussian uncertainty.

All that is required is the root formula
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
- During execution, there might be Pop-Ups that ask you for package installation. These are managed by your LaTeX distribution and indicate that you lack a LaTeX-package required for this app.
