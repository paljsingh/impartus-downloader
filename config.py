from envyaml import EnvYAML


class Config:

    config = EnvYAML("yaml.conf", strict=False)

    @classmethod
    def load(cls):
        return cls.config
