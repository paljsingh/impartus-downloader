from envyaml import EnvYAML
import yaml


class Config:

    config_maps = {
        'creds': {'filepath': 'etc/creds.conf', 'method': 'yaml'},
        'colorschemes': {'filepath': 'etc/color-schemes.conf', 'method': 'yaml'},
        'impartus': {'filepath': 'etc/impartus.conf', 'method': 'envyaml'},
        'mappings': {'filepath': 'etc/mappings.conf', 'method': 'yaml'},
    }
    configs = dict()

    @classmethod
    def load(cls, filetype):
        # keep only 1 config object per file.
        if cls.configs.get(filetype):
            return cls.configs[filetype]

        method = cls.config_maps[filetype]['method']
        if method == 'envyaml':
            cls.configs[filetype] = EnvYAML(cls.config_maps[filetype]['filepath'], strict=False)
        else:
            with open(cls.config_maps[filetype]['filepath'], 'r') as file:
                cls.configs[filetype] = yaml.load(file, Loader=yaml.FullLoader) or {}
        return cls.configs[filetype]

    @classmethod
    def save(cls, filetype):
        if filetype not in cls.config_maps.keys():
            return
        with open(cls.config_maps[filetype]['filepath'], 'w') as outfile:
            yaml.dump(cls.configs[filetype], outfile, default_flow_style=False, default_style="'")
