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

    def __init__(
        self, start_location=os.getcwd(), column_width=79, handle_inline=False
    ):
        self.start_location = start_location
        self.column_width = column_width
        self.handle_inline = handle_inline

        self.pylint_disable = '# pylint: disable='
        self.mapping = self._initalize_mapping()
        self.pattern = re.compile(
            r'\b(' + '|'.join(self.mapping.keys()) + r')\b'
        )

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
        self.perform_symbolizer_check()

    def _get_files(self):
        """
        Generates a list of files with extension in the directory structure

        :yields: str (filepath)
        """
        for dirpath, __, filenames in os.walk(self.start_location):
            for file_ in filenames:
                if file_.endswith('.py'):
                    yield "{0}/{1}".format(dirpath, file_)

    def perform_symbolizer_check(self):  # pragma: no cover
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

                    if not updated_file_text:
                        updated_file_text = new_line
                    else:
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
        new_line = self.pattern.sub(lambda x: self.mapping[x.group()], line)
        if line != new_line:
            line = self._check_line_length(new_line)

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
            return line
        else:
            new_line = u''
            count = 0
            first_line = []
            second_line = []
            for item in line.split(','):
                if count + len(item) < self.column_width:
                    first_line.append(item)
                    count += len(item)
                else:
                    second_line.append(item)

            if first_line and second_line:
                new_line = ','.join(first_line).replace('=,', '=')

                second_line = self._insert_pylint_disable(second_line)
                new_line = '{0}\n{1}'.format(
                    new_line, self._check_line_length(','.join(second_line))
                )

                return new_line

    def _insert_pylint_disable(self, line_list):
        """
        Checks if `# pylint: disable=` is in the first argument in the list.
        If it is not, inserts the above in the first index

        :param line_list: List of strings
        :param type: list
        :rtype: list
        """
        if not line_list[0].startswith(self.pylint_disable):
            line_list.insert(0, self.pylint_disable)

            return line_list

    def _leading_whitespace(self, line):
        """
        Get the leading whitespace and append either four spaces to the
        whitespace or a tab for the next logical line

        :param line: A string to with leading whitespace
        :rtype: str
        """
        indentation = ' ' * 4

        whitespace = line[:-len(line.lstrip())]
        if '\t' in whitespace:
            indentation = '\t'

        return whitespace + indentation
