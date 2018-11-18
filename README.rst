Full featured CLI CRUD and more for Django
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First, install ``djcli`` with pip. Then, don't add it to INSTALLED_APPS because
it's not necessary: djcli is here to automate your work, not to add more.

Then, change directory to a directory where you have a Django project manage.py
if you're not 100% sure about your DJANGO_SETTINGS_MODULE environment variable
being right, or have none: it will find it by parsing manage.py

Getting help
============

Run the ``djcli`` command without argument as such, note that you would have
colored output::

    $ djcli
    djcli: time for CLI party !

    It would like DJANGO_SETTINGS_MODULE env var, and does not require to be in
    INSTALLED_APPS because automation software should be made automatically
    available and adding to INSTALLED_APPS is a manual step.

    Otherwise, it will try to find out DJANGO_SETTINGS_MODULE itself, searching for
    a manage.py in the current working directory or sub directory.

    [Callables in /home/jpic/src/djcli/djcli.py]

    - chpasswd
    - save
    - delete
    - detail
    - ls
    - settings

    Try djcli help callable_name

Create/Update with the save command
===================================

You can get help with ``djcli help save``::

    $ djcli  help save
    Idempotent save function.

    First argument must be model name, for apps.get_model.
    With only keyword arguments, it will pass them to create().
    If you pass arguments, it will use update_or_create, passing
    any keyword argument name as defaults to update_or_create
    instead of kwarg.

    # Create a user, not idempotent
    djcli save auth.user username=foo email=joe@example.com

    # Create or update a user based on email, idempotent yay !
    djcli save auth.user email username=foo email=joe@example.com

    # oh, and with settings.* support for your model swapping fun hacks ;)
    djcli save settings.AUTH_USER_MODEL ...

Example creating a new user::

    $ djcli save settings.AUTH_USER_MODEL username=13337noob is_superuser=True is_staff=True first_name=Newb
    Auto-detected DJANGO_SETTINGS_MODULE=testproj2.settings
    If incorrect, set DJANGO_SETTINGS_MODULE env var
    ------------  --------------------------------
    id            5
    password
    last_login
    is_superuser  True
    username      13337noob
    first_name    Newb
    last_name
    email
    is_staff      True
    is_active     True
    date_joined   2018-11-18 12:23:59.903470+00:00
    ------------  --------------------------------

Example creating a user with an idempotent command based on username::

    $ djcli save settings.AUTH_USER_MODEL username username=13337noob is_superuser=False is_staff=True first_name=Newb
    Auto-detected DJANGO_SETTINGS_MODULE=testproj2.settings
    If incorrect, set DJANGO_SETTINGS_MODULE env var
    ------------  --------------------------------
    id            5
    password
    last_login
    is_superuser  False
    username      13337noob
    first_name    Newb
    last_name
    email
    is_staff      True
    is_active     True
    date_joined   2018-11-18 12:23:59.903470+00:00
    ------------  --------------------------------

Detail
======

Get help from the detail command with ``djcli help detail``::

    $ djcli  help detail
    Print detail for a model.

    kwargs are passed to filter()

    djcli detail pk=123

Show a model detail for example::

    $ djcli detail auth.User username=13337noob
    Auto-detected DJANGO_SETTINGS_MODULE=testproj2.settings
    If incorrect, set DJANGO_SETTINGS_MODULE env var
    ------------  --------------------------------
    id            5
    password
    last_login
    is_superuser  False
    username      13337noob
    first_name    Newb
    last_name
    email
    is_staff      True
    is_active     True
    date_joined   2018-11-18 12:23:59.903470+00:00
    ------------  --------------------------------

Change password with the chpasswd command
=========================================

Get help with the ``djcli help chpasswd`` command::

    $ djcli  help chpasswd
    Change the password for user.

    It takes the password as argument, that you can use `-` for stdin.
    All kwargs will be passed to get()

    Example:

        djcli chpasswd username=... thepassword
        echo thepassword | djcli chpasswd username=... -

Example::

    $ djcli chpasswd newpassword username=1337noob
    Auto-detected DJANGO_SETTINGS_MODULE=testproj2.settings
    If incorrect, set DJANGO_SETTINGS_MODULE env var
    Password updated !

Or::

    $ echo newpassword | djcli chpasswd - username=1337noob
    Auto-detected DJANGO_SETTINGS_MODULE=testproj2.settings
    If incorrect, set DJANGO_SETTINGS_MODULE env var
    Password updated !

Delete command
==============

Get help with the ``djcli help delete`` command::

    $ djcli help delete
    Delete a model filtered with kwargs.

    It will show all columns of the delete model prior to actual delete,
    otherwise the list of columns that were passed as argument.

    Example:

        # Show all columns by default
        djcli delete settings.AUTH_USER_MODEL username=1337noob

        # Show only username and email column
        djcli delete settings.AUTH_USER_MODEL email username username=1337noob

Example::

    $ djcli delete settings.AUTH_USER_MODEL email username username=foo
    Auto-detected DJANGO_SETTINGS_MODULE=testproj2.settings
    If incorrect, set DJANGO_SETTINGS_MODULE env var
    ---------------  --------
    email            username
    joe@example.com  foo
    ---------------  --------
    Deleted 1 objects

List with the ls command
========================

Get help with the ``djcli help ls`` command::

    $ djcli help ls
    Search models

    kwargs are passed to filter.
    It shows all fields by default, you can restrict them with args.

    Show username and email for superusers:

        djcli settings.AUTH_USER_MODEL is_superuser=1 username email

Example::

    $ djcli ls settings.AUTH_USER_MODEL is_staff=1 username email is_superuser
    Auto-detected DJANGO_SETTINGS_MODULE=testproj2.settings
    If incorrect, set DJANGO_SETTINGS_MODULE env var
    -----  ------------  ---------
    email  is_superuser  username
           True          newb
           False         13337noob
    -----  ------------  ---------

Show settings with the settings command
=======================================

Get help with ``djcli help settings``::

    $ djcli help settings
    Show settings from django.

    How many times have you done the following ?

        python manage.py shell
        from django.conf import settings
        settings.DATABASES # or something

    Well it's over now ! Try this instead:

        djcli settings DATABASES INSTALLED_APPS # etc

Example::

    $ djcli settings DATABASES INSTALLED_APPS
    Auto-detected DJANGO_SETTINGS_MODULE=testproj2.settings
    If incorrect, set DJANGO_SETTINGS_MODULE env var
    DATABASES={'default': {'ATOMIC_REQUESTS': False,
                 'AUTOCOMMIT': True,
                 'CONN_MAX_AGE': 0,
                 'ENGINE': 'django.db.backends.sqlite3',
                 'HOST': '',
                 'NAME': '/home/jpic/src/clitoo/testproj2/db.sqlite3',
                 'OPTIONS': {},
                 'PASSWORD': '',
                 'PORT': '',
                 'TEST': {'CHARSET': None,
                          'COLLATION': None,
                          'MIRROR': None,
                          'NAME': None},
                 'TIME_ZONE': None,
                 'USER': ''}}
    INSTALLED_APPS=['django.contrib.admin',
     'django.contrib.auth',
     'django.contrib.contenttypes',
     'django.contrib.sessions',
     'django.contrib.messages',
     'django.contrib.staticfiles']
