Viper
=======================

Introduction
------------
Viper is an application development framework for `Twisted <https://github.com/twisted/twisted>`_.

`Twisted <https://github.com/twisted/twisted>`_ is a very flexible platform to develop almost any type of application.
This can be overwhelming, especially when you need to prototype something quickly. There is no predefined way to structure the application's components and no clear way to handle deployment in production environments.

Viper, together with the `default skeleton application <https://github.com/Nixiware/viper-skeleton-application>`_ aims to simplify the development and deployment of server-side applications by using the building blocks that Twisted offers.

To get started have a look at the `default skeleton application <https://github.com/Nixiware/viper-skeleton-application>`_ which offers examples for:

* configuration
* HTTP REST API interface
* CRUD
* scheduled and recurring operations

Features
------------

* *MVCS* structure
* environment based configuration
* deployment using systemd
* MySQL service based on *twisted.enterprise.adbapi*
* mail service based on *smtplib*


Requirements
------------
* Python 3.6

Testing
------------
Unit tests are included in ``test/`` folder.

Performing tests

* Install pytest by running ``pip install pytest``
* Run ``py.test``

Links
------------
`Python Package Index - nx.viper <https://pypi.org/project/nx.viper/>`_


Notice
------------
Viper is currently in Beta stage.

The roadmap before public release is:

1. Tests
2. Documentation