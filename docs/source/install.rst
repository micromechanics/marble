.. _install:

Installation
************

MARBLE requires Python 3.10 or newer.

Prerequisites
=============

* python 3.10 or higher
* pip3

PyMarble
========

The MARBLE GUI and CLI are available through the
`pymarble package on PyPI <https://pypi.org/project/pymarble/>`_.
Install it using pip:

.. code-block:: bash

   pip install pymarble

Dark Mode
---------

When using macOS in dark mode, the GUI will sometimes display white text over white background. To fix this you have to temporarily use light mode.
The team is working on a fix at the moment.


Python
======

1. Download Python 3.10 or newer from the `official Python website <https://www.python.org/downloads/>`_.
2. Use Homebrew

   1. install xcode

      .. code-block:: bash

        xcode-select --install

   2. download the install script and run it

      .. code-block:: bash

        /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

   3. install python

      .. code-block:: bash

        brew install python3

   4. check if python works

      .. code-block:: bash

        python3 --version

   if it prompts you with its version you are good to go

3. Install pip with python3

  .. code-block:: bash

    python3 -m ensurepip


Development
===========

* clone this git repository
* install dependencies

  .. code-block:: bash

    pip install -r requirements.txt
    pip install -r requirements-devel.txt

* run the cli or gui in dev mode

  .. code-block:: bash

    python marbleCLI.py
    python marbleGUI.py

Installation on Windows
***********************

Install Python 3.10 or newer from the `official Python website <https://www.python.org/downloads/>`_,
make sure that Python is added to ``PATH``, and then run:

.. code-block:: powershell

   py -m pip install pymarble

The installed commands are:

.. code-block:: powershell

   marbleGUI
   marbleCLI
