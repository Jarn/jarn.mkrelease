Changelog
=========

5.0 - 2022-02-26
----------------

- NEW: File finder extensions are no longer installed by default.
  [stefan]

- NEW: push is now on by default
  [stefan]

- NEW: register is now off by default
  [stefan]

- NEW: formats now defaults to gztar + wheel
  [stefan]

- Do not require setup.py if setup.cfg exists.
  [stefan]

- Switch to the nose2 test runner for its fast multiprocessing plugin.
  [stefan]

4.4 - 2022-02-26
----------------

- Support Python 2.7 - 3.10.
  [stefan]

- Support local distutils in setuptools >= 60.0.0.
  [stefan]

- Add output colors.
  [stefan]

- Require twine_ for register and upload operations.
  [stefan]

- Move metadata to setup.cfg.
  [stefan]

- Move tests out of ``jarn.mkrelease`` namespace.
  [stefan]

- Include tests in sdist but not in wheel.
  [stefan]

4.3 - 2019-01-28
----------------

- Fix issue #10: Can no longer run from a zc.buildout.
  [stefan]

- Support ``python -m jarn.mkrelease``.
  [stefan]

4.2 - 2019-01-25
----------------

- Drop Python 2.6 support, add Python 3.7.
  [stefan]

- Update wheel and keyring dependencies.
  [stefan]

- Add a complete config file example to the README.
  [stefan]

- Accept ``dist-location`` as alias for ``distdefault`` in config files.
  [stefan]

- Convert dashes to underscores in config parser optionxform.
  [stefan]

4.1 - 2017-10-06
----------------

- Add -m option to skip setuptools extensions.
  [stefan]

- Never read existing ``SOURCES.txt`` files.
  [stefan]

- Allow --egg as alias for --binary.
  [stefan]

4.0.1 - 2017-07-20
------------------

- Fix conditional include of keyring.
  [stefan]

4.0 - 2017-07-20
----------------

- Add support for source distributions in gztar format.
  [stefan]

- Add support for wheel files.
  [stefan]

- Allow multiple archive formats per release.
  [stefan]

- Protect against bad or incomplete locale settings.
  [stefan]

- The secondary thread would sometimes not terminate in Python 2.
  [stefan]

3.10 - 2017-02-01
-----------------

- Support setuptools >= 33.1.0.
  [stefan]

3.9 - 2017-01-31
----------------

- Catch up with late-2016 PyPI API change.
  [stefan]

- Add -R option to skip the register step.
  [stefan]

- Support Python 2.6 - 3.6 without 2to3.
  [stefan]

- Handle return code changes in Mercurial 3.1.1.
  [stefan]

3.8 - 2013-11-21
----------------

- Support Python 3.x.
  [stefan]

3.7 - 2012-08-22
----------------

- Fix compilation of Python source files when the -b option is given.
  [stefan]

- Run check command as part of sdist and register commands.
  [stefan]

- Add SFTP support.
  [stefan]

- Allow ``sftp://`` and ``scp://`` URLs as dist-locations.
  [stefan]

3.6 - 2012-07-11
----------------

- Handle return code changes in Mercurial 2.1.
  [stefan]

- Add setuptools-subversion dependency.
  [stefan]

- Support Subversion 1.7 with the help of setuptools-subversion.
  [stefan]

3.5 - 2011-11-25
----------------

- Allow multiple values for the ``distdefault`` config file option.
  [stefan]

- Defer list-locations until after all arguments have been parsed.
  [stefan]

- Make tests run twice as fast by avoiding Subversion checkouts.
  [stefan]

3.4 - 2011-11-10
----------------

- Warn if -p is given but no upstream location is found.
  [stefan]

- Always push to default in Mercurial.
  [stefan]

- Avoid reading empty lines from terminating subprocesses.
  [stefan]

- Fix bug in handling of distbase.
  [stefan]

3.3 - 2011-10-31
----------------

- Add setuptools to the PYTHONPATH for subprocesses.
  [stefan]

- Unset any PYTHONPATH while executing SCM commands.
  [stefan]

- Support Git's short-form ``ssh://`` URLs.
  [stefan]

- Add -c option to specify a config file other than ~/.mkrelease.
  [stefan]

3.2 - 2011-10-21
----------------

- Fix the environment passed to subprocesses; Mercurial did not appreciate
  the mangled PYTHONPATH.
  [stefan]

- Allow to specify the branch or tag to check out from Git and Mercurial
  repositories.
  [stefan]

- Adapt to new status output in Subversion 1.6.
  [stefan]

- Always include ``distdefault`` in list-locations.
  [stefan]

- Detect Subversion repos from ``file://`` URLs.
  [stefan]

- Detect bare Git repos from ``file://`` URLs.
  [stefan]

3.1 - 2011-07-19
----------------

- Pass the PYTHONPATH to subprocesses so mkrelease works in zc.buildout
  environments.
  [stefan]

- Improve SCM detection in situations where one or more SCMs are nested.
  [stefan]

- Add support for relative ``file:`` URLs.
  [stefan]

- Depend on lazy_ instead of carrying a local implementation.
  [stefan]

.. _lazy: https://github.com/stefanholek/lazy

3.0.10 - 2011-07-07
-------------------

- Add -l option to list known dist-locations (i.e. servers and aliases).
  [stefan]

- Drop support for server URLs as dist-locations. Server URLs are
  not unique.
  [stefan]

- Update the Mercurial test repository so tagging tests don't fail
  under Mercurial 1.8.
  [stefan]

3.0.9 - 2010-12-31
------------------

- Rename ``[defaults]`` configuration file section to ``[mkrelease]``.
  [stefan]

- Various internal code cleanups.
  [stefan]

3.0.8 - 2010-08-13
------------------

- Avoid underscores in dependency names.
  [stefan]

- Handle return code changes in Mercurial 1.6.
  [stefan]

3.0.7 - 2010-07-07
------------------

- Improve documentation and error messages.
  [stefan]

3.0.5 - 2010-03-23
------------------

- Allow per-server configuration of -s and -i defaults.
  [stefan]

- Support the codespeak.net Subversion repository layout.
  [stefan]

3.0.4 - 2010-03-16
------------------

- Status checks didn't use the same path restrictions as commits
  (Mercurial and Git.)
  [stefan]

3.0.3 - 2010-03-16
------------------

- Change how we check for existing tags in Subversion repositories.
  [stefan]

- Make sandbox-status checks more robust in all three SCMs.
  [stefan]

3.0.2 - 2010-03-12
------------------

- Add support for Git 1.7.
  [stefan]

3.0.1 - 2010-02-07
------------------

- Stop when -d pypi is given but no configuration can be found.
  [stefan]

- Use ``gnu_getopt`` to parse the command line.
  [stefan]

3.0 - 2010-01-15
----------------

- Switch to -n for dry-run to be consistent with other tools.
  [stefan]

- Rename --skip-* long options to --no-* for the same reason.
  [stefan]

- Fix a bug in Mercurial and Git sandbox detection.
  [stefan]

- Prepare for standalone distutils.
  [stefan]

2.0.4 - 2010-01-10
------------------

- Improve Git support to handle remotes other than origin.
  [stefan]

- Fix SCM detection in ``ssh://`` URLs.
  [stefan]

2.0.3 - 2010-01-03
------------------

- Add -b option for releasing binary eggs.
  [stefan]

- Don't choke on dirty sandboxes when dry-running.
  [stefan]

2.0.2 - 2009-08-29
------------------

- Filter meta files (``.svn*``, ``.hg*``, ``.git*``) and never include
  them in releases.
  [stefan]

- Make sure to clean up all temporary files.
  [stefan]

2.0.1 - 2009-07-24
------------------

- Fixed bug which could cause mkrelease to issue eggs with faulty manifest
  files (Symptom: data files not installed).
  [stefan]

- The -e flag now implies -T. We never want to tag a development release.
  [stefan]

2.0 - 2009-07-16
----------------

- Allow command line options to appear after the argument. As in:
  ``mkrelease src/mypackage -q -d pypi``.
  [stefan]

2.0b2 - 2009-07-09
------------------

- Improve user feedback in the SCM-detection part.
  [stefan]

- Document the -e flag.
  [stefan]

- Drop global configuration file for YAGNI.
  [stefan]

- Allow to set default values for -s and -i in ~/.mkrelease.
  [stefan]

2.0b1 - 2009-07-03
------------------

- By default, ignore all version number extensions (dev-r12345)
  that may be configured in setup.cfg. Passing the -e flag
  disables this safeguard.
  [witsch, stefan]

- Delete any existing signature file before signing anew. This keeps
  GnuPG from complaining about existing (but left-over) files.
  [stefan]

2.0a2 - 2009-06-27
------------------

- Drop configurable Python and use sys.executable. This also means we
  now require Python 2.6.
  [stefan]

- Force setuptools to only use file-finders for the selected SCM type.
  This is required to support multi-SCM sandboxes (think git-svn).
  [stefan]

- Treat Subversion sandboxes just like the others and avoid the
  temporary checkout step.
  [stefan]

- Remove the -u flag for being pointless.
  [stefan]

2.0a1 - 2009-06-14
------------------

- Added support for Mercurial and Git.
  [stefan]

- Added 250+ unit tests.
  [stefan]

1.0.2 - 2009-06-13
------------------

- Documented long options.
  [stefan]

- Print a "Tagging ..." line before tagging.
  [stefan]

1.0 - 2009-05-14
----------------

- Print help and version to stdout, not stderr.
  [stefan]

1.0b4 - 2009-04-30
------------------

- Since distutils commands may return 0, successful or not, we must
  check their output for signs of failure.
  [stefan]

- Allow to pass argument list to ``main()``.
  [stefan]

1.0b3 - 2009-03-23
------------------

- No longer depend on grep.
  [stefan]

- Use subprocess.Popen instead of os.system and os.popen.
  [stefan]

- Protect against infinite alias recursion.
  [stefan]

- Drop -z option and always create zip files from now on.
  [stefan]

1.0b2 - 2009-03-19
------------------

- Checkin everything that's been modified, not just "relevant" files.
  [stefan]

- Expand aliases recursively.
  [stefan]

1.0b1 - 2009-03-18
------------------

- The distbase and distdefault config file options no longer have
  default values.
  [stefan]

- Read index servers from ~/.pypirc and allow them to be used with -d.
  [stefan]

- The -d option may be specified more than once.
  [stefan]

- Dropped -p option. Use -d pypi instead.
  [stefan]

- Dropped -c option. If your have non-standard SVN repositories you must
  tag by hand.
  [stefan]

0.19 - 2009-02-23
-----------------

- Absolute-ize the temp directory path.
  [stefan]

0.18 - 2009-01-26
-----------------

- Include README.txt and CHANGES.txt in long_description.
  [stefan]

- Rid unused imports and locals.
  [stefan]

0.17 - 2009-01-23
-----------------

- Add -c option to enable codespeak support. The codespeak.net repository
  uses ``branch`` and ``tag`` instead of ``branches`` and ``tags``.
  [gotcha, stefan]

0.16 - 2009-01-13
-----------------

- Fold regex construction into find and make find a method.
  [stefan]

- Update README.txt.
  [stefan]

0.15 - 2009-01-13
-----------------

- Support for reading default options from a config file.
  [fschulze, stefan]

0.14 - 2009-01-08
-----------------

- Add -s and -i options for signing PyPI uploads with GnuPG.
  [stefan]

- Stop execution after any failing step.
  [stefan]

0.13 - 2009-01-05
-----------------

- Stop execution when the checkin step fails.
  [stefan]

0.12 - 2009-01-02
-----------------

- setup.cfg may not exist.
  [stefan]

0.11 - 2008-12-02
-----------------

- Add setup.cfg to list of files we check in.
  [stefan]

0.10 - 2008-10-21
-----------------

- Don't capitalize GetOptError messages.
  [stefan]

0.9 - 2008-10-16
----------------

- Add -v option to print the script version.
  [stefan]

0.8 - 2008-10-16
----------------

- Lift restriction where only svn trunk could be released.
  [stefan]

0.7 - 2008-10-09
----------------

- Fix PyPI upload which must happen on the same command line as sdist.
  [stefan]

0.6 - 2008-10-08
----------------

- Update README.txt.
  [stefan]

0.5 - 2008-10-08
----------------

- Also locate and checkin HISTORY.txt to support ZopeSkel'ed eggs.
  [stefan]

0.4 - 2008-10-08
----------------

- Use svn checkout instead of svn export because it makes a difference
  to setuptools.
  [stefan]

- Add -p option for uploading to PyPI instead of dist-location.
  [stefan]

0.3 - 2008-10-06
----------------

- Also locate and checkin version.txt.
  [stefan]

0.2 - 2008-10-01
----------------

- Add -z option to create zip archives instead of the default tar.gz.
  [stefan]

0.1 - 2008-10-01
----------------

- Initial release
  [stefan]

