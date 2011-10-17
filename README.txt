==============
jarn.mkrelease
==============
---------------------------------------------------
Build and distribute Python eggs in one simple step
---------------------------------------------------

**mkrelease** is a no-frills Python egg releaser. It is designed to take
the cumber out of building and distributing Python eggs.

Motivation
==========

Here at Jarn we use zc.buildout and pinned egg versions for
customer deployments. This means that for every update, we have to make
proper egg releases of all packages involved.

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

mkrelease requires Python 2.6 or 2.7. Use
``easy_install jarn.mkrelease`` to install the ``mkrelease`` script.
Then put it on your system PATH by e.g. symlinking it to ``/usr/local/bin``.

mkrelease is known to work with the 0.6 series of setuptools
and distribute.

Usage
=====

``mkrelease [options] [scm-url [rev]|scm-sandbox]``

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
    Push sandbox modifications upstream.

``-e, --develop``
    Allow version number extensions (i.e. don't ignore
    respective setup.cfg options.)

``-b, --binary``
    Release a binary (bdist) egg.

``-q, --quiet``
    Suppress output of setuptools commands.

``-l, --list-locations``
    List known dist-locations and exit.

``-h, --help``
    Print the help message and exit.

``-v, --version``
    Print the version string and exit.

``scm-url``
    The URL of a remote SCM repository. The optional ``rev`` argument
    specifies a branch or tag to check out.

``scm-sandbox``
    A local SCM sandbox. Defaults to the current working
    directory.

Examples
========

Release my.package and upload it to PyPI::

  $ mkrelease -d pypi src/my.package

Release my.package and upload it via scp to the jarn.com server::

  $ mkrelease -d jarn.com:/var/dist/public src/my.package

Release my.package using the repository URL instead of a local working copy::

  $ mkrelease -d pypi https://svn.jarn.com/public/my.package/trunk

Release a development egg of my.package (while suppressing setuptools output)::

  $ mkrelease -qed jarn.com:/var/dist/public src/my.package

Configuration
=============

mkrelease reads available index servers from the distutils configuration
file ``~/.pypirc``. This file must contain your PyPI account information::

  [distutils]
  index-servers =
    pypi

  [pypi]
  username = fred
  password = secret

mkrelease also reads its own configuration file ``~/.mkrelease``.
Here's an example::

  [mkrelease]
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

Armed with this configuration we can shorten example 2 to::

  $ mkrelease -d public src/my.package

And because ``public`` is the default location, we can omit ``-d`` entirely::

  $ mkrelease src/my.package

Working with SCP
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

  [mkrelease]
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

Working with Index Servers
==========================

Another way of distributing Python eggs is by uploading them to dedicated
index servers, notably PyPI. Given the ``~/.pypirc`` file from above
we can release on PyPI by typing::

  $ mkrelease -d pypi src/my.package

Index servers are not limited to PyPI though.
For example, in the Plone world it is common practice to upload packages to
`plone.org`_ as well as to PyPI.

.. _`plone.org`: http://plone.org/products

We extend our ``~/.pypirc`` to add a second index server::

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

  $ mkrelease -d ploneorg src/my.package

The ``-d`` flag may be specified more than once::

  $ mkrelease -d pypi -d ploneorg src/my.package

Alternatively, we can group the servers by defining an alias in
``~/.mkrelease``::

  [aliases]
  plone =
    pypi
    ploneorg

And type::

  $ mkrelease -d plone src/my.package

Note: Setuptools rebuilds the egg for every index server it uploads it to.
This means that MD5 sums and GnuPG signatures will differ between servers.
If this is not what you want, upload to only one server and distribute from
there by other means.

Releasing a Tag
===============

Release my.package from an existing tag::

  $ mkrelease -T https://svn.jarn.com/public/my.package/tags/1.0

With Mercurial and Git we can use the second argument to specify the tag::

  $ mkrelease -T ssh://git@github.com/Jarn/my.package 1.0

Using GnuPG
===========

Release my.package and sign the archive with GnuPG::

  $ mkrelease -s -i fred@bedrock.com src/my.package

The ``-i`` flag is optional, and GnuPG will pick your default
key if not given. In addition, defaults for ``-s`` and ``-i`` can be
configured in ``~/.pypirc``::

  [distutils]
  index-servers =
    pypi

  [pypi]
  username = fred
  password = secret
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

* gpg

Limitations
===========

Subversion
----------

The release tag can only be created if the repository follows one of
these layouts:

* The standard Subversion layout: ``my.package/trunk``,
  ``my.package/branches``, and ``my.package/tags``.

* The singular-form layout variant: ``my.package/trunk``,
  ``my.package/branch``, and ``my.package/tag``.

Git
---

Git's short-hand notation for ``ssh://`` URLs is not supported.

