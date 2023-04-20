# Copyright 2011 Google Inc. All Rights Reserved.

"""Basic utilities for custom judges."""

__author__ = 'darthur@google.com (David Arthur)'

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
  return [filter(None, row.split(' ')) for row in text.split('\n')
          if row.strip()]


def _utils_TokenizeAndSplitCases(output_file, attempt, num_cases,
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
    case_sensitive: Whether to run in case-sensitive mode (for everything
      except the word 'Case' itself).

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
      if (len(line) >= 2 and
          line[0].lower() == 'case' and
          line[1].startswith('#')):
        # This line is a "Case #N:" line.
        expected_case = 1 + len(split_text)
        if line[1] != ('#%d:' % expected_case):
          return None, ('Expected "case #%d:", found "%s %s".'
                        % (expected_case, line[0], line[1]))
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
  """Returns int(s) if s is an integer in the given range. Otherwise None.

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
  """Returns float(s) if s is a float. Otherwise None.

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
"""A custom judge for Proper Shuffle problem."""




class Error(Exception):
  pass


class Limits(object):

  def __init__(self):
    self.TEST_CASES = 120
    self.MIN_CORRECT_CASES = 109
    self.correct_cases = 0


class TestCase(object):

  def __init__(self):
    self.n = 0
    self.perm = []


def ParseInput(input_file, limits):
  """Returns a list of TestCase."""
  input_lines = input_file.splitlines()
  test_cases = int(input_lines[0])
  if test_cases != limits.TEST_CASES:
    raise Error('Wrong number of test cases in the input. Got %d' % test_cases)
  index = 1
  result = []
  while index < len(input_lines):
    tc = TestCase()
    tc.n = int(input_lines[index])
    index += 1
    tc.perm = input_lines[index].split(' ')
    if len(tc.perm) != tc.n:
      raise Error(
          'Number of elements in test case is wrong in the input. Got %s' % len(
              tc.perm))
    result.append(tc)
    index += 1
  if len(result) != limits.TEST_CASES:
    raise Error('Number of test cases parsed from input file is wrong. Got %d' %
                len(result))
  return result


def JudgeCase(output, attempt, limits):
  """Judge a single test case.
  Assumes strings passed in are all lowercase

  Args:
    output: list of lists of strings
    attempt: list of lists of strings
  Returns:
    error string or None
  """

  if not attempt:
    return 'Empty attempt'

  if len(attempt[0]) != 1:
    return 'Expected one word GOOD or BAD, got %s' % attempt

  if attempt[0][0] != 'good' and attempt[0][0] != 'bad':
    return 'Expected GOOD or BAD, got %s' % attempt[0][0]

  if attempt[0] == output[0]:
    limits.correct_cases += 1

  return None


def FindError(unused_self, input_file, output_file, attempt):
  """Returns None if no errors found, string otherwise containing the error.

  Args:
    see judge.Judge.FindError().

  Returns:
    None on success; a string on error.
  """
  limits = Limits()
  try:
    input_cases = ParseInput(input_file, limits)
  except Error as e:
    return 'Error in I/O generator: %s' % str(e)

  output_cases, attempt_cases, error = _utils_TokenizeAndSplitCases(
      output_file, attempt, len(input_cases))
  if error is not None: return error

  for tc in xrange(len(input_cases)):
    error = JudgeCase(output_cases[tc], attempt_cases[tc], limits)
    if error is not None:
      return 'Case #%d: %s' % (tc + 1, error)
  if limits.correct_cases < limits.MIN_CORRECT_CASES:
    return 'Got %d correct cases, needs at least %d cases to pass' % (
        limits.correct_cases, limits.MIN_CORRECT_CASES)
  return None

import sys
if __name__ == "__main__":
  if sys.argv[1] == '-2':
    sys.exit(0)
  result = FindError(None,
                     file(sys.argv[1]).read(),
                     file(sys.argv[3]).read(),
                     file(sys.argv[2]).read())
  if result:
    print >> sys.stderr, result
    sys.exit(1)
