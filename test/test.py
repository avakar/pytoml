import os, json, sys, io, traceback
import pytoml as toml

def _testbench_literal(type, text, value):
    if type == 'table':
        return value
    if type == 'array':
        return { 'type': 'array', 'value': value }
    if type == 'str':
        return { 'type': 'string', 'value': value }
    _type_table = {'int': 'integer'}
    return {'type': _type_table.get(type, type), 'value': text}

def _main():
    succeeded = []
    failed = []

    for top, dirnames, fnames in os.walk('.'):
        for fname in fnames:
            if not fname.endswith('.toml'):
                continue

            if sys.argv[1:] and not any(arg in fname for arg in sys.argv[1:]):
                continue

            parse_error = None
            try:
                with open(os.path.join(top, fname), 'rb') as fin:
                    parsed = toml.load(fin)
            except toml.TomlError:
                parsed = None
                parse_error = sys.exc_info()
            else:
                dumped = toml.dumps(parsed)
                parsed2 = toml.loads(dumped)
                if parsed != parsed2:
                    failed.append((fname, None))
                    continue

                with open(os.path.join(top, fname), 'rb') as fin:
                    parsed = toml.load(fin, translate=_testbench_literal)

            try:
                with io.open(os.path.join(top, fname[:-5] + '.json'), 'rt', encoding='utf-8') as fin:
                    bench = json.load(fin)
            except IOError:
                bench = None

            if parsed != bench:
                failed.append((fname, parsed, bench, parse_error))
            else:
                succeeded.append(fname)

    for f, parsed, bench, e in failed:
        print('failed: {}\n{}\n{}'.format(f, json.dumps(parsed, indent=4), json.dumps(bench, indent=4)))
        if e:
            traceback.print_exception(*e)
    print('succeeded: {}'.format(len(succeeded)))
    return 1 if failed else 0

if __name__ == '__main__':
    sys.exit(_main())
