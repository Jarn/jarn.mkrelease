==============
jarn.mkrelease
==============
---------------------------------------------------
Python package releaser
---------------------------------------------------

**mkrelease** is a no-frills Python package releaser. It is designed to take
the cumber out of building and distributing Python packages.
The releaser supports source distributions, eggs, and wheels.

Motivation
==========

After preparing a package for release (update version strings, dates) we
typically have to:

1. Commit modified files.

2. Tag the release.

3. Build a source distribution and wheel.

4. Distribute the results via scp or upload them to an index server.

If we are doing this a lot, the need for automation becomes obvious.

Contents
========

* Installation_
* Usage_
* Options_
* Arguments_
* Configuration_
* `Upload with SCP`_
* `Upload to Index Servers`_
* `Using GnuPG`_
* Requirements_
* Footnotes_
* Related_
* Changelog_

Installation
============

mkrelease works with Python 2.7 - 3.10 and all released versions of
setuptools.

Use ``pip install jarn.mkrelease`` to install the ``mkrelease`` script.

Since version 4.4 mkrelease requires twine_ for register and upload
operations. Twine may be installed as a global utility on the system PATH or
into the same environment as jarn.mkrelease. [1]_

Use ``pip install jarn.mkrelease[twine]`` to install mkrelease + twine.

.. _twine: https://twine.readthedocs.io/en/stable/

Usage
=====

``mkrelease [options] [scm-sandbox|scm-url [rev]]``

Options
=======

``-C, --no-commit``
    Do not commit modified files from the sandbox.

``-T, --no-tag``
    Do not tag the release in SCM.

``-R, --no-register``
    Do not register the release with dist-location.

``-S, --no-upload``
    Do not upload the release to dist-location.

``-n, --dry-run``
    Dry-run; equivalent to ``-CTRS``. This flag turns mkrelease into a
    simple package builder.

``--svn, --hg, --git``
    Select the SCM type. Only required if the SCM type
    cannot be guessed from the argument.

``-d dist-location, --dist-location=dist-location``
    An scp destination specification, an index
    server configured in ``~/.pypirc``, or an alias name for
    either. This option may be specified more than once.

``-s, --sign``
    Sign the release with GnuPG.

``-i identity, --identity=identity``
    The GnuPG identity to sign with. Implies ``-s``.

``-z, --zip``
    Release a zip archive (the default).

``-g, --gztar``
    Release a tar.gz archive.

``-b, --binary``
    Release a binary egg.

``-w, --wheel``
    Release a wheel file.

``-p, --push``
    Push sandbox modifications upstream.

``-m, --manifest-only``
    Ignore setuptools file finder extensions and collect files via
    ``MANIFEST.in`` only.

``-e, --develop``
    Allow setuptools build tags. Implies ``-T``.

``-q, --quiet``
    Suppress output of setuptools commands.

``-t twine, --twine=twine``
    Override the twine executable used.

``-c config-file, --config-file=config-file``
    Use config-file instead of the default ``~/.mkrelease``.

``-l, --list-locations``
    List known dist-locations and exit.

``-h, --help``
    Print the help message and exit.

``-v, --version``
    Print the version string and exit.

``--no-color``
    Disable output colors.

Arguments
=========

``scm-sandbox``
    A local SCM sandbox. Defaults to the current working
    directory.

``scm-url [rev]``
    The URL of a remote SCM repository. The optional ``rev``
    argument specifies a branch or tag to check out.

Configuration
=============

mkrelease reads available index servers from the distutils_ configuration
file ``~/.pypirc``. This file should contain your PyPI account information: [2]_

.. code:: ini

  [distutils]
  index-servers =
      pypi

  [pypi]
  repository = https://upload.pypi.org/legacy/
  username = fred
  password = secret

Next, mkrelease reads its own configuration file ``~/.mkrelease``.
The file should contain at least:

.. code:: ini

  [mkrelease]
  push = yes
  register = no
  formats = gztar wheel
  manifest-only = yes

A more complete example may look like:

.. code:: ini

  [mkrelease]
  # Release steps
  commit = yes
  tag = yes
  push = yes
  register = no
  upload = yes

  # One or more of: zip gztar egg wheel
  formats = gztar wheel

  # Setuptools options
  manifest-only = yes
  develop = no
  quiet = no

  # Sign with GnuPG
  sign = no
  identity =

  # Default dist-location
  dist-location =

  [aliases]
  # Map name to one or more dist-locations
  customerA =
      jarn.com:/var/dist/customerA/
  public =
      jarn.com:/var/dist/public/
  world =
      pypi
      public

.. _distutils: https://packaging.python.org/en/latest/specifications/pypirc/

Upload with SCP
===============

The simplest distribution location is a server directory reachable by ssh.
Releasing a package means scp-ing it to the appropriate place
on the server:

.. code::

  $ mkrelease -d customerA
  $ mkrelease -d jarn.com:/var/dist/customerB/
  $ mkrelease -d scp://jarn.com/var/dist/customerC/
  $ mkrelease -d stefan@jarn.com:eggs -C -e -q

To upload via sftp instead of scp, use the ``sftp`` URL scheme:

.. code::

  $ mkrelease -d sftp://jarn.com/var/dist/customerD/

Note: Unlike scp, the sftp client does not prompt for login credentials.
This means that non-interactive login must be configured on the
destination server or the upload will fail.

Upload to Index Servers
=======================

Another way of publishing a Python package is by uploading it to a dedicated
index server like PyPI.
Given the ``~/.pypirc`` and ``~/.mkrelease``
files from above, we can release to PyPI simply by typing:

.. code::

  $ mkrelease -d pypi

Index servers are not limited to PyPI though.
There is `test.pypi.org`_, and there are alternative index servers like
devpi_.
We extend our ``~/.pypirc``: [2]_

.. code:: ini

  [distutils]
  index-servers =
      pypi
      testpypi

  [pypi]
  repository = https://upload.pypi.org/legacy/
  username = fred
  password = secret

  [testpypi]
  repository = https://test.pypi.org/legacy/
  username = fred
  password = secret

We can now release to TestPyPI with:

.. code::

  $ mkrelease -d testpypi -C -e

.. _`test.pypi.org`: https://test.pypi.org/
.. _devpi: https://www.devpi.net

Using GnuPG
===========

Release a package and sign the distributions with GnuPG:

.. code::

  $ mkrelease -d pypi -s -i fred@bedrock.com

The ``-i`` flag is optional and GnuPG will pick your default
key if not given.

Requirements
============

The following commands must be available on the system PATH (you only need
what you plan to use):

* svn

* hg

* git

* scp

* sftp

* gpg

* twine [1]_

Footnotes
=========

.. [1] The twine executable is determined by trying in order:

    1. Value of ``--twine`` command line option, or
    2. Value of ``TWINE`` environment variable, or
    3. Value of ``twine`` configuration file setting, or
    4. ``python -m twine`` if twine is importable, or
    5. ``twine``

.. [2] There are more secure ways to handle login credentials:

    1. Generate an `API token`_ on PyPI, and/or
    2. Make use of twine's `keyring support`_.

.. _`API token`: https://pypi.org/help/#apitoken
.. _`keyring support`: https://twine.readthedocs.io/en/stable/index.html#keyring-support

Related
=======

Also see our Python documentation viewer `jarn.viewdoc`_.

.. _`jarn.viewdoc`: https://github.com/Jarn/jarn.viewdoc

