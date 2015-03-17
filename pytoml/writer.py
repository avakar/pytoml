from __future__ import unicode_literals
import io, datetime, sys

if sys.version_info[0] == 3:
    long = int
    unicode = str

def dumps(obj):
    fout = io.StringIO()
    dump(fout, obj)
    return fout.getvalue()

_escapes = { '\n': 'n', '\r': 'r', '\\': '\\', '\t': 't', '\b': 'b', '\f': 'f', '"': '"' }

def _escape_string(s):
    res = []
    start = 0
    def flush():
        if start != i:
            res.append(s[start:i])
        return i + 1

    i = 0
    while i < len(s):
        c = s[i]
        if c in '"\\\n\r\t\b\f':
            start = flush()
            res.append('\\' + _escapes[c])
        elif ord(c) < 0x20:
            start = flush()
            res.append('\\u%04x' % ord(c))
        i += 1

    flush()
    return '"' + ''.join(res) + '"'

def _escape_id(s):
    if any(not c.isalnum() and c not in '-_' for c in s):
        return _escape_string(s)
    return s

def _format_list(v):
    return '[{}]'.format(', '.join(_format_value(obj) for obj in v))

def _format_value(v):
    if isinstance(v, bool):
        return 'true' if v else 'false'
    if isinstance(v, int) or isinstance(v, long):
        return unicode(v)
    if isinstance(v, float):
        return '{:.17f}'.format(v)
    elif isinstance(v, unicode) or isinstance(v, bytes):
        return _escape_string(v)
    elif isinstance(v, datetime.datetime):
        offs = v.utcoffset()
        offs = offs.total_seconds() // 60 if offs is not None else 0

        if offs == 0:
            suffix = 'Z'
        else:
            if offs > 0:
                suffix = '+'
            else:
                suffix = '-'
                offs = -offs
            suffix = '{}{:.02}{:.02}'.format(suffix, offs // 60, offs % 60)

        if v.microsecond:
            return v.strftime('%Y-%m-%dT%H:%M:%S.%f') + suffix
        else:
            return v.strftime('%Y-%m-%dT%H:%M:%S') + suffix
    elif isinstance(v, list):
        return _format_list(v)
    else:
        raise RuntimeError('XXX')

def dump(fout, obj):
    tables = [((), obj, False)]

    while tables:
        name, table, is_array = tables.pop()
        if name:
            section_name = '.'.join(_escape_id(c) for c in name)
            if is_array:
                fout.write('[[{}]]\n'.format(section_name))
            else:
                fout.write('[{}]\n'.format(section_name))

        for k in table:
            v = table[k]
            if isinstance(v, dict):
                tables.append((name + (k,), v, False))
            elif isinstance(v, list) and v and all(isinstance(o, dict) for o in v):
                tables.extend((name + (k,), d, True) for d in reversed(v))
            else:
                fout.write('{} = {}\n'.format(_escape_id(k), _format_value(v)))

        if tables:
            fout.write('\n')
