# -*- coding: utf-8 -*-
'''Command Line Tool to Work with Transit Format'''
from __future__ import print_function

import sys
import json
import argparse

from StringIO import StringIO
from . import edn
from transit.writer import Writer
from transit.reader import Reader
import transit.transit_types

def get_arg_parser():
    '''build the cli arg parser'''
    parser = argparse.ArgumentParser(description='Transit CLI')

    subparsers = parser.add_subparsers()
    p_t2j = subparsers.add_parser('t2j', help='convert transit to json')
    p_j2t = subparsers.add_parser('j2t', help='convert json to transit')
    p_e2t = subparsers.add_parser('e2t', help='convert edn to transit')
    p_t2e = subparsers.add_parser('t2e', help='convert transit to edn')

    p_t2j.set_defaults(action='t2j')
    p_t2j.add_argument('path',
            help='path to transit file, use - to read from stdin')

    p_j2t.set_defaults(action='j2t')
    p_j2t.add_argument('path',
            help='path to json file, use - to read from stdin')

    p_e2t.set_defaults(action='e2t')
    p_e2t.add_argument('path',
            help='path to edn file, use - to read from stdin')

    p_t2e.set_defaults(action='t2e')
    p_t2e.add_argument('path',
            help='path to transit file, use - to read from stdin')

    return parser

def parse_args():
    '''parse arguments and return them'''
    parser = get_arg_parser()
    args = parser.parse_args()
    return args

class EdnListHandler(object):
    @staticmethod
    def from_rep(l):
        return transit.transit_types.TaggedValue("list", l)

class JsonListHandler(object):
    @staticmethod
    def from_rep(l):
        return list(l)

class JsonFromRep(object):
    @staticmethod
    def from_rep(rep):
        return rep

EDN_HANDLERS = {
    "list": EdnListHandler
}

JSON_HANDLERS = {
    "list": JsonListHandler,
    "char": JsonFromRep
}

def json_encode_transit(obj):
    if isinstance(obj, transit.transit_types.Keyword):
        return ":" + obj.str
    elif isinstance(obj, transit.transit_types.Symbol):
        return "~" + obj.str
    elif obj is transit.transit_types.true:
        return True
    elif obj is transit.transit_types.false:
        return False

    raise TypeError(repr(obj) + " is not JSON serializable")

def read_transit(path, handlers=None):
    if path == '-':
        handle = sys.stdin
    else:
        handle = open(path)

    reader = Reader("json")

    if handlers:
        for tag, handler in handlers.items():
            reader.register(tag, handler)

    return reader.read(handle)

def read_edn(path):
    if path == '-':
        handle = sys.stdin
    else:
        handle = open(path)

    return edn.loads(handle.read())

def write_transit(value):
    sio = StringIO()
    writer = Writer(sio, "json")
    writer.write(value)
    return sio.getvalue()

def write_json(value):
    return json.dumps(value, default=json_encode_transit)

def write_edn(value):
    return edn.dumps(value)

def read_json(path):
    if path == '-':
        handle = sys.stdin
    else:
        handle = open(path)

    return json.load(handle)

def transit_to_json(args):
    '''handler for transit to json action'''
    value = read_transit(args.path, JSON_HANDLERS)
    print(write_json(value))

def transit_to_edn(args):
    '''handler for transit to edn action'''
    value = read_transit(args.path, EDN_HANDLERS)
    print(write_edn(value))

def json_to_transit(args):
    '''handler for json to transit action'''
    value = read_json(args.path)
    print(write_transit(value))

def edn_to_transit(args):
    '''handler for edn to transit action'''
    value = read_edn(args.path)
    print(write_transit(value))

HANDLERS = {
    't2j': transit_to_json,
    'j2t': json_to_transit,
    'e2t': edn_to_transit,
    't2e': transit_to_edn
}

def main():
    '''cli entry point'''
    args = parse_args()
    handler = HANDLERS[args.action]
    handler(args)
