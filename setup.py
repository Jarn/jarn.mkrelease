from setuptools import setup, find_packages

version = '4.3'

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
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: POSIX',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
      ],
      keywords='create release upload python egg eggs wheel wheels pypi releaser package packages publish',
      author='Stefan H. Holek',
      author_email='stefan@epy.co.at',
      url='https://github.com/Jarn/jarn.mkrelease',
      license='BSD-2-Clause',
      packages=find_packages(),
      namespace_packages=['jarn'],
      include_package_data=True,
      zip_safe=False,
      test_suite='jarn.mkrelease.tests',
      install_requires=[
          'setuptools',
          'setuptools-subversion >= 3.1',
          'setuptools-hg >= 0.4',
          'setuptools-git >= 1.2',
          'lazy >= 1.4',
          'wheel >= 0.32.3',
          'keyring >= 17.1.1; sys_platform == "darwin"',
      ],
      entry_points={
          'console_scripts': 'mkrelease=jarn.mkrelease.mkrelease:main',
      },
)
