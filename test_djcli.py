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
    ('ls_missing_model', 'ls'),
    ('ls_empty', 'ls auth.user'),
    ('chpasswd_empty', 'chpasswd username=fail'),
    ('delete_empty', 'delete auth.user'),
    ('save_staff', 'save auth.user is_staff=True username=staff'),
    ('chpasswd', 'chpasswd test username=staff'),
    ('save_me', 'save auth.user username=me'),
    ('ls', 'ls auth.user'),
    ('ls_me', 'ls auth.user username=me'),
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
        cli2.autotest(f'tests/{name}.txt', 'djcli ' + command)

'''

@pytest.mark.django_db
def test_delete():
    User.objects.create(username='john doe')
    User.objects.create(username='other')
    cli2.autotest(
        'tests/delete_john.txt',
        'djcli delete auth.user username="john doe"'
    )
    cli2.autotest(
        'tests/delete_all.txt',
        'djcli delete auth.user'
    )
    cli2.autotest(
        'tests/delete_empty.txt',
        'djcli delete auth.user'
    )


@pytest.mark.django_db
def test_detail():
    User.objects.create(username='john doe')
    cli2.autotest(
        'tests/detail.txt',
        'djcli detail auth.user username="john doe"'
    )


@pytest.mark.django_db
def test_settings():
    """Test settings method and to check settings variable."""
    djcli.settings('DATABASES', 'INSTALLED_APPS')
    cap = capsys.readouterr()
    assert 'AUTOCOMMIT' in cap.out


@pytest.mark.django_db
def test_empty_settings():
    """Test settings method and to check settings all variable."""
    djcli.settings()
    cap = capsys.readouterr()
    assert 'LANGUAGES' in cap.out


@pytest.mark.django_db
def test_save_for_args_or_kwargs():
    """Test save method for args and kwargs.

    Create new user 'TestUser1' for args and kwargs
    Test usernames:
        Test enter enter use name exist or not.
    """
    djcli.save(
        'settings.AUTH_USER_MODEL',
        'email',
        username='TestUser1',
        email='test2@gmail.com'
    )
    cap = capsys.readouterr()
    assert 'test2@gmail.com' in cap.out


@pytest.mark.django_db
def test_ls_for_not_exists_record():
    """Test ls method for not avaliable record.

    Check message content for the not avaliable record
    @response = 'No result found !'.
    """
    with pytest.raises(SystemExit):
        djcli.ls(
            'settings.AUTH_USER_MODEL',
            'first_name',
        )
    cap = capsys.readouterr()
    assert 'No result found !' in cap.out
    print(cap.out, cap.err)
'''
