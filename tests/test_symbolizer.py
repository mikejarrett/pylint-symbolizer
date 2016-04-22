# -*- coding: utf-8 -*-
import mock

from unittest2 import TestCase

from pylint_symbolizer.symbolizer import Symbolizer


class TestSymbolizer(TestCase):

    @mock.patch('pylint_symbolizer.symbolizer.os.walk')
    def test_get_files(self, os_walk):
        os_walk.return_value = [
            [
                'dirpath/',
                ['dir', 'names'],
                ['files.py', 'names.x']
            ]
        ]
        for file_path in Symbolizer()._get_files():
            self.assertEqual(file_path, 'dirpath/files.py')

    def test_insert_pylint_disable(self):
        line_list = ['too-many-lines']
        expected = ['# pylint: disable=', 'too-many-lines']
        ret_val = Symbolizer()._insert_pylint_disable(line_list)
        self.assertEqual(ret_val, expected)

    @mock.patch('pylint_symbolizer.symbolizer.Symbolizer._check_line_length')
    def test_replace_id_with_symbol(self, check_length):
        expected = '# pylint: disable=too-many-lines'
        check_length.return_value = expected
        line = '# pylint: disable=C0302'
        ret_val = Symbolizer().replace_id_with_symbol(line)

        self.assertEqual(ret_val, expected)

    def test_replace_id_with_symbol_no_matches(self):
        line = 'No disabled pylint here'
        ret_val = Symbolizer().replace_id_with_symbol(line)
        self.assertEqual(ret_val, line)

    def test_check_line_length_short(self):
        short_line = 'This is less than 79 chars\n'
        ret_val = Symbolizer()._check_line_length(short_line)
        self.assertEqual(ret_val, short_line)

    def test_check_line_length(self):
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
        self.assertEqual(ret_val, expected)

    def test_check_line_length_inline(self):
        line = (
            '        def foo(self, bar):  # pylint: disable='
            'too-many-instance-attributes,too-many-public-methods,W07030,'
            'deprecated-module,too-many-lines,old-style-class,fixme'
        )
        expected = (
            '        def foo(self, bar):\n'
            '            # pylint: disable=too-many-instance-attributes,W07030,'
            'fixme\n'
            '            # pylint: disable=too-many-public-methods,'
            'deprecated-module\n'
            '            # pylint: disable=too-many-lines,old-style-class\n'
        )
        symb = Symbolizer()
        symb._set_leading_whitespace(line)
        ret_val = symb._check_line_length(line)
        self.assertEqual(ret_val, expected)


    @mock.patch('pylint_symbolizer.symbolizer.Symbolizer.perform_symbolization')
    def test_call(self, perform_symbolization):
        Symbolizer()()
        self.assertEqual(perform_symbolization.call_count, 1)


    def test_fix_second_line_list_not_class_nor_def(self):
        line = (
            '            self._template = Template(self.template)'
            '  # pylint: disable=attribute-defined-outside-init\n'
        )
        expected = (
            '            # pylint: disable=attribute-defined-outside-init'
            '\n            self._template = Template(self.template)\n'
        )

        symb = Symbolizer()
        ret_val = symb._fix_second_line_list([line])
        self.assertEqual(ret_val, expected)


    def test_fix_second_line_list_with_def(self):
        line = (
            '    def __init__(self, item, request):  '
            '# pylint: disable=super-init-not-called\n'
        )
        expected = (
            '    def __init__(self, item, request):\n'
            '        # pylint: disable=super-init-not-called\n'
        )

        symb = Symbolizer()
        symb._leading_whitespace = '        '
        ret_val = symb._check_line_length(line)
        self.assertEqual(ret_val, expected)


    def test_a_lot_of_disables_with_some_already_changed_to_symbol(self):
        line = '# pylint: disable=R0902,R0904,R0201,C0302,R0915,maybe-no-member'
        expected = (
            '# pylint: disable=too-many-instance-attributes,'
            'too-many-public-methods\n'
            '# pylint: disable=no-self-use,too-many-lines,too-many-statements\n'
            '# pylint: disable=maybe-no-member\n'
        )

        symb = Symbolizer()
        ret_val = symb.replace_id_with_symbol(line)
        self.assertEqual(ret_val, expected)


    def test_case_where_first_line_lst_may_not_be_generated(self):
        lines = [
            '# pylint: disable=R0904,C0302,R0201,C1001,C0103,R0924\n',
            '# -*- coding: utf8 -*-\n'
        ]
        expected = [
            '# pylint: disable=too-many-public-methods,too-many-lines'
            ',no-self-use,R0924\n# pylint: disable=old-style-class,'
            'invalid-name\n',
            '# -*- coding: utf8 -*-\n'
        ]

        ret_list = []
        symb = Symbolizer()
        for line in lines:
            ret_list.append(symb.replace_id_with_symbol(line))

        self.assertEqual(ret_list, expected)
