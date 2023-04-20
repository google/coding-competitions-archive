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
# Copyright 2012 Google Inc. All Rights Reserved.

"""A custom judge for the Aerobics problem."""

__author__ = "wdtseng@google.com (Dustin Tseng)"




class CaseInput(object):
  """Holds information for a single test case.

  Args:
    n: (int) number of students.
    width: (int) width of mat.
    length: (int) length of mat.
    radii: (list(int)) radius of students.
  """

  def __init__(self, n, width, length, radii):
    self.n = n
    self.width = width
    self.length = length
    self.radii = radii


def ConsumeCase(input_lines, first_line):
  """Parses an input case into a CaseInput object.

  Args:
    input_lines: (list(str)) The list of all lines in the input file.
    first_line: (int) The index of the first line to start reading from.

  Returns:
    (tuple(CaseInput, int)) Returns the CaseInput object and the number of lines
        that were consumed.
  """
  # Get problem dimensions
  (n, width, length) = input_lines[first_line].split()
  # Get radii
  radii = input_lines[first_line + 1].split()
  radii = [int(radius) for radius in radii]
  return (CaseInput(int(n), int(width), int(length), radii), 2)


def ParseInputFile(input_file):
  """Prases all input cases from the input file.

  Args:
    input_file: (str) The input file as a string.

  Returns:
    (list(CaseInput)) Returns a list of CaseInput objects.
  """
  input_lines = input_file.splitlines()
  num_cases = int(input_lines[0])
  result = []
  total_lines_consumed = 1
  for _ in xrange(num_cases):
    (case, lines_consumed) = ConsumeCase(input_lines, total_lines_consumed)
    total_lines_consumed += lines_consumed
    result.append(case)
  return result


def CheckCase(case, coordinates):
  """Checks the contestant's output for one test case.

  Args:
    case: (CaseInput) A description of the test case.
    coordinates: (list((float, float))) A list of coordinates for students.

  Returns:
    (str|None) An error string, or None if everything is correct.
  """
  # Verify the number of coordinates matches number of students.
  if case.n != len(coordinates):
    return "Wrong number of coordinates."

  # Verify all students are on the mat.
  eps = 0.00001
  for (x, y) in coordinates:
    if not (0 <= x <= case.width and 0 <= y <= case.length):
      return "Student is off the mat."

  # Verify all pairs of students will not hit each other.
  for i in xrange(case.n):
    for j in xrange(i + 1, case.n):
      (x1, y1) = coordinates[i]
      r1 = case.radii[i]
      (x2, y2) = coordinates[j]
      r2 = case.radii[j]
      if ((x1 - x2)**2 + (y1 - y2)**2) < (r1 + r2)**2 - eps:
        return "Student %d and %d just killed each other." % (i, j)

  return None


def FindError(unused_self, input_file, unused_output_file, attempt):
  """Validate contestant's output file.

  Args:
    see judge.Judge.FindError().

  Returns:
    (str|None) Returns None if the output is correct, and a 'str' error otherwise.
  """
  input_cases = ParseInputFile(input_file)
  num_cases = len(input_cases)

  tokenized_output = _utils_Tokenize(attempt, False)
  if tokenized_output is None:
    return "Output file contains invalid or non-ASCII characters."
  output_index = 0

  for test_case in xrange(1, num_cases + 1):
    # Read the line of contestant's output for this test case.
    if output_index >= len(tokenized_output):
      return "Insufficient output."
    line = tokenized_output[output_index]
    output_index += 1

    # Check line header.
    if (len(line) < 2 or
        line[0] != "case" or
        line[1] != "#%d:" % test_case):
      return "Case header is broken for case #%d" % test_case
    line = line[2:]
    try:
      coordinates = [
          (float(line[i]), float(line[i+1])) for i in xrange(0, len(line), 2)]
    except IndexError:
      return "Odd number of coordinates for case #%d." % test_case
    except ValueError:
      return "Cannot parse a coordinate for case #%d." % test_case

    # Check the list for correctness.
    error = CheckCase(input_cases[test_case - 1], coordinates)
    if error is not None:
      return error

  if output_index != len(tokenized_output):
    return "Extra junk at the end of the file"

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
