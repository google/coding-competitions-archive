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
# Copyright 2008 Google Inc. All Rights Reserved.

"""A custom judge for the TriangleAreas problem.
"""

__author__ = "abednego@google.com (Igor Naverniouk)"

import re


def FindError(_, input_file, output_file, attempt):
  """Returns None if the output is correct and a 'str' error otherwise.

  Ignores leading and trailing whitespace in the file.
  Ignores whitespace-only lines.
  Ignores differences in the amount of whitespace on a single line.
  Checks that the IMPOSSIBLEs match up.
  Checks that the given triangles have valid coordinates.
  Checks that triangles have the correct area.

  Makes strict assumptions about the formatting of input_file and output_file.

  Args:
    see judge.Judge.FindError().
  """
  # Read N, M and A for each test case.
  input_lines = input_file.splitlines()
  num_cases = int(input_lines[0])
  if len(input_lines) != 1 + num_cases:
    return "BAD! The input data is wrong."
  (n, m, a) = ([], [], [])
  for line in input_lines[1:]:
    (ni, mi, ai) = line.split(" ")
    n.append(int(ni))
    m.append(int(mi))
    a.append(int(ai))

  # Read the correct answers to find the impossible cases.
  output_lines = output_file.splitlines()
  if len(output_lines) != num_cases:
    return "BAD! The output data is wrong."
  imposs_pattern = re.compile(r"Case #\d+: IMPOSSIBLE$")
  is_possible = [imposs_pattern.match(line) is None for line in output_lines]

  # Strip leading and trailing whitespace from the output file.
  attempt = attempt.strip()

  # Extract non-whitespace lines of output and strip them, too.
  attempt_lines = filter(None, map(lambda x: x.strip(), attempt.splitlines()))

  # What remains must have one line per test case.
  if len(attempt_lines) != num_cases:
    return "Incorrect number of lines in the output file"

  # Match each test case to the correct answer.
  attempt_pattern = re.compile(r"Case\s+#(\d+):\s+(.*)$")
  points_pattern = re.compile(r"(\d+)\s+" * 5 + r"(\d+)$")
  for i, attempt_line in enumerate(attempt_lines):
    # Parse the Case number.
    match = attempt_pattern.match(attempt_line)
    if not match or len(match.groups()) != 2:
      return "Line %d does not look like an answer" % (i + 1)
    case_number = int(match.groups()[0])
    attempt_body = match.groups()[1]
    if case_number != i + 1:
      return "Expected case %d; found %d." % (i + 1, case_number)

    # Deal with IMPOSSIBLE answers.
    if attempt_body == "IMPOSSIBLE" and is_possible[i]:
      return "Case #%d is possible" % case_number
    if attempt_body != "IMPOSSIBLE" and not is_possible[i]:
      return "Case #%d is impossible" % case_number
    if attempt_body == "IMPOSSIBLE" and not is_possible[i]:
      continue

    # Extract the triangle points.
    match = points_pattern.match(attempt_body)
    if not match or len(match.groups()) != 6:
      return "Case #%d does not contain 6 integers" % (i + 1)
    (ax, ay, bx, by, cx, cy) = map(int, match.groups())

    # Make sure they are in range.
    if not (0 <= ax <= n[i] and 0 <= ay <= m[i]):
      return "Case #%d: the first triangle point is out of range" % case_number
    if not (0 <= bx <= n[i] and 0 <= by <= m[i]):
      return "Case #%d: the second triangle point is out of range" % case_number
    if not (0 <= cx <= n[i] and 0 <= cy <= m[i]):
      return "Case #%d: the third triangle point is out of range" % case_number

    # Make sure the area is correct.
    if abs((bx - ax) * (cy - by) - (by - ay) * (cx - bx)) != a[i]:
      return "Case #%d: triangle area is incorrect" % case_number

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
