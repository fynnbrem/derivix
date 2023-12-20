from enum import Enum
from pathlib import Path

from PySide6.QtGui import QPixmap, Qt


class Images(Enum):
    def get_pixmap(self, width: int | None = None) -> QPixmap:
        if width is None:
            width = self.__class__.get_default_width()
        pix = QPixmap(self.get_path_string())
        pix = pix.scaledToWidth(width, Qt.TransformationMode.SmoothTransformation)
        return pix

    def get_path(self) -> Path:
        return self.__class__.get_base_folder() / self.value

    def get_path_string(self, absolute=True) -> str:
        if absolute:
            return str(self.get_path().absolute())
        else:
            return str(self.get_path())

    @classmethod
    def validate_existence(cls):
        for member in cls:
            assert member.get_path().exists(), f"The file \"{member.get_path_string()}\" was not found."

    @classmethod
    def get_default_width(cls):
        raise NotImplementedError("Implement `get_default_width()` if you do not specify a `width`.")

    @classmethod
    def get_base_folder(cls):
        raise NotImplementedError("Implement `get_base_folder()` to specify the folder of the icons.")



class ToolIcons(Images):
    """A collection of small, simple icons used to indicate certain functions."""

    var_x = "var_x.png"
    var_f = "var_f.png"
    var_c_delta = "var_c_delta.png"
    var_v_delta = "var_v_delta.png"
    copy = "copy.png"

    @classmethod
    def get_default_width(cls):
        return 16

    @classmethod
    def get_base_folder(cls):
        return Path() / "res" / "images"

ToolIcons.validate_existence()
