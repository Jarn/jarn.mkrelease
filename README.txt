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

1. Check in modified files.

2. Tag the release in Subversion.

3. Package up an egg.

4. Distribute the egg via scp or upload it to an index server.

Now multiply by the number of packages needing a release, and the moment
of `I gotta script this` approaches at warp 9.

Enter jarn.mkrelease.

Usage
=====

``mkrelease [options] [svn-url|svn-sandbox]``

Options
=======

``-C, --skip-checkin``
    Do not checkin modified files from the sandbox.

``-T, --skip-tag``
    Do not tag the release in subversion.

``-S, --skip-scp``
    Do not scp the release to dist-location.

``-D, --dry-run``
    Dry-run; equivalent to ``-CTS``.

``-K, --keep-temp``
    Keep the temporary build directory.

``-s, --sign``
    Sign the release with GnuPG.

``-i identity, --identity=identity``
    The GnuPG identity to sign with.

``-d dist-location, --dist-location=dist-location``
    An scp destination specification, or an index server
    configured in ``~/.pypirc``, or an alias name for either.
    This option may be specified more than once.

``-h, --help``
    Print the help message and exit.

``-v, --version``
    Print the version string and exit.

``svn-url``
    A URL with protocol svn, svn+ssh, http, https, or file.

``svn-sandbox``
    A local directory; defaults to the current working directory.

Examples
========

Release my.package trunk, using version information from the
package's ``setup.py``, and distribute it to the default location::

  $ mkrelease https://svn.jarn.com/public/my.package/trunk

The same as above, but the URL is taken from the SVN sandbox in ``src/my.package``::

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

mkrelease furthermore reads its own configuration files,
``/etc/mkrelease`` and ``~/.mkrelease``. Here's an example::

  [defaults]
  python = python2.6
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
Apache. Releasing eggs means scp'ing them to the server::

  $ mkrelease -d jarn.com:/var/dist/public src/my.package

We have a distribution point for every project, so customer A does not
see customer B's releases::

  $ mkrelease -d jarn.com:/var/dist/customerB src/my.package

Typing the full destination every time is tedious, even setting up an alias
for each and every customer is, so we configure distbase instead::

  [defaults]
  python = python2.6
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

  $ mkrelease -d ploneorg -d pypi src/my.package

Next, we define an alias in ``~/.mkrelease``::

  [defaults]
  python = python2.6

  [aliases]
  plone =
    ploneorg
    pypi

Which allows us to write::

  $ mkrelease -d plone src/my.package

Releasing a tag
===============

Release my.package from an existing tag::

  $ mkrelease -T https://svn.jarn.com/public/my.package/tags/1.0

Using GnuPG
===========

Release my.package to PyPI and sign the archive with PGP (the ``gpg``
command must be on the system PATH)::

  $ mkrelease -d pypi -s -i fred@bedrock.com src/my.package

Requirements
============

The following commands must be available on the system PATH:

* svn

* scp

* python2.6 (alternatively, configure the interpeter in ``~/.mkrelease``)

Limitations
===========

The release tag can only be made if the package follows the
standard Subversion repository layout: ``package.name/trunk``,
``package.name/branches/xxx``, and ``package.name/tags/xxx``.
If you have a non-standard repository, you must tag by hand
and run mkrelease with the ``-T`` option.

