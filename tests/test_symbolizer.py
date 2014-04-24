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
    short_line = 'This is less than 79 chars\n'
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
        'deprecated-module,too-many-lines,old-style-class,fixme\n'
    )
    ret_val = Symbolizer()._check_line_length(line)
    assert_equals(ret_val, expected)


def test_check_line_length_inline():
    line = (
        u'        def foo(self, bar):  # pylint: disable='
        u'too-many-instance-attributes,too-many-public-methods,W07030,'
        u'deprecated-module,too-many-lines,old-style-class,fixme'
    )
    expected = (
        u'        def foo(self, bar):\n'
        u'            # pylint: disable=too-many-instance-attributes,W07030,'
        u'fixme\n'
        u'            # pylint: disable=too-many-public-methods,'
        u'deprecated-module\n'
        u'            # pylint: disable=too-many-lines,old-style-class\n'
    )
    symb = Symbolizer()
    symb._set_leading_whitespace(line)
    ret_val = symb._check_line_length(line)
    assert_equals(ret_val, expected)


@mock.patch('symbolizer.symbolizer.Symbolizer.perform_symbolization')
def test_call(perform_symbolization):
    Symbolizer()()
    assert_equals(perform_symbolization.call_count, 1)


def test_fix_second_line_list_not_class_nor_def():
    line = (
        u'            self._template = Template(self.template)'
        u'  # pylint: disable=attribute-defined-outside-init\n'
    )
    expected = (
        u'            # pylint: disable=attribute-defined-outside-init'
        u'\n            self._template = Template(self.template)\n'
    )

    symb = Symbolizer()
    ret_val = symb._fix_second_line_list([line])
    assert_equals(ret_val, expected)


def test_fix_second_line_list_with_def():
    line = (
        u'    def __init__(self, item, request):  '
        u'# pylint: disable=super-init-not-called\n'
    )
    expected = (
        u'    def __init__(self, item, request):\n'
        u'        # pylint: disable=super-init-not-called\n'
    )

    symb = Symbolizer()
    symb._leading_whitespace = '        '
    ret_val = symb._check_line_length(line)
    assert_equals(ret_val, expected)


def test_a_lot_of_disables_with_some_already_changed_to_symbol():
    line = '# pylint: disable=R0902,R0904,R0201,C0302,R0915,maybe-no-member'
    expected = (
        u'# pylint: disable=too-many-instance-attributes,'
        u'too-many-public-methods\n'
        u'# pylint: disable=no-self-use,too-many-lines,too-many-statements\n'
        u'# pylint: disable=maybe-no-member\n'
    )

    symb = Symbolizer()
    ret_val = symb.replace_id_with_symbol(line)
    assert_equals(ret_val, expected)


def test_case_where_first_line_lst_may_not_be_generated():
    lines = [
        u'# pylint: disable=R0904,C0302,R0201,C1001,C0103,R0924\n',
        u'# -*- coding: utf8 -*-\n'
    ]
    expected = [
        u'# pylint: disable=too-many-public-methods,too-many-lines'
        u',no-self-use,R0924\n# pylint: disable=old-style-class,'
        u'invalid-name\n',
        u'# -*- coding: utf8 -*-\n'
    ]

    ret_list = []
    symb = Symbolizer()
    for line in lines:
        ret_list.append(symb.replace_id_with_symbol(line))

    assert_equals(ret_list, expected)
