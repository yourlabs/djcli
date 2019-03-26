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
    ('checkdb_available', 'checkdb'),
    ('checkdb_available_debug', 'checkdb --debug'),
])
@pytest.mark.django_db
def test_djcli_empty(name, command):
    cli2.autotest(f'tests/{name}.txt', 'djcli ' + command)


@pytest.mark.parametrize('name,command', [
    ('checkdb_missing', 'checkdb sleep_for=0.1 max_tries=5'),
    ('checkdb_missing_debug', 'checkdb sleep_for=0.1 max_tries=5 --debug'),
])
@pytest.mark.django_db
def test_checkdb_missing(name, command, settings):
    """Override settings to simulate a missing database.

    Add a new database to avoid conflict with the test runner in-memory db.
    """
    settings.DATABASES['fake_sqlite3'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/fake_djcli_test_path/fake.sqlite3',
    }
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
