==============
jarn.mkrelease
==============
------------------
Release sdist eggs
------------------

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
    Do not scp the release tarball to dist-location.

-D
    Dry-run; equivalent to ``-CTS``.

-K
    Keep the temporary build directory.

-z
    Create a zip archive instead of the default tar.gz.

-s
    Sign the release tarball with GnuPG.

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

Files
=====

``/etc/mkrelease``
    Global configuration file.

``~/.mkrelease``
    Per user configuration file.

The configuration file consists of sections, led by a "[section]" header
and followed by "name = value" entries.

The [defaults] section has the following options:

``python``
    The Python executable used; defaults to ``python2.6``.

``distbase``
    The value prepended if dist-location does not contain a
    host part. Applies to scp dist-locations only.

``distdefault``
    The default value for dist-location.

The [aliases] section may be used to define short names for (one or more)
dist-locations.

