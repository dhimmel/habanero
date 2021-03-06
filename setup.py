import codecs
from setuptools import setup
from setuptools import find_packages

with codecs.open('README.rst', 'r', 'utf-8') as f:
    readme = f.read()

with codecs.open('Changelog.rst', 'r', 'utf-8') as f:
    changes = f.read()

long_description = '\n\n' + readme + '\n\n' + changes

setup(
	name             = 'habanero',
	version          = '0.2.6.1',
	description      = 'Low Level Client for Crossref Search API',
	long_description = long_description,
  author           = 'Scott Chamberlain',
  author_email     = 'myrmecocystus@gmail.com',
  url              = 'https://github.com/sckott/habanero',
  license          = 'MIT',
  packages         = find_packages(exclude=['test-*']),
  install_requires = ['requests>=2.7.0'],
  classifiers      = (
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Science/Research',
    'Intended Audience :: Developers',
    'Topic :: Scientific/Engineering :: Bio-Informatics',
    'Natural Language :: English',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3'
	)
)
