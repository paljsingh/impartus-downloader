import tkinter as tk

from lib.config import Config, ConfigType
from ui.data import Columns


class Variables(object):

    _lecture_quality_var = None
    _display_columns_vars = None
    _colorscheme_var = None

    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            orig = super(Variables, cls)
            cls._instance = orig.__new__(cls)
            cls._colorscheme_var = tk.StringVar(None, None)
            _cs_config = Config.load(ConfigType.COLORSCHEMES)
            cls._colorscheme_var.set(_cs_config['default'])

            cls._display_columns_vars = {
                k: tk.IntVar(None, 1) for k, v in Columns.display_columns.items()
            }

            cls._lecture_quality_var = tk.StringVar(None, Config.load(ConfigType.IMPARTUS)['video_quality'])
        return cls._instance

    @classmethod
    def colorscheme_var(cls, value=None):
        if value:
            cls._colorscheme_var.set(value)
        else:
            return cls._colorscheme_var

    @classmethod
    def display_columns_vars(cls, name=None):
        if name:
            return cls._display_columns_vars[name]
        else:
            return cls._display_columns_vars

    @classmethod
    def lecture_quality_var(cls, lecture_quality=None):
        if lecture_quality:
            cls._lecture_quality_var.set(lecture_quality)
        else:
            return cls._lecture_quality_var
