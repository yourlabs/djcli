"""
Global Django test settings are located in conftest.py

Requires pytest-django package to be installed.
"""
import pytest

import cli2


@pytest.mark.parametrize('name,command', [
    ('settings', 'settings'),
    ('setting_raw', 'setting -r DATABASES.default.NAME'),
    ('setting', 'setting INSTALLED_APPS DATABASES.default'),
    ('setting_no_args', 'setting'),
    ('setting_no_args_all', 'setting -a'),
    ('ls_missing_model', 'ls'),
    ('ls_empty', 'ls auth.user username first_name'),
    ('chpasswd_empty', 'chpasswd username=fail'),
    ('delete_empty', 'delete auth.user username'),
])
@pytest.mark.django_db
def test_djcli_empty(name, command):
    cli2.autotest(f'tests/{name}.txt', 'djcli ' + command)


story = [
    'save auth.user username=me is_staff=True'
    ' username=staff -password -date_joined',
    'chpasswd test username=staff',
    'save auth.user +username=me first_name=test -password -date_joined',
    'ls auth.user first_name username is_staff',
    'ls auth.user username=me username first_name',
]


@pytest.mark.django_db
def test_djcli_crud_story():
    """To rewrite tests: TEST_REWRITE=1 py.test"""
    for num, cmd in enumerate(story):
        cli2.autotest(f'tests/{num}_{cmd.split(" ")[0]}.txt', f'djcli {cmd}')
