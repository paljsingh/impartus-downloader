import pytest


@pytest.fixture
def config_maps_yaml():
    return {'creds': 'etc/creds.conf',
            'mappings': 'etc/mappings.conf',
            'colorschemes': 'etc/colorschemes.conf'
            }


@pytest.fixture
def config_maps_envyaml():
    return {'impartus': 'etc/impartus.conf'}


def test_load_yaml(mocker, config_maps_yaml, config_maps_envyaml):

    mock_yaml = mocker.patch('yaml.load')
    mock_envyaml = mocker.patch('envyaml.EnvYAML')

    mock_builtins_open = mocker.patch('builtins.open')
    mock_builtins_open.return_value.side_effect = [v for v in config_maps_yaml.values()]

    from lib.config import Config
    import yaml

    for filetype, filepath in config_maps_yaml.items():
        Config.load(filetype)
        assert mock_yaml.call_count == 1
        mock_yaml.aseert_call_once_with(filepath, Loader=yaml.FullLoader)
        mock_yaml.reset_mock()

    # a second call should not result in config load.
    for filetype, filepath in config_maps_yaml.items():
        Config.load(filetype)
        assert mock_yaml.call_count == 0
        mock_yaml.reset_mock()

    for filetype, filepath in config_maps_envyaml.items():
        Config.load(filetype)
        assert mock_envyaml.call_count == 1
        mock_envyaml.reset_mock()

    # a second call should not result in config load.
    for filetype, filepath in config_maps_yaml.items():
        Config.load(filetype)
        assert mock_envyaml.call_count == 0
        mock_envyaml.reset_mock()


def test_save(mocker, config_maps_yaml):
    config_dict = {'foo': 'bar', 'foobar': 'foobaz'}

    mocker.patch('yaml.load', return_value=config_dict)
    mock_yaml_dump = mocker.patch('yaml.dump')

    mock_builtins_open = mocker.patch('builtins.open')

    # duplicate each element in list, as we are calling open twice (first with Config.load(), later with Config.save()
    mock_builtins_open.return_value.__enter__.side_effect = [v for v in config_maps_yaml.values() for _ in (0, 1)]

    from lib.config import Config
    for filetype, filepath in config_maps_yaml.items():
        Config.load(filetype)
        Config.save(filetype)
        mock_yaml_dump.aseert_call_once_with(config_dict, filepath, default_flow_style=False, default_style="'")
        mock_yaml_dump.reset_mock()

    # invalid filetypes should return None
    assert Config.save('foo') is None
