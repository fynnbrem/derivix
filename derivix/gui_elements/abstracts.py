class WidgetControl:
    """An abstract class to streamline and group various widget configuration operations.
    When inheriting from this, all operations should be performed in the abstract methods provided by this class.

    The constructor of the inheriting class should be minimal, but must call `self.init_widget()`
    to invoke the execution of all the implementations of this class' abstract methods.


    Abstract methods provided by this class (In sequential order):
    - `init_content`
        Perform minimal initialization of widgets.
    - `init_positions`
        Place each widget in the layout.
    - `init_style`
        Apply style to the widgets.
    - `init_values`
        Set specific (default) values for the widgets.
    - `init_control`
        Configure internal control logic for the widgets.
    """
    def init_widget(self):
        self.init_content()
        self.init_positions()
        self.init_style()
        self.init_values()
        self.init_control()

    def init_content(self):
        ...

    def init_positions(self):
        ...

    def init_style(self):
        ...

    def init_values(self):
        ...

    def init_control(self):
        ...
