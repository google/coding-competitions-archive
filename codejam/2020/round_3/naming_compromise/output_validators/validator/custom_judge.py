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

"""Custom judge for Naming Compromise, Code Jam 2020."""

__author__ = 'johngs@google.com (Jonathan Irvin Gunawan)'

import collections


_BAD_OUTPUT_ERROR_STR = 'Our output is incorrect:'
_BAD_OUTPUT_ERROR = (_BAD_OUTPUT_ERROR_STR + ' {}').format

_BAD_FORMAT_ERROR = 'Output is not well-formatted'

_NON_LETTER_CHARACTER_ERROR = (
    'At least one character was not an English alphabet letter')
_STRING_TOO_LONG_ERROR = (
    'String length is more than |C| + |J|. Edit distance cannot be optimal')
_EDIT_DISTANCE_TOO_FAR_ERROR = (
    'The edit distance to C ({}) is too far from the edit distance to J ({})'
    ).format

_MORE_EDIT_DISTANCE_ERROR = (
    'Solution has different edit distance ({}) than our solution ({})').format
_LESS_EDIT_DISTANCE_ERROR = _BAD_OUTPUT_ERROR(
    'Solution has less edit distance ({}) than our solution ({})').format

"""Parsed information for a single test case.

Attributes:
  c: Cameron's name preference
  j: Jamie's name preference
"""
_CaseInput = collections.namedtuple('_CaseInput', ['c', 'j'])


def ParseInputFile(input_file):
  """Turns an input file into a list of _CaseInputs."""
  input_lines = _utils_Tokenize(input_file)[1:]  # skip the number of cases
  cases = []
  while input_lines:
    c, j = input_lines.pop(0)
    cases.append(_CaseInput(c, j))
  return cases


def ComputeEditDistance(s, t):
  """Returns the edit distance from s to t."""
  dp = [[0] * (len(t) + 1) for _ in range(len(s) + 1)]

  for i in range(len(s) + 1):
    dp[i][len(t)] = len(s) - i
  for j in range(len(t) + 1):
    dp[len(s)][j] = len(t) - j

  for i in range(len(s) - 1, -1, -1):
    for j in range(len(t) - 1, -1, -1):
      if s[i] == t[j]:
        dp[i][j] = dp[i + 1][j + 1]
      else:
        dp[i][j] = min(dp[i + 1][j], dp[i][j + 1], dp[i + 1][j + 1]) + 1

  return dp[0][0]


def VerifyOutput(lines, case, min_edit_distance):
  """Checks the output for a single test case.

  Args:
    lines: Tokenized lines (either from our I/OGen's output or a contestant's
      attempt.)
    case: A _CaseInput representing a single test case.
    min_edit_distance: Minimum edit distance based on our output.
                       We assume that our output is correct.


  Returns:
    A tuple of two values:
        1. None if the output is correct, or an error message.
        2. The edit distance from C (and J) to output if correct, or None.
  """

  if not lines or len(lines) != 1:
    return _BAD_FORMAT_ERROR, None

  if not lines[0] or len(lines[0]) != 1:
    return _BAD_FORMAT_ERROR, None

  s = lines[0][0].upper()

  if not all(cs.isupper() for cs in s):
    return _NON_LETTER_CHARACTER_ERROR, None

  if len(s) > len(case.c) + len(case.j):
    return _STRING_TOO_LONG_ERROR, None

  edit_distance_c = ComputeEditDistance(case.c, s)
  edit_distance_j = ComputeEditDistance(case.j, s)

  if min_edit_distance:
    if edit_distance_c + edit_distance_j < min_edit_distance:
      return _LESS_EDIT_DISTANCE_ERROR(edit_distance_c + edit_distance_j,
                                       min_edit_distance), None
    elif edit_distance_c + edit_distance_j > min_edit_distance:
      return _MORE_EDIT_DISTANCE_ERROR(edit_distance_c + edit_distance_j,
                                       min_edit_distance), None

  if abs(edit_distance_c - edit_distance_j) > 1:
    return _EDIT_DISTANCE_TOO_FAR_ERROR(edit_distance_c, edit_distance_j), None

  return None, edit_distance_c + edit_distance_j


def VerifyCase(output_lines, attempt_lines, case):
  """Checks a single test case.

  Args:
    output_lines: Tokenized lines from our I/OGen's output.
    attempt_lines: Tokenized lines from the contestant's attempt.
    case: A CaseInput representing a single test case.

  Returns:
    An error, or None if there is no error.
  """

  output_error, min_edit_distance = VerifyOutput(output_lines, case, None)
  if output_error is not None:
    return _BAD_OUTPUT_ERROR(output_error)
  attempt_error, _ = VerifyOutput(attempt_lines, case, min_edit_distance)
  return attempt_error


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


class NamingCompromiseUnitTest():
  def assertIsNone(self, a):
    assert a is None

  def assertEqual(self, a, b):
    assert a == b, "{} != {} but should be equal".format(a, b)

  input_lines = ['1', 'XYZZY ZZYZX']
  input_file = '\n'.join(input_lines)
  output_lines = ['Case #1: ZZY']
  output_file = '\n'.join(output_lines)

  def testInvalidCharacterCausesError(self):
    self.assertEqual(
        'Invalid attempt file: Invalid or non-ASCII characters.',
        FindError(None, self.input_file, self.output_file, chr(6)))

  def testEmptyAttemptCausesError(self):
    self.assertEqual('Invalid attempt file: Too few cases.',
                     FindError(None, self.input_file, self.output_file, ''))

  def testBadHeaderCausesError(self):
    self.assertEqual(
        'Invalid attempt file: Expected "case #1:", found "case ##1:".',
        FindError(None, self.input_file, self.output_file, 'Case ##1: ZZY'))

  def testBadFormatCausesError(self):
    self.assertEqual(
        'Case #1: ' + _BAD_FORMAT_ERROR,
        FindError(None, self.input_file, self.output_file,
                     '\n'.join(['Case #1:', 'ZZY'])))

    self.assertEqual(
        'Case #1: ' + _BAD_FORMAT_ERROR,
        FindError(None, self.input_file, self.output_file,
                     '\n'.join(['Case #1: ZZ Y'])))

  def testNonLetterCharacterCausesError(self):
    self.assertEqual(
        'Case #1: ' + _NON_LETTER_CHARACTER_ERROR,
        FindError(None, self.input_file, self.output_file, 'Case #1: 22Y'))
    self.assertEqual(
        'Case #1: ' + _NON_LETTER_CHARACTER_ERROR,
        FindError(None, self.input_file, self.output_file, 'Case #1: ZZY.'))

  def testStringTooLongCausesError(self):
    self.assertEqual(
        'Case #1: ' + _STRING_TOO_LONG_ERROR,
        FindError(None, self.input_file, self.output_file,
                  'Case #1: AXYZZYZZYZX'))

  def testEditDistanceTooFarCausesError(self):
    self.assertEqual(
        'Case #1: ' + _EDIT_DISTANCE_TOO_FAR_ERROR(1, 3),
        FindError(None, self.input_file, self.output_file, 'Case #1: YZZY'))

  def testMoreEditDistanceCausesError(self):
    self.assertEqual(
        'Case #1: ' + _MORE_EDIT_DISTANCE_ERROR(5, 4),
        FindError(None, self.input_file, self.output_file,
                  'Case #1: ZZZZZ'))

  def testAlternateCorrectSolutionPasses(self):
    self.assertIsNone(
        FindError(None, self.input_file, self.output_file, 'Case #1: XZZX'))
    self.assertIsNone(
        FindError(None, self.input_file, self.output_file, 'Case #1: ZYYZY'))
    self.assertIsNone(
        FindError(None, self.input_file, self.output_file, 'case #1: ZZY'))

  def testOurWrongSolutionCausesError(self):
    self.assertEqual(
        'JUDGE_ERROR Case #1: ' + _LESS_EDIT_DISTANCE_ERROR(4, 5),
        FindError(None, self.input_file, 'Case #1: ZZZZZ',
                  self.output_file))

  def testTwoCasesJudgedCorrectly(self):
    """Tests a file with two cases.

    Case #1: contestant's answer is correct
    Case #2: contestant's answer is incorrect

    Then changes the contestant's first answer to be wrong, and tests again.
    """

    two_case_input = '\n'.join(['2', 'XYZZY ZZYZX', 'Y Z'])
    two_case_output = '\n'.join(['Case #1: ZZY', 'Case #2: Y'])
    two_case_attempt = '\n'.join(['Case #1: ZZY', 'Case #2: Q'])
    self.assertEqual(
        'Case #2: ' + _MORE_EDIT_DISTANCE_ERROR(2, 1),
        FindError(None, two_case_input, two_case_output, two_case_attempt))

    two_case_attempt = '\n'.join(['Case #1: ZZZZZ', 'Case #2: Q'])
    self.assertEqual(
        'Case #1: ' + _MORE_EDIT_DISTANCE_ERROR(5, 4),
        FindError(None, two_case_input, two_case_output, two_case_attempt))

  def testEmptyStringIsNeverAccepted(self):
    self.assertIsNone(
        FindError(None, '\n'.join(['1', 'A B']), 'Case #1: A', 'Case #1: B'))
    self.assertEqual(
        'Case #1: ' + _BAD_FORMAT_ERROR,
        FindError(None, '\n'.join(['1', 'A B']), 'Case #1: A', 'Case #1: '))

  def testEditDistance(self):
    testcases = [
        (('', ''), 0),
        (('', 'A'), 1),
        (('EDIT', 'DISTANCE'), 6),
        (('AB', 'BA'), 2),
        (('ABABAB', 'BABABA'), 2),
        (('ABABAB', 'ABABAB'), 0),
        (('ABCDEFGHIJKLM', 'NOPQRSTUVWXYZ'), 13),
        (('BBABBBABBBABABBBAA', 'CCCACAAACACAAACACA'), 14),
        (('GOOGLE', 'CODEJAM'), 6),
        (('HELPIAMTRAPPED', 'INAUNITTESTFACTORY'), 15)
    ]

    for testcase in testcases:
      self.assertEqual(
          testcase[1], ComputeEditDistance(testcase[0][0], testcase[0][1]))
      self.assertEqual(
          testcase[1], ComputeEditDistance(testcase[0][1], testcase[0][0]))


def RunUnitTests():
  namingCompromiseUnitTest = NamingCompromiseUnitTest()
  namingCompromiseUnitTest.testInvalidCharacterCausesError()
  namingCompromiseUnitTest.testEmptyAttemptCausesError()
  namingCompromiseUnitTest.testBadHeaderCausesError()
  namingCompromiseUnitTest.testBadFormatCausesError()
  namingCompromiseUnitTest.testNonLetterCharacterCausesError()
  namingCompromiseUnitTest.testStringTooLongCausesError()
  namingCompromiseUnitTest.testEditDistanceTooFarCausesError()
  namingCompromiseUnitTest.testMoreEditDistanceCausesError()
  namingCompromiseUnitTest.testAlternateCorrectSolutionPasses()
  namingCompromiseUnitTest.testOurWrongSolutionCausesError()
  namingCompromiseUnitTest.testTwoCasesJudgedCorrectly()
  namingCompromiseUnitTest.testEmptyStringIsNeverAccepted()
  namingCompromiseUnitTest.testEditDistance()
  print('NamingCompromiseUnitTest passes.')
  sys.exit(0)


import sys
if __name__ == "__main__":
  if sys.argv[1] == '-2':
    RunUnitTests()

  result = FindError(None,
                     file(sys.argv[1]).read(),
                     file(sys.argv[3]).read(),
                     file(sys.argv[2]).read())
  if result:
    print >> sys.stderr, result
    sys.exit(1)
