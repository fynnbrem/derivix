from PySide6.QtCore import QThreadPool, QRunnable, Signal, QObject
from PySide6.QtWidgets import QApplication


class ExceptionWorkerSignals(QObject):
    """A minimal signal-class to be used with the `ExceptionWorker`.
    Only provides the `error` signal by itself, which will be used by the exception worker.
    """
    error = Signal(Exception)


def emit_exception(func):
    def inner(inst: "ExceptionWorker", *args, **kwargs):
        try:
            func(inst, *args, **kwargs)
        except Exception as err:
            inst.handle_exception(err)

    return inner


class ExceptionWorker(QRunnable):
    """A base class when using `QRunnable`. This class provides a streamlined way to handle Exceptions:
    - The `handle_exception()`-Method to customize in-thread error handling. By default, the error gets emitted via
        the `error` signal.
    - Methods that are decorated by the `@emit_exception`-Decorator will propagate the error to `handle_exception()`.
        - The decorator can be found in this module.

    When defining a Signals-class for a subclass, use the corresponding `ExceptionWorkerSignals` class as base.
    """

    def handle_exception(self, err: Exception):
        self.signals.error.emit(err)


def raise_exc(err: Exception):
    raise RuntimeError("Thready") from err


if __name__ == '__main__':
    app = QApplication()
    t_threadpool = QThreadPool()
    t_worker = ExceptionWorker()
    t_worker.signals.error.connect(raise_exc)
    t_threadpool.start(t_worker)
    app.exec()
