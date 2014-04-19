.. _main_page:

Projet Impérium
===============

.. begin_description

Le projet est composé d’une unité principale de contrôle qui communique avec différents sous module. Son objectif est d’effectuer le traitement de l’information et la collection de l’information provenant des sous-modules. Ce module principal peut se connecter à l’internet pour réaliser le contrôle par téléphone intelligent ou d’autres appareils. Avec cet élément, il est possible d’ajouter d’autres sous module si jamais on décide d’agrandir l’échelle du projet.

Le premier sous-module comprend un système intelligent pour déverrouiller la serrure d’une porte. Aujourd’hui, avec cet âge informatique et technologique, la majorité des gens ont des téléphones intelligents et les apportent tout au long de la journée. Leur cellulaire devient leurs identités et pourrait aussi être leurs clés et plusieurs de ces outils ont maintenant la technologie NFC intégrée. En exploitant ces facteurs, on peut créer une serrure intelligente qui pourrait être déverrouillée à distance. Cela permet aux clients de faciliter la tâche lorsqu’ils veulent entrer chez eux. En somme, le module est capable de déverrouiller une porte à distance à l’aide d’un appareil, déverrouiller une porte à l’aide de la technologie RFID ou d’une clé en cas d’urgence.

Le deuxième sous-module comprend un système de mesure. Il sera capable de mesurer la puissance de chaque circuit individuel provenant du panneau électrique d’une maison. Il enverra les données à notre unité principale pour effectuer le traitement des données, tel que l’analyse des coûts et de la consommation. De plus, l’unité principale sauvegardera les données pour qu’ils soient accessibles à n’importe quel moment. La demande d’énergie continue d’augmenter et donc ce sous-module devient un projet très important à réaliser pour la gestion d’énergie consommée.

.. end_description

.. begin_installation

.. _installation:

Installation
------------

Les fichiers du projet devrons être copier sur un Raspberry-pi.
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



.. end_installation

