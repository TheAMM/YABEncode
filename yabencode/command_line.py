import sys
import argparse
import pprint

import yabencode

parser = argparse.ArgumentParser(description='Bdecode a file/standard input and pretty-print the resulting data')
parser.add_argument('file', metavar='FILE', help='Input file. Use - for stdin')
parser.add_argument('-t', '--truncate', metavar='KEY', action='append', default=[], help='Truncate values under given key. May be repeated for multiple values')
parser.add_argument('-r', '--raw', action='store_true', help='Raw keys - do not decode dictionary keys')
parser.add_argument('-T', '--truncate-pieces', action='store_true', help='Shortcut flag for --truncate pieces')
parser.add_argument('-V', '--version', action='version', version='%(prog)s {}'.format(yabencode.version), help='Show the version number and exit')


class NoStringWrappingPrettyPrinter(pprint.PrettyPrinter):
    '''PrettyPrinter which does not wrap strings or bytes'''
    def _format(self, object, *args):
        if isinstance(object, (str, bytes)):
            width = self._width
            self._width = sys.maxsize
            try:
                super()._format(object, *args)
            finally:
                self._width = width
        else:
            super()._format(object, *args)


def _truncate_keys(target_dict, keys):
    '''Replace given keys with <truncated>'''
    keys = set(keys)

    for key, value in target_dict.items():
        if key in keys:

            truncated = None
            if isinstance(value, bytes):
                truncated = '<truncated {} bytes>'.format(len(value))
            elif isinstance(value, str):
                truncated = '<truncated {}-char string>'.format(len(value))
            elif isinstance(value, list):
                truncated = '<truncated {}-item list>'.format(len(value))
            elif isinstance(value, dict):
                truncated = '<truncated {}-item dict>'.format(len(value))

            target_dict[key] = truncated or '<truncated>'

        elif isinstance(value, dict):
            _truncate_keys(value, keys)


def main():
    args = parser.parse_args()
    if args.truncate_pieces:
        args.truncate.append('pieces')

    if args.file == '-':
        # .buffer for raw bytes
        in_file = sys.stdin.buffer
    else:
        in_file = open(args.file, 'rb')

    try:
        key_encoding = None if args.raw else 'utf-8'
        decoded_data = yabencode.decode(in_file, key_encoding=key_encoding)

        if args.truncate:
            if args.raw:
                args.truncate = [k.encode() for k in args.truncate]
            _truncate_keys(decoded_data, args.truncate)

        # Print the result
        NoStringWrappingPrettyPrinter().pprint(decoded_data)

    finally:
        if in_file is not sys.stdin:
            in_file.close()