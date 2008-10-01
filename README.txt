Usage: mkrelease [-CTSDK] [-d dist-location] [svn-url|svn-sandbox]

Release an sdist egg.

Options:
  -C                Do not checkin CHANGES.txt and setup.py.
  -T                Do not tag the release in subversion.
  -S                Do not scp the release tarball to dist-location.
  -D                Dry-run; equivalent to -CTS.
  -K                Keep the temporary build directory.

  -d dist-location  A full scp destination specification.
                    There is a shortcut for Jarn use: If the location does not
                    contain a host part, jarn.com:/home/psol/dist is prepended.
                    Defaults to public (jarn.com:/home/psol/dist/public).

  svn-url           A URL with protocol svn, svn+ssh, http, https, or file.
  svn-sandbox       A local directory; defaults to the current working directory.

Examples:
  mkrelease -d nordic https://svn.jarn.com/customers/nordic/nordic.content/trunk

  mkrelease -d nordic src/nordic.content

  cd src/jarn.somepackage
  mkrelease

