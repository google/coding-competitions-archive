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


"""Custom judge for Rock Paper Scissors, Kick Start."""

import collections
import math

_BAD_OUTPUT_ERROR_STR = 'Our output is incorrect:'
_BAD_OUTPUT_ERROR = (_BAD_OUTPUT_ERROR_STR + ' {}').format

_BAD_FORMAT_ERROR = 'Output is not well-formatted'
_WRONG_ANSWER = ('The list of choices result in an average expected value '
                 'smaller than X')

_DAYS = 60
_PRODUCT1TO60 = math.factorial(60)
"""Parsed information for a single test case."""
_CaseInput = collections.namedtuple('_CaseInput', ['W', 'E'])


def ParseInputFile(input_file):
  """Turns an input file into a list of _CaseInputs."""
  # skip the number of cases (line 0)
  X = _utils_Tokenize(input_file)[1]
  input_lines = _utils_Tokenize(input_file)[2:]
  cases = []
  for input_line in input_lines:
    W, E = map(int, input_line)
    cases.append(_CaseInput(W, E))
  return (X, cases)


def VerifyOutput(lines, case):
  """Checks the output for a single test case.

  Args:
    lines: Tokenized lines (either from our I/OGen's output or a contestant's
      attempt.)
    case: A _CaseInput representing a single test case.

  Returns:
    None if the output is correct, or an error message.
  """

  if len(lines) != 1 or len(lines[0]) != 1 or len(lines[0][0]) != _DAYS:
    return _BAD_FORMAT_ERROR

  strategy = lines[0][0]

  for i in range(_DAYS):
    if strategy[i] not in 'RSP':
      return _BAD_FORMAT_ERROR

  return None


def GetScore(lines, case):
  """Returns expected value for a given test case.

  Args same as above.
  Returns:
    expected value for this test case.
  """

  def win_against(move):
    if move == 'R':
      return 'P'
    if move == 'S':
      return 'R'
    if move == 'P':
      return 'S'
    return None

  def lose_against(move):
    if move == 'R':
      return 'S'
    if move == 'S':
      return 'P'
    if move == 'P':
      return 'R'
    return None

  def get_expected_value(strategy, W, E):
    counter = collections.defaultdict(int)
    counter[strategy[0]] += 1
    ret = _PRODUCT1TO60 * W / 3 + _PRODUCT1TO60 * E / 3
    for i in range(1, _DAYS):
      ret += _PRODUCT1TO60 * counter[win_against(strategy[i])] * W / i
      ret += _PRODUCT1TO60 * counter[lose_against(strategy[i])] * E / i
      counter[strategy[i]] += 1
    return ret

  strategy = lines[0][0]

  return get_expected_value(strategy, case.W, case.E)


def VerifyCase(output_lines, attempt_lines, case):
  """Checks a single test case.

  Args:
    output_lines: Tokenized lines from our I/OGen's output.
    attempt_lines: Tokenized lines from the contestant's attempt.
    case: A CaseInput representing a single test case.

  Returns:
    An error, or None if there is no error.
  """

  output_error = VerifyOutput(output_lines, case)
  if output_error is not None:
    return _BAD_OUTPUT_ERROR(output_error)

  attempt_error = VerifyOutput(attempt_lines, case)
  if attempt_error is not None:
    return attempt_error

  return None


def FindError(unused_self, input_file, output_file, attempt_file):
  """See judge.Judge.FindError()."""
  X, input_cases = ParseInputFile(input_file)
  X_value = int(X[0])
  num_cases = len(input_cases)
  output_cases, attempt_cases, error = _utils_TokenizeAndSplitCases(
      output_file, attempt_file, num_cases, True)
  if error is not None:
    return error

  total_score = 0
  for case_num, (case, output_lines, attempt_lines) in enumerate(
      zip(input_cases, output_cases, attempt_cases), start=1):
    error = VerifyCase(output_lines, attempt_lines, case)
    if error is not None:
      je = 'JUDGE_ERROR ' if error.startswith(_BAD_OUTPUT_ERROR_STR) else ''
      return '{}Case #{}: {}'.format(je, case_num, error)
    total_score += GetScore(attempt_lines, case)

  if total_score < X_value * _PRODUCT1TO60 * num_cases:
    return _WRONG_ANSWER + ' (got: %.2f, needed: %.2f)' % (
        total_score / _PRODUCT1TO60 / num_cases, X_value)

  # Everything passes.
  return None


class RockPaperScissorsUnitTest():

  def assertIsNone(self, a):
    assert a is None

  def assertEqual(self, a, b):
    assert a == b, (a, b)

  def assertStartsWith(self, a, b):
    assert a.startswith(b), (a, b)

  input_file = """
2
60
60 0
60 60
""".lstrip()
  output_file = """
Case #1: RSRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR
Case #2: PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
""".lstrip()

  def testCorrectAnswerDoesNotCauseError(self):
    self.assertIsNone(
        FindError(None, self.input_file, self.output_file, self.output_file))

  def testAlternativeCorrectAnswerDoesNotCauseError(self):
    self.assertIsNone(
        FindError(
            None, self.input_file, self.output_file, """
Case #1: RSRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR
Case #2: RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR
""".lstrip()))

  def testIncorrectAnswerCausesError(self):
    self.assertStartsWith(
        FindError(
            None, self.input_file, self.output_file, """
Case #1: RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR
Case #2: RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR
""".lstrip()), _WRONG_ANSWER)

  def testEmptyAttemptCausesError(self):
    self.assertEqual('Invalid attempt file: Too few cases.',
                     FindError(None, self.input_file, self.output_file, ''))

  def testBadHeaderCausesError(self):
    self.assertEqual(
        'Invalid attempt file: Expected "case #1:", found "Case ##1:".',
        FindError(None, self.input_file, self.output_file,
                  'Case ##1: IMPOSSIBLE'))

  def testBadFormatCausesError(self):
    self.assertEqual(
        'Case #1: ' + _BAD_FORMAT_ERROR,
        FindError(
            None, self.input_file, self.output_file, """
Case #1:
Case #2: RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR
""".lstrip()))

    self.assertEqual(
        'Case #1: ' + _BAD_FORMAT_ERROR,
        FindError(
            None, self.input_file, self.output_file, """
Case #1: RR
Case #2: RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR
""".lstrip()))

    self.assertEqual(
        'Case #1: ' + _BAD_FORMAT_ERROR,
        FindError(
            None, self.input_file, self.output_file, """
Case #1: RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRS
Case #2: RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR
""".lstrip()))

    self.assertEqual(
        'Case #1: ' + _BAD_FORMAT_ERROR,
        FindError(
            None, self.input_file, self.output_file, """
Case #1: AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
Case #2: RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR
""".lstrip()))


def RunUnitTests():
  test = RockPaperScissorsUnitTest()
  test_methods = [
      method_name for method_name in dir(test)
      if callable(getattr(test, method_name)) and method_name.startswith('test')
  ]
  for test_method in test_methods:
    print(test_method)
    getattr(test, test_method)()

  print('BrokenClockUnitTest passes.')
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
