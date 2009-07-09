==============
jarn.mkrelease
==============
------------------
Release sdist eggs
------------------

**jarn.mkrelease** is a no-frills Python egg releaser. It was created to take
the cumber out of building and distributing Python eggs.

Motivation
==========

Here at Jarn, we have switched to zc.buildout and pinned egg versions for
customer deployments. This means that for every update, we have to make
proper egg releases of all modified packages.

Turns out it's quite a bit of work to put a new egg on a
distribution server! After preparing a package for release (update
version strings, etc.), we typically have to:

1. Commit modified files.

2. Tag the release in SCM.

3. Package up an egg.

4. Distribute the egg via scp or upload it to an index server.

Now multiply by the number of packages needing a release, and the moment
of `I gotta script this` approaches at warp 9.

Enter jarn.mkrelease.

Installation
============

jarn.mkrelease requires Python 2.6 for its improved distutils support. Use
``easy_install jarn.mkrelease`` to install the ``mkrelease`` script.
Then put it on your system PATH by e.g. symlinking it to ``/usr/local/bin``.

Usage
=====

``mkrelease [options] [scm-url|scm-sandbox]``

Options
=======

``-C, --skip-checkin``
    Do not checkin modified files from the sandbox.

``-T, --skip-tag``
    Do not tag the release in SCM.

``-S, --skip-upload``
    Do not upload the release to dist-location.

``-D, --dry-run``
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
    Push changes upstream (Mercurial and Git).

``-e, --develop``
    Allow version number extensions (i.e. don't ignore the
    respective setup.cfg options).

``-q, --quiet``
    Suppress output of setuptools commands.

``-k, --keep-temp``
    Keep the temporary build directory.

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

Release my.package, using version information from the package's
``setup.py``, and distribute it to the default location::

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
``~/.pypirc``.)

Armed with this configuration we can shorten example 3 to::

  $ mkrelease -d public src/my.package

And, because ``public`` is the default location, we can omit ``-d`` entirely::

  $ mkrelease src/my.package

.. _elsewhere: http://docs.python.org/distutils/packageindex.html#the-pypirc-file

Working with scp
================

The simplest distribution location is a server directory shared through
Apache. Releasing eggs means scp-ing them to the server::

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

In the Plone world, it is common practice to upload packages to plone.org
`and` PyPI. For this to work, we first need a ``~/.pypirc`` file::

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

We can now type::

  $ mkrelease -d pypi -d ploneorg src/my.package

Next, we define an alias in ``~/.mkrelease``::

  [aliases]
  plone =
    pypi
    ploneorg

Which allows us to write::

  $ mkrelease -d plone src/my.package

Releasing a tag
===============

Release my.package from an existing tag::

  $ mkrelease -T https://svn.jarn.com/public/my.package/tags/1.0

Only Subversion allows us to specify a branch or tag to check out. With
Mercurial and Git we need a local working copy, switched to the tag
we want to release::

  $ git checkout -f 1.0
  $ mkrelease -T

Using GnuPG
===========

Release my.package to PyPI and sign the archive with GnuPG (the ``gpg``
command must be available on the system PATH)::

  $ mkrelease -d pypi -s -i fred@bedrock.com src/my.package

For convenience, and to support mandatory-signing scenarios, defaults
for ``-s`` and ``-i`` may be configured in ``~/.mkrelease``::

  [defaults]
  distbase = jarn.com:/var/dist
  distdefault = public
  sign = true
  identity = fred@bedrock.com

Requirements
============

The following commands must be available on the system PATH:

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

Giving the ``-p`` option results in ``git push origin`` and
``git push origin tag <tagid>`` respectively. If this does not fit your
setup, avoid ``-p`` and push manually.

Git's short-hand notation for ``ssh://`` URLs is not supported.

