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
"""A custom judge for "The Gardener of Seville", Code Jam 2016.

Problem description at:
https://gcj-loadtest.appspot.com/codejam/contest/problems/do?
    cmd=ShowProblemPage&id=5838157937377280

TODO(tullis): Update this link when the problem gets loaded onto the production
site after the external round.
"""

__author__ = 'tullis@google.com (Ian Tullis)'

import collections


# The various errors we can return.
_ATTEMPT_FALSE_NEGATIVE_ERROR = 'Got IMPOSSIBLE when answer exists.'
_BAD_HEADER_ERROR = 'Extra token(s) in header: %s'
_INVALID_CHARACTER_ERROR = 'Row %d, column %d: Invalid character %s.'
_OUTPUT_BAD_GRID_ERROR = 'Output grid is not a valid solution: %s'
_OUTPUT_FALSE_NEGATIVE_ERROR = 'Attempt grid is correct for IMPOSSIBLE case.'
_WRONG_CONNECTION_ERROR = 'Lover %d connects to %d instead of %d.'
_WRONG_NUM_COLUMNS_ERROR = 'Expected %d columns, got %d in row %d.'
_WRONG_NUM_ROWS_ERROR = 'Expected %d rows, got %d.'
_WRONG_ROW_TOKENS_ERROR = 'More than 1 token in row %d: %s'

# Constants for use in VerifyOutput and VerifyCase.
# These classify answers to test cases, which may come from our own I/OGen or
# from contestants.
_IMPOSSIBLE = 0  # The given answer is "IMPOSSIBLE".
_INCORRECT = 1  # An answer is claimed, but is incorrect.
_POSSIBLE = 2  # An answer is claimed, and is correct.


# The four sides of each cell in the grid. Used in CheckGrid.
_LEFT, _TOP, _RIGHT, _BOTTOM = 0, 1, 2, 3

# This dictionary takes two keys -- either a / or a \, and one of the four
# directions _LEFT, _TOP, _RIGHT, _BOTTOM -- and returns a tuple of:
# row offset to get to next cell, column offset to get to next cell,
# side from which next cell will be entered
move_dict = {'/':
             {_LEFT: (-1, 0, _BOTTOM), _TOP: (0, -1, _RIGHT),
              _RIGHT: (1, 0, _TOP), _BOTTOM: (0, 1, _LEFT)},
             '\\':
             {_LEFT: (1, 0, _TOP), _TOP: (0, 1, _LEFT),
              _RIGHT: (-1, 0, _BOTTOM), _BOTTOM: (0, -1, _RIGHT)}}

# A LoverData object stores useful stats for a single lover. This is used
#    in CheckGrid.
#
# Attributes:
#   row: The row of the padded grid in which this lover appears.
#   col: The column of the padded grid in which this lover appears.
#   entry_side: The side of the first cell from which the lover will enter,
#       from the perspective of that cell.
LoverData = collections.namedtuple(
    'LoverData', ['row', 'col', 'entry_side'])

# A CaseInput stores parsed information for a single test case.
#
# Attributes:
#   case_num: The number of the test case, starting from 1.
#   num_rows: The number of rows in the answer grid if there is an answer.
#   num_cols: The number of columns in the answer grid if there is an answer.
#   connections: A dictionary with lover numbers as keys, and the lovers
#       to who they should be connected as values.
CaseInput = collections.namedtuple(
    'CaseInput', ['case_num', 'num_rows', 'num_cols', 'connections'])


def ParseInputFile(input_file):
  """Turns an input file of two-line test cases into a list of CaseInputs."""

  input_lines = _utils_Tokenize(input_file)
  num_cases = int(input_lines[0][0])

  result = []
  for i in xrange(num_cases):
    r, c = [int(x) for x in input_lines[1 + 2*i]]
    lovers = [int(x) for x in input_lines[2 + 2*i]]
    connections = {}
    for j in xrange(r+c):
      connections[lovers[2*j]] = lovers[1 + 2*j]
      connections[lovers[1 + 2*j]] = lovers[2*j]
    result.append(CaseInput(i+1, r, c, connections))
  return result


def CheckGrid(row_lines, case):
  """Determines whether a grid is a correct solution.

  Turns the raw strings representing the grid into a two-dimensional array,
  padded with one row above and below and one column to the left and right.
  Then, adds lovers to the grid (in a clockwise fashion, starting from the
  upper left) and populates a dictionary of the cells from which they will
  enter, and sides from which they will enter those cells.

  Args:
    row_lines: A list of case.num_rows lines, each of which has one entry that
        is a string of length case.num_cols.
    case: The InputCase for this test case.
  Returns:
    A _WRONG_CONNECTION_ERROR, or None if there is no error.
  """

  grid = [[None]*(case.num_cols+2)]
  for row_line in row_lines:
    grid.append([None] + list(row_line[0]) + [None])
  grid.append([None]*(case.num_cols+2))

  num_lovers = 2 * (case.num_rows + case.num_cols)

  lover_stats = ['unused'] + [None]*num_lovers

  lover_num = 1
  for n in xrange(case.num_cols):
    grid[0][n + 1] = lover_num
    lover_stats[lover_num] = LoverData(1, 1 + n, _TOP)
    lover_num += 1
  for n in xrange(case.num_rows):
    grid[1 + n][case.num_cols + 1] = lover_num
    lover_stats[lover_num] = LoverData(1 + n, case.num_cols, _RIGHT)
    lover_num += 1
  for n in xrange(case.num_cols):
    grid[case.num_rows + 1][case.num_cols - n] = lover_num
    lover_stats[lover_num] = LoverData(
        case.num_rows, case.num_cols - n, _BOTTOM)
    lover_num += 1
  for n in xrange(case.num_rows):
    grid[case.num_rows - n][0] = lover_num
    lover_stats[lover_num] = LoverData(case.num_rows - n, 1, _LEFT)
    lover_num += 1

  def _FindOutlet(lover_num):
    """Determines where a lover will emerge from the grid."""
    curr_r, curr_c, curr_e_side = lover_stats[lover_num]
    while grid[curr_r][curr_c] in move_dict:
      r_off, c_off, new_e_side = move_dict[grid[curr_r][curr_c]][curr_e_side]
      curr_r, curr_c, curr_e_side = curr_r + r_off, curr_c + c_off, new_e_side
    return grid[curr_r][curr_c]

  for lover_num in xrange(1, num_lovers+1):
    connection = _FindOutlet(lover_num)
    if connection != case.connections[lover_num]:
      return _WRONG_CONNECTION_ERROR % (
          lover_num, connection, case.connections[lover_num])

  return None


def VerifyOutput(lines, case):
  """Checks the output for a single test case.

  Act as if the grid is solvable, even if we think it isn't, just in case the
  contestant has a valid answer that we overlooked.

  Args:
    lines: Tokenized lines (either from our I/OGen's output or a contestant's
        attempt.
    case: A CaseInput representing a single test case.

  Returns:
    A tuple with these entries:
    1. One of _IMPOSSIBLE, _INCORRECT, or _POSSIBLE
    2. An error message (in the case of _INCORRECT)
  """

  header, row_lines = lines[0], lines[1:]

  # The header should be empty after TokenizeAndSplitCases.
  if header:
    return _INCORRECT, _BAD_HEADER_ERROR % header

  if len(row_lines) == 1 and row_lines[0] == ['impossible']:
    return _IMPOSSIBLE, None

  expected_rows = case.num_rows
  actual_rows = len(row_lines)
  if expected_rows != actual_rows:
    return _INCORRECT, _WRONG_NUM_ROWS_ERROR % (
        expected_rows, actual_rows)

  for row_num in xrange(actual_rows):
    row_line = row_lines[row_num]
    if len(row_line) != 1:
      return _INCORRECT, _WRONG_ROW_TOKENS_ERROR % (
          row_num+1, row_line)
    row = row_line[0]
    if len(row) != case.num_cols:
      return _INCORRECT, _WRONG_NUM_COLUMNS_ERROR % (
          case.num_cols, len(row), row_num + 1)
    for col_num in xrange(len(row)):
      if row[col_num] not in ['/', '\\']:
        return _INCORRECT, _INVALID_CHARACTER_ERROR % (
            row_num+1, col_num+1, row[col_num])

  grid_error = CheckGrid(row_lines, case)

  if grid_error:
    return _INCORRECT, grid_error
  else:
    return _POSSIBLE, None


def VerifyCase(output_lines, attempt_lines, case):
  """Checks a single test case.

  Args:
    output_lines: Tokenized lines from our I/OGen's output.
    attempt_lines: Tokenized lines from the contestant's attempt.
    case: A CaseInput representing a single test case.
  Returns:
    An error, or None if there is no error.
  """

  output_res, output_error = VerifyOutput(output_lines, case)
  attempt_res, attempt_error = VerifyOutput(attempt_lines, case)
  if attempt_res == _INCORRECT:
    return attempt_error
  if output_res == _INCORRECT:
    return _OUTPUT_BAD_GRID_ERROR % output_error
  if output_res == _IMPOSSIBLE:
    if attempt_res == _IMPOSSIBLE:
      return None
    else:
      return _OUTPUT_FALSE_NEGATIVE_ERROR
  else:
    if attempt_res == _IMPOSSIBLE:
      return _ATTEMPT_FALSE_NEGATIVE_ERROR
    else:
      return None


def FindError(unused_self, input_file, output_file, attempt):
  """See judge.Judge.FindError()."""
  input_cases = ParseInputFile(input_file)
  num_cases = len(input_cases)
  output, attempt, error = _utils_TokenizeAndSplitCases(
      output_file, attempt, num_cases)
  if error is not None:
    return error

  for case_num, (case, output_lines, attempt_lines) in enumerate(
      zip(input_cases, output, attempt), start=1):
    error = VerifyCase(output_lines, attempt_lines, case)
    if error is not None:
      return 'Case #%s: %s' % (case_num, error)

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
