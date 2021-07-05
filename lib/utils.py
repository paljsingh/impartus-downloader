import json
import os
import platform
import re
import shutil
import subprocess
from typing import List
import webbrowser
from datetime import datetime


class Utils:
    """
    Utility functions.
    """

    @classmethod
    def delete_files(cls, files: List):
        for file in files:
            os.unlink(file)

    @classmethod
    def get_temp_dir(cls):
        for env_var in ['TMPDIR', 'TEMP', 'TMP']:
            if os.environ.get(env_var):
                return os.environ.get(env_var)
        for tmp_path in ['/tmp', '/var/tmp', 'c:\\windows\\temp']:
            if os.path.exists(tmp_path):
                return tmp_path

    @classmethod
    def open_file(cls, path, event=None):   # noqa
        if re.match('https?', path) or re.match('file:', path):
            webbrowser.open(r'{}'.format(path))
        elif platform.system() == 'Darwin':
            # when preview.app, keynote.app is already launched,
            # a second window often throws an error: 'cannot import <file>'
            # use 'open' launcher.
            subprocess.run(["open", path])
        else:
            webbrowser.open(r'file://{}'.format(path))

    @classmethod
    def date_difference(cls, date1, date2):
        date_format = "%Y-%m-%d"
        delta = datetime.strptime(date1, date_format) - datetime.strptime(date2, date_format)
        return delta.days

    @classmethod
    def move_and_rename_file(cls, source, destination):
        if source != destination:
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            shutil.move(source, destination)

    @classmethod
    def save_json(cls, content, filepath):
        with open(filepath, "w") as fh:
            json.dump(content, fh, indent=4)
