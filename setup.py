from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

from yabencode import version

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='yabencode',

    version=version,

    description='YABEncode - Yet Another Bencode module',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/TheAMM/YABEncode',

    # Author details
    author='AMM',
    author_email='the.actual.amm@gmail.com',
    license='MIT',

    classifiers=[
        'Development Status :: 4 - Beta',

        'Intended Audience :: Developers',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    python_requires='>=3.3, <4',
    keywords='bencode bdecode torrent bencoding',
    packages=['yabencode'],
    entry_points={
        'console_scripts': ['yabencode=yabencode.command_line:main']
    }

)
