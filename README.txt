==============
jarn.mkrelease
==============
-------------------
Python egg releaser
-------------------

**mkrelease** is a no-frills Python egg releaser. It was created to take
the cumber out of building and distributing Python eggs.

Motivation
==========

Here at Jarn, we use zc.buildout and pinned egg versions for
customer deployments. This means that for every update, we have to make
proper egg releases of all modified packages.

Turns out it's quite a bit of work to put a new egg on a
distribution server! After preparing a package for release (update
version strings, etc) we typically have to:

1. Commit modified files.

2. Tag the release.

3. Package up an egg.

4. Distribute the egg via scp or upload it to an index server.

Now multiply by the number of packages waiting for release, and the moment of
*I gotta script this* approaches at warp 9.

Installation
============

mkrelease requires Python 2.6 for its improved distutils support. Use
``easy_install jarn.mkrelease`` to install the ``mkrelease`` script.
Then put it on your system PATH by e.g. symlinking it to ``/usr/local/bin``.

mkrelease is known to work with the 0.6 series of setuptools (0.6c11)
and distribute (0.6.10).

Usage
=====

``mkrelease [options] [scm-url|scm-sandbox]``

Options
=======

``-C, --no-commit``
    Do not commit modified files from the sandbox.

``-T, --no-tag``
    Do not tag the release in SCM.

``-S, --no-upload``
    Do not upload the release to dist-location.

``-n, --dry-run``
    Dry-run; equivalent to ``-CTS``.

``--svn, --hg, --git``
    Select the SCM type. Only required if the SCM type
    cannot be guessed from the argument.

``-d dist-location, --dist-location=dist-location``
    An scp destination specification, or an index server
    configured in ``~/.pypirc``, or an alias name for either.
    This option may be specified more than once.

``-s, --sign``
    Sign the release with GnuPG.

``-i identity, --identity=identity``
    The GnuPG identity to sign with.

``-p, --push``
    Push changes upstream (Mercurial and Git.)

``-e, --develop``
    Allow version number extensions (i.e. don't ignore
    respective setup.cfg options.)

``-b, --binary``
    Release a binary (bdist) egg.

``-q, --quiet``
    Suppress output of setuptools commands.

``-h, --help``
    Print the help message and exit.

``-v, --version``
    Print the version string and exit.

``scm-url``
    The URL of a remote SCM repository.

``scm-sandbox``
    A local SCM sandbox; defaults to the current working
    directory.

Examples
========

Release my.package, using version information from its ``setup.py``,
and distribute it to the default location::

  $ mkrelease https://svn.jarn.com/public/my.package/trunk

The same as above, but release the contents of the SCM sandbox in
``src/my.package``::

  $ mkrelease src/my.package

Release my.package and distribute it via scp to
``jarn.com:/var/dist/public``::

  $ mkrelease -d jarn.com:/var/dist/public src/my.package

Release my.package and upload it to PyPI::

  $ mkrelease -d pypi src/my.package

Configuration
=============

mkrelease reads available index servers from the distutils configuration
file ``~/.pypirc``. How this file must look is documented elsewhere_.

mkrelease furthermore reads its own configuration file
``~/.mkrelease``. Here's an example::

  [defaults]
  distbase =
  distdefault = public

  [aliases]
  public =
    jarn.com:/var/dist/public
  customerA =
    jarn.com:/var/dist/customerA
  world =
    public
    pypi

(Note that ``pypi`` refers to the index server `pypi` as configured in
``~/.pypirc``. More on this later.)

Armed with the above configuration we can shorten example 3 to::

  $ mkrelease -d public src/my.package

And, because ``public`` is the default location, we can omit ``-d`` entirely::

  $ mkrelease src/my.package

.. _elsewhere: http://docs.python.org/distutils/packageindex.html#the-pypirc-file

Working with scp
================

The simplest distribution location is a server directory shared through
Apache. Releasing an egg means scp-ing it to the appropriate place on the
server::

  $ mkrelease -d jarn.com:/var/dist/public src/my.package

We have a distribution point for every project, so customer A does not
see customer B's releases::

  $ mkrelease -d jarn.com:/var/dist/customerB src/my.package

Typing the full destination every time is tedious, even setting up an alias
for each and every customer is, so we configure distbase instead::

  [defaults]
  distbase = jarn.com:/var/dist
  distdefault = public

  [aliases]
  world =
    public
    pypi

The distbase is prepended if an scp destination does not contain a
host part. We can now write::

  $ mkrelease -d public src/my.package
  $ mkrelease -d customerB src/my.package

Working with index servers
==========================

Another way of distributing Python eggs is by uploading to dedicated
index servers, notably PyPI. We first need a ``~/.pypirc`` file::

  [distutils]
  index-servers =
    pypi

  [pypi]
  username = fred
  password = secret

To release a package on PyPI we can now type::

  $ mkrelease -d pypi src/my.package

Index servers are not limited to PyPI though.
For example, in the Plone world it is common practice to upload packages to
plone.org as well as PyPI. Let's extend our ``~/.pypirc``::

  [distutils]
  index-servers =
    pypi
    ploneorg

  [pypi]
  username = fred
  password = secret

  [ploneorg]
  repository = http://plone.org/products
  username = fred
  password = secret

This allows us to write::

  $ mkrelease -d pypi -d ploneorg src/my.package

Finally, we can group the servers by defining an alias in ``~/.mkrelease``::

  [aliases]
  plone =
    pypi
    ploneorg

And type::

  $ mkrelease -d plone src/my.package

Note: Due to the way setuptools works, the egg is rebuilt for every index
server it is uploaded to. This means that MD5 sums and GnuPG signatures will
differ between servers. If this is not what you want, upload to only one
server and distribute from there by other means (e.g. replication).

Releasing a tag
===============

Release my.package from an existing tag::

  $ mkrelease -T https://svn.jarn.com/public/my.package/tags/1.0

Only Subversion allows us to specify the tag as part of the URL. With
Mercurial and Git we need a local working copy, switched to the tag
we want to release::

  $ git checkout -f 1.0
  $ mkrelease -T

Using GnuPG
===========

Release my.package and sign the archive with GnuPG (the ``gpg``
command must be available on the system PATH)::

  $ mkrelease -s -i fred@bedrock.com -d pypi src/my.package

The ``-i`` flag is entirely optional, and GnuPG will pick your default
key if not given. Additionally, defaults for ``-s`` and ``-i`` may be
configured in ``~/.mkrelease``::

  [defaults]
  sign = yes
  identity = fred@bedrock.com

Requirements
============

The following commands must be available on the system PATH (you only need
what you plan to use):

* svn

* hg

* git

* scp

Limitations
===========

Subversion
----------

The release tag can only be created if the package follows the
standard Subversion repository layout: ``package.name/trunk``,
``package.name/branches``, and ``package.name/tags``.
If you have a non-standard repository, you must tag by hand
and run mkrelease with the ``-T`` option.

Git
---

Git's short-hand notation for ``ssh://`` URLs is not supported.

