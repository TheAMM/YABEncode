from io import BytesIO

version_info = (0, 2, 1)
version = '.'.join(str(c) for c in version_info)

__all__ = ['encode', 'decode', 'BencodeException', 'MalformedBencodeException']


def _pairwise(iterable):
    """ Returns items from an iterable two at a time, ala
        [0, 1, 2, 3, ...] -> [(0, 1), (2, 3), ...] """
    iterable = iter(iterable)
    return zip(iterable, iterable)


class BencodeException(Exception):
    pass


class MalformedBencodeException(BencodeException):
    pass


class ReadPositionFileWrapper(object):
    def __init__(self, file_object):
        self.file_object = file_object
        self.position = 0

        try:
            # For example, stdin can't be .tell()'d
            self.position += file_object.tell()
        except OSError:
            pass

    def read(self, size=-1):
        data = self.file_object.read(size)
        self.position += len(data)
        return data

    def __getattr__(self, attr):
        return getattr(self.file_object, attr)


# bencode types
_DIGITS = b'0123456789'
_B_INT  = b'i'
_B_LIST = b'l'
_B_DICT = b'd'
_B_END  = b'e'


# Decoding of bencoded data
def _bencode_decode(file_object, key_encoding='utf-8'):
    """ Decodes a bencoded value, raising a MalformedBencodeException on errors.
        key_encoding specifies an encoding to decode dict keys with, generally UTF-8. Set it to None
        to keep the dictionary keys as bytestrings """
    if isinstance(file_object, str):
        file_object = file_object.encode('utf8')
    if isinstance(file_object, bytes):
        file_object = BytesIO(file_object)

    file_object = ReadPositionFileWrapper(file_object)

    def create_ex(msg):
        msg += ' at position {0} (0x{0:02X})'.format(file_object.position)
        return MalformedBencodeException(msg)

    def _read_list():
        """ Decodes values from stream until a None is returned ('e') """
        items = []
        while True:
            value = _bencode_decode(file_object, key_encoding=key_encoding)
            if value is None:
                break
            items.append(value)
        return items

    if key_encoding:
        def _decode_key(key_bytes):
            try:
                return key_bytes.decode(key_encoding)
            except Exception as e:
                raise BencodeException('Unable to decode key: ' + repr(key_bytes)) from e
    else:
        _decode_key = lambda k : k

    kind = file_object.read(1)
    if not kind:
        raise create_ex('EOF, expecting kind')

    if kind == _B_INT:  # Integer
        int_bytes = b''
        while True:
            c = file_object.read(1)
            if not c:
                raise create_ex('EOF, expecting more integer')
            elif c == _B_END:
                try:
                    return int(int_bytes.decode('utf8'))
                except Exception as e:
                    raise create_ex('Unable to parse int')

            # not a digit OR '-' in the middle of the int
            if (c not in _DIGITS + b'-') or (c == b'-' and int_bytes):
                raise create_ex('Unexpected input while reading an integer: ' + repr(c))
            else:
                int_bytes += c

    elif kind == _B_LIST:  # List
        return _read_list()

    elif kind == _B_DICT:  # Dictionary
        keys_and_values = _read_list()
        if len(keys_and_values) % 2 != 0:
            raise MalformedBencodeException('Uneven amount of key/value pairs')

        # "Technically" the bencode dictionary keys are bytestrings,
        # but real-world they're always(?) UTF-8.
        decoded_dict = dict((_decode_key(k), v)
                            for k, v in _pairwise(keys_and_values))
        return decoded_dict

    # List/dict end, but make sure input is not just 'e'
    elif kind == _B_END and file_object.position > 0:
        return None

    elif kind in _DIGITS:  # Bytestring
        str_len_bytes = kind  # keep first digit
        # Read string length until a ':'
        while True:
            c = file_object.read(1)
            if not c:
                raise create_ex('EOF, expecting more string len')
            if c in _DIGITS:
                str_len_bytes += c
            elif c == b':':
                break
            else:
                raise create_ex('Unexpected input while reading string length: ' + repr(c))
        try:
            str_len = int(str_len_bytes.decode())
        except Exception as e:
            raise create_ex('Unable to parse bytestring length')

        bytestring = file_object.read(str_len)
        if len(bytestring) != str_len:
            raise create_ex('Read only {} bytes, {} wanted'.format(len(bytestring), str_len))

        return bytestring
    else:
        raise create_ex('Unexpected data type ({})'.format(repr(kind)))


# Bencoding
def _bencode_int(value, encoding='utf-8'):
    """ Encode an integer, eg 64 -> i64e """
    return _B_INT + str(value).encode(encoding) + _B_END


def _bencode_bytes(value, encoding='utf-8'):
    """ Encode a bytestring (strings as UTF-8), eg 'hello' -> 5:hello """
    if isinstance(value, str):
        value = value.encode(encoding)
    return str(len(value)).encode(encoding) + b':' + value


def _bencode_list(value, encoding='utf-8'):
    """ Encode a list, eg [64, "hello"] -> li64e5:helloe """
    return _B_LIST + b''.join(_bencode(item, encoding=encoding) for item in value) + _B_END


def _bencode_dict(value, encoding='utf-8'):
    """ Encode a dict, which is keys and values interleaved as a list,
        eg {"hello":123}-> d5:helloi123ee """
    dict_keys = sorted(value.keys())  # Sort keys as per spec

    def key_value_bencoder(key):
        if not isinstance(key, (str, bytes)):
            raise BencodeException('Dictionary key must be str/bytes, not ' + str(type(key)))
        return _bencode_bytes(key) + _bencode(value[key], encoding=encoding)

    return _B_DICT + b''.join(key_value_bencoder(key) for key in dict_keys) + _B_END


def _bencode(value, encoding='utf-8'):
    """ Bencode any supported value (int, bytes, str, list, dict) """
    if isinstance(value, int):
        return _bencode_int(value, encoding=encoding)
    elif isinstance(value, (str, bytes)):
        return _bencode_bytes(value, encoding=encoding)
    elif isinstance(value, list):
        return _bencode_list(value, encoding=encoding)
    elif isinstance(value, dict):
        return _bencode_dict(value, encoding=encoding)

    raise BencodeException('Unsupported type ' + str(type(value)))


# Because of recursion, I like to keep the internal function names specific.
encode = _bencode
decode = _bencode_decode