"""
Global Django test settings are located in conftest.py

Requires pytest-django package to be installed.
"""
import pytest
import subprocess
import os


import cli2
import djcli


@pytest.mark.parametrize('name,command', [
    ('setup', 'setup'),
    ('settings', 'settings'),
    ('settings_root_urlconf', 'settings --value ROOT_URLCONF'),
    ('ls_missing_model', 'ls'),
    ('ls_empty', 'ls auth.user username first_name'),
    ('chpasswd_empty', 'chpasswd username=fail'),
    ('delete_empty', 'delete auth.user username'),
    ('save_staff', 'save auth.user is_staff=True username=staff -password -date_joined'),
    ('chpasswd', 'chpasswd test username=staff'),
    ('save_me', 'save auth.user username=me first_name=test -password -date_joined'),
    ('ls', 'ls auth.user first_name username is_staff'),
    ('ls_me', 'ls auth.user username=me username first_name'),
])
def test_djcli(name, command):
    if name == 'setup':
        db = 'djcli_test_project/db.sqlite3'
        if os.path.exists(db):
            os.unlink(db)
        proc = subprocess.Popen('djcli_test_project/manage.py migrate',
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out, err = proc.communicate()
        print(out)
        assert not err, out + err
    else:
        cli2.autotest(
            f'tests/{name}.txt',
            'djcli ' + command,
            [
                '^pbkdf2_sha256[^ ]*',
            ]
        )
