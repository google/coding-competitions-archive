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
"""A custom judge for "Linear AB", Code Jam 2016.

Problem statement:
//recruiting/contest_data/codejam/gcj_2016/linear_ab/statement.html
"""



# The various errors we can return.
# (Incorrect) Can't determine if the original pattern has both an A and a B
EMPTY_LINE = 'Empty line after case #'
INCONCLUSIVE = 'Cannot know whether original pattern has gold'
INVALID_NUM_TILES = ('Invalid number of tiles restored: {}, '
                     'should be between 1 and {}.'.format)
INVALID_TILE_NUMBER = (
    'Invalid tile number: {}, should be between 1 and {}.'.format)
REPEATED_TILE = 'Tile occurs more than once: {}.'.format
WRONG_NUM_LINES = (
    'Wrong number of lines of output: {}, expected 1.'.format)


def ParseInputFile(input_file):
  """Parses an input text into individual text cases.

  Assumes that the input text is valid according to the problem statement.

  Args:
    input_file: str, the raw contents of an input text file.

  Returns:
    A list of (K, R, X) tuples for each test case.
  """
  input_lines = _utils_Tokenize(input_file)
  # Skip the first line, which is just the number of test cases.
  return [tuple(int(val) for val in line) for line in input_lines[1:]]


def ParseAttempt(case, attempt):
  """Parses a contestant's output for a given input case.

  See the 'Output' section of the problem statement for details.

  Args:
    case: A (K, C, S) tuple defining the inputs for a single test case.
    attempt: Tokenized lines from the contestant's attempt for this case.

  Returns:
    A pair (tiles, error). If the contestant's output doesn't fit the expected
    syntax, error will be an error string. Otherwise, error will be None and
    tiles will be a set of ints or None if their output was IMPOSSIBLE.
  """
  k, c, s = case
  final_art_length = k ** c

  # Note: the "Case #x:" has been stripped away by TokenizeAndSplitCases.
  if len(attempt) != 1:
    # Note: the error message might not exactly match the first line of the
    # contestant's output (e.g. since the tokenizer lowercases the input).
    return None, WRONG_NUM_LINES(len(attempt))

  line = attempt[0]

  if len(line) < 1:
    return None, EMPTY_LINE

  if len(line) == 1 and line[0] == 'impossible':
    return set(), None

  num_tiles = len(line)
  if not 1 <= num_tiles <= s:
    return None, INVALID_NUM_TILES(num_tiles, s)

  tiles = set()
  for tile_str in line:
    try:
      tile = int(tile_str)
    except ValueError:
      tile = 0
    if not 1 <= tile <= final_art_length:
      return None, INVALID_TILE_NUMBER(tile_str, final_art_length)
    if tile in tiles:
      return None, REPEATED_TILE(tile)
    tiles.add(tile)
  return tiles, None


def TileInfluence(n, k, c):
  """Gives the indices of all original tiles that influence tile n.

  Args:
    n: int, the index of the tile (counting from 1) to check.
    k: int, the length of the original pattern.
    c: int, the complexity, as in the input.

  Returns:
    A list of ints with the indices of all original tiles that influence tile
    n after r rounds.
  """
  n -= 1  # Zero-index the tile number.
  influence = set()
  for _ in xrange(c):
    influence.add((n % k) + 1)
    n //= k
  return influence


def CheckCorrectness(case, tiles):
  """Checks if a parsed solution tiles is a correct solution of case.

  Args:
    case: tuple of ints
        A (K, C, S) tuple defining the inputs for a single test case.
    tiles: list of (char, int) tuples
        Tiles that have been chosen to restore, given as (artist, index) tuples.

  Returns:
    A boolean saying if tiles is a correct solution according to the problem
    statement.
  """
  k, c, s = case

  if not tiles:
    return s * c < k

  # this is checked at parsing time for efficiency so it should never happen
  # here, but just in case.
  if len(tiles) > s:
    return False

  indices = set()
  for tile in tiles:
    indices.update(TileInfluence(tile, k, c))

  # notice that we don't check if we believe this case is impossible, if they
  # have all the indices, fine.
  return len(indices) == k


def VerifyCase(case, attempt):
  """Checks a single test case.

  Args:
    case: tuple of ints
      A (K, C, S) tuple defining the inputs for a single test case.
    attempt: list of list of str
      Tokenized lines from the contestant's attempt for this case.

  Returns:
    An error string, or None if there is no error.
  """
  tiles, error = ParseAttempt(case, attempt)
  if error:
    return error
  if not CheckCorrectness(case, tiles):
    return INCONCLUSIVE
  return None


def FindError(unused_self, input_file, output_file, attempt):
  """See judge.Judge.FindError()."""
  input_cases = ParseInputFile(input_file)

  _, attempt, error = _utils_TokenizeAndSplitCases(output_file, attempt,
                                                  len(input_cases))
  if error:
    return error

  for case_num, (input_case, attempt_lines) in enumerate(
      zip(input_cases, attempt),
      start=1):
    error = VerifyCase(input_case, attempt_lines)
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
