Tests require the following commands on the system PATH:

  - svn
  - hg
  - git

To run tests create a Python 2.6 virtualenv in the top-level directory::

  $ virtualenv .
  $ ./bin/python setup.py -q develop
  $ ./bin/python setup.py -q test

