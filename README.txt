::

  Usage: mkrelease [-CTSDK] [-z] [-d dist-location] [svn-url|svn-sandbox]
         mkrelease [-CTSDK] [-z] [-p [-s [-i identity]]] [svn-url|svn-sandbox]

  Release an sdist egg.

  Options:
    -C                Do not checkin release-relevant files from the sandbox.
    -T                Do not tag the release in subversion.
    -S                Do not scp the release tarball to dist-location.
    -D                Dry-run; equivalent to -CTS.
    -K                Keep the temporary build directory.

    -z                Create .zip archive instead of the default .tar.gz.

    -d dist-location  A full scp destination specification.
                      There is a shortcut for Jarn use: If the location does not
                      contain a host part, jarn.com:/home/psol/dist is prepended.
                      Defaults to jarn.com:/home/psol/dist/public.

    -p                Upload the release to PyPI.
    -s                Sign the release tarball with GnuPG.
    -i identity       The GnuPG identity to sign with.

    svn-url           A URL with protocol svn, svn+ssh, http, https, or file.
    svn-sandbox       A local directory; defaults to the current working
                      directory.

  Configuration:
    You can set global default options in ~/.mkrelease or
    /etc/jarn.mkrelease.conf.

    The configuration file consists of sections, led by a "[section]" header and
    followed by "name = value" entries.

    The [default] section has the following options:

      python            The python executable to use, defaults to python2.4.
      distbase          The value prepended if dist-location contains no host
                        part.
      distdefault       The default value for dist-location.

  Examples:
    mkrelease -d foobar https://svn.jarn.com/customers/foobar/foobar.theme/trunk

    mkrelease -d foobar src/foobar.theme

    cd src/jarn.somepackage
    mkrelease

