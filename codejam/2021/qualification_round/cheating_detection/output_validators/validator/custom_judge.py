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


"""Custom judge for Cheating Detection, Code Jam 2021."""

__author__ = 'tbuzzelli@google.com (Timothy Buzzelli)'

import collections

_BAD_OUTPUT_ERROR_STR = 'Our output is incorrect:'
_BAD_OUTPUT_ERROR = (_BAD_OUTPUT_ERROR_STR + ' {}').format

_BAD_INPUT_ERROR = 'Input is not well-formatted'

_BAD_FORMAT_ERROR = 'Output is not well-formatted'
_NOT_INTEGER_IN_RANGE_ERROR = 'Output is not an integer between 1 and 100'


def JudgeOneCase(output_lines, attempt_lines):
  if len(output_lines) != 1 or len(output_lines[0]) != 1:
    return None, _BAD_OUTPUT_ERROR(_BAD_FORMAT_ERROR)
  if (not str.isdigit(output_lines[0][0])) or int(
      output_lines[0][0]) < 1 or int(output_lines[0][0]) > 100:
    return None, _BAD_OUTPUT_ERROR(_NOT_INTEGER_IN_RANGE_ERROR)

  if len(attempt_lines) != 1 or len(attempt_lines[0]) != 1:
    return None, _BAD_FORMAT_ERROR
  if (not str.isdigit(attempt_lines[0][0])) or int(
      attempt_lines[0][0]) < 1 or int(attempt_lines[0][0]) > 100:
    return None, _NOT_INTEGER_IN_RANGE_ERROR

  return int(output_lines[0][0]) == int(attempt_lines[0][0]), None


def FindError(unused_self, input_file, output_file, attempt_file):
  """See judge.Judge.FindError()."""
  input_tokens = _utils_Tokenize(input_file)
  num_cases = int(input_tokens[0][0])
  percent_needed = int(input_tokens[1][0])
  num_needed = (num_cases * percent_needed + 99) // 100
  output_cases, attempt_cases, error = _utils_TokenizeAndSplitCases(
      output_file, attempt_file, num_cases, True)
  if error is not None:
    return error

  num_correct = 0
  for case_num, (output_lines, attempt_lines) in enumerate(
      zip(output_cases, attempt_cases), start=1):
    is_case_correct, error = JudgeOneCase(output_lines, attempt_lines)
    if error is not None:
      return 'Case #{}: {}'.format(case_num, error)
    if is_case_correct:
      num_correct = num_correct + 1

  print("Expected >={}, got {} correct".format(num_needed, num_correct))
  if num_correct < num_needed:
    return 'Too few correct! Expected >={} but got {} correct.'.format(
        num_needed, num_correct)

  # Everything passes.
  return None


def AssertEqual(a, b):
  if a != b:
    print('Not true that the following are equal:')
    print(a)
    print(b)
  assert a == b


def RunUnitTests():
  AssertEqual('Case #1: Our output is incorrect: Output is not well-formatted',
              FindError(None, '1\n100\n', 'Case #1: 1\n2\n', 'Case #1: 12\n'))
  AssertEqual('Case #1: Our output is incorrect: Output is not well-formatted',
              FindError(None, '1\n100\n', 'Case #1: 1 2\n', 'Case #1: 12\n'))
  AssertEqual('Case #1: Our output is incorrect: Output is not well-formatted',
              FindError(None, '1\n100\n', 'Case #1: 1 2\n', 'Case #1: 12\n'))
  AssertEqual(
      'Case #1: Our output is incorrect: Output is not an integer between 1 and 100',
      FindError(None, '1\n100\n', 'Case #1: abc\n', 'Case #1: 12\n'))
  AssertEqual(
      'Case #1: Our output is incorrect: Output is not an integer between 1 and 100',
      FindError(None, '1\n100\n', 'Case #1: 0\n', 'Case #1: 12\n'))
  AssertEqual(
      'Case #1: Our output is incorrect: Output is not an integer between 1 and 100',
      FindError(None, '1\n100\n', 'Case #1: 101\n', 'Case #1: 12\n'))

  AssertEqual('Case #1: Output is not well-formatted',
              FindError(None, '1\n100\n', 'Case #1: 12\n', 'Case #1: 1\n2\n'))
  AssertEqual('Case #1: Output is not well-formatted',
              FindError(None, '1\n100\n', 'Case #1: 12\n', 'Case #1: 1 2\n'))
  AssertEqual('Case #1: Output is not well-formatted',
              FindError(None, '1\n100\n', 'Case #1: 12\n', 'Case #1: 1 2\n'))
  AssertEqual('Case #1: Output is not an integer between 1 and 100',
              FindError(None, '1\n100\n', 'Case #1: 12\n', 'Case #1: abc\n'))
  AssertEqual('Case #1: Output is not an integer between 1 and 100',
              FindError(None, '1\n100\n', 'Case #1: 12\n', 'Case #1: 0\n'))
  AssertEqual('Case #1: Output is not an integer between 1 and 100',
              FindError(None, '1\n100\n', 'Case #1: 12\n', 'Case #1: 101\n'))

  AssertEqual(None, FindError(None, '1\n100\n', 'Case #1: 12\n',
                              'Case #1: 12\n'))
  AssertEqual(
      None,
      FindError(None, '2\n100\n', 'Case #1: 12\nCase #2: 13\n',
                'Case #1: 12\nCase #2: 13\n'))
  AssertEqual(
      'Too few correct! Expected >=2 but got 1 correct.',
      FindError(None, '2\n100\n', 'Case #1: 12\nCase #2: 13\n',
                'Case #1: 12\nCase #2: 12\n'))

  print('CheatingDetectionUnitTest passes.')
  sys.exit(0)


import sys
if __name__ == '__main__':
  if sys.argv[1] == '-2':
    RunUnitTests()

  result = FindError(None,
                     file(sys.argv[1]).read(),
                     file(sys.argv[3]).read(),
                     file(sys.argv[2]).read())
  if result:
    print >> sys.stderr, result
    sys.exit(1)
