.. _main_page:

Projet Impérium
===============

.. begin_description

Le projet est composé d’une unité principale de contrôle qui communique avec différents sous-modules. Son objectif est d’effectuer le traitement de l’information et la collection de l’information provenant des sous-modules. Ce module principal peut se connecter à l’internet afin de permettre le contrôle par téléphone intelligent ou d’autres appareils. Avec cet élément, il est possible d’ajouter des sous-modules et de communiquer entre eux.

Le premier sous-module comprend un système intelligent pour déverrouiller une porte. Aujourd’hui, avec cet âge informatique et technologique, la majorité des gadgets électroniques sont connectés à l’internet. Donc, la connexion internet d’une porte donne à l’utilisateur une plus grande flexibilité à l’accès de sa maison. En exploitant ces facteurs, on peut créer une serrure intelligente qui pourrait être déverrouillée à distance. Cela permet aux clients de faciliter la tâche lorsqu’ils veulent entrer chez eux. En somme, le module est capable de déverrouiller une porte à distance à l’aide d’un appareil, déverrouiller une porte à l’aide de la technologie RFID ou d’une clé en cas d’urgence.

Le deuxième sous-module comprend un système de mesure d’énergie. Il sera capable de prendre des lecture de puissance de chaque circuit individuel provenant du panneau électrique d’une maison. Toutefois, en raison de plusieurs défis, l’idée à été modifié pour prendre des mesures de puissance d’un appareil brancher aux prises dans un maison. Ensuite, il enverra les données à l’unité principale pour effectuer le traitement des données, tel que l’analyse des coûts et de la consommation. De plus, l’unité principale sauvegardera les données pour qu’ils soient accessibles à n’importe quel moment. La demande d’énergie continue d’augmenter et donc ce sous-module devient un projet très important à réaliser pour la gestion d’énergie consommée.

.. end_description

.. begin_installation

.. _installation:

Installation
------------

Les fichiers du projet devrons être copier sur un Raspberry Pi.

Ce projet dépend sur les librairies suivantes:

Serveur Web:

    `- flask <http://flask.pocoo.org/docs/>`_

    `- flask.ext.sqlalchemy <http://flask.pocoo.org/docs/patterns/sqlalchemy/>`_

    `- flask.ext.wtf <https://flask-wtf.readthedocs.org/en/latest/>`_

    `- awesome-slugify <https://pypi.python.org/pypi/awesome-slugify/1.2.4>`_


Communication Serie:

    `- pyserial <https://pypi.python.org/pypi/pyserial>`_

Acquisition de la température de ville:

    `- xmltodict <https://pypi.python.org/pypi/xmltodict>`_

    `- requests <http://docs.python-requests.org/en/latest/>`_

Voici des guides que nous avions suivi pour activer le port série du
RaspberryPi:

    `- Enable Serial <http://www.hobbytronics.co.uk/raspberry-pi-serial-port>`_

    `- Python Serial <http://www.elinux.org/Serial_port_programming>`_

Enfin pour exécuter l'application web,

.. code-block:: bash

   $ python run.py

Pour uttiliser le système de notification, un fichier creds.txt dans le répertoire principal devrait être crée avec les détails gmail.



Projet réaliser par,
--------------------

Emmanuel Thompson

Dominic Savoie

Gilles Samson

Mathieu Doucet

Mac Gregore Brunis

Projet de conception - GELE3422 - Microprocesseurs

.. end_installation

