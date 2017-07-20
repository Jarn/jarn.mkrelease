import sys

from setuptools import setup
from setuptools import find_packages

version = '4.1'

install_requires = [
    'setuptools',
    'setuptools-subversion >= 3.1',
    'setuptools-hg >= 0.4',
    'setuptools-git >= 1.2',
    'lazy >= 1.3',
    'wheel >= 0.29.0',
]

if sys.platform == "darwin":
    install_requires += [
        'keyring >= 10.4.0',
    ]

setup(name='jarn.mkrelease',
      version=version,
      description='Python package releaser',
      long_description=open('README.rst').read() + '\n' +
                       open('CHANGES.rst').read(),
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Operating System :: MacOS',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: POSIX',
          'Operating System :: POSIX :: Linux',
          'Operating System :: POSIX :: BSD',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
      ],
      keywords='create release upload python egg eggs wheel wheels pypi',
      author='Stefan H. Holek',
      author_email='stefan@epy.co.at',
      url='https://github.com/Jarn/jarn.mkrelease',
      license='BSD-2-Clause',
      packages=find_packages(),
      namespace_packages=['jarn'],
      include_package_data=True,
      zip_safe=False,
      test_suite='jarn.mkrelease.tests',
      install_requires=install_requires,
      entry_points={
          'console_scripts': 'mkrelease=jarn.mkrelease.mkrelease:main',
      },
)
