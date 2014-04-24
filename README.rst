pylint-symbolizer
=================

Renames disabled Pylint IDs to Pylint symbolic names

Requirements
============

Required
--------

``python`` and the following module

  - ``pylint>=1.2.0``

Optional
--------

If you would like to run tests you will need:

 - ``nose``
 - ``mock``

Installation
============

Installation using pip:

.. code:: sh

    $ sudo pip install pylint-symbolizer

Installation from source:

.. code:: sh

    $ git clone https://github.com/mikejarrett/pylint-symbolizer.git
    $ cd pylint-symbolizer
    $ sudo python setup.py install

Usage
=====

.. code:: sh

    usage: symbolizer [-h] [-w [WIDTH]] module_or_file

    Renames disabled Pylint IDs to Pylint symbolic names

    positional arguments:
        module_or_file

    optional arguments:
    -h, --help            show this help message and exit
    -w [WIDTH], --width [WIDTH]
                          Set the window width limit

.. code:: python

    >>> from symbolizer.symbolizer import Symbolizer
    >>> symb = Symbolizer(start_location='/file/path.py', column_width=100)
    >>> symb()
    Processing -- /file/path.py

TODO
====

[ ] Cleanup `setup.py` and prep for PyPI

[ ] Handle things like `# -*- coding: utf-8 -*-` at the top of the file

[x] Handle inline disables

[x] Fix bug with trailing comma when adding a new line

[x] Update entry point for inlines

[x] Handle single file input


Licence
=======

Apache v2 License

http://www.apache.org/licenses/
