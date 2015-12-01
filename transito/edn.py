from __future__ import print_function

import re
import ast
import collections

from transit.transit_types import Keyword, Symbol, TaggedValue
import transit.transit_types

transit_true = transit.transit_types.true
transit_false = transit.transit_types.false

from rply import ParserGenerator, LexerGenerator

lg = LexerGenerator()

SYMBOL_RE = r"[\.\*\+\!\-\_\?\$%&=a-zA-Z][\.\*\+\!\-\_\?\$%&=a-zA-Z0-9:#]*"
NS_SYMBOL = SYMBOL_RE + "/" + SYMBOL_RE

lg.add("boolean", r"(true|false)")
lg.add("nil", r"nil")
lg.add("float", r"\d+\.\d+")
lg.add("number", r"[-+]?\d+")
lg.add("olist", r"\(")
lg.add("clist", r"\)")
lg.add("omap", r"{")
lg.add("cmap", r"}")
lg.add("ovec", r"\[")
lg.add("cvec", r"\]")
lg.add("oset", r"#{")
lg.add("colon", r":")
lg.add("char_nl", r"\\newline")
lg.add("char_tab", r"\\tab")
lg.add("char_return", r"\\return")
lg.add("char_space", r"\\space")
lg.add("char", r"\\.")
lg.add("ns_symbol", NS_SYMBOL)
lg.add("symbol", SYMBOL_RE)
lg.add("string", r'"(\\\^.|\\.|[^\"])*"')
lg.add("tag", "#" + SYMBOL_RE)

lg.ignore(r"[\s,\n]+")
lg.ignore(r";.*\n")

lexer = lg.build()

pg = ParserGenerator(["boolean", "nil", "float", "number", "olist", "clist",
"omap", "cmap", "ovec", "cvec", "oset", "colon", "char_nl", "char_tab",
"char_return", "char_space", "char", "symbol", "ns_symbol", "string", "tag"])

class Char(TaggedValue):
    def __init__(self, rep):
        TaggedValue.__init__(self, 'char', rep)

class List(TaggedValue):
    def __init__(self, rep):
        TaggedValue.__init__(self, 'list', rep)

NL = Char('\n')
TAB = Char('\t')
RETURN = Char('\r')
SPACE = Char(' ')

class State(object):
    def __init__(self, tagged, accept_unknown_tags):
        self.tagged = tagged if tagged is not None else {}
        self.accept_unknown_tags = accept_unknown_tags

@pg.production("main : value")
def main(state, p):
    return p[0]

@pg.production("items : value")
def value_items_one(state, p):
    return [p[0]]

@pg.production("pairs : value value pairs")
def value_pairs(state, p):
    return [(p[0], p[1])] + p[2]

@pg.production("pairs : value value")
def value_pairs_one(state, p):
    return [(p[0], p[1])]

@pg.production("items : value items")
def value_items_more(state, p):
    return [p[0]] + p[1]

@pg.production("value : oset cmap")
def value_empty_set(state, p):
    return set()

@pg.production("value : omap cmap")
def value_empty_map(state, p):
    return {}

@pg.production("value : omap pairs cmap")
def value_map(state, p):
    return dict(p[1])

@pg.production("value : ovec cvec")
def value_empty_vec(state, p):
    return []

@pg.production("value : olist clist")
def value_empty_list(state, p):
    return List([])

@pg.production("value : oset items cmap")
def value_set(state, p):
    return set(p[1])

@pg.production("value : ovec items cvec")
def value_vec(state, p):
    return p[1]

@pg.production("value : olist items clist")
def value_list(state, p):
    return List(p[1])

@pg.production("value : number")
def value_integer(state, p):
    return int(p[0].value)

@pg.production("value : float")
def value_float(state, p):
    return float(p[0].value)

@pg.production("value : nil")
def value_nil(state, p):
    return None

@pg.production("value : boolean")
def value_boolean(state, p):
    return p[0].value == "true"

@pg.production("value : char_nl")
def value_char_nl(state, p):
    return NL

@pg.production("value : char_tab")
def value_char_tab(state, p):
    return TAB

@pg.production("value : char_return")
def value_char_return(state, p):
    return RETURN

@pg.production("value : char_space")
def value_char_space(state, p):
    return SPACE

@pg.production("value : char")
def value_char(state, p):
    return Char(p[0].value[1])

@pg.production("value : string")
def value_string(state, p):
    return ast.literal_eval(p[0].value)

@pg.production("value : ns_symbol")
def value_symbol_ns(state, p):
    return Symbol(p[0].value)

@pg.production("value : symbol")
def value_symbol(state, p):
    return Symbol(p[0].value)

@pg.production("value : colon symbol")
def value_keyword(state, p):
    return Keyword(p[1].value)

@pg.production("value : colon ns_symbol")
def value_keyword_ns(state, p):
    return Keyword(p[1].value)

@pg.production("value : tag value")
def value_tagged(state, p):
    tag_name = p[0].value[1:]
    if tag_name in state.tagged:
        constr = state.tagged[tag_name]
        return constr(p[1])
    elif state.accept_unknown_tags:
        return TaggedValue(tag_name, p[1])
    else:
        raise KeyError("No registered constructor for tag '{}'".format(tag_name))

parser = pg.build()

def loads(code, tagged=None, accept_unknown_tags=False):
    state = State(tagged, accept_unknown_tags)
    return parser.parse(lexer.lex(code), state)

CHARS = {
    '\t': 'tab',
    '\n': 'newline',
    '\r': 'return',
    ' ': 'space'
}

ESCAPE = re.compile(r'[\x00-\x1f\\"\b\f\n\r\t]')
ESCAPE_DCT = {
    '\\': '\\\\',
    '"': '\\"',
    '\b': '\\b',
    '\f': '\\f',
    '\n': '\\n',
    '\r': '\\r',
    '\t': '\\t',
}

for i in range(0x20):
    ESCAPE_DCT.setdefault(chr(i), '\\u{0:04x}'.format(i))

def encode_basestring(s):
    """Return a edn representation of a Python string"""
    def replace(match):
        return ESCAPE_DCT[match.group(0)]

    return '"' + ESCAPE.sub(replace, s) + '"'

def dumps(obj):
    if hasattr(obj, "to_edn"):
        return dumps(obj.to_edn())
    elif isinstance(obj, TaggedValue):
        if obj.tag == "list":
            return "(%s)" % " ".join([dumps(item) for item in obj.rep])
        elif obj.tag == "char":
            return "\\%s" % CHARS.get(obj.rep, obj.rep)
        else:
            return "#{} {}".format(obj.tag, dumps(obj.rep))
    elif isinstance(obj, (list, tuple)):
        return "[%s]" % " ".join([dumps(item) for item in obj])
    elif isinstance(obj, dict):
        keyvals = ", ".join([" ".join([dumps(k), dumps(v)]) \
                                for k, v in obj.items()])
        return "{%s}" % keyvals
    elif isinstance(obj, Keyword):
        return ":" + str(obj)
    elif isinstance(obj, Symbol):
        return str(obj)
    elif obj is True or obj is transit_true:
        return "true"
    elif obj is False or obj is transit_false:
        return "false"
    elif obj is None:
        return "nil"
    elif isinstance(obj, basestring):
        return encode_basestring(obj)
    elif isinstance(obj, set):
        return "#{%s}" % " ".join([dumps(item) for item in obj])
    elif isinstance(obj, (int, float)):
        return str(obj)
    elif isinstance(obj, collections.Iterable):
        return "(%s)" % " ".join([dumps(item) for item in obj])
    else:
        raise ValueError("Unknown value {} of type {}".format(obj, type(obj)))

@pg.error
def error_handler(token):
    raise ValueError("Ran into a %s where it wasn't expected" % token.gettokentype())

if __name__ == "__main__":
    #show_lex('{:foo 1 "bar" 1.2 :baz true false nil [1 #{}] (2 []) key #mg.value 42}')

    class YError(TaggedValue):
        def __init__(self, value):
            TaggedValue.__init__(self, "y.Error", value)

    print(loads("42"))
    print(loads("nil"))
    print(loads("true"))
    print(loads("false"))
    print(loads("1.2"))
    print(repr(loads(r"\tab")))
    print(str(loads(r"\tab")))
    print(repr(loads(r"\newline")))
    print(str(loads(r"\newline")))
    print(repr(loads(r"\return")))
    print(str(loads(r"\return")))
    print(repr(loads(r"\space")))
    print(str(loads(r"\space")))
    print(repr(loads(r"\s")))
    print(str(loads(r"\s")))
    print(loads('"a string"'))
    print(repr(loads("symbol")))
    print(str(loads("symbol")))
    print(repr(loads(":keyword")))
    print(str(loads(":keyword")))
    print(repr(loads("#{}")))
    print(str(loads("#{}")))
    print(repr(loads("#{1}")))
    print(str(loads("#{1}")))
    print(repr(loads("#{1 2}")))
    print(str(loads("#{1 2}")))
    print(repr(loads("{}")))
    print(str(loads("{}")))
    print(repr(loads("[]")))
    print(str(loads("[]")))
    print(repr(loads("[1]")))
    print(str(loads("[1]")))
    print(repr(loads("()")))
    print(str(loads("()")))
    print(repr(loads("([] () {} #{})")))
    print(str(loads("([] () {} #{})")))
    print(repr(loads("(1)")))
    print(str(loads("(1)")))
    print(repr(loads("(1 true nil)")))
    print(str(loads("(1 true nil)")))
    print(repr(loads("{:foo 42}")))
    print(str(loads("{:foo 42}")))
    print(repr(loads("{:foo 42 bar true \\a 12.3}")))
    print(str(loads("{:foo 42 bar true \\a 12.3}")))
    print(repr(loads("#y.Error {:foo 42}", {"y.Error": YError})))
    print(str(loads("#y.Error {:foo 42}", {"y.Error": YError})))

    print()

    print(dumps("asd"))
    print(dumps(loads(r'"a\"sd"')))
    print(dumps(loads("(1 true nil [1.2 {:foo 42 bar true \\a 12.3 \"asd\" \\newline}])")))
    print(dumps(TaggedValue("y.Error", loads('{:reason "asd" :status 500}'))))
    print(dumps(loads("#y.Error {:foo 42}", {"y.Error": YError})))
    print(dumps(loads("#y.Error {:foo 42}", accept_unknown_tags=True)))
