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
"""A custom judge for the Minesweeper Hero problem."""

__author__ = "abednego@google.com (Igor Naverniouk)"




class Error(Exception):
  pass


def ParseInput(input_file):
  """Returns the list of (R, C, M) triples, one for each case.

  Args:
    input_file: entire contents of the input file

  Returns:
    A list of triples of integers.

  Raises:
    Error: if the input cannot be parsed.
  """
  input_lines = input_file.splitlines()
  if not input_lines: raise Error("The input file is empty")
  num_cases = int(input_lines[0])
  if len(input_lines) != 1 + num_cases:
    raise Error("The input data is wrong.")
  cases = []
  for line in input_lines[1:]:
    cases.append(tuple(map(int, line.split(" "))))
  return cases


def NeighborsOf(r, c, ui, uj):
  """Yields coordinates of neighbors of (ui, uj) on an r-by-c board.

  Args:
    r: number of rows of a grid
    c: number of columns of a grid
    ui: 0-based row index in the grid
    uj: 0-based column index in the grid

  Yields:
    Pairs of integers -- coordinates of neighboring cells in the grid.
  """
  for vi in xrange(max(0, ui - 1), min(ui + 2, r)):
    for vj in xrange(max(0, uj - 1), min(uj + 2, c)):
      if vi != ui or vj != uj: yield (vi, vj)


def CheckCase(r, c, m, is_possible, attempt):
  """Returns None if the output for this case is correct, or a str error.

  Args:
    r: number of rows
    c: number of columns
    m: number of mines
    is_possible: whether the case is solvable
    attempt: output lines

  Returns:
    None on success; a string on error.
  """
  # Deal with cases in which the contestant says "Impossible".
  if (len(attempt) == 2 and not attempt[0] and len(attempt[1]) == 1 and
      attempt[1][0] == "impossible"):
    if is_possible: return "Said 'Impossible' when a solution exists"
    return None

  # If the correct answer is "Impossible", let's check the output anyway.
  # We might catch a bug in the IO generator.

  # Check dimensions of 'attempt'.
  if len(attempt) != 1 + r:
    return "Output has %d rows instead of %d" % (len(attempt) - 1, r)
  if attempt[0]:
    return "Garbage on the Case line: %s" % str(attempt[0])
  for i in xrange(r):
    if len(attempt[1 + i]) != 1:
      return "Bad board line: %s" % " ".join(attempt[1 + i])
    if len(attempt[1 + i][0]) != c:
      return "Output has %d columns instead of %d" % (len(attempt[1 + i][0]), c)

  # Convert input into a boolean board, and get the click location.
  click_i, click_j = None, None
  is_mine = [[False] * c for _ in xrange(r)]
  mines_count = 0
  for i in xrange(r):
    for j in xrange(c):
      char = attempt[1 + i][0][j]
      if char == "*":
        mines_count += 1
        is_mine[i][j] = True
      elif char == "c":
        if click_i is not None: return "More than one 'c' character."
        click_i, click_j = i, j
      elif char == ".":
        pass
      else:
        return "Bad character: '%s'" % char
  if click_i is None or click_j is None: return "Board without 'c' character"
  if mines_count != m:
    return "Board contains %d mines instead of %d" % (mines_count, m)

  # For each cell, compute whether it has a neighboring mine.
  has_neighboring_mines = [[False] * c for _ in xrange(r)]
  for ui in xrange(r):
    for uj in xrange(c):
      for vi, vj in NeighborsOf(r, c, ui, uj):
        if is_mine[vi][vj]:
          has_neighboring_mines[ui][uj] = True
          break

  # Set up a BFS starting with the clicked location.
  seen = [[False] * c for _ in xrange(r)]
  seen[click_i][click_j] = True
  num_seen = 1
  q = []
  front = 0
  if not has_neighboring_mines[click_i][click_j]:
    q.append((click_i, click_j))

  # Run the BFS.
  while front < len(q):
    ui, uj = q[front]
    front += 1
    for vi, vj in NeighborsOf(r, c, ui, uj):
      if not seen[vi][vj]:
        seen[vi][vj] = True
        num_seen += 1
        if not has_neighboring_mines[vi][vj]: q.append((vi, vj))

  # If we failed to open the whole board, find an unopened cell.
  if num_seen + m != r * c:
    for i in xrange(r):
      for j in xrange(c):
        if not seen[i][j] and not is_mine[i][j]:
          return "Cell (%d, %d) left unopened" % (i, j)

  # Did we find an answer to a supposedly impossible case?
  if not is_possible:
    return "Bug in the IO generator: (%dx%d, %d) is solvable." % (r, c, m)

  return None


def FindError(_, input_file, output_file, attempt):
  """Returns None if the output is correct and a 'str' error otherwise.

  Makes strict assumptions about the formatting of input_file and output_file.

  Args:
    see judge.Judge.FindError().

  Returns:
    None on success; a string on error.
  """
  # Parse everything.
  try:
    cases = ParseInput(input_file)
  except Error as e:
    return "Error in IO generator: " + str(e)
  parsed_output, parsed_attempt, error = _utils_TokenizeAndSplitCases(
      output_file, attempt, len(cases))
  if error is not None:
    return "_utils_TokenizeAndSplitCases() found an error: %s" % error

  # Run a sanity check on the official output.
  for case_out in parsed_output:
    if len(case_out) < 2 or case_out[0] or len(case_out[1]) != 1:
      return "Error in IO generator: bad case output:\n%s" % str(case_out)

  # Validate case by case.
  for case in xrange(len(cases)):
    (r, c, m) = cases[case]
    is_possible = (parsed_output[case][1][0] != "impossible")
    error = CheckCase(r, c, m, is_possible, parsed_attempt[case])
    if error is not None:
      return "Error in case #%d: %s" % (case + 1, error)

  return None

import sys
if __name__ == "__main__":
  if sys.argv[1] == "-2":
    sys.exit(0)
  result = FindError(None,
                     file(sys.argv[1]).read(),
                     file(sys.argv[3]).read(),
                     file(sys.argv[2]).read())
  if result:
    print >> sys.stderr, result
    sys.exit(1)
