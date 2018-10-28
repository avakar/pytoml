#!/usr/bin/env python

import argparse
import json
import pytoml
import sys

def _main():
    ap = argparse.ArgumentParser()
    ap.add_argument('-i', '--input', type=argparse.FileType('r', encoding='utf-8'))
    ap.add_argument('-o', '--output', type=argparse.FileType('w', encoding='utf-8'), default='-')
    args = ap.parse_args()

    if not args.input:
        args.input = sys.stdin.buffer

    v = pytoml.load(args.input)
    translated = pytoml.translate_to_test(v)
    json.dump(translated, args.output)

if __name__ == '__main__':
    _main()
