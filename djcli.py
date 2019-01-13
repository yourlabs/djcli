"""djcli: time for CLI party !

Will try to auto-detect $DJANGO_SETTINGS_MODULE by searching for settings.py
from the current directory.
"""
import glob
import os
import pprint
import re
import sys
import traceback

import cli2

import django
from django.apps import apps

import tabulate



def _model_data(obj, keys=None):
    keys = keys or [
        k for k in obj.__dict__.keys()
        if not k.startswith('_')
    ]

    return {k: getattr(obj, k) for k in keys}


def _printqs(qs, keys=None):
    keys = keys or None
    header = sorted(list(_model_data(qs[0], keys).keys()))
    print(tabulate.tabulate([header] + [
        [getattr(i, k) for k in header]
        for i in qs
    ]))


def _model_get(modelname):
    if modelname.startswith('settings.'):
        from django.conf import settings
        modelname = getattr(settings, modelname.split('.')[1])
    return apps.get_model(modelname)


def save(modelname, *args, **kwargs):
    """Idempotent create function.

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
    """
    model = _model_get(modelname)

    if not args:
        obj = model.objects.create(**kwargs)
        created = True
    else:
        defaults = {}
        for key, value in kwargs.copy().items():
            if key not in args:
                defaults[key] = kwargs.pop(key)
        obj, created = model.objects.update_or_create(defaults, **kwargs)

    print(tabulate.tabulate([
        (k, v)
        for k, v in _model_data(obj).items()
    ]))


@cli2.config(color=cli2.GREEN)
def ls(modelname, *args, **kwargs):
    """Search models

    kwargs are passed to filter.
    It shows all fields by default, you can restrict them with args.

    Show username and email for superusers::

        djcli ls auth.user is_superuser=1 username email
    """

    model = _model_get(modelname)
    models = model.objects.filter(**kwargs)
    if not models:
        print('No result found !')
        sys.exit(0)

    _printqs(models, args)


@cli2.config(color=cli2.RED)
def delete(modelname, *args, **kwargs):
    """
    Delete a model filtered with kwargs.

    It will show all columns of the delete model prior to actual delete,
    otherwise the list of columns that were passed as argument.

    Example:

        # Show all columns by default
        djcli delete settings.AUTH_USER_MODEL username=1337noob

        # Show only username and email column
        djcli delete settings.AUTH_USER_MODEL email username username=1337noob
    """
    model = _model_get(modelname)
    qs = model.objects.filter(**kwargs)
    if not qs:
        print('No model to delete !')
        return
    _printqs(qs, args)
    count = len(qs)
    qs.delete()
    print(f'Deleted {count} objects')


@cli2.config(color=cli2.GREEN)
def detail(modelname, *args, **kwargs):
    """Print detail for a model.

    kwargs are passed to filter()

    Example::

        djcli cat pk=123
    """
    model = _model_get(modelname)
    obj = model.objects.get(**kwargs)
    print(tabulate.tabulate([
        (k, v)
        for k, v in _model_data(obj).items()
        if k in args or not args
    ]))


def chpasswd(password, **kwargs):
    """Change the password for user.

    It takes the password as argument, that you can use `-` for stdin.
    All kwargs will be passed to get()

    Example:

        djcli chpasswd username=... thepassword
        echo thepassword | djcli chpasswd username=... -
    """

    from django.conf import settings
    model = apps.get_model(settings.AUTH_USER_MODEL)
    user = model.objects.get(**kwargs)
    user.set_password(password)
    user.save()
    print('Password updated !')


@cli2.config(color=cli2.GREEN)
def settings(*names):
    """Show settings from django.

    How many times have you done the following ?

        python manage.py shell
        from django.conf import settings
        settings.DATABASES # or something

    Well it's over now ! Try this instead:

        djcli settings DATABASES INSTALLED_APPS # etc

    To have only the value printed to stdout, use --value, ie.::

        MEDIA_ROOT=$(djcli settings --value MEDIA_ROOT)
    """
    from django.conf import settings

    for name in names:
        if 'value' in console_script.parser.dashargs:
            print(f'{getattr(settings, name)}')
        else:
            print(f'{name}={pprint.pformat(getattr(settings, name))}')


class ConsoleScript(cli2.ConsoleScript):
    def django_setup(self):
        found = glob.glob('**/manage.py', recursive=True)
        if found and 'DJANGO_SETTINGS_MODULE' not in os.environ:
            if '.' not in sys.path:
                sys.path.insert(0, os.path.dirname(found[0]))

            with open(found[0], 'r') as f:
                for line in f.readlines():
                    m = re.match('.*[\'"]([^\'"]*.settings[^\'"]*)[\'"]', line)
                    if m:
                        mod = m.group(1)
                        print(f'{cli2.GREEN}'
                              f'Auto-detected DJANGO_SETTINGS_MODULE={mod}',
                              file=sys.stderr)
                        print(f'If incorrect, set DJANGO_SETTINGS_MODULE env var'
                              f' {cli2.RESET}',
                              file=sys.stderr)
                        os.environ['DJANGO_SETTINGS_MODULE'] = mod
                        break

        try:
            django.setup()
        except Exception:
            print(f'{cli2.RED}Setting up django has failed !')
            if 'DJANGO_SETTINGS_MODULE' in os.environ:
                print(f'DJANGO_SETTINGS_MODULE='
                      f'{os.getenv("DJANGO_SETTINGS_MODULE")}')
                traceback.print_exc()
            else:
                print('DJANGO_SETTINGS_MODULE env var not set !')
            print(f'{cli2.RESET}')
            sys.exit(1)

    def call(self, command):
        if command.name != 'help':
            self.django_setup()
        return super().call(command)


console_script = ConsoleScript(__doc__).add_module('djcli')
