from lib.config import Config, ConfigType


class Mappings:

    @staticmethod
    def update_mappings(mapping_name, old_value, new_value):
        mappings_config = Config.load(ConfigType.MAPPINGS)
        if not mappings_config.get(mapping_name):
            mappings_config[mapping_name] = {}
        mappings_config.get(mapping_name)[old_value] = new_value
        Config.save(ConfigType.MAPPINGS)
