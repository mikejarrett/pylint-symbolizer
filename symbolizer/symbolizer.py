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

import os
import re

from pylint import lint


class Symbolizer(object):

    def __init__(self, start_location=os.getcwd(), column_width=79):
        self.start_location = start_location
        self.column_width = column_width

        self._pylint_disable = u'# pylint: disable='
        self._mapping = self._initalize_mapping()
        self._pattern = re.compile(
            ur'\b(' + '|'.join(self._mapping.keys()) + ur')\b'
        )
        self._leading_whitespace = u''

    @staticmethod
    def _initalize_mapping():
        """
        Initialize Pylint with defaults and any plugins.

        Returns a mapping to be used by regex for finding and replacing
        Pylint ids with Pylint symbols

        :rtpe: dict
        """
        linter = lint.PyLinter()
        linter.load_defaults()
        linter.load_default_plugins()

        mapping = {}
        for symbol, msg in linter._messages.iteritems():
            mapping[msg.msgid] = symbol

        return mapping

    def __call__(self):
        self.perform_symbolization()

    def _get_files(self):
        """
        Generates a list of files with extension in the directory structure

        :yields: str (filepath)
        """
        for dirpath, __, filenames in os.walk(self.start_location):
            for file_ in filenames:
                if file_.endswith(u'.py'):
                    yield "{0}/{1}".format(dirpath, file_)

    def perform_symbolization(self):  # pragma: no cover
        """
        Cycle through python files, reading the contents and processing each
        line and writing out to the same file
        """
        for filename in self._get_files():
            print u"Processing file -- {0}".format(filename)
            updated_file_text = u''
            with open(filename, 'r') as fin:
                for line in fin.readlines():
                    new_line = self.replace_id_with_symbol(line)

                    if not updated_file_text and new_line:
                        updated_file_text = new_line
                    elif new_line:
                        updated_file_text += new_line

            with open(filename, 'w') as fout:
                fout.write(updated_file_text)

    def replace_id_with_symbol(self, line):
        """
        Given a line, check to see if any of the Pylint message ids are
        in the line. If it is replace with the Pylint symbolic name.

        If the line has been changed verify the length is within the standard
        monitor width

        :param line: A line of text
        :param type: str

        :rtype: str
        """
        new_line = self._pattern.sub(lambda x: self._mapping[x.group()], line)
        if line != new_line:
            self._set_leading_whitespace(new_line)
            line = self._check_line_length(new_line)
            self._reset_leading_whitespace()

        return line

    def _check_line_length(self, line):
        """
        If the line is within the given character count, return it unchanged.
        Else split the line on `,` (the standard delimiter for multiple
        disabled arguments for Pylint) and build a string verifying that it
        is still within the given column width.

        Recursively calls itself until the line has been fully processed

        :param line: A line of tet
        :rtype: str
        """
        if len(line) < self.column_width:
            if line.endswith('\n'):
                return line
            else:
                return u'{0}\n'.format(line)
        elif u'class ' in line or u'def ' in line:
            definition, lint_ = line.split(self._pylint_disable)

            processed_lint = self._check_line_length(u'{0}{1}{2}'.format(
                self._leading_whitespace, self._pylint_disable, lint_
            ))
            return u'{0}\n{1}'.format(definition.rstrip(), processed_lint)
        else:
            return self._process_line(line)

    def _process_line(self, line):
        count = 0
        first_line_lst = []
        second_line_lst = []
        for item in line.split(u','):
            if count + len(item) < self.column_width:
                first_line_lst.append(item)
                count += len(item) + 1  # For commas
            else:
                second_line_lst.append(item)

        if first_line_lst and second_line_lst:
            return self._build_new_line(first_line_lst, second_line_lst)
        elif not first_line_lst and second_line_lst:
            return self._fix_second_line_list(second_line_lst)

    def _build_new_line(self, first_line_lst, second_line_lst):
        new_line = u','.join(first_line_lst).rstrip()

        second_line_lst = self._insert_pylint_disable(second_line_lst)
        second_line_lst = self._insert_leading_whitespace(
            second_line_lst)

        second_line = ','.join(second_line_lst).replace(
            u'disable=,', 'disable=')
        second_line = self._check_line_length(second_line)
        new_line = u'{0}\n{1}'.format(
            new_line, second_line
        )

        return new_line

    def _fix_second_line_list(self, second_line_lst):
        for index, string in enumerate(second_line_lst):
            if self._pylint_disable in string:
                code, lint_ = string.split(self._pylint_disable)
                if u'class ' in code or u'def ' in code:
                    second_line_lst[index] = u'{0}\n'.format(code.rstrip())
                    second_line_lst.insert((index + 1), (u'{0}{1}{2}\n'.format(
                        self._leading_whitespace, self._pylint_disable,
                        lint_
                    )))
                else:
                    second_line_lst[index] = (u'{0}{1}{2}'.format(
                        self._get_whitespace(string),
                        self._pylint_disable,
                        lint_
                    ))
                    second_line_lst.insert(
                        (index + 1), u'{0}\n'.format(code.rstrip())
                    )

        return u''.join(second_line_lst)

    def _insert_pylint_disable(self, line_list):
        """
        Checks if `# pylint: disable=` is in the first argument in the list.
        If it is not, inserts the above in the first index

        :param line_list: List of strings
        :param type: list
        :rtype: list
        """
        if not line_list[0].startswith(self._pylint_disable):
            line_list.insert(0, self._pylint_disable)

        return line_list

    def _insert_leading_whitespace(self, line_list):
        """
        If we have calculated leading whitespace, insert the leading whitespace
        into the first position of the list

        :param line_list: List of string
        :param type: list
        :rtpe: list
        """
        if self._leading_whitespace:
            line_list[0] = u'{0}{1}'.format(
                self._leading_whitespace, line_list[0]
            )

        return line_list

    def _set_leading_whitespace(self, line):
        """
        Get the leading whitespace and append either four spaces to the
        whitespace or a tab for the next logical line

        Add indentation only if `# pylint: disable=` isn't the first part of
        the line.

        :param line: A string to with leading whitespace
        :rtype: str
        """
        whitespace = u''
        indentation = u''

        if self._pylint_disable in line and line.index(self._pylint_disable):
            indentation = u' ' * 4
            whitespace = self._get_whitespace(line)
            if u'\t' in whitespace:
                indentation = u'\t'

        self._leading_whitespace = whitespace + indentation

    @staticmethod
    def _get_whitespace(line):
        return line[:-len(line.lstrip())]

    def _reset_leading_whitespace(self):
        self._leading_whitespace = 0
