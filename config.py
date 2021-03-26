from envyaml import EnvYAML


class Config:

    config = {}

    @classmethod
    def load(cls, file='yaml.conf'):
        if not cls.config.get(file):
            cls.config[file] = EnvYAML(file, strict=False)
        return cls.config[file]
