from setuptools import setup, find_packages

version = '4.0'

setup(name='jarn.mkrelease',
      version=version,
      description='Python egg releaser',
      long_description=open('README.txt').read() + '\n' +
                       open('CHANGES.txt').read(),
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: POSIX',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
      ],
      keywords='create release python egg eggs',
      author='Stefan H. Holek',
      author_email='stefan@epy.co.at',
      url='http://pypi.python.org/pypi/jarn.mkrelease',
      license='BSD',
      packages=find_packages(),
      namespace_packages=['jarn'],
      include_package_data=True,
      zip_safe=False,
      test_suite='jarn.mkrelease.tests',
      install_requires=[
          'setuptools',
          'setuptools-subversion >= 2.1',
          'setuptools-hg',
          'setuptools-git',
          'lazy >= 1.1',
      ],
      entry_points={
          'console_scripts': 'mkrelease=jarn.mkrelease.mkrelease:main',
      },
      use_2to3=True,
      use_2to3_exclude_fixers=[
        'lib2to3.fixes.fix_filter',
        'lib2to3.fixes.fix_xrange',
      ],
)
