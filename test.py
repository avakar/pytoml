import toml, os, json, sys

def _testbench_literal(type, text):
    _type_table = {'str': 'string', 'int': 'integer'}
    return {'type': _type_table.get(type, type), 'value': text}

def _testbench_array(values):
    return {'type': 'array', 'value': values}

def _main():
    succeeded = []
    failed = []

    for top, dirnames, fnames in os.walk('test'):
        for fname in fnames:
            if not fname.endswith('.toml'):
                continue

            try:
                with open(os.path.join(top, fname), 'rb') as fin:
                    parsed = toml.load(fin, _testbench_literal, _testbench_array)
            except toml.TomlError:
                parsed = None

            try:
                with open(os.path.join(top, fname[:-5] + '.json'), 'rb') as fin:
                    bench = json.load(fin)
            except IOError:
                bench = None

            if parsed != bench:
                failed.append(fname)
            else:
                succeeded.append(fname)

    for f in failed:
        print 'failed: {f}'.format(f=f)
    print 'succeeded: {succ}'.format(succ=len(succeeded))
    return 1 if failed else 0

if __name__ == '__main__':
    sys.exit(_main())

