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
"""A custom judge for Raise the Roof."""


def Minus((px, py, pz), (qx, qy, qz)):
  return (px - qx, py - qy, pz - qz)


def Mult((x, y, z), scalar):
  return x * scalar, y * scalar, z * scalar


def Dot((px, py, pz), (qx, qy, qz)):
  return px * qx + py * qy + pz * qz


def Cross((px, py, pz), (qx, qy, qz)):
  return (py * qz - pz * qy,
          pz * qx - px * qz,
          px * qy - py * qx)


def GetPlaneNormal((p, q, r)):
  """Gets an upward pointing normal to the plane defined by 3 points."""
  normal = Cross(Minus(q, p), Minus(r, q))
  if Dot(normal, (0, 0, 1)) < 0: normal = Mult(normal, -1)
  return normal


def ParseInput(input_file):
  """Returns a list of lists of 3D points."""
  input_lines = input_file.splitlines()
  num_cases = int(input_lines[0].strip())
  cases = []
  next_line = 1
  for _ in xrange(num_cases):
    assert next_line < len(input_lines), "Not enough input cases"
    n = int(input_lines[next_line].strip())
    next_line += 1
    assert next_line + n <= len(input_lines), "Not enough points in input"
    case_lines = input_lines[next_line:next_line + n]
    next_line += n
    cases.append([map(int, line.split()) for line in case_lines])
  return cases


def ParseAttempt(n, attempt_lines):
  """Returns a list of integers."""
  assert len(attempt_lines) == 1, "Wrong number of output lines"
  assert len(attempt_lines[0]) == n, "Wrong number of points"
  ints = map(int, attempt_lines[0])
  assert len(set(ints)) == n, "Duplicate points"
  assert min(ints) == 1, "The smallest point should be 1"
  assert max(ints) == n, "The largest point should be %d" % n
  return [i - 1 for i in ints]


def JudgeCase(inp, attempt):
  """Judges a single case.

  Args:
    inp: a list of 3D points
    attempt: a permutation of n zero-based indices

  Returns:
    error string or None
  """
  pts = [inp[i] for i in attempt]
  n = len(pts)

  for i in xrange(3, n):
    normal = GetPlaneNormal(pts[i - 2:i + 1])
    for j in xrange(i - 2):
      if Dot(normal, Minus(pts[j], pts[i])) > 0:
        return "Roof #%d got lowered at column %d" % (i - 2, j)
      base_j = (pts[j][0], pts[j][1], 0)
      if Dot(normal, Minus(base_j, pts[i])) > 0:
        return "Roof #%d went under ground at %d" % (i - 2, j)

  return None


def FindError(unused_self, input_file, output_file, attempt):
  """Judges a contestant's output.

  Args:
    see judge.Judge.FindError().

  Returns:
    None on success; a string on error.
  """
  try:
    input_cases = ParseInput(input_file)
  except Exception as e:
    return "Error in I/O generator: %s" % str(e)

  _, attempt_cases, error = _utils_TokenizeAndSplitCases(
      output_file, attempt, len(input_cases))
  if error is not None: return error

  for tc in xrange(len(input_cases)):
    try:
      attempt = ParseAttempt(len(input_cases[tc]), attempt_cases[tc])
    except Exception as e:
      return "Error parsing attempt: %s" % str(e)
    error = JudgeCase(input_cases[tc], attempt)
    if error is not None:
      return "Case #%d: %s" % (tc + 1, error)

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
