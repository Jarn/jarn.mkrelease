from setuptools import setup, find_packages

version = '3.3'

setup(name='jarn.mkrelease',
      version=version,
      description='Build and distribute Python eggs in one simple step',
      long_description=open('README.txt').read() + '\n' +
                       open('CHANGES.txt').read(),
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: POSIX',
          'Programming Language :: Python :: 2',
      ],
      keywords='create release python egg eggs',
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
          'setuptools-hg',
          'setuptools-git',
          'lazy',
      ],
      entry_points={
          'console_scripts': 'mkrelease=jarn.mkrelease.mkrelease:main',
      },
)
