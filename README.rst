Full featured CLI CRUD and more for Django
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- install ``djcli`` with pip,
- go in a directory where you have a Django project,
- run ``djcli``

Refer to ``djcli/tests/*.txt`` for reference output.

::

   [jpic@hack djcli]$ djcli
   djcli: time for CLI party !

   Will try to auto-detect $DJANGO_SETTINGS_MODULE by searching for settings.py
   from the current directory.

     help      Get help for a command.
     chpasswd  Change the password for user.
     dbcheck   Check all database connections.
     delete    Delete a model filtered with kwargs.
     detail    Print detail for a model.
     ls        Search models
     run       Execute a callback in Django context.
     save      Update or create a model.
     setting   Show settings from django.
     settings  Print out DJANGO_SETTINGS_MODULE.
