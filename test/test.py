import os, json, sys, io, traceback, argparse
import pytoml as toml
from pytoml.utils import parse_rfc3339

def is_bench_equal(a, b):
    if isinstance(a, dict):
        if 'type' in a:
            if b.get('type') != a['type']:
                return False

            if a['type'] == 'float':
                return float(a['value']) == float(b['value'])
            if a['type'] == 'datetime':
                x = parse_rfc3339(a['value'])
                y = parse_rfc3339(b['value'])
                return x == y
            if a['type'] == 'array':
                return is_bench_equal(a['value'], b['value'])
            return a['value'] == b['value']

        return (isinstance(b, dict) and len(a) == len(b)
            and all(k in b and is_bench_equal(a[k], b[k]) for k in a))

    if isinstance(a, list):
        return (isinstance(b, list) and len(a) == len(b)
            and all(is_bench_equal(x, y) for x, y in zip(a, b)))

    raise RuntimeError('Invalid data in the bench JSON')

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
            print('error: not a dir: {0}'.format(path))
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
                    dumped = toml.dumps(parsed, sort_keys=False)
                    dumped_sorted = toml.dumps(parsed, sort_keys=True)
                    parsed2 = toml.loads(dumped)
                    parsed2_sorted = toml.loads(dumped_sorted)
                    if parsed != parsed2 or parsed != parsed2_sorted:
                        failed.append((fname, parsed, [parsed2, parsed2_sorted], None))
                        continue

                    with open(os.path.join(top, fname), 'rb') as fin:
                        parsed = toml.load(fin)
                    parsed = toml.translate_to_test(parsed)

                try:
                    with io.open(os.path.join(top, fname[:-5] + '.json'), 'rt', encoding='utf-8') as fin:
                        bench = json.load(fin)
                except IOError:
                    bench = None

                if (parsed is None) != (bench is None) or (parsed is not None and not is_bench_equal(parsed, bench)):
                    failed.append((fname, parsed, bench, parse_error))
                else:
                    succeeded.append(fname)

    for f, parsed, bench, e in failed:
        try:
            print('failed: {}\n{}\n{}'.format(f, json.dumps(parsed, indent=4), json.dumps(bench, indent=4)))
        except TypeError:
            print('failed: {}\n{}\n{}'.format(f, parsed, bench))

        if e:
            traceback.print_exception(*e)
    print('succeeded: {0}'.format(len(succeeded)))
    return 1 if failed or not succeeded else 0

if __name__ == '__main__':
    r = _main()
    if r:
        sys.exit(r)
