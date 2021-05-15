import logging
from typing import Dict

from lib.config import Config, ConfigType


class ColorSchemes:

    def __init__(self):
        self.components = list()

    @classmethod
    def get_color_schemes(cls):
        color_schemes = dict()
        colorschemes_config = Config.load(ConfigType.COLORSCHEMES)
        for k in colorschemes_config.keys():
            # skip non-dict keys, skip nested keys
            if type(colorschemes_config[k]) == dict and '.' not in k:
                color_schemes[k] = colorschemes_config[k]
        return color_schemes

    def register_component(self, component: object) -> bool:
        logger = logging.getLogger(ColorSchemes.__name__)
        func_name = 'set_colorscheme'
        if not type(getattr(component, func_name) == 'func'):
            logger.warning('{} has no function named {}.'.format(component.__class__.__name__, func_name))
            return False
        self.components.append(component)

    def set_colorscheme(self, cs: Dict):
        for comp in self.components:
            comp.set_colorscheme(cs)
