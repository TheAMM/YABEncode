YABEncode - Yet Another Bencode module
======================================

An implementation of bencoding/bdecoding in Python 3, with somewhat descriptive
Exceptions for decode errors.
Also includes a command-line tool for decoding and pretty-printing bencoded data!

Installing
------------------

To install from `PyPI <https://pypi.python.org/pypi/yabencode>`_:

.. code-block:: bash

    pip install yabencode

----

Usage:
######

In Python...

.. code-block:: python

    import yabencode
    # bencode supports dicts, lists, ints and strings (bytestrings)
    yabencode.encode({'foo':'baz', 'list':['eggs', 'spam', 'bacon']})
    # Input can be string, bytes or a file object
    yabencode.decode(b'd3:foo3:baz4:listl4:eggs4:spam5:baconee')

    try:
        # Malformed data, 'spam' is missing an 'a'
        yabencode.decode(b'd3:foo3:baz4:listl4:eggs4:spm5:baconee')
    except yabencode.MalformedBencodeException as e:
        print(e)
        # Unexpected data type (b':') at position 31 (0x1F hex)

    try:
        # Bencode does not support floats
        yabencode.encode({'float':3.14})
    except yabencode.BencodeException as e:
        print(e)
        # Unsupported type <class 'float'>

or with the command-line tool:

.. code-block:: bash

    $ yabencode -h
    usage: yabencode [-h] [-t KEY] [-r] FILE

    Bdecode a file/standard input and pretty-print the resulting data

    positional arguments:
      FILE                  Input file. Use - for stdin

    optional arguments:
      -h, --help            show this help message and exit
      -t KEY, --truncate KEY
                            Truncate values under given key. May be repeated for
                            multiple values
      -r, --raw             Raw keys - do not decode dictionary keys

    $ # The 'pieces'-bytestring is rather long, so let's truncate it
    $ yabencode -t pieces ubuntu-17.04-desktop-amd64.iso.torrent
    {'announce': b'http://torrent.ubuntu.com:6969/announce',
     'announce-list': [[b'http://torrent.ubuntu.com:6969/announce'],
                       [b'http://ipv6.torrent.ubuntu.com:6969/announce']],
     'comment': b'Ubuntu CD releases.ubuntu.com',
     'creation date': 1492077159,
     'info': {'length': 1609039872,
              'name': b'ubuntu-17.04-desktop-amd64.iso',
              'piece length': 524288,
              'pieces': '<truncated>'}}

    $ # Reading bytes from stdin (using -r to not decode the keys)
    $ curl -s 'http://torrent.ubuntu.com:6969/scrape?info_hash=%59%06%67%69%b9%ad%42%da%2e%50%86%11%c3%3d%7c%44%80%b3%85%7b' | yabencode -r -
    {b'files': {b'Y\x06gi\xb9\xadB\xda.P\x86\x11\xc3=|D\x80\xb3\x85{': {b'complete': 3473,
                                                                        b'downloaded': 33029,
                                                                        b'incomplete': 102,
                                                                        b'name': b'ubuntu-17.04-desktop-amd64.iso'}}}
