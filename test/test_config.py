import pytest


def test_load_yaml(mocker):
    config_maps_yaml = {'creds': 'etc/creds.conf',
                        'mappings': 'etc/mappings.conf',
                        'colorschemes': 'etc/colorschemes.conf'
                        }
    config_maps_envyaml = {'impartus': 'etc/impartus.conf'}
    mock_yaml = mocker.patch('yaml.load')
    mock_builtins_open = mocker.patch('builtins.open')
    mock_envyaml = mocker.patch('envyaml.EnvYAML')

    mock_builtins_open.return_value.side_effect = [v for v in config_maps_yaml.values()]

    from app.config import Config
    import yaml

    for filetype, val in config_maps_yaml.items():
        Config.load(filetype)
        assert mock_yaml.call_count == 1
        mock_yaml.aseert_call_once_with(val, Loader=yaml.FullLoader)
        mock_yaml.reset_mock()

    # a second call should not result in config load.
    for filetype, val in config_maps_yaml.items():
        Config.load(filetype)
        assert mock_yaml.call_count == 0
        mock_yaml.reset_mock()

    for filetype, item in config_maps_envyaml.items():
        Config.load(filetype)
        assert mock_envyaml.call_count == 1
        mock_envyaml.reset_mock()

    # a second call should not result in config load.
    for filetype, item in config_maps_yaml.items():
        Config.load(filetype)
        assert mock_envyaml.call_count == 0
        mock_envyaml.reset_mock()
