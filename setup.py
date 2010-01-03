from setuptools import setup, find_packages

version = '2.0.3'

setup(name='jarn.mkrelease',
      version=version,
      description='Python egg releaser',
      long_description=open('README.txt').read() + '\n' +
                       open('CHANGES.txt').read(),
      classifiers=[
          'Programming Language :: Python',
      ],
      keywords='release sdist bdist eggs',
      author='Jarn AS',
      author_email='info@jarn.com',
      url='http://www.jarn.com/',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
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
