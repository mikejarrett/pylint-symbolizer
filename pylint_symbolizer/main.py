#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=relative-import
import argparse

from .symbolizer import Symbolizer


def main():  # pragma: no cover
    parser = argparse.ArgumentParser(
        description='Renames disabled Pylint IDs to Pylint symbolic names'
    )
    parser.add_argument(
        '-w',
        '--width',
        default=79,
        nargs='?',
        help='Set the window width limit'
    )
    parser.add_argument('module_or_file', nargs=1)

    args = parser.parse_args()
    Symbolizer(
        start_location=args.module_or_file[0],
        column_width=args.width
    )()


if __name__ == "__main__":
    main()
