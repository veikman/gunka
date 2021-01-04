"""Native Python package build instructions."""

from setuptools import setup
from setuptools import find_packages

import gunka

setup(name=gunka.__name__,
      version=gunka.__version__,
      author='Viktor Eikman',
      author_email='viktor.eikman@gmail.com',
      url='viktor.eikman.se',
      description='Tree-structured work encapsulation',
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 3',
          'Topic :: Software Development :: Libraries :: Python Modules',
      ],
      packages=find_packages(),
      )
