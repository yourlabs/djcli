"""djcli: time for CLI party !

Will try to auto-detect $DJANGO_SETTINGS_MODULE by searching for settings.py
from the current directory.
"""
import glob
import inspect
import os
import pprint
import re
import sys
import tabulate
import traceback

import cli2

from django.apps import apps


class ConsoleScript(cli2.Group):
    def setup(self):
        mod = os.getenv('DJANGO_SETTINGS_MODULE', settings())

        if not mod:
            print('DJANGO_SETTINGS_MODULE not found')
            sys.exit(1)

        os.environ['DJANGO_SETTINGS_MODULE'] = mod

        try:
            import django
        except ImportError:
            print('ImportError: django package not found')
            sys.exit(1)

        try:
            django.setup()
        except Exception:
            print(f'{cli2.c.red}Setting up django has failed !')

            if 'DJANGO_SETTINGS_MODULE' in os.environ:
                print(f'DJANGO_SETTINGS_MODULE='
                      f'{os.getenv("DJANGO_SETTINGS_MODULE")}')
                traceback.print_exc()

            else:
                print('DJANGO_SETTINGS_MODULE env var not set !')

            print(f'{cli2.c.reset}')
            sys.exit(1)

        self._setup = True

    def __call__(self, *argv):
        if argv and argv[0] not in ('help', 'settings'):
            if not getattr(self, '_setup', False):
                self.setup()

        return super().__call__(*argv)


cli = ConsoleScript(doc=__doc__)


@cli.cmd(color='green')
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


@cli.cmd
def save(modelname, **kwargs):
    """Update or create a model.

    # Create user or update their email by username
    djcli save auth.user +username=test email=new@email.com
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
        print(f'{obj} {cli2.c.yellow}Created{cli2.c.reset}')
    else:
        print(f'{obj} {cli2.c.green}Updated{cli2.c.reset}')


@cli.cmd(color='green')  # noqa
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
        return

    _printqs(models, args)


@cli.cmd(color='red')
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


@cli.cmd(color='green')
def detail(modelname, *args, **kwargs):
    """Print detail for a model.

    kwargs are passed to filter()

    Example::

        djcli widgets.Widget pk=123
    """
    model = _model_get(modelname)
    obj = model.objects.get(**kwargs)
    print(tabulate.tabulate([
        (k, v)
        for k, v in _model_data(obj).items()
        if k in args or not args
    ]))


@cli.cmd
def run(callback, *args, **kwargs):
    """Execute a callback in Django context.

    Args and kwargs are forwarded to callee.

    Example::

        djcli run yourapp.models.somecallback
    """
    importable = cli2.Node.factory(callback)
    if importable.target is None:
        print('Could not import ' + callback)
        sys.exit(1)
    elif callable(importable.target):
        return importable.target(*args, **kwargs)
    else:
        return importable.target


@cli.cmd
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
        print(str(e))
        sys.exit(1)
    user.set_password(password)
    user.save()
    print('Password updated !')


@cli.cmd(color='green')  # noqa
@cli.arg('raw', alias=['-r', '--raw'], doc='Raw value print')
@cli.arg(
    'print_all',
    alias='--all',
    doc='Print all settings, including default values'
)
def setting(*names, raw: bool = False, print_all: bool = False):
    """Show settings from django.

    How many times have you done the following ?

        python manage.py shell
        from django.conf import settings
        settings.DATABASES # or something

    Well it's over now ! Try this instead to pretty print some setting:

        djcli setting DATABASES INSTALLED_APPS  # etc.

    The --raw option will call raw print, to enable the following:

        MEDIA_ROOT=$(djcli setting --raw MEDIA_ROOT)

    With no arguments, all settings in settings.py will be printed.
    The --all option, with no arguments, will cause all Django settings to be
    printed, including those with default values.
    """

    def print_setting(setting):
        if raw:
            print(setting)
        else:
            print(f'{name}={pprint.pformat(setting)}')

    if names:
        for name in names:
            importable = cli2.Node.factory(
                f'django.conf.settings.{name}'
            )
            print_setting(importable.target)
    else:
        importable = cli2.Node.factory('django.conf.settings')
        for name in dir(importable.target):
            setting = getattr(importable.target, name)
            if ((not name.startswith('_')
                 and not callable(setting)
                 and (print_all or importable.target.is_overridden(name))
                 and not inspect.ismodule(setting))):
                print_setting(setting)


@cli.cmd(color='green')
@cli.arg('quiet', alias='--quiet')
@cli.arg('debug', alias='--debug')
def dbcheck(quiet: bool = False, debug: bool = False, sleep_for: float = 1,
            max_tries: int = None):
    """Check all database connections.

    Verify that all the databases are ready (e.g. before attempting to start
    Django dev server).

    :param bool quiet:      Silence all output.
    :param bool debug:      Display debug output (overrides -q)
    :param float sleep_for: Seconds to sleep between attempts.
    :param int max_tries:   Number of attempts to retry before failing.
    """
    from django.db import connections
    from django.db.utils import OperationalError
    from time import sleep

    max_tries = int(max_tries) if max_tries else None
    exc = None

    if debug:
        print(
            f'dbcheck parameters: sleep_for={sleep_for}; max_tries={max_tries}'
        )

    for conn in connections:
        db_conn = False
        attempts = 0

        def wait():
            return attempts < max_tries if max_tries else True

        while wait():
            try:
                connections[conn].ensure_connection()
                db_conn = True
            except (OperationalError,) as e:
                if debug:
                    print(
                        f'Waiting {sleep_for} second(s) for database {conn}...'
                    )
                exc = e
                sleep(sleep_for)
                attempts += 1
            if db_conn:
                break
        if not db_conn:
            break

    if not db_conn:
        if not quiet or debug:
            print(
                f'Attempting to connect to database {conn} returns an error:'
            )
            print(exc)
        sys.exit(1)
