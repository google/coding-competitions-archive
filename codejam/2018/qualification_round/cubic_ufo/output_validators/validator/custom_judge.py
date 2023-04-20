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
"""Custom judge for Cubic UFO, Code Jam 2018."""

import math


# We allow 1.1e-6 instead of 1e-6 tolerances to account for errors in the custom
# judge computations.
DISTANCE_TOLERANCE = 1.1e-6
ANGLE_TOLERANCE = 1.1e-6
AREA_TOLERANCE = 1.1e-6


# The various errors we can return.
_EMPTY_OUTPUT = 'Empty output'
_WRONG_AMOUNT_OF_LINES = 'Must have exactly 4 lines per case'
_EXTRA_INFORMATION_IN_HEADER_LINE = 'Extra information after the case number'
_COULD_NOT_PARSE_FLOAT = 'Could not parse a coordinate as floating-point number'
_WRONG_AMOUNT_OF_TOKENS = 'Each line must have exactly 3 tokens'
_WRONG_DISTANCE = (
    'The distance from ({0:.10f}, {1:.10f}, {2:.10f}) to origin is {3:.10f},'
    ' which is too far from 0.5'.format)
_WRONG_ANGLE = (
    'The angle between ({0:.10f}, {1:.10f}, {2:.10f}) and ({3:.10f}, {4:.10f},'
    ' {5:.10f}) differs from pi/2 too much (cosine = {6:.10f})'.format)
_WRONG_AREA = (
    'The area of the projection is {0:.10f}, which differs too much from'
    ' {1:.6f}'.format)


def ParseInputFile(input_file):
  """Turns an input file into a list of floats - case inputs."""
  input_lines = _utils_Tokenize(input_file)
  return [float(k) for (k,) in input_lines[1:1 + int(input_lines[0][0])]]


def HullArea(points):
  """Finds the area of a convex hull for a set of 2D points."""
  # NOTE(petya): Since we're working with floating-point numbers, we try
  # to avoid algorithms that depend on angles, like the nlogn
  # convex hull algorithms. Instead, since we're working with just 8 points,
  # we implement a slow but numerically stable algorithm.
  sorted_xs = sorted(x for x, y in points)
  area = 0.0
  for x_left, x_right in zip(sorted_xs[:-1], sorted_xs[1:]):
    # Between x_left and x_right, we have a trapezoid, and its area is equal to
    # width times the height in the middle.
    width = x_right - x_left
    x = (x_left + x_right) / 2
    min_y = float('inf')
    max_y = float('-inf')
    for x1, y1 in points:
      if x1 == x:
        min_y = min(min_y, y1)
        max_y = max(max_y, y1)
      elif x1 < x:
        for x2, y2 in points:
          if x2 > x:
            y = ((x - x1) * y2 + (x2 - x) * y1) / (x2 - x1)
            min_y = min(min_y, y)
            max_y = max(max_y, y)
    area += width * (max_y - min_y)
  return area


def Verify(lines, case):
  """Checks the output for a case for correctness.

  Args:
    lines: Tokenized lines of output.
    case: A float representing the input for the case.
  Returns:
    An error, or None if there is no error.
  """
  if not lines:
    # I think this never happens, because the line after "Case #1:" is always
    # returned, but is it guaranteed by py?..
    return _EMPTY_OUTPUT
  if len(lines) != 4:
    return _WRONG_AMOUNT_OF_LINES
  if lines[0]:
    return _EXTRA_INFORMATION_IN_HEADER_LINE

  points = []
  for i in xrange(3):
    line = lines[i + 1]
    if len(line) != 3:
      return _WRONG_AMOUNT_OF_TOKENS
    point = []
    for token in line:
      coordinate = _utils_ToFloat(token)
      if coordinate is None:
        return _COULD_NOT_PARSE_FLOAT
      point.append(coordinate)
    points.append(point)

  for point in points:
    len2 = sum(coordinate ** 2 for coordinate in point) ** 0.5
    if abs(len2 - 0.5) > DISTANCE_TOLERANCE:
      return _WRONG_DISTANCE(*(point + [len2]))

  for i1 in xrange(len(points)):
    p1 = points[i1]
    for i2 in xrange(i1):
      p2 = points[i2]
      len1 = sum(coordinate ** 2 for coordinate in p1) ** 0.5
      len2 = sum(coordinate ** 2 for coordinate in p2) ** 0.5
      cosine = sum(c1 * c2 for c1, c2 in zip(p1, p2)) / (len1 * len2)
      # cos(pi/2 - x) == sin(x)
      max_cosine = math.sin(ANGLE_TOLERANCE)
      if abs(cosine) > max_cosine:
        return _WRONG_ANGLE(*(p1 + p2 + [cosine]))

  projections = []
  for s0 in [-1, 1]:
    for s1 in [-1, 1]:
      for s2 in [-1, 1]:
        projections.append(
            (s0 * points[0][0] + s1 * points[1][0] + s2 * points[2][0],
             s0 * points[0][2] + s1 * points[1][2] + s2 * points[2][2]))
  hull_area = HullArea(projections)
  if abs(hull_area - case) > AREA_TOLERANCE:
    return _WRONG_AREA(hull_area, case)

  return None


def VerifyCase(reference_lines, lines, case):
  """Checks a single test case.

  Args:
    reference_lines: Tokenized lines from our I/OGen's output.
    lines: Tokenized lines from the contestant's attempt.
    case: A float representing the input for the case.
  Returns:
    An error, or None if there is no error.
  """
  reference_error = Verify(reference_lines, case)
  if reference_error is not None:
    return 'JUDGE_ERROR! Reference output wrong: %s' % reference_error
  return Verify(lines, case)


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
