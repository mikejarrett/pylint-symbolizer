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

import mock

from nose.tools import eq_ as assert_equals

from symbolizer.symbolizer import Symbolizer


@mock.patch('symbolizer.symbolizer.os.walk')
def test_get_files(os_walk):
    os_walk.return_value = [
        ['dirpath', ['dir', 'names'], ['files.py', 'names.x']]
    ]
    for file_path in Symbolizer()._get_files():
        assert_equals(file_path, 'dirpath/files.py')


def test_insert_pylint_disable():
    line_list = ['too-many-lines']
    expected = ['# pylint: disable=', 'too-many-lines']
    ret_val = Symbolizer()._insert_pylint_disable(line_list)
    assert_equals(ret_val, expected)


@mock.patch('symbolizer.symbolizer.Symbolizer._check_line_length')
def test_replace_id_with_symbol(check_length):
    expected = '# pylint: disable=too-many-lines'
    check_length.return_value = expected
    line = '# pylint: disable=C0302'
    ret_val = Symbolizer().replace_id_with_symbol(line)

    assert_equals(ret_val, expected)


def test_replace_id_with_symbol_no_matches():
    line = 'No disabled pylint here'
    ret_val = Symbolizer().replace_id_with_symbol(line)
    assert_equals(ret_val, line)


def test_check_line_length_short():
    short_line = 'This is less than 79 chars'
    ret_val = Symbolizer()._check_line_length(short_line)
    assert_equals(ret_val, short_line)


def test_check_line_length():
    line = (
        '# pylint: disable=too-many-instance-attributes,'
        'too-many-public-methods,W07030,deprecated-module,'
        'too-many-lines,old-style-class,fixme'
    )
    expected = (
        '# pylint: disable=too-many-instance-attributes,'
        'too-many-public-methods,W07030\n# pylint: disable='
        'deprecated-module,too-many-lines,old-style-class,fixme'
    )
    ret_val = Symbolizer()._check_line_length(line)
    assert_equals(ret_val, expected)


def test_check_line_length_inline():
    line = (
        "        def foo(self, bar):  # pylint disable="
        "too-many-instance-attributes,too-many-public-methods,W07030,"
        "deprecated-module,too-many-lines,old-style-class,fixme"
    )
    expected = (
        "        def foo(self, bar):\n"
        "            # pylint: disable=too-many-instance-attributes\n"
        "            # pylint: disable=too-many-public-methods,W07030,"
        "deprecated-module\n"
        "            # pylint: disable=too-many-lines,old-style-class,fixme"
    )
    ret_val = Symbolizer()._check_line_length(line)
    assert_equals(ret_val, expected)


@mock.patch('symbolizer.symbolizer.Symbolizer.perform_symbolizer_check')
def test_call(perform_symbolizer_check):
    Symbolizer()()
    assert_equals(perform_symbolizer_check.call_count, 1)
