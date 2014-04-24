#!/usr/bin/env python
# -*- coding: utf-8 -*-

#  Copyright 2014 Mike Jarrett
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

# pylint: disable=relative-import
import argparse

from symbolizer import Symbolizer


def main():
    parser = argparse.ArgumentParser(
        description='Renames disabled Pylint IDs to Pylint symbolic names'
    )
    parser.add_argument('-w', '--width', nargs='?', default=79,
                        help='Set the window width limit')
    parser.add_argument('module_or_file', nargs=1)

    args = parser.parse_args()
    Symbolizer(start_location=args.module_or_file[0],
               column_width=args.width)()


if __name__ == "__main__":
    main()
