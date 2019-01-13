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
     delete    Delete a model filtered with kwargs.
     detail    Print detail for a model.
     ls        Search models
     save      Update or create a model.
     settings  Show settings from django.
