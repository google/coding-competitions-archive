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
"""Custom judge for X Marks the Spot."""

__author__ = 'tomek@google.com (Tomek Czajka)'

import re



MAX_PRECISION = 9
SCALE = 10 ** MAX_PRECISION
MAX_COORDINATE = 10**9 * SCALE


def Plus(p, q):
  """Vector addition."""
  return (p[0] + q[0], p[1] + q[1])


def Minus(p, q):
  """Vector subtraction."""
  return (p[0] - q[0], p[1] - q[1])


def CrossProduct(p, q):
  """Vector cross product."""
  return p[0] * q[1] - p[1] * q[0]


def Rotate90(p):
  """Rotate a vector by 90 degrees counter-clockwise."""
  return (-p[1], p[0])


class AttemptFailedException(Exception):
  pass


def Quadrant(p, a, b, c):
  """Compute quadrant of p.

  Args:
    p: a point
    a: center of the X
    b: a point on one of the arms of the X
    c: a point on the other arm of the X
  Returns:
    0 to 3
  Raises:
    AttemptFailedException: if p lies on the X
  """
  cp1 = CrossProduct(Minus(b, a), Minus(p, a))
  cp2 = CrossProduct(Minus(c, a), Minus(p, a))
  if cp1 == 0 or cp2 == 0:
    raise AttemptFailedException('%s lies on the X' % (p,))
  return 2 * (cp1 < 0) + (cp2 < 0)


FIXED_POINT_RE = re.compile(r'^(-)?(\d*)(\.(\d*))?$')


def ParseFixedPoint(s):
  """Parse a decimal number.

  Args:
    s: str
  Returns:
    parsed number * SCALE
  Raises:
    AttemptFailedException: if s doesn't parse
  """
  match = FIXED_POINT_RE.match(s)
  if not match:
    raise AttemptFailedException('Number does not parse: %s' % s)
  minus_sign, integral, fractional = match.group(1, 2, 4)
  if not integral and not fractional:
    raise AttemptFailedException('Number does not parse: %s' % s)
  if not integral: integral = '0'
  if not fractional: fractional = ''
  if len(fractional) > MAX_PRECISION:
    raise AttemptFailedException('Too many digits of precision in %s' % s)
  fractional = (fractional + MAX_PRECISION * '0')[:MAX_PRECISION]
  value = int(integral) * SCALE + int(fractional)
  if value > MAX_COORDINATE:
    raise AttemptFailedException('Out of range: %s' % s)
  if minus_sign:
    value = -value
  return value


def ParseInput(input_file):
  """Parse input.

  Args:
    input_file: str
  Returns:
    list of list of (int, int)
  """
  lines = input_file.splitlines()
  ntc = int(lines[0])
  test_cases = []
  index = 1
  for _ in xrange(ntc):
    n = int(lines[index])
    index += 1
    test_case = []
    for _ in xrange(4 * n):
      x, y = map(int, lines[index].split())
      index += 1
      test_case.append((x, y))
    test_cases.append(test_case)
  return test_cases


def JudgeCase(test_case, attempt):
  """Judge a single test case.

  Args:
    test_case: list of points
    attempt: list of lists of strings (tokens)
  Raises:
    AttemptFailedException: if attempt is wrong
  """
  if len(attempt) != 1:
    raise AttemptFailedException('Expected 1 line, got %d lines' % len(attempt))
  if len(attempt[0]) != 4:
    raise AttemptFailedException(
        'Expected 4 tokens, got %d tokens' % len(attempt[0]))
  coords = map(ParseFixedPoint, attempt[0])
  points = [(x * SCALE, y * SCALE) for (x, y) in test_case]
  a = (coords[0], coords[1])
  b = (coords[2], coords[3])
  if a == b:
    raise AttemptFailedException('Output points coincide')
  c = Plus(a, Rotate90(Minus(b, a)))
  # the cross lines are a-b, a-c
  quadrant_counts = [0, 0, 0, 0]
  for p in points:
    q = Quadrant(p, a, b, c)
    quadrant_counts[q] += 1
  for qc in quadrant_counts:
    if 4 * qc != len(points):
      raise AttemptFailedException(
          'Unequal split: %d out of %d' % (qc, len(points)))
  # Success!


def FindError(unused_self, input_file, output_file, attempt):
  """Judges an attempt.

  Args:
    input_file: input
    output_file: must have the right number of test cases, but contents
      are ignored
    attempt: solution attempt
  Returns:
    None if the attempt is correct or a str error otherwise.
  """
  input_cases = ParseInput(input_file)
  unused_output_cases, attempt_cases, error = _utils_TokenizeAndSplitCases(
      output_file, attempt, len(input_cases))
  if error is not None: return error
  for tc in xrange(len(input_cases)):
    try:
      JudgeCase(input_cases[tc], attempt_cases[tc])
    except AttemptFailedException as e:
      return 'Case #%d: %s' % (tc + 1, e.message)
  return None  # Huge success!

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
