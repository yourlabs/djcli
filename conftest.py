from django.conf import settings


def pytest_configure():
    settings.configure(
        INSTALLED_APPS=[
            'django.contrib.contenttypes',
            'django.contrib.auth',
        ],
        DATABASES=dict(default=dict(
            ENGINE='django.db.backends.sqlite3',
            NAME=':memory:',
        ))
    )
