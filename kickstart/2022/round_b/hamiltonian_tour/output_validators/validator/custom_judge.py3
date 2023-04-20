# Copyright 2011 Google Inc. All Rights Reserved.

"""Basic utilities for custom judges."""

__author__ = 'darthur@google.com (David Arthur)'

import logging
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
  return [list(filter(None, row.split(' '))) for row in text.split('\n')
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


"""Custom judge for Hamiltonian Tour, Kickstart."""

__author__ = 'johngs@google.com (Jonathan Irvin Gunawan)'

import collections


_BAD_IMPOSSIBLE_CLAIM_ERROR = (
    'Solution claims a tour does not exist while our solution finds one')
_BAD_FORMAT_ERROR = 'Output is not a single string'
_BAD_STRING_ERROR = 'Output is not of the form (N|S|E|W)* or IMPOSSIBLE'
_BAD_OUTPUT_ERROR = 'Our output is incorrect: {0}'.format
_BAD_POSSIBLE_CLAIM_ERROR = _BAD_OUTPUT_ERROR(
    'Solution shows that a tour exists while our solution does not find one')

_BAD_TOUR_HITS_A_BUILDING = 'The tour hits a building'
_BAD_TOUR_GOES_OUT_OF_BOUNDS = 'The tour goes out of bounds'
_BAD_TOUR_REVISIT_CELL = 'The tour revisits a cell'
_BAD_TOUR_UNVISITED_CELL = 'The tour does not visit every empty cell'
_BAD_TOUR_ENDS_NOT_VALID = 'The tour does not end at the top-left corner'

"""Parsed information for a single test case.

Attributes:
  r: The number of rows
  c: The number of columns
  grid: A list of length r. grid[i] is a string or c characters, representing
        the i-th row of the grid.
"""
_CaseInput = collections.namedtuple('_CaseInput', ['r', 'c', 'grid'])


def ParseInputFile(input_file):
  """Turns an input file into a list of _CaseInputs."""
  input_lines = _utils_Tokenize(input_file)[1:]  # skip the number of cases
  cases = []
  while input_lines:
    r, c = [int(x) for x in input_lines.pop(0)]
    grid = []
    for _ in range(r):
      grid.append(input_lines.pop(0)[0])
    cases.append(_CaseInput(r, c, grid))
  return cases


def VerifyOutput(lines, case, expected_tour_exists):
  """Checks the output for a single test case.

  Args:
    lines: Tokenized lines (either from our I/OGen's output or a contestant's
        attempt.)
    case: A _CaseInput representing a single test case.
    expected_tour_exists: Whether a tour exists based on our output. We assume
        that our output's is correct.

  Returns:
    A tuple of two values:
        1. None if the output is correct, or an error message.
        2. Whether there is a tour if the output is correct, or None.
  """
  if (not lines) or (len(lines) != 1) or (len(lines[0]) != 1):
    return _BAD_FORMAT_ERROR, None

  output = lines[0][0].upper()
  tour_exists = True
  if output == 'IMPOSSIBLE':
    tour_exists = False
  else:
    if any(ch not in 'NSEW' for ch in output):
      return _BAD_STRING_ERROR, None

    visited = [[False] * (2 * case.c) for _ in range(2 * case.r)]
    current_pos = [0, 0]
    direction = {}
    direction['N'] = [-1, 0]
    direction['E'] = [0, 1]
    direction['S'] = [1, 0]
    direction['W'] = [0, -1]

    for ch in output:
      current_pos[0] += direction[ch][0]
      current_pos[1] += direction[ch][1]
      if current_pos[0] < 0 or current_pos[0] >= 2 * case.r or \
         current_pos[1] < 0 or current_pos[1] >= 2 * case.c:
        return _BAD_TOUR_GOES_OUT_OF_BOUNDS, None
      if case.grid[current_pos[0] // 2][current_pos[1] // 2] == '#':
        return _BAD_TOUR_HITS_A_BUILDING, None
      if visited[current_pos[0]][current_pos[1]]:
        return _BAD_TOUR_REVISIT_CELL, None
      visited[current_pos[0]][current_pos[1]] = True

    if current_pos[0] != 0 or current_pos[1] != 0:
      return _BAD_TOUR_ENDS_NOT_VALID, None

    for i in range(2 * case.r):
      for j in range(2 * case.c):
        if not visited[i][j] and case.grid[i // 2][j // 2] == '*':
          return _BAD_TOUR_UNVISITED_CELL, None

  if expected_tour_exists is not None:
    if expected_tour_exists and (not tour_exists):
      return _BAD_IMPOSSIBLE_CLAIM_ERROR, None
    if (not expected_tour_exists) and tour_exists:
      return _BAD_POSSIBLE_CLAIM_ERROR, None

  return None, tour_exists


def VerifyCase(output_lines, attempt_lines, case):
  """Checks a single test case.

  Args:
    output_lines: Tokenized lines from our I/OGen's output.
    attempt_lines: Tokenized lines from the contestant's attempt.
    case: A CaseInput representing a single test case.
  Returns:
    An error, or None if there is no error.
  """

  output_error, tour_exists = VerifyOutput(output_lines, case, None)
  if output_error is not None:
    return _BAD_OUTPUT_ERROR(output_error)
  attempt_error, _ = VerifyOutput(attempt_lines, case, tour_exists)
  return attempt_error


def FindError(input_file, output_file, attempt_file):
  """See judge.Judge.FindError()."""
  input_cases = ParseInputFile(input_file)
  num_cases = len(input_cases)
  output_cases, attempt_cases, error = _utils_TokenizeAndSplitCases(output_file,
                                                                   attempt_file,
                                                                   num_cases)
  if error is not None:
    return error

  for case_num, (case, output_lines, attempt_lines) in enumerate(
      zip(input_cases, output_cases, attempt_cases), start=1):
    error = VerifyCase(output_lines, attempt_lines, case)
    if error is not None:
      return 'Case #{}: {}'.format(case_num, error)

  # Everything passes.
  return None


class HamiltonianTourUnitTest():
  def assertIsNone(self, a):
    assert a is None

  def assertEqual(self, a, b):
    assert a == b, (a, b)

  def assertStartsWith(self, a, b):
    assert a.startswith(b), (a, b)


class HamiltonianTourPossibleTest(HamiltonianTourUnitTest):
  input_lines = ['1', '2 2', '**', '*#']
  input_file = '\n'.join(input_lines)
  output_lines = ['Case #1: EEESWWSSWNNN']
  output_file = '\n'.join(output_lines)

  def testInvalidCharacterCausesError(self):
    self.assertEqual(
        'Invalid attempt file: Invalid or non-ASCII characters.',
        FindError(self.input_file, self.output_file, chr(6)))

  def testEmptyAttemptCausesError(self):
    self.assertEqual('Invalid attempt file: Too few cases.',
                     FindError(self.input_file, self.output_file, ''))

  def testBadHeaderCausesError(self):
    self.assertEqual(
        'Invalid attempt file: Expected "case #1:", found "case ##1:".',
        FindError(self.input_file, self.output_file,
                     '\n'.join(['Case ##1: EEESWWSSWNNN'])))

  def testBadImpossibleClaimCausesError(self):
    self.assertEqual(
        'Case #1: ' + _BAD_IMPOSSIBLE_CLAIM_ERROR,
        FindError(self.input_file, self.output_file,
                     '\n'.join(['Case #1: IMPOSSIBLE'])))

  def testBadFormatOrStringCausesError(self):
    self.assertEqual(
        'Case #1: ' + _BAD_FORMAT_ERROR,
        FindError(self.input_file, self.output_file,
                     '\n'.join(['Case #1: '])))
    self.assertEqual(
        'Case #1: ' + _BAD_FORMAT_ERROR,
        FindError(self.input_file, self.output_file,
                     '\n'.join(['Case #1: CODE JAM'])))
    self.assertEqual(
        'Case #1: ' + _BAD_STRING_ERROR,
        FindError(self.input_file, self.output_file,
                     '\n'.join(['Case #1: CODEJAM'])))

  def testBadTourHitsBuildingCausesError(self):
    self.assertEqual(
        'Case #1: ' + _BAD_TOUR_HITS_A_BUILDING,
        FindError(self.input_file, self.output_file,
                     '\n'.join(['Case #1: EEESWWSEESWWWNNN'])))

  def testBadTourGoesOutOfBoundCausesError(self):
    self.assertEqual(
        'Case #1: ' + _BAD_TOUR_GOES_OUT_OF_BOUNDS,
        FindError(self.input_file, self.output_file,
                     '\n'.join(['Case #1: EEEESWWWSSWNNN'])))

  def testBadTourRevisitsCellCausesError(self):
    self.assertEqual(
        'Case #1: ' + _BAD_TOUR_REVISIT_CELL,
        FindError(self.input_file, self.output_file,
                     '\n'.join(['Case #1: EEESWWSSWNSNNN'])))

  def testBadTourUnvisitedCellCausesError(self):
    self.assertEqual(
        'Case #1: ' + _BAD_TOUR_UNVISITED_CELL,
        FindError(self.input_file, self.output_file,
                     '\n'.join(['Case #1: EESWSSWNNN'])))

  def testBadTourEndsNotValidCausesError(self):
    self.assertEqual(
        'Case #1: ' + _BAD_TOUR_ENDS_NOT_VALID,
        FindError(self.input_file, self.output_file,
                     '\n'.join(['Case #1: EWSSSENNEENW'])))

  def testOurWrongSolutionCausesError(self):
    self.assertEqual(
        'Case #1: ' + _BAD_OUTPUT_ERROR(_BAD_STRING_ERROR),
        FindError(self.input_file,
                     '\n'.join(['Case #1: KICKSTART']),
                     self.output_file))

    self.assertEqual(
        'Case #1: ' + _BAD_POSSIBLE_CLAIM_ERROR,
        FindError(self.input_file,
                     '\n'.join(['Case #1: IMPOSSIBLE']),
                     self.output_file))

    self.assertEqual(
        'Case #1: ' + _BAD_OUTPUT_ERROR(_BAD_TOUR_GOES_OUT_OF_BOUNDS),
        FindError(self.input_file,
                     '\n'.join(['Case #1: EEEESWWWSSWNNN']),
                     self.output_file))

    self.assertEqual(
        'Case #1: ' + _BAD_OUTPUT_ERROR(_BAD_TOUR_REVISIT_CELL),
        FindError(self.input_file,
                     '\n'.join(['Case #1: EEESWWSSWNSNNN']),
                     self.output_file))

  def testCorrectSolutionPasses(self):
    self.assertIsNone(
        FindError(self.input_file, self.output_file, self.output_file))
    self.assertIsNone(
        FindError(self.input_file, self.output_file,
                     '\n'.join(['Case #1: SSSENNEENWWW'])))

  def testCorrectLowerCaseSolutionPasses(self):
    self.assertIsNone(
        FindError(self.input_file, self.output_file,
                     '\n'.join(['Case #1: eeeswwsswnnn'])))

  def testTwoCasesJudgedCorrectly(self):
    """Tests a file with two cases.

    Case #1: contestant's answer is correct
    Case #2: contestant's answer is incorrect

    Then changes the contestant's first answer to be wrong, and tests again.
    """

    two_case_input = '\n'.join(
        ['1', '2 2', '**', '*#', '1 1', '*'])
    two_case_output = '\n'.join(
        ['Case #1: EEESWWSSWNNN', 'Case #2: ESWN'])
    two_case_attempt = '\n'.join(
        ['Case #1: SSSENNEENWWW', 'Case #2: EESWWN'])
    self.assertEqual(
        'Case #2: ' + _BAD_TOUR_GOES_OUT_OF_BOUNDS,
        FindError(two_case_input, two_case_output, two_case_attempt))
    two_case_attempt = '\n'.join(
        ['Case #1: EEEESWWWSSWNNN', 'Case #2: EESWWN'])
    self.assertEqual(
        'Case #1: ' + _BAD_TOUR_GOES_OUT_OF_BOUNDS,
        FindError(two_case_input, two_case_output, two_case_attempt))


class HamiltonianTourImpossibleTest(HamiltonianTourUnitTest):
  input_lines = ['1', '2 2', '*#', '#*']
  input_file = '\n'.join(input_lines)
  output_lines = ['Case #1: IMPOSSIBLE']
  output_file = '\n'.join(output_lines)

  def testInvalidCharacterCausesError(self):
    self.assertEqual(
        'Invalid attempt file: Invalid or non-ASCII characters.',
        FindError(self.input_file, self.output_file, chr(6)))

  def testEmptyAttemptCausesError(self):
    self.assertEqual('Invalid attempt file: Too few cases.',
                     FindError(self.input_file, self.output_file, ''))

  def testBadHeaderCausesError(self):
    self.assertEqual(
        'Invalid attempt file: Expected "case #1:", found "case ##1:".',
        FindError(self.input_file, self.output_file,
                     '\n'.join(['Case ##1: IMPOSSIBLE'])))

  def testBadFormatCausesError(self):
    self.assertEqual(
        'Case #1: ' + _BAD_FORMAT_ERROR,
        FindError(self.input_file, self.output_file,
                     '\n'.join(['Case #1: '])))
    self.assertEqual(
        'Case #1: ' + _BAD_FORMAT_ERROR,
        FindError(self.input_file, self.output_file,
                     '\n'.join(['Case #1: CODE JAM'])))
    self.assertEqual(
        'Case #1: ' + _BAD_STRING_ERROR,
        FindError(self.input_file, self.output_file,
                     '\n'.join(['Case #1: CODEJAM'])))

  def testBadTourHitsBuildingCausesError(self):
    self.assertEqual(
        'Case #1: ' + _BAD_TOUR_HITS_A_BUILDING,
        FindError(self.input_file, self.output_file,
                     '\n'.join(['Case #1: EEESSSWNNWWN'])))

  def testBadTourGoesOutOfBoundCausesError(self):
    self.assertEqual(
        'Case #1: ' + _BAD_TOUR_GOES_OUT_OF_BOUNDS,
        FindError(self.input_file, self.output_file,
                     '\n'.join(['Case #1: NS'])))

  def testBadTourRevisitsCellCausesError(self):
    self.assertEqual(
        'Case #1: ' + _BAD_TOUR_REVISIT_CELL,
        FindError(self.input_file, self.output_file,
                     '\n'.join(['Case #1: ESNW'])))

  def testBadTourUnvisitedCellCausesError(self):
    self.assertEqual(
        'Case #1: ' + _BAD_TOUR_UNVISITED_CELL,
        FindError(self.input_file, self.output_file,
                     '\n'.join(['Case #1: ESWN'])))

  def testOurWrongSolutionCausesError(self):
    self.assertEqual(
        'Case #1: ' + _BAD_OUTPUT_ERROR(_BAD_STRING_ERROR),
        FindError(self.input_file,
                     '\n'.join(['Case #1: CODEJAM']),
                     self.output_file))

    self.assertEqual(
        'Case #1: ' + _BAD_OUTPUT_ERROR(_BAD_TOUR_GOES_OUT_OF_BOUNDS),
        FindError(self.input_file,
                     '\n'.join(['Case #1: NS']),
                     self.output_file))

    self.assertEqual(
        'Case #1: ' + _BAD_OUTPUT_ERROR(_BAD_TOUR_REVISIT_CELL),
        FindError(self.input_file,
                     '\n'.join(['Case #1: ESNW']),
                     self.output_file))

  def testCorrectSolutionPasses(self):
    self.assertIsNone(
        FindError(self.input_file, self.output_file, self.output_file))

  def testCorrectLowerCaseSolutionPasses(self):
    self.assertIsNone(
        FindError(self.input_file, self.output_file,
                     '\n'.join(['Case #1: impossible'])))

  def testTwoCasesJudgedCorrectly(self):
    """Tests a file with two cases.

    Case #1: contestant's answer is correct
    Case #2: contestant's answer is incorrect

    Then changes the contestant's first answer to be wrong, and tests again.
    """

    two_case_input = '\n'.join(
        ['2', '2 2', '*#', '#*', '1 3', '*#*'])
    two_case_output = '\n'.join(
        ['Case #1: IMPOSSIBLE', 'Case #2: IMPOSSIBLE'])
    two_case_attempt = '\n'.join(
        ['Case #1: IMPOSSIBLE', 'Case #2: ESNW'])
    self.assertEqual(
        'Case #2: ' + _BAD_TOUR_REVISIT_CELL,
        FindError(two_case_input, two_case_output, two_case_attempt))
    two_case_attempt = '\n'.join(
        ['Case #1: ESNW', 'Case #2: ESNW'])
    self.assertEqual(
        'Case #1: ' + _BAD_TOUR_REVISIT_CELL,
        FindError(two_case_input, two_case_output, two_case_attempt))


def RunUnitTestClass(test):
  test_methods = [
      method_name for method_name in dir(test)
      if callable(getattr(test, method_name)) and method_name.startswith('test')
  ]

  for test_method in test_methods:
    print(test_method)
    getattr(test, test_method)()


def RunUnitTests():
  RunUnitTestClass(HamiltonianTourPossibleTest())
  RunUnitTestClass(HamiltonianTourImpossibleTest())

  print('HamiltonianTourUnitTests passed.')
  sys.exit(0)


if __name__ == "__main__":
  if sys.argv[1] == '-2':
    RunUnitTests()

  result = FindError(open(sys.argv[1]).read(),
                     open(sys.argv[3]).read(),
                     open(sys.argv[2]).read())
  if result:
    print(sys.stderr, result)
    sys.exit(1)
