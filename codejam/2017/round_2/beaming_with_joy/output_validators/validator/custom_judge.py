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
"""Custom judge for Beaming With Joy, Code Jam 2017."""

__author__ = 'tullis@google.com (Ian Tullis)'



# The various errors we can return.
_ATTEMPT_FALSE_NEGATIVE_ERROR = 'Got IMPOSSIBLE when answer exists.'
_BAD_CHANGE_ERROR = 'Illegal change to original grid.'
_BAD_HEADER_ERROR = 'Missing header, or extra tokens or wrong word in header.'
_BAD_OUTPUT_ERROR = 'Our output is incorrect: {}'.format
_GRID_FOR_IMPOSSIBLE_ERROR = 'Gave a grid after answering IMPOSSIBLE.'
_HIT_SHOOTER_ERROR = (
    'Beam starting from {} side of ({}, {}) hits a shooter'.format)
_MISSED_EMPTY_CELLS_ERROR = 'Missed at least one empty cell: {}'.format
_OUTPUT_FALSE_NEGATIVE_ERROR = 'Attempt grid is correct for IMPOSSIBLE case.'
_WRONG_DIMENSIONS_ERROR = 'Grid dimensions are wrong, or extra tokens in grid'

# Constants for use in VerifyOutput and VerifyCase.
# These classify answers to test cases, which may come from our own I/OGen or
# from contestants.
_IMPOSSIBLE = 0  # The given answer is "IMPOSSIBLE".
_INCORRECT = 1  # An answer is claimed, but is incorrect.
_POSSIBLE = 2  # An answer is claimed, and is correct.

# Code for when a beam hits a beam shooter.
_HIT_SHOOTER = 'kaboom!'


def ParseInputFile(input_file):
  """Turns an input file into a list of grids."""
  input_lines = _utils_Tokenize(input_file)[1:]  # Skip the number of cases.
  cases = []
  while input_lines:
    r, _ = map(int, input_lines.pop(0))
    cases.append([input_lines.pop(0)[0] for _ in xrange(r)])
  return cases


def _TraceBeam(grid, rr, cc, entry_side):
  """Follows one beam through the grid.

  Args:
    grid: The grid in which the beam travels.
    rr: The row of the cell in which the beam originates.
    cc: The column of the cell in which the beam originates.
    entry_side: The border of the cell in which the beam originates:
      'T' (top), 'R' (right), 'B' (bottom), or 'L' (left).

  Returns:
    A list of the empty cells the beam travels through. If the beam hits a
      beam shooter, it will end with _HIT_SHOOTER.
  """
  path = []
  while True:
    if (rr < 0 or rr >= len(grid) or cc < 0 or cc >= len(grid[0])
        or grid[rr][cc] == '#'):
      break
    if grid[rr][cc] in '|-':  # hit another shooter!
      path += [_HIT_SHOOTER]
      break
    if grid[rr][cc] == '/':
      rr = {'T': rr, 'R': rr + 1, 'B': rr, 'L': rr - 1}[entry_side]
      cc = {'T': cc - 1, 'R': cc, 'B': cc + 1, 'L': cc}[entry_side]
      entry_side = {'T': 'R', 'R': 'T', 'B': 'L', 'L': 'B'}[entry_side]
    elif grid[rr][cc] == '\\':
      rr = {'T': rr, 'R': rr - 1, 'B': rr, 'L': rr + 1}[entry_side]
      cc = {'T': cc + 1, 'R': cc, 'B': cc - 1, 'L': cc}[entry_side]
      entry_side = {'T': 'L', 'R': 'B', 'B': 'R', 'L': 'T'}[entry_side]
    else:  # empty cell
      path += [(rr, cc)]
      rr = {'T': rr + 1, 'R': rr, 'B': rr - 1, 'L': rr}[entry_side]
      cc = {'T': cc, 'R': cc - 1, 'B': cc, 'L': cc + 1}[entry_side]
  return path


def _CheckGrid(grid):
  """Determines whether a grid obeys the rules.

  Args:
    grid: A grid (which could be ours or the contestant's)

  Returns:
    A tuple (bool, string): whether or not the grid is valid, and an error
      string if the grid is not valid.
  """
  r = len(grid)
  c = len(grid[0])
  # Make one pass to find all the shooters and empty cells.
  shooter_locs = []
  empty_cells_set = set()
  for rr in xrange(r):
    for cc in xrange(c):
      if grid[rr][cc] in '|-':
        shooter_locs.append((rr, cc))
      elif grid[rr][cc] == '.':
        empty_cells_set.add((rr, cc))
  seen_empty_cells_set = set()
  for rr, cc in shooter_locs:
    if grid[rr][cc] == '|':
      args = ((rr - 1, cc, 'B'), (rr + 1, cc, 'T'))
    else:
      args = ((rr, cc - 1, 'R'), (rr, cc + 1, 'L'))
    for rr_arg, cc_arg, es_arg in args:
      result = _TraceBeam(grid, rr_arg, cc_arg, es_arg)
      if result and result[-1] == _HIT_SHOOTER:
        return False, _HIT_SHOOTER_ERROR(es_arg, rr_arg, cc_arg)
      seen_empty_cells_set |= set(result)
  missed_empty_cells = empty_cells_set - seen_empty_cells_set
  if missed_empty_cells:
    # This list could be huge, so just return one example. Sort to ensure
    # consistent behavior for the tests.
    return False, _MISSED_EMPTY_CELLS_ERROR(sorted(missed_empty_cells)[0])
  else:
    return True, None


def VerifyOutput(lines, old_grid):
  """Checks the output for a single test case.

  Act as if the grid is solvable, even if we think it isn't, just in case the
  contestant has a valid answer that we overlooked.

  Args:
    lines: Tokenized lines (either from our I/OGen's output or a contestant's
        attempt.)
    old_grid: The original grid from a single test case.

  Returns:
    A tuple with these entries:
    1. One of _IMPOSSIBLE, _INCORRECT, or _POSSIBLE
    2. An error message (in the case of _INCORRECT)
  """

  header, row_lines = lines[0], lines[1:]
  if (not header) or len(header) != 1:
    return _INCORRECT, _BAD_HEADER_ERROR

  if header[0] == 'impossible':
    if row_lines:
      return _INCORRECT, _GRID_FOR_IMPOSSIBLE_ERROR
    return _IMPOSSIBLE, None
  elif header[0] != 'possible':
    return _INCORRECT, _BAD_HEADER_ERROR

  num_rows = len(old_grid)
  if len(row_lines) != num_rows:
    return _INCORRECT, _WRONG_DIMENSIONS_ERROR
  num_cols = len(old_grid[0])

  new_grid = []
  for row_num in xrange(num_rows):
    row_line = row_lines[row_num]
    if len(row_line) != 1:
      return _INCORRECT, _WRONG_DIMENSIONS_ERROR
    row = row_line[0]
    if len(row) != num_cols:
      return _INCORRECT, _WRONG_DIMENSIONS_ERROR
    for col_num in xrange(num_cols):
      old_char = old_grid[row_num][col_num]
      new_char = row[col_num]
      if old_char != new_char:
        if ((old_char == '-' and new_char == '|') or
            (old_char == '|' and new_char == '-')):
          continue
        return _INCORRECT, _BAD_CHANGE_ERROR
    new_grid.append(row)

  ok, err = _CheckGrid(new_grid)
  if not ok:
    return _INCORRECT, err
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
    return _BAD_OUTPUT_ERROR(output_error)
  if output_res == _IMPOSSIBLE:
    return None if attempt_res == _IMPOSSIBLE else _OUTPUT_FALSE_NEGATIVE_ERROR
  else:
    return (
        _ATTEMPT_FALSE_NEGATIVE_ERROR if attempt_res == _IMPOSSIBLE else None)


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
      return 'Case #{}: {}'.format(case_num, error)

  # Everything passes.
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
