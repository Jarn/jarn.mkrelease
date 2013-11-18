==============
jarn.mkrelease
==============
---------------------------------------------------
Python egg releaser
---------------------------------------------------

**mkrelease** is a no-frills Python egg releaser. It is designed to take
the cumber out of building and distributing Python eggs.

Also see `jarn.viewdoc`_.

.. _`jarn.viewdoc`: https://pypi.python.org/pypi/jarn.viewdoc

Motivation
==========

Python eggs are great, and we strive to release all software in egg form.
However, as projects grow larger and are comprised of more and more eggs,
release requirements can become a burden.

This is because it takes some work to put a new egg on a
distribution server. After preparing a package for release (update
version strings, etc.), we typically have to:

1. Commit modified files.

2. Tag the release.

3. Package up an egg.

4. Distribute the egg via scp or upload it to an index server.

Now imagine doing this a lot, and the need for automation becomes
obvious.

Installation
============

mkrelease works with Python 2.6 - 3.3 and all released versions of setuptools
and distribute.

Use ``easy_install jarn.mkrelease`` to install the ``mkrelease`` script.
Then put it on your system PATH by e.g. symlinking it to ``/usr/local/bin``.

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
    An scp or sftp destination specification, an index
    server configured in ``~/.pypirc``, or an alias name for
    either. This option may be specified more than once.

``-s, --sign``
    Sign the release with GnuPG.

``-i identity, --identity=identity``
    The GnuPG identity to sign with.

``-p, --push``
    Push sandbox modifications upstream.

``-e, --develop``
    Allow version number extensions (i.e. don't ignore
    respective ``setup.cfg`` options.)

``-b, --binary``
    Release a binary (bdist) egg.

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

Release a development egg of my.package while suppressing setuptools output::

  $ mkrelease -qed jarn.com:/var/dist/private src/my.package

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
      pypi
      public

(Note that ``pypi`` refers to the index server *pypi* as configured in
``~/.pypirc`` above.)

Armed with this configuration we can shorten example 2 to::

  $ mkrelease -d public src/my.package

And because ``public`` is the default location, we can omit ``-d`` entirely::

  $ mkrelease src/my.package

Working with SCP and SFTP
=========================

The simplest distribution location is a server directory shared through
Apache. Releasing an egg just means scp-ing it to the appropriate place on the
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
      pypi
      public

The distbase is prepended when an scp destination does not contain a
host part. We can now write::

  $ mkrelease -d public src/my.package
  $ mkrelease -d customerB src/my.package

To upload via sftp instead of scp, specify the destination in URL form::

  $ mkrelease -d sftp://jarn.com/var/dist/public src/my.package

For consistency scp URLs are supported as well::

  $ mkrelease -d scp://jarn.com/var/dist/public src/my.package

Note: Unlike scp, the sftp client does not prompt for login credentials.
This means that for sftp non-interactive login must be configured on
the destination server.

Working with Index Servers
==========================

Another way of distributing Python eggs is by uploading them to dedicated
index servers, notably PyPI. Given the ``~/.pypirc`` file from above
we can release to PyPI by typing::

  $ mkrelease -d pypi src/my.package

Index servers are not limited to PyPI though.
For example, in the Plone world it is common practice to upload packages to
`plone.org`_ as well as to PyPI.

.. _`plone.org`: https://plone.org/products

We extend our ``~/.pypirc`` to add a second index server::

  [distutils]
  index-servers =
      pypi
      plone

  [pypi]
  username = fred
  password = secret

  [plone]
  repository = https://plone.org/products
  username = fred
  password = secret

This allows us to release to plone.org by typing::

  $ mkrelease -d plone src/my.package

The ``-d`` option can be specified more than once::

  $ mkrelease -d pypi -d plone src/my.package

Alternatively, we can group the servers by creating an alias in
``~/.mkrelease``::

  [aliases]
  plone-world =
      pypi
      plone

And type::

  $ mkrelease -d plone-world src/my.package

Note: Setuptools rebuilds the egg for every index server it uploads it to.
This means that MD5 sums and GnuPG signatures will differ between servers.
If this is not what you want, upload to only one server and distribute from
there by other means.

Releasing a Tag
===============

Release my.package from an existing Subversion tag::

  $ mkrelease -T https://svn.jarn.com/public/my.package/tags/1.0

With Mercurial and Git we can use the second argument to specify the tag::

  $ mkrelease -T git@github.com:Jarn/my.package 1.0

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

* sftp

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

