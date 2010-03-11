from setuptools import setup, find_packages

version = '3.0.2'

setup(name='jarn.mkrelease',
      version=version,
      description='Python egg releaser',
      long_description=open('README.txt').read() + '\n' +
                       open('CHANGES.txt').read(),
      classifiers=[
          'Programming Language :: Python',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: POSIX',
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
      ],
      keywords='release sdist bdist eggs',
      author='Jarn AS',
      author_email='info@jarn.com',
      url='http://www.jarn.com/',
      license='BSD',
      packages=find_packages(),
      namespace_packages=['jarn'],
      include_package_data=True,
      zip_safe=False,
      test_suite='jarn.mkrelease.tests',
      install_requires=[
          'setuptools',
          'setuptools_hg',
          'setuptools_git',
      ],
      entry_points = {
          'console_scripts': 'mkrelease=jarn.mkrelease.mkrelease:main',
      },
)
