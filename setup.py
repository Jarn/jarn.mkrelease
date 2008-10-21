from setuptools import setup, find_packages

version = '0.11'

setup(name='jarn.mkrelease',
      version=version,
      description='Release sdist eggs.',
      long_description="",
      classifiers=[
          'Programming Language :: Python',
      ],
      keywords='',
      author='Jarn AS',
      author_email='info@jarn.com',
      url='http://www.jarn.com/',
      license='Private',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['jarn'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
      ],
      entry_points = {
          'console_scripts': 'mkrelease=jarn.mkrelease.mkrelease:main',
      },
)
