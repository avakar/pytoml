import string, re, sys, datetime
from .core import TomlError

if sys.version_info[0] == 2:
    _chr = unichr
else:
    _chr = chr

def _translate_datetime(s):
    match = _datetime_re.match(s)

    y = int(match.group(1))
    m = int(match.group(2))
    d = int(match.group(3))
    H = int(match.group(4))
    M = int(match.group(5))
    S = int(match.group(6))

    if match.group(7) is not None:
        micro = float(match.group(7))
    else:
        micro = 0

    if match.group(8) is not None:
        tzh = int(match.group(8))
        tzm = int(match.group(9))
        if tzh < 0:
            tzm = -tzm
        offs = tzh * 60 + tzm
    else:
        offs = 0

    dt = datetime.datetime(y, m, d, H, M, S, int(micro * 1000000),
        _TimeZone(datetime.timedelta(0, offs*60)))

    return dt

def load(fin, translate=lambda t, x, v: v):
    return loads(fin.read(), translate=translate, filename=fin.name)

def loads(s, filename='<string>', translate=lambda t, x, v: v):
    if isinstance(s, bytes):
        s = s.decode('utf-8')

    s = s.replace('\r\n', '\n')

    root = {}
    tables = {}
    scope = root

    from parser2 import parse
    ast = parse(s, filename=filename)

    def error(msg):
        raise TomlError(msg, pos[0], pos[1], filename)

    def process_value(v):
        kind, text, value, pos = v
        if kind == 'str' and value.startswith('\n'):
            value = value[1:]
        if kind == 'array':
            if value and any(k != value[0][0] for k, t, v, p in value[1:]):
                error('array-type-mismatch')
            value = [process_value(item) for item in value]
        elif kind == 'table':
            value = { k: process_value(value[k]) for k in value }
        return translate(kind, text, value)

    for kind, value, pos in ast:
        if kind == 'kv':
            k, v = value
            if k in scope:
                error('duplicate_keys. Key "{}" was used more than once.'.format(k))
            scope[k] = process_value(v)
        else:
            is_table_array = (kind == 'table_array')
            cur = tables
            for name in value[:-1]:
                if isinstance(cur.get(name), list):
                    d, cur = cur[name][-1]
                else:
                    d, cur = cur.setdefault(name, (None, {}))

            scope = {}
            name = value[-1]
            if name not in cur:
                if is_table_array:
                    cur[name] = [(scope, {})]
                else:
                    cur[name] = (scope, {})
            elif isinstance(cur[name], list):
                if not is_table_array:
                    error('table_type_mismatch')
                cur[name].append((scope, {}))
            else:
                if is_table_array:
                    error('table_type_mismatch')
                old_scope, next_table = cur[name]
                if old_scope is not None:
                    error('duplicate_tables')
                cur[name] = (scope, next_table)

    def merge_tables(scope, tables):
        if scope is None:
            scope = {}
        for k in tables:
            if k in scope:
                error('key_table_conflict')
            v = tables[k]
            if isinstance(v, list):
                scope[k] = [merge_tables(sc, tbl) for sc, tbl in v]
            else:
                scope[k] = merge_tables(v[0], v[1])
        return scope

    return merge_tables(root, tables)
