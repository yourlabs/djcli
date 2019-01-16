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

from django.apps import apps

import tabulate


@cli2.command(color=cli2.GREEN)
def settings():
    """Print out DJANGO_SETTINGS_MODULE."""
    if 'DJANGO_SETTINGS_MODULE' in os.environ:
        return os.environ['DJANGO_SETTINGS_MODULE']

    found = glob.glob('**/manage.py', recursive=True)
    if not found:
        return

    if '.' not in sys.path:
        sys.path.insert(0, os.path.dirname(found[0]))

    with open(found[0], 'r') as f:
        for line in f.readlines():
            m = re.match('.*[\'"]([^\'"]*.settings[^\'"]*)[\'"]', line)
            if m:
                mod = m.group(1)
                return mod


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
    """Update or create a model.

    # Create user or update their email by username, don't show their password
    djcli save auth.user +username=test email=new@email.com -password

    # same but show only email
    djcli save auth.user +username=test email=new@email.com email
    """
    model = _model_get(modelname)

    defaults = dict()
    for name in [*kwargs.keys()]:
        if name.startswith('+'):
            kwargs[name[1:]] = kwargs.pop(name)
        else:
            defaults[name] = kwargs.pop(name)

    if defaults:
        obj, created = model.objects.update_or_create(defaults, **kwargs)
    else:
        obj, created = model.objects.get_or_create(**kwargs)

    if created:
        print(f'{cli2.YELLOW}Created{cli2.RESET}')
    else:
        print(f'{cli2.GREEN}Updated{cli2.RESET}')

    print(tabulate.tabulate([
        (k, v)
        for k, v in _model_data(obj).items()
        if k in args or not args and k not in console_script.parser.dashargs
    ]))


@cli2.command(color=cli2.GREEN)
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


@cli2.command(color=cli2.RED)
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


@cli2.command(color=cli2.GREEN)
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
    try:
        user = model.objects.get(**kwargs)
    except model.DoesNotExist as e:
        raise cli2.Cli2Exception(str(e))
    user.set_password(password)
    user.save()
    print('Password updated !')


@cli2.command(color=cli2.GREEN)
@cli2.option('raw', alias='r', color=cli2.GREEN, help='Raw value print')
def setting(*names):
    """Show settings from django.

    How many times have you done the following ?

        python manage.py shell
        from django.conf import settings
        settings.DATABASES # or something

    Well it's over now ! Try this instead to pretty print some setting:

        djcli setting DATABASES INSTALLED_APPS # etc

    The --raw option will call raw print:

        MEDIA_ROOT=$(djcli setting --value MEDIA_ROOT)
    """
    for name in names:
        importable = cli2.Importable.factory(f'django.conf.settings.{name}')
        if console_script.parser.options.get('raw', False):
            print(importable.target)
        else:
            print(f'{name}={pprint.pformat(importable.target)}')


class ConsoleScript(cli2.ConsoleScript):
    def setup(self):
        mod = os.getenv('DJANGO_SETTINGS_MODULE', settings())

        if not mod:
            raise cli2.Cli2Exception('DJANGO_SETTINGS_MODULE not found')

        os.environ['DJANGO_SETTINGS_MODULE'] = mod

        try:
            import django
        except ImportError:
            raise cli2.Cli2Exception('ImportError: django package not found')

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

        self._setup = True

    def call(self, command):
        if command.name not in ('help', 'settings_find'):
            if not getattr(self, '_setup', False):
                self.setup()

        return super().call(command)


console_script = ConsoleScript(__doc__).add_module('djcli')
