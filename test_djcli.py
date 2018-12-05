"""Write test cases for the Djcli."""

import pytest
from django.contrib.auth.models import User
import djcli


@pytest.mark.django_db
def test_ls(capsys):
    """Test ls method for multiple user.

    Create new user 'TestUser1' and check username in the list.
    """
    User.objects.create(username='lol')
    djcli.ls(
        'settings.AUTH_USER_MODEL',
        'username',
        'email',
        username='lol'
    )
    cap = capsys.readouterr()
    assert 'lol' in cap.out


@pytest.mark.django_db
def test_save(capsys):
    """Test save method for multiple user.

    Enter UserNames:
        @username = ['TestUser1', 'TestUser2', 'TestUser3', 'TestUser4']
        Create users according to username list.
    Test User count:
        enter user count = save user count
    Test usernames:
        Test enter enter use name exist or not.
    """
    usernames = ['TestUser1', 'TestUser2', 'TestUser3', 'TestUser4']

    for username in usernames:
        djcli.save(
            'settings.AUTH_USER_MODEL',
            username=username,
            is_superuser=True,
            first_name='Test',
            is_staff=True
        )
    cap = capsys.readouterr()
    users = User.objects.all()
    assert 'TestUser1' in cap.out
    assert 'TestUser2' in cap.out
    assert 'TestUser3' in cap.out
    assert 'TestUser4' in cap.out
    assert users.count() == len(usernames)


@pytest.mark.django_db
def test_delete():
    """Test delete method for the user.

    Create new user 'TestUser1' and check user count is 1
    Delete the exiting user and check user count is 0.
    """
    User.objects.create(username='TestUser1')

    users = User.objects.all()
    assert users.count() == 1

    djcli.delete(
        'settings.AUTH_USER_MODEL',
        username='TestUser1',
    )
    assert users.count() == 0


@pytest.mark.django_db
def test_detail(capsys):
    """Test detail method for the user.

    Create new user 'TestUser1' and check user count is 1
    Get user details according to selected user and check username.
    """
    User.objects.create(username='TestUser1')

    djcli.detail(
        'settings.AUTH_USER_MODEL',
        username='TestUser1',
    )

    cap = capsys.readouterr()
    assert 'TestUser1' in cap.out


@pytest.mark.django_db
def test_delete_for_not_exists_record(capsys):
    """Test delete method for not avaliable record.

    Delete not existing user from the model and check response
    @response = 'No model to delete'.
    """
    djcli.delete(
        'settings.AUTH_USER_MODEL',
        username='TestUser1',
    )
    cap = capsys.readouterr()
    assert 'No model to delete' in cap.out


@pytest.mark.django_db
def test_chpasswd(capsys):
    """Test change password method for user.

    Create new user 'TestUser1' and check user count is 1
    Update the password according to username and check response.
    @response = 'Password updated !'.
    """
    User.objects.create(username='TestUser1')
    djcli.chpasswd(
        'newpassword',
        username='TestUser1'
    )
    cap = capsys.readouterr()
    assert 'Password updated !' in cap.out
