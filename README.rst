YABEncode - Yet Another Bencode module
======================================

An implementation of bencoding/bdecoding in Python 3, with somewhat descriptive
Exceptions for decode errors.

Installing
------------------

To install from `PyPI <https://pypi.python.org/pypi/yabencode>`_:

.. code-block:: bash

	pip install yabencode

----

Usage:

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

