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
"""Custom judge for Spanning Planning, Code Jam 2017."""




MIN_VERTICES = 2
MAX_VERTICES = 22

# We do all computations modulo this prime number.
# It's more than 22**20, the largest possible number of spanning trees for a
# graph with not more than 22 vertices. Just to be safe, it's more than 2*22**20
# (so even if we mess the sign up we can't get a coincidental match).
_MODULO = 1410858997372808088415895579

# The various errors we can return.
_WRONG_CHARACTER = 'Expected 0 or 1, found {0}'.format
_EMPTY_OUTPUT = 'Empty output'
_EXPECTED_EXACTLY_ONE_TOKEN = 'Expected exactly one token on each output line'
_GRAPH_HAS_LOOP = 'The graph has a loop'
_MATRIX_NOT_SYMMETRIC = 'The matrix is not symmetric'
_WRONG_NUMBER_OF_VERTICES = 'Wrong number of vertices: {0}'.format
_WRONG_AMOUNT_OF_LINES = (
    'Number of lines in output does not match the number of vertices')
_WRONG_LINE_LENGTH = (
    'The length of a line in output does not match the number of vertices')
_WRONG_ANSWER = (
    'The number of spanning trees wrong: expected {0}, found {1}'
    .format)


def PowModulo(a, k):
  """Finds a**k modulo _MODULO."""
  if k == 0:
    return 1
  if k % 2 == 0:
    return PowModulo(a * a % _MODULO, k / 2)
  return a * PowModulo(a, k - 1) % _MODULO


def DeterminantModulo(matrix):
  """Finds determinant of the given matrix modulo _MODULO."""
  n = len(matrix)
  multiplier = 1
  for i in xrange(n):
    nonzero = -1
    for k in xrange(i, n):
      if matrix[k][i] != 0:
        nonzero = k
        break
    if nonzero < 0:
      return 0
    if nonzero > i:
      matrix[i], matrix[nonzero] = matrix[nonzero], matrix[i]
      multiplier = (_MODULO - multiplier) % _MODULO
    assert 0 < matrix[i][i] < _MODULO
    multiplier = (multiplier * matrix[i][i]) % _MODULO
    inverse = PowModulo(matrix[i][i], _MODULO - 2)
    for j in xrange(i, n):
      matrix[i][j] = (matrix[i][j] * inverse) % _MODULO
    assert matrix[i][i] == 1
    for k in xrange(i + 1, n):
      by = _MODULO - matrix[k][i]
      for j in xrange(n):
        matrix[k][j] = (matrix[k][j] + by * matrix[i][j]) % _MODULO
      assert matrix[k][i] == 0
  return multiplier


def ParseInputFile(input_file):
  """Turns an input file into a list of integers - case inputs."""
  input_lines = _utils_Tokenize(input_file)
  return [int(k) for (k,) in input_lines[1:1 + int(input_lines[0][0])]]


def VerifyCase(unused_output_lines, lines, case):
  """Checks a single test case.

  Args:
    unused_output_lines: Tokenized lines from our I/OGen's output. Not used.
        We don't check our reference output for correctness to avoid making
        the judge 2x slower here.
    lines: Tokenized lines from the contestant's attempt.
    case: An int representing a single test case.
  Returns:
    An error, or None if there is no error.
  """
  if any(len(line) != 1 for line in lines):
    return _EXPECTED_EXACTLY_ONE_TOKEN
  if not lines:
    # I think this never happens, because the line after "Case #1:" is always
    # returned, but is it guaranteed by py?..
    return _EMPTY_OUTPUT
  n = _utils_ToInteger(
      lines[0][0], minimum_value=MIN_VERTICES, maximum_value=MAX_VERTICES)
  if n is None:
    return _WRONG_NUMBER_OF_VERTICES(lines[0][0])
  if len(lines) != n + 1:
    return _WRONG_AMOUNT_OF_LINES
  matrix = [[0] * n for _ in xrange(n)]
  for i in xrange(n):
    token = lines[i + 1][0]
    if len(token) != n:
      return _WRONG_LINE_LENGTH
    for j in xrange(n):
      if token[j] != '0' and token[j] != '1':
        return _WRONG_CHARACTER(token[j])
      if token[j] == '1':
        if i == j:
          return _GRAPH_HAS_LOOP
        matrix[i][j] = _MODULO - 1
        matrix[i][i] += 1
  for i in xrange(n):
    for j in xrange(n):
      if matrix[i][j] != matrix[j][i]:
        return _MATRIX_NOT_SYMMETRIC
  number_of_trees = DeterminantModulo([row[1:] for row in matrix[1:]])
  if number_of_trees != case:
    return _WRONG_ANSWER(case, number_of_trees)
  return None


def FindError(unused_self, input_file, output_file, attempt):
  """See judge.Judge.FindError()."""
  input_cases = ParseInputFile(input_file)
  num_cases = len(input_cases)
  output, attempt, error = _utils_TokenizeAndSplitCases(output_file, attempt,
                                                       num_cases)
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
