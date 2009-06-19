from setuptools import setup, find_packages

version = '2.6'

setup(name='testpackage',
      version=version,
      description='Test package.',
      long_description=open('README.txt').read(),
      classifiers=[
          'Programming Language :: Python',
      ],
      keywords='test package',
      author='Jarn AS',
      author_email='info@jarn.com',
      url='http://www.jarn.com/',
      license='private',
      packages = find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
      ],
)
