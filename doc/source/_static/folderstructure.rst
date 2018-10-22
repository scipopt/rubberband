Structure of project
====================

Main tree
---------

- Source code: ``rubberband``
- Documentation: ``doc, CONTRIBUTING.md, README.md``
- Test utilities and configuration: ``runcodecheckers, runtests, tests, .travis.yml``
- Requirements for installing: ``requirements-dev.txt requirements.txt``
- Configuration files: ``config, setup.cfg, setup.py``
- Server script: ``server.py``, start server with ``python server.py`` (from inside virtual environment).
- Script to interact with the database for initialization, manipulation apart from rubberband functionality: ``bin/rubberband-ctl``

Source directory
----------------

* ``boilerplate.py``: Constructs the application, gets called by ``server.py`` and ``bin/rubberband-ctl``.
* ``constants.py``: Contains constants used in various places.
* ``handlers``: Contains all different RequestHandlers.
* ``models``: Contains the datamodels used by rubberband and elasticsearch.
* ``routes.py``: Routingtable.
* ``static``: Contains static files like CSS, Javascript and Webserverfiles.
* ``utils``: Contains pythoncode that is independent of tornado, like the gitlab and ipet connections.

