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
"""A custom judge for Shoot the Aliens, Code Jam 2016."""

# pylint: disable=missing-docstring

__author__ = 'pokorski@google.com (Karol Pokorski)'

from collections import deque


FIRST_LINE_INPUT_ERROR = ('First line of input is not an integer '
                          '(should be amount of test cases).')
FIRST_LINE_CASE_INPUT_ERROR = ('First line of input test case is in '
                               'incorrect format. (should be w, h, r).')
BOARD_INPUT_ERROR = ('Format of board is incorrect (should be h x w array '
                     'of #, ., S and O chars).')
FATALITY_ERROR = 'JUDGE_ERROR! Something is broken! {0}'.format


def ParseInputFile(input_file):
  input_lines = _utils_Tokenize(input_file)
  pos_line = 0

  if len(input_lines[pos_line]) != 1: return FIRST_LINE_INPUT_ERROR
  try:
    num_cases = int(input_lines[pos_line][0])
    pos_line += 1
  except ValueError:
    return FIRST_LINE_INPUT_ERROR

  cases = []
  for i in xrange(num_cases):
    try:
      n, m, k = map(int, input_lines[pos_line])
      pos_line += 1
    except ValueError:
      return FIRST_LINE_CASE_INPUT_ERROR

    board = input_lines[pos_line : pos_line + m]
    if len(board) != m: return BOARD_INPUT_ERROR
    for board_line in board:
      if len(board_line) != 1:
        return BOARD_INPUT_ERROR
    board = [board_line[0] for board_line in board]
    for board_line in board:
      if len(board_line) != n: return BOARD_INPUT_ERROR
      for board_char in board_line:
        if board_char not in '#.ST': return BOARD_INPUT_ERROR
    pos_line += m

    soldiers, outposts = [], []
    for i in xrange(m):
      for j in xrange(n):
        if board[i][j] == 'S': soldiers.append((i, j))
        if board[i][j] == 'T': outposts.append((i, j))

    cases.append((n, m, k, board, soldiers, outposts))
  return cases


def Inside(x, y, w, h):
  return (0 <= x < w) and (0 <= y < h)


def FillToSides(m, h, w, i, j, delta, wall):
  dd = ((-1, 0), (1, 0), (0, -1), (0, 1))
  m[i][j] += delta
  for di, dj in dd:
    ni, nj = i + di, j + dj
    while Inside(ni, nj, h, w) and m[ni][nj] != wall:
      m[ni][nj] += delta
      ni += di
      nj += dj


def VerifyOutput(output, case):
  w, h, k, board, sold, outp = case

  if (not output) or (len(output[0]) != 1):
    return 'Incorrect format of output first line.'
  try:
    result = int(output[0][0])
  except ValueError:
    return 'Incorrect format of output first line.'

  if len(output) != result + 1:
    return ('Incorrect format of output. '
            '(amount of lines does not match claimed result)')

  try:
    matching = [map(int, line) for line in output[1:]]
  except ValueError:
    return 'Incorrect format of output. (soldier/outpost not an integer).'

  sold_matched, outp_matched = [], []
  for i in xrange(len(matching)):
    line = matching[i]
    if len(line) != 2:
      return ('Incorrect format of output. '
              '(soldiers/outposts matching line length)')
    if not (1 <= line[0] <= len(sold) and 1 <= line[1] <= len(outp)):
      return ('Incorrect format of output. '
              '(soldiers/outposts matching out of range)')
    line[0] -= 1
    line[1] -= 1
    sold_matched.append(line[0])
    outp_matched.append(line[1])

  if len(set(sold_matched)) != result:
    return 'Incorrect format of output. (output soldiers not distinct)'
  if len(set(outp_matched)) != result:
    return 'Incorrect format of output. (output outposts not distinct)'

  # We put timestamps in the board to avoid resetting. <= current_ts means
  # empty space. current_ts + d < current_ts + ts_offset means distance d
  # in current BFS. current_ts = current_ts + ts_offset - 1 means current
  # destination. >= current_ts + ts_offset means wall. Each turn we increase
  # current_ts by ts_offset, so all cells used during BFS and killed turret
  # become empty space.
  ts_offset = (w + 2) * (h + 2) + 3
  wall = ts_offset * (len(sold_matched) + 2) + 3

  # The timestamp of last visit to this cell, or "wall" for walls.
  m = [[0] * w for _ in xrange(h)]
  # The number of alive turrets covering this cell, or "wall" for walls.
  hit_count = [[0] * w for _ in xrange(h)]
  # Temporary array containing 1 for cells covered by the turret we're trying
  # to destroy, "wall" for walls, and 0 otherwise.
  current_dest = [[0] * w for _ in xrange(h)]

  for i in xrange(h):
    for j in xrange(w):
      if board[i][j] == '#':
        m[i][j] = wall
        hit_count[i][j] = wall
        current_dest[i][j] = wall

  for i, j in outp:
    FillToSides(hit_count, h, w, i, j, 1, wall)

  current_ts = 1
  for soldier, outpost in matching:
    ti, tj = outp[outpost]
    found = False
    limit = current_ts + k
    FillToSides(current_dest, h, w, ti, tj, 1, wall)
    que = deque()
    que.append(sold[soldier])
    si, sj = sold[soldier]
    m[si][sj] = current_ts
    while que:
      i, j = que.popleft()
      # If we can hit the turret, we're done
      if current_dest[i][j] == 1:
        found = True
        break
      # If this position is covered by at least one alive turret, we can't
      # move further.
      if hit_count[i][j] > 0:
        continue
      d = m[i][j]
      # If we already spent all our moves, we can't move further.
      if d >= limit:
        continue
      if i < h - 1:
        ni, nj = i + 1, j
        if m[ni][nj] < current_ts:
          m[ni][nj] = d + 1
          que.append((ni, nj))
      if i > 0:
        ni, nj = i - 1, j
        if m[ni][nj] < current_ts:
          m[ni][nj] = d + 1
          que.append((ni, nj))
      if j < w - 1:
        ni, nj = i, j + 1
        if m[ni][nj] < current_ts:
          m[ni][nj] = d + 1
          que.append((ni, nj))
      if j > 0:
        ni, nj = i, j - 1
        if m[ni][nj] < current_ts:
          m[ni][nj] = d + 1
          que.append((ni, nj))

    if not found:
      return ('Solution is wrong. (soldier %d cannot reach outpost %d)' %
              (soldier+1, outpost+1))
    current_ts += ts_offset
    # Incrementally update the arrays to avoid incurring a quadratic time
    # for resetting them from scratch.
    FillToSides(current_dest, h, w, ti, tj, -1, wall)
    FillToSides(hit_count, h, w, ti, tj, -1, wall)

  return None


def VerifyCase(output, attempt, case):
  # output_error = VerifyOutput(output, case)
  # if output_error is not None:
  #   return FATALITY_ERROR('Our output is incorrect. ' + output_error)
  attempt_error = VerifyOutput(attempt, case)
  if attempt_error is not None: return attempt_error
  if int(attempt[0][0]) > int(output[0][0]):
    return FATALITY_ERROR('Our output is not optimal. [%d vs %d]'
                          % (int(attempt[0][0]), int(output[0][0])))
  if int(attempt[0][0]) < int(output[0][0]):
    return 'Solution not optimal. [%d vs %d]' % (int(attempt[0][0]),
                                                 int(output[0][0]))
  return None


def FindError(unused_self, input_file, output_file, attempt_file):
  input_cases = ParseInputFile(input_file)
  if type(input_cases) is str:
    return input_cases

  num_cases = len(input_cases)
  output, attempt, error = _utils_TokenizeAndSplitCases(
      output_file, attempt_file, num_cases)
  if error is not None:
    return error

  for case_num, (case, o, a) in enumerate(zip(input_cases, output, attempt),
                                          start=1):
    error = VerifyCase(o, a, case)
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
