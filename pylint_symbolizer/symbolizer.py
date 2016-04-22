# -*- coding: utf-8 -*-
import os
import re

from pylint import lint


class Symbolizer(object):

    def __init__(self, start_location=os.getcwd(), column_width=79):
        self.start_location = start_location
        self.column_width = column_width

        self._pylint_disable = '# pylint: disable='
        self._mapping = self._initalize_mapping()
        self._pattern = re.compile(
            r'\b(' + '|'.join(self._mapping.keys()) + r')\b'
        )
        self._leading_whitespace = ''

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

        mapping = {
            message.msgid: message.symbol
            for message in linter.msgs_store.messages
        }

        return mapping

    def __call__(self):
        self.perform_symbolization()

    def _get_files(self):
        """ Generates a list of files with extension in the dir structure.

        Yields:
            str: filepath
        """
        # pylint: disable=unused-variable
        for dirpath, __, filenames in os.walk(self.start_location):
            for file_ in filenames:
                if file_.endswith('.py'):
                    yield "{0}{1}".format(dirpath, file_)

    def perform_symbolization(self):  # pragma: no cover
        """
        Cycle through python files, reading the contents and processing each
        line and writing out to the same file
        """
        # pylint: disable=redefined-variable-type
        if os.path.isfile(self.start_location):
            files = [self.start_location]
        else:
            files = self._get_files()

        for filename in files:
            print("Processing file -- {0}".format(filename))
            updated_file_text = ''
            updated_file_text = ''
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

        Args:
            line (str): A line of text

        Returns:
            str
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

        Will be recursively called by helper functions until the line has
        been processed and broken up properly

        Args:
            line (str): A line of text

        Returns:
            str
        """
        if len(line) < self.column_width:
            if line.endswith('\n'):
                return line
            else:
                return '{0}\n'.format(line)
        elif 'class ' in line or 'def ' in line:
            definition, lint_ = line.split(self._pylint_disable)

            processed_lint = self._check_line_length('{0}{1}{2}'.format(
                self._leading_whitespace, self._pylint_disable, lint_
            ))
            return '{0}\n{1}'.format(definition.rstrip(), processed_lint)
        else:
            return self._process_line(line)

    def _process_line(self, line):
        """
        Loops through each disabled symbolic name of form:
            `# pylint: disable=too-many-lines,too-many-public-methods`

        If the the disabled symbol can be added to the first_line_list it
        will be.

        Else it will be added to the second_line_list to be processed further

        Args:
            line (str): A string with pylint disable symbols

        Returns:
            str
        """
        count = 0
        first_line_list = []
        second_line_list = []
        for item in line.split(','):
            if count + len(item) < self.column_width:
                first_line_list.append(item)
                count += len(item) + 1  # For commas
            else:
                second_line_list.append(item)

        if first_line_list and second_line_list:
            return self._build_new_line(first_line_list, second_line_list)
        elif not first_line_list and second_line_list:
            return self._fix_second_line_list(second_line_list)

    def _build_new_line(self, first_line_list, second_line_list):
        """
        Processes the lists of strings and builds one long string that is
        broken up by a new line character (current just `\n`)

        Args:
            first_line_list (list): List of strings
            second_line_list (list): List of strings

        Returns:
            str
        """
        new_line = ','.join(first_line_list).rstrip()

        second_line_list = self._insert_pylint_disable(second_line_list)
        second_line_list = self._insert_leading_whitespace(
            second_line_list)

        second_line = ','.join(second_line_list).replace(
            'disable=,', 'disable=')
        second_line = self._check_line_length(second_line)
        new_line = '{0}\n{1}'.format(
            new_line, second_line
        )

        return new_line

    def _fix_second_line_list(self, second_line_list):
        """
        Given a list of strings. Determine where the pylint disable should
        reside.

        If it is a class or function definition, the disable line
        should reside indented below the definition.

        Else if it is an inline disable that is not inline with class or
        function definition it should reside above that line of code

        Args:
            second_line_list (list): List of strings

        Returns:
            str
        """
        for index, string in enumerate(second_line_list):
            if self._pylint_disable in string:
                code, lint_ = string.split(self._pylint_disable)
                if 'class ' in code or 'def ' in code:
                    # If a class or function, split the lines and place the
                    # newly indented pylint disable on the next line
                    second_line_list[index] = '{0}\n'.format(code.rstrip())
                    second_line_list.insert((index + 1), ('{0}{1}{2}\n'.format(
                        self._leading_whitespace, self._pylint_disable,
                        lint_
                    )))
                else:
                    # Insert the newly created pylint disable on the line above
                    # the line with the inline disable
                    second_line_list[index] = ('{0}{1}{2}'.format(
                        self._get_whitespace(string),
                        self._pylint_disable,
                        lint_
                    ))
                    second_line_list.insert(
                        (index + 1), '{0}\n'.format(code.rstrip())
                    )

        return ''.join(second_line_list)

    def _insert_pylint_disable(self, line_list):
        """
        Checks if `# pylint: disable=` is in the first argument in the list.
        If it is not, inserts the above in the first index

        Args:
            line_list (list): List of strings

        Returns:
            list
        """
        if not line_list[0].startswith(self._pylint_disable):
            line_list.insert(0, self._pylint_disable)

        return line_list

    def _insert_leading_whitespace(self, line_list):
        """
        If we have calculated leading whitespace, insert the leading whitespace
        into the first position of the list

        Args:
            line_list (list): List of string

        Returns:
            list
        """
        if self._leading_whitespace:
            line_list[0] = '{0}{1}'.format(
                self._leading_whitespace, line_list[0]
            )

        return line_list

    def _set_leading_whitespace(self, line):
        """
        Get the leading whitespace and append either four spaces to the
        whitespace or a tab for the next logical line

        Add indentation only if `# pylint: disable=` isn't the first part of
        the line.

        Args:
            line (str): A string to deal with leading whitespace

        Returns:
            str
        """
        whitespace = ''
        indentation = ''

        if self._pylint_disable in line and line.index(self._pylint_disable):
            indentation = ' ' * 4
            whitespace = self._get_whitespace(line)
            if '\t' in whitespace:
                indentation = '\t'

        self._leading_whitespace = whitespace + indentation

    @staticmethod
    def _get_whitespace(line):
        """ Get the leading whitespace from a string """
        return line[:-len(line.lstrip())]

    def _reset_leading_whitespace(self):
        """ Reset leading whitespace to an empty string """
        self._leading_whitespace = ''
