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

Turns out it's quite a bit of work to make a new egg available on a
distribution server. After preparing a package for release (update
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

-C
    Do not checkin modified files from the sandbox.

-T
    Do not tag the release in subversion.

-S
    Do not scp the release to dist-location.

-D
    Dry-run; equivalent to ``-CTS``.

-K
    Keep the temporary build directory.

-s
    Sign the release with GnuPG.

-i identity
    The GnuPG identity to sign with.

-d dist-location
    An scp destination specification, or an index server
    configured in ``~/.pypirc``, or an alias name for either.
    This option may be specified more than once.

``svn-url``
    A URL with protocol svn, svn+ssh, http, https, or file.

``svn-sandbox``
    A local directory; defaults to the current working directory.

Examples
========

Release jarn.somepackage trunk, using version information from the
package's ``setup.py``, and distribute it to the default location::

  $ mkrelease https://svn.jarn.com/public/jarn.somepackage/trunk

The same as 1, but the URL is taken from the SVN sandbox in ``src/jarn.somepackage``::

  $ mkrelease src/jarn.somepackage

Release jarn.somepackage and distribute it via scp to
``jarn.com:/var/dist/public``::

  $ mkrelease -d jarn.com:/var/dist/public src/jarn.somepackage

Release jarn.somepackage and upload it to PyPI::

  $ mkrelease -d pypi src/jarn.somepackage

Configuration
=============

jarn.mkrelease reads available index servers from the distutils configuration
file ``~/.pypirc``. How this file must look is documented elsewhere_.

jarn.mkrelease furthermore reads its own configuration files,
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

  $ mkrelease -d public src/jarn.somepackage

And, because ``public`` is the default location, we can omit ``-d`` entirely::

  $ mkrelease src/jarn.somepackage

.. _elsewhere: http://docs.python.org/distutils/packageindex.html#the-pypirc-file

Working with scp
================

The simplest distribution location is a server directory shared through
Apache. Releasing eggs means scp'ing them to the server::

  $ mkrelease -d jarn.com:/var/dist/public src/jarn.somepackage

We have a distribution point for every project, so customer A does not
see customer B's releases::

  $ mkrelease -d jarn.com:/var/dist/customerB src/jarn.somepackage

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

  $ mkrelease -d public src/jarn.somepackage
  $ mkrelease -d customerB src/jarn.somepackage

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

  $ mkrelease -d ploneorg -d pypi src/jarn.somepackage

Next, we define an alias in ``~/.mkrelease``::

  [defaults]
  python = python2.6

  [aliases]
  plone =
    ploneorg
    pypi

Which allows us to write::

  $ mkrelease -d plone src/jarn.somepackage

Releasing a tag
===============

Release jarn.somepackage from an existing tag::

  $ mkrelease -T https://svn.jarn.com/public/jarn.somepackage/tags/1.0

Using GnuPG
===========

Release jarn.somepackage to PyPI, signing the archive with PGP (the ``gpg``
command must be available on the system PATH)::

  $ mkrelease -d pypi -s -i fred@bedrock.com src/jarn.somepackage

Requirements
============

The following commands must be available on the system PATH:

* svn

* scp

* python2.6

Limitations
===========

The release tag can only be made if the package follows the
standard Subversion repository layout: ``package.name/trunk``,
``package.name/branches/xxx``, and ``package.name/tags/xxx``.
If you have a non-standard repository, you must tag by hand
and run mkrelease with the ``-T`` option.

