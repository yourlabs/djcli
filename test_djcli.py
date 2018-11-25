import pytest

from django.contrib.auth.models import User

from djcli import ls


@pytest.mark.django_db
def test_ls(capsys):
    User.objects.create(username='lol')
    ls(
        'settings.AUTH_USER_MODEL',
        'username',
        'email',
        username='lol'
    )
    cap = capsys.readouterr()
    assert 'lol' in cap.out
