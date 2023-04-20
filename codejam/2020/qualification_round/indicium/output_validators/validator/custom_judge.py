# Copyright 2011 Google Inc. All Rights Reserved.
"""Basic utilities for custom judges."""

import logging


# Copied from judge.py
def _utils_Tokenize(text, case_sensitive=True):
  """Converts a block of text into a two-dimensional array of strings.

  Args:
    text: A block of text, probably either a contestant or generator output.
    case_sensitive: Whether all text should be converted to lower-case.

  Returns:
    A two-dimensional array of strings. There is one element for each non-blank
    row in the output, and there is one inner element for each token on that
    row. If text contains any characters outside ASCII range 32-126 (with the
    exception of tabs, carriage returns, and line feeds), None is returned.
  """
  if not case_sensitive:
    text = text.lower()
  text = text.replace('\t', ' ').replace('\r', '\n')
  for char in text:
    if not (32 <= ord(char) <= 126) and char != '\n':
      return None
  return [
      filter(None, row.split(' ')) for row in text.split('\n') if row.strip()
  ]


def _utils_TokenizeAndSplitCases(output_file,
                                 attempt,
                                 num_cases,
                                 case_sensitive=False):
  """Tokenizes the generator output file and attempt file by case number.

  This is similar to Tokenize except that:
    - It applies to both output_file and attempt.
    - The results are 3-dimensional vectors split by case number, and with the
      "Case #N:" tokens removed.
    - There could be empty rows due to the previous.
    - The number of cases in the output file and attempt must match num_cases.
    - An error string is returned if something is incorrect.

  Args:
    output_file: The output file, as given in FindError.
    attempt: The attempt file, as given in FindError.
    num_cases: The number of cases in the input file.
    case_sensitive: Whether to run in case-sensitive mode (for everything except
      the word 'Case' itself).

  Returns:
    On success, tokenized_output, tokenized_attempt, None is returned. Each of
    these are 3-dimensional arrays of tokens, sorted by case number, line
    number, and token. On failure, None, None, error is returned.
  """

  def ProcessOneFile(text, num_cases):
    """Similar to TokenizeAndSplitCases except applied to only one file."""

    # Tokenize and validate ASCII-ness. Case insensitive checking allows, for
    # example, contestants to output "case #N:" instead of "Case #N:".

    tokenized_text = _utils_Tokenize(text, case_sensitive=case_sensitive)
    if tokenized_text is None:
      return None, 'Invalid or non-ASCII characters.'

    # Build our result in split text.
    split_text = []
    # Even if case-sensitivity is on, allow the contestant to use any form of
    # 'case', since some contestants may have gotten accustomed to the
    # older, more flexible rules.
    for line in tokenized_text:
      line = list(line)
      if (len(line) >= 2 and line[0].lower() == 'case' and
          line[1].startswith('#')):
        # This line is a "Case #N:" line.
        expected_case = 1 + len(split_text)
        if line[1] != ('#%d:' % expected_case):
          return None, ('Expected "case #%d:", found "%s %s".' %
                        (expected_case, line[0], line[1]))
        if expected_case > num_cases:
          return None, 'Too many cases.'
        split_text.append([line[2:]])
      else:
        # This line is any other kind of line.
        if not split_text:
          return None, 'File does not begin with "case #1:".'
        split_text[-1].append(line)

    # At the end, make sure we had enough cases.
    if len(split_text) < num_cases:
      return None, 'Too few cases.'
    return split_text, None

  # Parse the generator output file. If something is wrong here, log an error.
  split_output, error = ProcessOneFile(output_file, num_cases)
  if error:
    error = 'Invalid generator output file: %s' % error
    logging.error(error)
    return None, None, error

  # Parse the user output file attempt.
  split_attempt, error = ProcessOneFile(attempt, num_cases)
  if error:
    error = 'Invalid attempt file: %s' % error
    return None, None, error
  return split_output, split_attempt, None


def _utils_ToInteger(s, minimum_value=None, maximum_value=None):
  """Returns int(s) if s is an integer in the given range.

  Otherwise None.

  The range is inclusive. Also, leading zeroes and negative zeros are not
  allowed.

  Args:
    s: A string to convert to an integer.
    minimum_value: If not-None, then s must be at least this value.
    maximum_value: If not-None, then s must be at most this value.

  Returns:
    An integer in the given range or None.
  """
  try:
    value = int(s)
    if len(s) > 1 and s.startswith('0'):
      return None
    if s.startswith('-0'):
      return None
    if minimum_value is not None and value < minimum_value:
      return None
    if maximum_value is not None and value > maximum_value:
      return None
    return value
  except ValueError:
    return None


def _utils_ToFloat(s):
  """Returns float(s) if s is a float.

  Otherwise None.

  Disallows infinities and nans.

  Args:
    s: A string to convert to a float.

  Returns:
    An float or None.
  """
  try:
    x = float(s)
    if x not in [float('inf'), float('-inf')] and x == x:  # not NaN
      return x
    else:
      return None
  except ValueError:
    return None


"""Custom judge for Latin Trace, Code Jam 2020."""

import collections

_BAD_OUTPUT_ERROR_STR = 'Our output is incorrect:'
_BAD_OUTPUT_ERROR = (_BAD_OUTPUT_ERROR_STR + ' {}').format

_BAD_FORMAT_ERROR = 'Output is not well-formatted'
_ROW_HAS_WRONG_NUMBER_OF_ELEMENTS = 'Row {} has {} elements'.format
_ROW_NOT_PERMUTATION = 'Row {} is not a permutation of [1, N]'.format
_COLUMN_NOT_PERMUTATION = 'Column {} is not a permutation of [1, N]'.format
_MAIN_DIAGONAL_SUM_NOT_CORRECT = 'Main diagonal has invalid sum {}'.format
_WRONG_NO_SOLUTION = 'Contestant did not find solution'

_POSSIBLE = 'possible'
_IMPOSSIBLE = 'impossible'
"""Parsed information for a single test case.

Attributes:
  n: Desired size of the matrix
  k: desired sum of main diagonal
"""
_CaseInput = collections.namedtuple('_CaseInput', ['n', 'k'])


def ParseInputFile(input_file):
  """Turns an input file into a list of _CaseInputs."""
  input_lines = _utils_Tokenize(input_file)[1:]  # skip the number of test cases
  cases = []
  while input_lines:
    n, k = map(int, input_lines.pop(0))
    cases.append(_CaseInput(n, k))
  return cases


def VerifyOutput(lines, case):
  """Checks the output for a single test case.

  Args:
    lines: Tokenized lines (either from our IOgen's output or a contestant's
      attempt.)
    case: A _CaseInput representing a single test case.

  Returns:
    A tuple of two values:
        1. None if the output is correct, or an error message.
        2. A boolean value, indicating whether there is a solution.
  """
  if not lines:
    return _BAD_FORMAT_ERROR, None

  # Check 1st line:
  if not lines[0] or len(lines[0]) != 1:
    return _BAD_FORMAT_ERROR, None
  if not lines[0][0] in [_POSSIBLE, _IMPOSSIBLE]:
    return _BAD_FORMAT_ERROR, None

  # Impossible case.
  if lines[0][0] == _IMPOSSIBLE:
    if len(lines) != 1:
      return _BAD_FORMAT_ERROR, None
    return None, False

  # Possible case.
  lines = lines[1:]  # Remove "POSSIBLE" line
  if len(lines) != case.n:
    return _BAD_FORMAT_ERROR, None
  # Convert to int
  try:
    a = [map(int, line) for line in lines]
  except ValueError:
    return _BAD_FORMAT_ERROR, None

  # Check length of all rows.
  for i, row in enumerate(a):
    if len(row) != case.n:
      return _ROW_HAS_WRONG_NUMBER_OF_ELEMENTS(i, len(row)), None

  # Rows must be unique and contain all numbers in [1, N]
  one_to_n = set(range(1, case.n + 1))
  for i, row in enumerate(a):
    if set(row) != one_to_n:
      return _ROW_NOT_PERMUTATION(i), None

  # Columns must be unique.
  for i in range(case.n):
    values = set([row[i] for row in a])
    if values != one_to_n:
      return _COLUMN_NOT_PERMUTATION(i), None

  # Check sum of main diagonal.
  diagonal_sum = sum([a[i][i] for i in range(case.n)])
  if diagonal_sum != case.k:
    return _MAIN_DIAGONAL_SUM_NOT_CORRECT(diagonal_sum), None

  return None, True


def VerifyCase(output_lines, attempt_lines, case):
  """Checks a single test case.

  Args:
    output_lines: Tokenized lines from our IOgen's output.
    attempt_lines: Tokenized lines from the contestant's attempt.
    case: A CaseInput representing a single test case.

  Returns:
    An error, or None if there is no error.
  """
  output_error, iogen_has_answer = VerifyOutput(output_lines, case)
  if output_error is not None:
    return _BAD_OUTPUT_ERROR(output_error)

  attempt_error, attempt_has_answer = VerifyOutput(attempt_lines, case)
  if (not iogen_has_answer) and attempt_has_answer:
    return _BAD_OUTPUT_ERROR('Contestant found answer but we do not')

  if attempt_error:
    return attempt_error

  if iogen_has_answer and (not attempt_has_answer):
    return _WRONG_NO_SOLUTION

  return None


def FindError(unused_self, input_file, output_file, attempt_file):
  """See judge.Judge.FindError()."""
  input_cases = ParseInputFile(input_file)
  num_cases = len(input_cases)
  output_cases, attempt_cases, error = _utils_TokenizeAndSplitCases(
      output_file, attempt_file, num_cases)
  if error is not None:
    return error

  for case_num, (case, output_lines, attempt_lines) in enumerate(
      zip(input_cases, output_cases, attempt_cases), start=1):
    error = VerifyCase(output_lines, attempt_lines, case)
    if error is not None:
      je = 'JUDGE_ERROR ' if error.startswith(_BAD_OUTPUT_ERROR_STR) else ''
      return '{}Case #{}: {}'.format(je, case_num, error)

  # Everything passes.
  return None


def AssertEqual(a, b):
  if a != b:
    print('Not true that the following are equal:')
    print(a)
    print(b)
  assert a == b


def UnitTests():
  input_lines = ['2', '3 6', '2 3']
  output_lines = [
      'Case #1: POSSIBLE', '2 1 3', '3 2 1', '1 3 2', 'Case #2: IMPOSSIBLE'
  ]
  input_file = '\n'.join(input_lines)
  output_file = '\n'.join(output_lines)

  def modifyOutput(output_lines, change_at, new_value):
    """Modify a single line in output."""
    lines = list(output_lines)
    lines[change_at] = new_value
    return '\n'.join(lines)

  def addToOutput(output_lines, insert_at, new_value):
    """Add a new line to output."""
    lines = list(output_lines)
    lines.insert(insert_at, new_value)
    return '\n'.join(lines)

  def removeFromOutput(output_lines, delete_at):
    """Delete one line from output."""
    lines = list(output_lines)
    lines.pop(delete_at)
    return '\n'.join(lines)

  # Test group 1: Judge Error, Invalid token.
  AssertEqual('Invalid generator output file: Too few cases.',
              FindError(None, input_file, '', output_file))

  # Test group 2: Judge Error, output has wrong format.
  AssertEqual(
      'JUDGE_ERROR Case #1: Our output is incorrect: Output is not well-formatted',
      FindError(None, input_file, removeFromOutput(output_lines, 2),
                output_file))

  # Test group 3: Judge Error, output is wrong.
  AssertEqual(
      'JUDGE_ERROR Case #1: Our output is incorrect: Row 1 has 4 elements',
      FindError(None, input_file, modifyOutput(output_lines, 2, '3 2 1 4'),
                output_file))
  AssertEqual(
      'JUDGE_ERROR Case #1: Our output is incorrect: Row 1 is not a permutation of [1, N]',
      FindError(None, input_file, modifyOutput(output_lines, 2, '3 2 3'),
                output_file))

  # Test group 4: Attempt error, Invalid token.
  AssertEqual('Invalid attempt file: Invalid or non-ASCII characters.',
              FindError(None, input_file, output_file, chr(6)))
  AssertEqual('Invalid attempt file: Too few cases.',
              FindError(None, input_file, output_file, ''))
  AssertEqual(
      'Invalid attempt file: Expected "case #1:", found "case ##1:".',
      FindError(None, input_file, output_file,
                modifyOutput(output_lines, 0, 'Case ##1: POSSIBLE')))

  # Test group 5: Attempt Error, output has wrong format.
  AssertEqual(
      'Case #2: Output is not well-formatted',
      FindError(None, input_file, output_file,
                addToOutput(output_lines, len(output_lines), '1 2 3')))
  AssertEqual(
      'Case #2: Output is not well-formatted',
      FindError(None, input_file, output_file,
                modifyOutput(output_lines, -1, 'Case #2: imposible')))
  AssertEqual(
      'Case #1: Output is not well-formatted',
      FindError(None, input_file, output_file,
                addToOutput(output_lines, 2, '1 2 3')))
  AssertEqual(
      'Case #1: Output is not well-formatted',
      FindError(None, input_file, output_file,
                removeFromOutput(output_lines, 2)))
  AssertEqual(
      'Case #1: Output is not well-formatted',
      FindError(None, input_file, output_file,
                modifyOutput(output_lines, 2, '3 2 1.0')))
  AssertEqual(
      'Case #1: Output is not well-formatted',
      FindError(None, input_file, output_file,
                modifyOutput(output_lines, 2, '3 2 a')))

  # Test group 6: Attempt Error, output is wrong.
  AssertEqual(
      'Case #1: Row 1 has 4 elements',
      FindError(None, input_file, output_file,
                modifyOutput(output_lines, 2, '3 2 1 4')))
  AssertEqual(
      'Case #1: Row 2 has 2 elements',
      FindError(None, input_file, output_file,
                modifyOutput(output_lines, 3, '1 3')))
  AssertEqual(
      'Case #1: Row 1 is not a permutation of [1, N]',
      FindError(None, input_file, output_file,
                modifyOutput(output_lines, 2, '3 2 3')))
  AssertEqual(
      'Case #1: Column 0 is not a permutation of [1, N]',
      FindError(None, input_file, output_file,
                modifyOutput(output_lines, 3, '2 3 1')))
  AssertEqual(
      'Case #1: Row 2 is not a permutation of [1, N]',
      FindError(None, input_file, output_file,
                modifyOutput(output_lines, 3, '1 3 4')))

  wrong_output_lines = [
      'Case #1: possible', '132', '213', '321', 'Case #2: impossible'
  ]
  AssertEqual(
      'Case #1: Row 0 has 1 elements',
      FindError(None, input_file, output_file, '\n'.join(wrong_output_lines)))

  wrong_output_lines = [
      'Case #1: possible', '1 3 2', '2 1 3', '3 2 1', 'Case #2: impossible'
  ]
  AssertEqual(
      'Case #1: Main diagonal has invalid sum 3',
      FindError(None, input_file, output_file, '\n'.join(wrong_output_lines)))

  wrong_output_lines = ['Case #1: impossible', 'Case #2: impossible']
  AssertEqual(
      'Case #1: Contestant did not find solution',
      FindError(None, input_file, output_file, '\n'.join(wrong_output_lines)))

  # Test group 7: Some cases where contestant find correct diagonal sum, but fail because of something else.
  input_lines = ['1', '3 6']
  correct_output_lines = ['Case #1: POSSIBLE', '1 3 2', '3 2 1', '2 1 3']
  wrong_output_lines = ['Case #1: POSSIBLE', '4 0 2', '0 2 4', '2 4 0']
  AssertEqual(
      'Case #1: Row 0 is not a permutation of [1, N]',
      FindError(None, '\n'.join(input_lines), '\n'.join(correct_output_lines),
                '\n'.join(wrong_output_lines)))

  wrong_output_lines = ['Case #1: POSSIBLE', '2 2 2', '2 2 2', '2 2 2']
  AssertEqual(
      'Case #1: Row 0 is not a permutation of [1, N]',
      FindError(None, '\n'.join(input_lines), '\n'.join(correct_output_lines),
                '\n'.join(wrong_output_lines)))

  wrong_output_lines = ['Case #1: POSSIBLE', '1 2 3', '1 2 3', '1 2 3']
  AssertEqual(
      'Case #1: Column 0 is not a permutation of [1, N]',
      FindError(None, '\n'.join(input_lines), '\n'.join(correct_output_lines),
                '\n'.join(wrong_output_lines)))

  wrong_output_lines = ['Case #1: POSSIBLE', '3 2 1', '1 0 2', '2 1 3']
  AssertEqual(
      'Case #1: Row 1 is not a permutation of [1, N]',
      FindError(None, '\n'.join(input_lines), '\n'.join(correct_output_lines),
                '\n'.join(wrong_output_lines)))

  wrong_output_lines = [
      'Case #1: POSSIBLE', '1 3 2 4', '3 2 4 1', '2 4 1 3', '4 1 3 2'
  ]
  AssertEqual(
      'Case #1: Output is not well-formatted',
      FindError(None, '\n'.join(input_lines), '\n'.join(correct_output_lines),
                '\n'.join(wrong_output_lines)))

  # Test group 8: Correct output
  AssertEqual(None, FindError(None, input_file, output_file, output_file))

  correct_output_lines = [
      'Case #1: POSSIBLE', '1 2 3', '2 3 1', '3 1 2', 'Case #2: IMPOSSIBLE'
  ]
  AssertEqual(
      None,
      FindError(None, input_file, output_file, '\n'.join(correct_output_lines)))

  # Test group 9: N = 2, K = 4, check all 2x2 grid.
  input_lines = ['1', '2 4']
  correct_output_lines = ['Case #1: POSSIBLE', '2 1', '1 2']
  for a in range(1, 3):
    for b in range(1, 3):
      for c in range(1, 3):
        for d in range(1, 3):
          output_lines = [
              'Case #1: POSSIBLE', '{} {}'.format(a, b), '{} {}'.format(c, d)
          ]
          judge_result = FindError(None, '\n'.join(input_lines),
                                   '\n'.join(correct_output_lines),
                                   '\n'.join(output_lines))

          # Note: there is exactly 1 correct answer for this case.
          if output_lines == correct_output_lines:
            AssertEqual(None, judge_result)
          else:
            assert judge_result is not None

  print('Unit tests passed')
  sys.exit(0)


import sys
if __name__ == '__main__':
  if sys.argv[1] == '-2':
    UnitTests()

  result = FindError(
      None,
      file(sys.argv[1]).read(),  # input path
      file(sys.argv[3]).read(),  # iogen output path
      file(sys.argv[2]).read())  # attempt output path
  if result:
    print >> sys.stderr, result
    sys.exit(1)
