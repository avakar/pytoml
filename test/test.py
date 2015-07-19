import os, json, sys, io, traceback, argparse
import pytoml as toml

def _testbench_literal(type, text, value):
    if type == 'table':
        return value
    if type == 'array':
        return { 'type': 'array', 'value': value }
    if type == 'datetime':
        offs = value.tzinfo.utcoffset(value).total_seconds() // 60
        offs = 'Z' if offs == 0 else '{}{}:{}'.format('-' if offs < 0 else '-', abs(offs) // 60, abs(offs) % 60)
        v = '{:04}-{:02}-{:02}T{:02}:{:02}:{:02}{}'.format(value.year, value.month, value.day, value.hour, value.minute, value.second, offs)
        return { 'type': 'datetime', 'value': v }
    if type == 'bool':
        return { 'type': 'bool', 'value': 'true' if value else 'false' }
    if type == 'float':
        return { 'type': 'float', 'value': value }
    if type == 'str':
        return { 'type': 'string', 'value': value }
    if type == 'int':
        return { 'type': 'integer', 'value': str(value) }

def adjust_bench(v):
    if isinstance(v, dict):
        if v.get('type') == 'float':
            v['value'] = float(v['value'])
            return v
        return { k: adjust_bench(v) for k, v in v.iteritems() }
    if isinstance(v, list):
        return [adjust_bench(v) for v in v]
    return v

def _main():
    ap = argparse.ArgumentParser()
    ap.add_argument('-d', '--dir', action='append')
    ap.add_argument('testcase', nargs='*')
    args = ap.parse_args()

    if not args.dir:
        args.dir = [os.path.join(os.path.split(__file__)[0], 'toml-test/tests')]

    succeeded = []
    failed = []

    for path in args.dir:
        if not os.path.isdir(path):
            print('error: not a dir: {}'.format(path))
            return 2
        for top, dirnames, fnames in os.walk(path):
            for fname in fnames:
                if not fname.endswith('.toml'):
                    continue

                if args.testcase and not any(arg in fname for arg in args.testcase):
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

                if parsed != adjust_bench(bench):
                    failed.append((fname, parsed, bench, parse_error))
                else:
                    succeeded.append(fname)

    for f, parsed, bench, e in failed:
        print('failed: {}\n{}\n{}'.format(f, json.dumps(parsed, indent=4), json.dumps(bench, indent=4)))
        if e:
            traceback.print_exception(*e)
    print('succeeded: {}'.format(len(succeeded)))
    return 1 if failed or not succeeded else 0

if __name__ == '__main__':
    sys.exit(_main())
