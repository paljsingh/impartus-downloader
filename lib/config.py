import pathlib

from envyaml import EnvYAML
import yaml
import enum


class ConfigType(enum.Enum):
    """
    enum for configuration types.
    """
    CREDENTIALS = 1
    MAPPINGS = 2
    IMPARTUS = 3


class Config:
    """
    class for loading configurations.
    """
    config_maps = {
        ConfigType.CREDENTIALS: {'filepath': 'etc/creds.conf', 'method': 'yaml'},
        ConfigType.MAPPINGS: {'filepath': 'etc/mappings.conf', 'method': 'yaml'},
        ConfigType.IMPARTUS: {'filepath': 'etc/impartus.conf', 'method': 'envyaml'},
    }
    configs = dict()

    @classmethod
    def load(cls, config_type: ConfigType):
        # keep only 1 config object per file.
        if cls.configs.get(config_type):
            return cls.configs[config_type]

        method = cls.config_maps[config_type]['method']
        this_dir = pathlib.Path(__file__).parent.resolve()
        if method == 'envyaml':
            cls.configs[config_type] = EnvYAML('{}/../{}'.format(this_dir, cls.config_maps[config_type]['filepath']), strict=False)
        else:
            with open('{}/../{}'.format(this_dir, cls.config_maps[config_type]['filepath']), 'r') as file:
                cls.configs[config_type] = yaml.load(file, Loader=yaml.FullLoader) or {}
        return cls.configs[config_type]

    @classmethod
    def save(cls, config_type: ConfigType):
        if config_type not in cls.config_maps.keys():
            return
        with open(cls.config_maps[config_type]['filepath'], 'w') as outfile:
            yaml.dump(cls.configs[config_type], outfile, default_flow_style=False, default_style="'")
