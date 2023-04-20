# Copyright 2011 Google Inc. All Rights Reserved.
"""Basic utilities for custom judges."""

import fractions
import sys


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
  return list(filter(None, row.split(' '))
              for row in text.split('\n')
              if row.strip())



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


"""Custom judge for Range Partition, Kick Start."""

import collections

_BAD_OUTPUT_ERROR_STR = 'Our output is incorrect:'
_BAD_OUTPUT_ERROR = (_BAD_OUTPUT_ERROR_STR + ' {}').format

_BAD_FORMAT_ERROR = 'Output is not well-formatted'
_WRONG_ANSWER = 'The answer is not correct'
_INCORRECT_RATIO = 'The ratio is not equivalent to X:Y'
_REPEATED_NUMBERS_IN_SUBSET = "Duplicate numbers are in the subset."
_ANSWER_SIZE_MISMATCH = 'The given subset size does not match the given numbers'
_SUBSET_OUT_OF_RANGE = "Numbers in the subset are not within [1, N]"

"""Parsed information for a single test case."""
_CaseInput = collections.namedtuple('_CaseInput', ['N', 'X', 'Y'])


def ParseInputFile(input_file):
  """Turns an input file into a list of _CaseInputs."""
  # skip the number of cases (line 0)
  input_lines = _utils_Tokenize(input_file)[1:]
  cases = []
  for input_line in input_lines:
    N, X, Y = map(int, input_line)
    cases.append(_CaseInput(N, X, Y))
  return cases


def VerifyOutput(lines, case):
  """Checks the output for a single test case.

  Args:
    lines: Tokenized lines (either from our I/OGen's output or a contestant's
      attempt.)
    case: A _CaseInput representing a single test case.

  Returns:
    None if the output is correct, or an error message.
  """
  # Check POSSIBLE input
  if len(lines) > 1:
    if len(lines[0]) != 1 or lines[0][0] != 'POSSIBLE':
      return _BAD_FORMAT_ERROR

    if len(lines) != 3:
      return _BAD_FORMAT_ERROR

    if len(lines[1]) != 1 or _utils_ToInteger(lines[1][0]) is None:
      return _BAD_FORMAT_ERROR

    alice_subset_numbers = list(map(_utils_ToInteger, lines[2]))
    for n in alice_subset_numbers:
      if n is None:
        return _BAD_FORMAT_ERROR

      if n < 1 or n > case.N:
        return _SUBSET_OUT_OF_RANGE

    if len(alice_subset_numbers) != len(set(alice_subset_numbers)):
      return _REPEATED_NUMBERS_IN_SUBSET

  # Check IMPOSSIBLE input
  if len(lines) == 1:
    if len(lines[0]) != 1 or lines[0][0] != 'IMPOSSIBLE':
      return _BAD_FORMAT_ERROR

  return None


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


def FindError(input_file, output_file, attempt_file):
  """See judge.Judge.FindError()."""
  input_cases = ParseInputFile(input_file)
  num_cases = len(input_cases)
  output_cases, attempt_cases, error = _utils_TokenizeAndSplitCases(
      output_file, attempt_file, num_cases, True)
  if error is not None:
    return error

  for case_num, (case, output_lines, attempt_lines) in enumerate(
      zip(input_cases, output_cases, attempt_cases), start=1):
    error = VerifyCase(output_lines, attempt_lines, case)
    if error is not None:
      je = 'JUDGE_ERROR ' if error.startswith(_BAD_OUTPUT_ERROR_STR) else ''
      return '{}Case #{}: {}'.format(je, case_num, error)

    # Check IMPOSSIBLE case
    if len(attempt_lines) == 1:
      if (attempt_lines[0][0] != output_lines[0][0]):
        return _WRONG_ANSWER + ' (got: %s, expected: %s)' % (
          attempt_lines[0][0], output_lines[0][0])

    # Check POSSIBLE case
    else:
      alice_subset_size = _utils_ToInteger(attempt_lines[1][0])
      alice_subset_numbers = list(map(_utils_ToInteger, attempt_lines[2]))
      alice_subset_sum = sum(alice_subset_numbers)

      bob_subset_numbers = [n for n in range(1, case.N + 1)
                            if n not in set(alice_subset_numbers)]
      bob_subset_sum = sum(bob_subset_numbers)

      if alice_subset_size != len(alice_subset_numbers):
        return _ANSWER_SIZE_MISMATCH

      if bob_subset_sum == 0:
        return _INCORRECT_RATIO + ' (got: [X:%s, Y:0], expected: [X:%s, Y:%s])' % (
            alice_subset_sum, case.X, case.Y)

      f = fractions.Fraction(alice_subset_sum, bob_subset_sum)

      if f.numerator != case.X or f.denominator != case.Y:
        return _INCORRECT_RATIO + ' (got: [X:%s, Y:%s], expected: [X:%s, Y:%s])' % (
            f.numerator, f.denominator, case.X, case.Y)

  # Everything passes.
  return None


class RangePartitionUnitTest():

  def assertIsNone(self, a):
    assert a is None

  def assertEqual(self, a, b):
    assert a == b, (a, b)

  def assertStartsWith(self, a, b):
    assert a.startswith(b), (a, b)

  input_file = """
3
3 1 2
3 1 1
3 1 3
""".lstrip()

  output_file = """
Case #1: POSSIBLE
1
2
Case #2: POSSIBLE
2
1 2
Case #3: IMPOSSIBLE
""".lstrip()

  def testCorrectAnswerDoesNotCauseError(self):
    self.assertIsNone(
        FindError(self.input_file, self.output_file, self.output_file))

  def testCorrectAnswerDifferentSubsetDoesNotCauseError(self):
    self.assertIsNone(
        FindError(self.input_file, self.output_file, """
Case #1: POSSIBLE
1
2
Case #2: POSSIBLE
1
3
Case #3: IMPOSSIBLE
""".lstrip()))

  def testCorrectAnswerUnsortedDoesNotCauseError(self):
    self.assertIsNone(
        FindError(self.input_file, self.output_file, """
Case #1: POSSIBLE
1
2
Case #2: POSSIBLE
2
2 1
Case #3: IMPOSSIBLE
""".lstrip()))

  def testIncorrectPossibleAnswerCausesError(self):
    self.assertStartsWith(
        FindError(self.input_file, self.output_file, """
Case #1: IMPOSSIBLE
Case #2: IMPOSSIBLE
Case #3: IMPOSSIBLE
""".lstrip()), _WRONG_ANSWER)

  def testIncorrectImpossibleAnswerCausesError(self):
    self.assertStartsWith(
        FindError(self.input_file, self.output_file, """
Case #1: POSSIBLE
1
2
Case #2: POSSIBLE
2
1 2
Case #3: POSSIBLE
1
2
""".lstrip()), _INCORRECT_RATIO)

  def testIncorrectRatioCausesError(self):
    self.assertStartsWith(
        FindError(self.input_file, self.output_file, """
Case #1: POSSIBLE
1
2
Case #2: POSSIBLE
1
1
Case #3: IMPOSSIBLE
""".lstrip()), _INCORRECT_RATIO)

    self.assertStartsWith(
        FindError(self.input_file, self.output_file, """
Case #1: POSSIBLE
1
2
Case #2: POSSIBLE
3
1 2 3
Case #3: IMPOSSIBLE
""".lstrip()), _INCORRECT_RATIO)

  def testIncorrectSubsetSizeCausesError(self):
    self.assertStartsWith(
        FindError(self.input_file, self.output_file, """
Case #1: POSSIBLE
1
2
Case #2: POSSIBLE
1
1 2
Case #3: IMPOSSIBLE
""".lstrip()), _ANSWER_SIZE_MISMATCH)

  def testRepeatedNumbersInSubsetCausesError(self):
    self.assertEqual(
        'Case #1: ' + _REPEATED_NUMBERS_IN_SUBSET,
        FindError(self.input_file, self.output_file, """
Case #1: POSSIBLE
2
1 1
Case #2: POSSIBLE
2
1 2
Case #3: IMPOSSIBLE
""".lstrip()))

  def testSubsetNumbersOutOfRangeCausesError(self):
    self.assertEqual(
        'Case #2: ' + _SUBSET_OUT_OF_RANGE,
        FindError(self.input_file, self.output_file, """
Case #1: POSSIBLE
1
2
Case #2: POSSIBLE
1
4
Case #3: IMPOSSIBLE
""".lstrip()))

    self.assertEqual(
        'Case #1: ' + _SUBSET_OUT_OF_RANGE,
        FindError(self.input_file, self.output_file, """
Case #1: POSSIBLE
2
0 2
Case #2: POSSIBLE
2
1 2
Case #3: IMPOSSIBLE
""".lstrip()))

  def testEmptyAttemptCausesError(self):
    self.assertEqual('Invalid attempt file: Too few cases.',
                     FindError(self.input_file, self.output_file, ''))

  def testBadHeaderCausesError(self):
    self.assertEqual(
        'Invalid attempt file: Expected "case #1:", found "Case ##1:".',
        FindError(self.input_file, self.output_file,
                  'Case ##1: IMPOSSIBLE'))

  def testBadFormatCausesError(self):
    pass
    self.assertEqual(
        'Case #1: ' + _BAD_FORMAT_ERROR,
        FindError(
            self.input_file, self.output_file, """
Case #1:
Case #2: POSSIBLE
Case #3: POSSIBLE
""".lstrip()))

    self.assertEqual(
        'Case #1: ' + _BAD_FORMAT_ERROR,
        FindError(
            self.input_file, self.output_file, """
Case #1: POSSIBLE
Case #2: POSSIBLE
Case #3: IMPOSSIBLE
""".lstrip()))

    self.assertEqual(
        'Case #1: ' + _BAD_FORMAT_ERROR,
        FindError(
            self.input_file, self.output_file, """
Case #1: POSSIBLE 3 1 2
Case #2: POSSIBLE
Case #3: IMPOSSIBLE
""".lstrip()))

    self.assertEqual(
        'Case #1: ' + _BAD_FORMAT_ERROR,
        FindError(
            self.input_file, self.output_file, """
Case #1: YES
Case #2: YES
Case #3: NO
""".lstrip()))

  def testMissingCaseCausesError(self):
    self.assertEqual(
        'Invalid attempt file: Too few cases.',
        FindError(
            self.input_file, self.output_file, """
Case #1: POSSIBLE
""".lstrip()))


def RunUnitTests():
  test = RangePartitionUnitTest()
  test_methods = [
      method_name for method_name in dir(test)
      if callable(getattr(test, method_name)) and method_name.startswith('test')
  ]
  for test_method in test_methods:
    print(test_method)
    getattr(test, test_method)()

  print('RangePartitionnUnitTest passes.')
  sys.exit(0)


if __name__ == '__main__':
  if sys.argv[1] == '-2':
    RunUnitTests()

  result = FindError(open(sys.argv[1]).read(),
                     open(sys.argv[3]).read(),
                     open(sys.argv[2]).read())
  if result:
    print(result, file=sys.stderr)
    sys.exit(1)
