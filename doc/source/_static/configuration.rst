Configuration
=============

In the config directory there is an example configuration file for nginx with oauth2_proxy.
There is also a template configuration ``app.cfg`` for rubberband that you can copy into ``/etc/rubberband/`` and change it according to your needs.
You will find required and optional attributes indicated in that file.

Rubberband and Elasticsearch
----------------------------

Set a port and a production URL, as well as secret tokens and the elasticsearch URL.
You can also require elasticsearch to verify certificates.

optional Gitlab
---------------

Specify URL, private token and the project indices where you develop your LP-Solver.

