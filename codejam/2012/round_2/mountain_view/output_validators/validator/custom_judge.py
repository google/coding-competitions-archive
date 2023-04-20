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

"""Judge for Mountain View."""

__author__ = """amissine@google.com (Andrei Missine),
                onufry@google.com (Onufry Wojtaszczyk)"""



MIN_HEIGHT = int(0)
MAX_HEIGHT = int(1e9)


def Gcd(a, b):
  if a: return Gcd(b % a, a)
  return b


class Rat(object):
  """Rational numbers."""

  def __init__(self, a, b=1):
    assert b
    self.a = a
    self.b = b
    self.Fix()

  def Fix(self):
    g = Gcd(self.a, self.b)
    self.a /= g
    self.b /= g
    if self.b < 0:
      self.a = -self.a
      self.b = -self.b

  def __cmp__(self, other):
    return cmp(self.a * other.b, self.b * other.a)


def VerifyFormat(expected_number_of_peaks, attempt):
  """Check formatting of the attempt.

  Expected format of attempt: a single line containing either the single
  word "Impossible", or expected_number_of_peaks-1 space-separated integers.

  Args:
    expected_number_of_peaks: Correct number of peaks, given in the problem
        description.
    attempt: A contestant's attempt as a 2D string array, already split by
        the Tokenizer.

  Returns:
    None if formatting check passed, string error otherwise.
  """
  if not attempt or not attempt[0]:
    return 'Attempt was empty'
  if len(attempt) != 1:
    return 'Attempt must fit on one line'

  if attempt[0][0] == 'impossible':
    return None

  heights = attempt[0]
  if expected_number_of_peaks != len(heights):
    return 'Incorrect number of peaks, expected %s, but was %s' % (
        expected_number_of_peaks, len(heights))
  for h in heights:
    if _utils_ToInteger(h, MIN_HEIGHT, MAX_HEIGHT) is None:
      return 'All heights must be integers in range [%s, %s]' % (
          MIN_HEIGHT, MAX_HEIGHT)
  return None


def VerifyAttempt(total_peaks, input_list, attempt_list):
  """Check correctness of the attempt_list.

  Args:
    total_peaks: Total number of peaks in the given problem.
    input_list: List of next-visible-peak indices; given as problem input.
    attempt_list: List of heights given by the contestant as an attempted
        solution.

  Returns:
    None if formatting check passed, string error otherwise.
  """
  prev_peaks = [0] * total_peaks
  for peak in range(total_peaks - 1, 0, -1):  # 1-based indices.
    height = attempt_list[peak - 1]
    visible_peak = input_list[peak - 1]
    visible_height = attempt_list[visible_peak - 1]
    visible_slope = Rat(visible_height - height, visible_peak - peak)

    if visible_peak != total_peaks:
      next_peak = input_list[visible_peak - 1]
      next_height = attempt_list[next_peak - 1]
      next_slope = Rat(next_height - height, next_peak - peak)
      if next_slope > visible_slope:
        return 'We should see peak %d from peak %d, but peak %d is visible.' % (
            visible_peak, peak, next_peak)

    if prev_peaks[visible_peak - 1]:
      between_peak = prev_peaks[visible_peak - 1]
      between_height = attempt_list[between_peak - 1]
      between_slope = Rat(between_height - height, between_peak - peak)
      if between_slope >= visible_slope:
        return 'We should see peak %d from peak %d, but peak %d obscures.' % (
            visible_peak, peak, between_peak)
    prev_peaks[visible_peak - 1] = peak


def FindError(_, input_file, output_file, attempt):
  """Check attempts against output file."""
  input_lines = input_file.splitlines()
  testcases = int(input_lines[0])
  input_index = 1

  attempt = attempt.lower()
  parsed_output, parsed_attempt, error = _utils_TokenizeAndSplitCases(
      output_file, attempt, testcases)
  if error is not None: return error

  for testcase in range(testcases):
    total_peaks = int(input_lines[input_index])
    input_index += 1
    input_list = map(int, input_lines[input_index].split())
    input_index += 1

    attempt = parsed_attempt[testcase]
    format_check_result = VerifyFormat(total_peaks, attempt)
    if format_check_result:
      return 'Formatting is incorrect for case %s: %s' % (
          testcase + 1, format_check_result)

    output = parsed_output[testcase]
    if attempt[0][0] == 'impossible' or output[0][0] == 'impossible':
      if not attempt[0][0] == output[0][0]:
        if attempt[0][0] == 'impossible':
          return 'Solution is not impossible for case %s' % (testcase + 1)
        else:
          return 'Solution should be impossible for case %s' % (
              testcase + 1)
    else:
      attempts = []
      for item in attempt[0]:
        attempts.append(_utils_ToInteger(item))
      solution_check_result = VerifyAttempt(
          total_peaks, input_list, attempts)
      if solution_check_result:
        return 'Solution is incorrect for case %s: %s' % (
            testcase + 1, solution_check_result)

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
