==============
jarn.mkrelease
==============
------------------
Release sdist eggs
------------------

Usage
=====

``mkrelease [-CTSDK] [-cz] [-d dist-location] [svn-url|svn-sandbox]``

``mkrelease [-CTSDK] [-cz] [-p [-s [-i identity]]] [svn-url|svn-sandbox]``

Options
=======

-C
    Do not checkin release-relevant files from the sandbox.

-T
    Do not tag the release in subversion.

-S
    Do not scp the release tarball to dist-location.

-D
    Dry-run; equivalent to ``-CTS``.

-K
    Keep the temporary build directory.

-c
    Assume a codespeak.net-style repository layout.

-z
    Create a zip archive instead of the default tar.gz.

-d dist-location
    An scp destination specification.

-p
    Upload the release to PyPI.

-s
    Sign the release tarball with GnuPG.

-i identity
    The GnuPG identity to sign with.

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
    The Python executable used; defaults to ``python2.4``.

``distbase``
    The value prepended if dist-location does not contain a
    host part; defaults to ``jarn.com:/home/psol/dist``.

``distdefault``
    The default value for dist-location; defaults to
    ``jarn.com:/home/psol/dist/public``.

The [aliases] section may be used to define short names for (one or more)
dist-locations.

