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
"""A custom judge for 'Map Reduce', Code Jam 2016."""

__author__ = 'alextrovert@google.com (Alex Li)'

import collections



# The various errors we can return.
_BAD_HEADER_ERROR = 'Incorrect number of tokens, or wrong data, in header.'
_BAD_LINE_ERROR = 'Wrong number of tokens / length / characters in output line.'
_BAD_OUTPUT_ERROR = 'Our output is incorrect!'
_FALSE_NEGATIVE_ERROR = 'Got IMPOSSIBLE when answer exists.'
_FALSE_POSITIVE_ERROR = 'Attempt is made on IMPOSSIBLE case.'
_INVALID_GRID_ERROR = 'The grid is invalid or not "good": {}'.format
_SHORTEST_PATH_NOT_EXACTLY_D = 'Expected {} for shortest path, got {}.'.format


class _CaseInput(collections.namedtuple('_CaseInput', ('r', 'c', 'd', 'grid'))):
  """Parsed information for a single test case.

  Attributes:
    r: The R parameter (number of grid rows) for the test case.
    c: The C parameter (number of grid columns) for the test case.
    d: The D parameter (target distance for shortest path) for the test case.
    grid: The input grid as a list with R strings of length C.
  """


def _ParseInputFile(input_file):
  """Turns an input file of test cases into a list of _CaseInputs."""
  lines = input_file.splitlines()
  num_cases = int(lines[0])
  result = []
  line_idx = 1
  for _ in xrange(num_cases):
    r, c, d = map(int, lines[line_idx].split())
    line_idx += 1
    # Convert S and F to lowercase because the output we compare with later will
    # already be lowered by TokenizeAndSplitCases.
    result.append(_CaseInput(r, c, d, [s.lower() for s in
                                       lines[line_idx : line_idx + r]]))
    line_idx += r
  return result


def _VerifyPossibleOutput(lines, case):
  """Checks the output for a single test case which is NOT impossible.

  Args:
    lines: Tokenized lines (either from our I/OGen's output or a contestant's
        attempt).
    case: A _CaseInput representing a single test case.
  Returns:
    An error, or None if there is no error.
  """
  DOT, HASH, S, F = map(ord, '.#sf')

  if len(lines) - 1 != case.r:
    return _INVALID_GRID_ERROR('Expected {} rows of grid, got {}.'
                               .format(case.r, len(lines) - 1))
  case_grid = [map(ord, row) for row in case.grid]
  grid = []
  dot_count = 0
  for i in xrange(1, len(lines)):
    if len(lines[i]) != 1:
      return _BAD_LINE_ERROR  # line should be a continuous string
    row = lines[i][0]
    if len(row) != case.c:
      return _INVALID_GRID_ERROR('Expected {} characters per row, got {}.'
                                 .format(case.c, len(row)))
    dot_count += row.count('.')
    grid.append(map(ord, row))

  # Verify that the grid is identical to the input, except that walls in the
  # input grid may be changed to spaces.
  for i in xrange(case.r):
    for j in xrange(case.c):
      if grid[i][j] != case_grid[i][j]:
        if not (grid[i][j] == DOT and case_grid[i][j] == HASH):
          return _INVALID_GRID_ERROR('Invalid grid characters or wall removal.')

  # Check that the grid is bordered by walls.
  for i in xrange(case.r):
    if grid[i][0] != HASH or grid[i][-1] != HASH:
      return _INVALID_GRID_ERROR('Borders must consist of "#" only.')
  if grid[0] != [HASH] * case.c or grid[-1] != [HASH] * case.c:
    return _INVALID_GRID_ERROR('Borders must consist of "#" only.')

  # Check every 2x2 square to make sure walls meet at edges, not corners.
  for i in xrange(case.r - 1):
    for j in xrange(case.c - 1):
      tl, tr, bl, br = grid[i][j], grid[i][j+1], grid[i+1][j], grid[i+1][j+1]
      if ((tl == HASH and br == HASH and tr != HASH and bl != HASH) or
          (tr == HASH and bl == HASH and tl != HASH and br != HASH)):
        return _INVALID_GRID_ERROR('Walls cannot meet at corners.')

  # Breadth first search to find the shortest path and to check if all empty
  # cells are reachable from each other.
  q = collections.deque()
  for i in xrange(case.r):
    for j in xrange(case.c):
      if grid[i][j] == S:
        q.append((i, j, 0))
        break
    if q: break
  num_visited = 0
  mindist = -1
  while q:
    i, j, d = q.popleft()
    if grid[i][j] == HASH:
      continue
    if grid[i][j] == F:
      mindist = d  # Don't break because we still want to check dot_count.
    grid[i][j] = HASH
    num_visited += 1
    if grid[i - 1][j] != HASH: q.append((i - 1, j, d + 1))
    if grid[i + 1][j] != HASH: q.append((i + 1, j, d + 1))
    if grid[i][j - 1] != HASH: q.append((i, j - 1, d + 1))
    if grid[i][j + 1] != HASH: q.append((i, j + 1, d + 1))

  # Check that all non-wall cells are in the same component.
  if num_visited != 2 + dot_count:
    return _INVALID_GRID_ERROR('Not all empty cells are in the same component.')
  # Check that the shortest path is as expected.
  if mindist != case.d:
    return _SHORTEST_PATH_NOT_EXACTLY_D(case.d, mindist)
  return None


def _VerifyCase(output_lines, attempt_lines, case):
  """Checks a single test case.

  Args:
    output_lines: Tokenized lines from our I/OGen's output.
    attempt_lines: Tokenized lines from the contestant's attempt.
    case: A _CaseInput representing a single test case.
  Returns:
    An error, or None if there is no error.
  """
  output_header = output_lines[0]
  attempt_header = attempt_lines[0]
  # After processing by TokenizeAndSplitCases, the header should have only one
  # token: either 'possible' or 'impossible'. They are lowercased here because
  # the output text has been lowercased by TokenizeAndSplitCases.
  if len(output_header) != 1 or (output_header[0] not in
                                 {'possible', 'impossible'}):
    return _BAD_OUTPUT_ERROR
  if len(attempt_header) != 1 or (attempt_header[0] not in
                                  {'possible', 'impossible'}):
    return _BAD_HEADER_ERROR

  output_impossible = (output_header[0] == 'impossible')
  attempt_impossible = (attempt_header[0] == 'impossible')

  if output_impossible:
    if attempt_impossible:
      return None
    # Even if the I/OGen output claims "impossible", we'll give the contestant
    # the benefit of the doubt and try to verify their attempt. If the attempt
    # is actually valid, then our output must be bad, and we'll still give the
    # contestant an AC. Unfortunately, there's no way here for us to report
    # _BAD_OUTPUT_ERROR since we are obligated to return None to let them pass.
    attempt_error = _VerifyPossibleOutput(attempt_lines, case)
    if attempt_error is not None:
      return _FALSE_POSITIVE_ERROR
    return None

  if attempt_impossible:
    # We'll give the contestant the benefit of the doubt, making sure that the
    # I/OGen output is actually valid before declaring that the contestant's
    # "impossible" claim is wrong.
    output_error = _VerifyPossibleOutput(output_lines, case)
    if output_error is None:
      return _FALSE_NEGATIVE_ERROR
    return None

  attempt_error = _VerifyPossibleOutput(attempt_lines, case)
  return attempt_error


def FindError(unused_self, input_file, output_file, attempt):
  """See judge.Judge.FindError()."""
  input_cases = _ParseInputFile(input_file)
  output, attempt, error = _utils_TokenizeAndSplitCases(
      output_file, attempt, len(input_cases))
  if error is not None:
    return error
  for case_num, (case, output_lines, attempt_lines) in enumerate(
      zip(input_cases, output, attempt), start=1):
    error = _VerifyCase(output_lines, attempt_lines, case)
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
