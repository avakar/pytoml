import os, json, sys, io
import pytoml as toml

def _testbench_literal(type, text):
    _type_table = {'str': 'string', 'int': 'integer'}
    return {'type': _type_table.get(type, type), 'value': text}

def _testbench_array(values):
    return {'type': 'array', 'value': values}

def _main():
    succeeded = []
    failed = []

    for top, dirnames, fnames in os.walk('.'):
        for fname in fnames:
            if not fname.endswith('.toml'):
                continue

            try:
                with open(os.path.join(top, fname), 'rb') as fin:
                    parsed = toml.load(fin)
            except toml.TomlError:
                parsed = None
            else:
                dumped = toml.dumps(parsed)
                parsed2 = toml.loads(dumped)
                if parsed != parsed2:
                    failed.append(fname)
                    continue

                with open(os.path.join(top, fname), 'rb') as fin:
                    parsed = toml.load(fin, _testbench_literal, _testbench_array)

            try:
                with io.open(os.path.join(top, fname[:-5] + '.json'), 'rt', encoding='utf-8') as fin:
                    bench = json.load(fin)
            except IOError:
                bench = None

            if parsed != bench:
                failed.append(fname)
            else:
                succeeded.append(fname)

    for f in failed:
        print('failed: {}'.format(f))
    print('succeeded: {}'.format(len(succeeded)))
    return 1 if failed else 0

if __name__ == '__main__':
    sys.exit(_main())

