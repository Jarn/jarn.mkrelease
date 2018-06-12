==============
jarn.mkrelease
==============
---------------------------------------------------
Python package releaser
---------------------------------------------------

**mkrelease** is a no-frills Python package releaser. It is designed to take
the cumber out of building and distributing Python packages.

mkrelease supports source distributions, binary eggs, and `wheels`_.

.. _`wheels`: https://wheel.readthedocs.io/

Motivation
==========

After preparing a package for release (update version strings, dates,
etc.), we typically have to:

1. Commit modified files.

2. Tag the release.

3. Build a source distribution, egg, or wheel.

4. Distribute the result via scp or upload it to an index server.

Now imagine doing this a lot, and the need for automation becomes
obvious.

Installation
============

mkrelease works with Python 2.6 - 3.6 and all released versions of setuptools
and distribute.

Use ``pip install jarn.mkrelease`` to install the ``mkrelease`` script.

Usage
=====

``mkrelease [options] [scm-sandbox | scm-url [rev]]``

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
    Dry-run; equivalent to ``-CTRS``.

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
    Ignore setuptools extensions and collect files via
    ``MANIFEST.in`` only.

``-e, --develop``
    Allow setuptools build tags. Implies ``-T``.

``-q, --quiet``
    Suppress output of setuptools commands.

``-c config-file, --config-file=config-file``
    Use config-file instead of the default ``~/.mkrelease``.

``-l, --list-locations``
    List known dist-locations and exit.

``-h, --help``
    Print the help message and exit.

``-v, --version``
    Print the version string and exit.

``scm-sandbox``
    A local SCM sandbox. Defaults to the current working
    directory.

``scm-url [rev]``
    The URL of a remote SCM repository. The optional ``rev``
    argument specifies a branch or tag to check out.

Examples
========

Release mypackage and upload it to PyPI::

  $ mkrelease -d pypi src/mypackage

Release mypackage using the repository URL instead of a local working copy::

  $ mkrelease -d pypi git@github.com:Jarn/mypackage

Release mypackage and upload it via scp to the jarn.com server::

  $ mkrelease -d jarn.com:/var/dist/public src/mypackage

Release a development egg of mypackage while suppressing setuptools output::

  $ mkrelease -qed stefan@jarn.com:eggs src/mypackage

Configuration
=============

mkrelease reads available index servers from the distutils_ configuration
file ``~/.pypirc``. This file must contain your PyPI account information::

  [distutils]
  index-servers =
      pypi

  [pypi]
  repository = https://upload.pypi.org/legacy/
  username = fred
  password = secret

mkrelease also reads its own configuration file ``~/.mkrelease``.
Here's an example::

  [mkrelease]
  # Release steps
  commit = yes
  tag = yes
  push = yes
  register = no
  upload = yes

  # Default dist-location
  dist-location =

  # One or more of: zip gztar egg wheel
  formats = zip

  # Sign with GnuPG
  sign = no
  identity =

  # Setuptools options
  manifest-only = no
  develop = no
  quiet = no

  [aliases]
  # Map name to one or more dist-locations
  public =
      jarn.com:/var/dist/public
  customerA =
      jarn.com:/var/dist/customerA
  world =
      pypi
      public

The ``register``, ``sign``, and ``identity`` options may be overridden on a
per-server basis by placing them in the respective server sections in
``~/.pypirc``.

.. _distutils: https://docs.python.org/3/distutils/packageindex.html#pypirc

Upload with SCP
================

The simplest distribution location is a server directory shared through
Apache. Releasing a package means scp-ing it to the appropriate place
on the server::

  $ mkrelease -d jarn.com:/var/dist/customerB src/mypackage

To upload via sftp instead of scp, specify the destination in URL form::

  $ mkrelease -d sftp://jarn.com/var/dist/customerB src/mypackage

For consistency scp URLs are supported as well::

  $ mkrelease -d scp://jarn.com/var/dist/customerB src/mypackage

Note: Unlike scp, the sftp client does not prompt for login credentials.
This means that non-interactive login must be configured on the
destination server or the upload will fail.

Upload to Index Servers
==========================

Another way of distributing Python packages is by uploading them to dedicated
index servers, notably PyPI. Given the ``~/.pypirc`` file from above
we can release to PyPI by typing::

  $ mkrelease -d pypi src/mypackage

Index servers are not limited to PyPI though.
There is `test.pypi.org`_, and there are alternative index servers like
`devpi`_.

.. _`test.pypi.org`: https://test.pypi.org/
.. _`devpi`: https://www.devpi.net

We extend our ``~/.pypirc`` to add an additional server::

  [distutils]
  index-servers =
      pypi
      test

  [pypi]
  repository = https://upload.pypi.org/legacy/
  username = fred
  password = secret

  [test]
  repository = https://test.pypi.org/legacy/
  username = fred
  password = secret

This allows us to release to test.pypi.org by typing::

  $ mkrelease -CT -d test src/mypackage

Note: Setuptools rebuilds the package for every index server it uploads it to.
This means that SHA sums and GnuPG signatures will differ between servers.
If this is not what you want, upload to only one server or use an upload tool
like `twine`_::

    $ mkrelease -RS -z -w src/mypackage
    $ twine upload src/mypackage/dist/*

.. _`twine`: https://twine.readthedocs.io

Releasing a Tag
===============

Release mypackage from an existing tag::

  $ mkrelease -T -d pypi git@github.com:Jarn/mypackage 1.0

Using GnuPG
===========

Release mypackage and sign the archive with GnuPG::

  $ mkrelease -s -i fred@bedrock.com -d pypi src/mypackage

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

Keyring Support
===============

On Mac OS X, mkrelease installs the `keyring`_ module which provides access
to the Mac OS X Keychain. To store your PyPI password in the Keychain type::

  $ keyring set https://upload.pypi.org/legacy/ <pypi-username>

Then delete the password line from ``~/.pypirc``.

Note: `keyring`_ works on other platforms but because of C-language
dependencies you have to install it yourself.

.. _`keyring`: https://github.com/jaraco/keyring

Related
=======

Also see our Python documentation viewer `jarn.viewdoc`_.

.. _`jarn.viewdoc`: https://github.com/Jarn/jarn.viewdoc

