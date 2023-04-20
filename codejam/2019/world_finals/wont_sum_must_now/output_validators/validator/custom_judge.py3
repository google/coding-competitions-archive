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
  return [list(filter(None, row.split(' '))) for row in text.split('\n')
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
"""Custom judge for Won't sum? Must now."""



_BETTER_CONTESTANT_SOLUTION_ERROR = (
    "Contestant solution is valid and uses fewer terms than ours")
_INVALID_SUMMAND_ERROR = "Invalid summand: {}".format
_LEADING_ZERO_ERROR = "{} begins with a 0.".format
_NON_PALINDROME_ERROR = "{} is not a palindrome.".format
_TOO_MANY_SUMMANDS_ERROR = "Too many summands: wanted {}, got {}".format
_WRONG_NUM_LINES_ERROR = "Did not print exactly one line."
_WRONG_SUM_ERROR = "Wrong sum: {} instead of {}".format


def CheckAttempt(attempt_lines, case, fewest_summands):
  """Checks a solution, either ours or the contestant's."""
  if len(attempt_lines) != 1:
    return _WRONG_NUM_LINES_ERROR
  line = attempt_lines[0]
  total = 0
  for summand in line:
    if summand[0] == "0":
      return _LEADING_ZERO_ERROR(summand)
    if "".join(reversed(summand)) != summand:
      return _NON_PALINDROME_ERROR(summand)
    summand_int = _utils_ToInteger(summand, minimum_value=1, maximum_value=case)
    if summand_int is None:
      return _INVALID_SUMMAND_ERROR(summand)
    total += summand_int
  if total != case:
    return _WRONG_SUM_ERROR(total, case)
  # If fewest_summands has not been passed in as an arg, we are looking at our
  # own I/OGen's output. Otherwise, we are looking at the contestant's attempt.
  if fewest_summands is None:
    fewest_summands = len(line)
  if len(line) > fewest_summands:
    return _TOO_MANY_SUMMANDS_ERROR(fewest_summands, len(line))
  elif len(line) < fewest_summands:
    return _BETTER_CONTESTANT_SOLUTION_ERROR
  return None


def FindError(unused_self, input_file, output_file, attempt_file):
  """See judge.Judge.FindError()."""
  inputs = [int(line[0]) for line in _utils_Tokenize(input_file)[1:]]
  num_cases = len(inputs)
  outputs, attempts, error = _utils_TokenizeAndSplitCases(
      output_file, attempt_file, num_cases)
  if error is not None:
    return error

  for case_num, (case, output_lines, attempt_lines) in enumerate(
      zip(inputs, outputs, attempts), start=1):
    output_error = CheckAttempt(output_lines, case, None)
    if output_error is not None:
      return "JUDGE_ERROR: Case #{}: {}".format(case_num, output_error)
    attempt_error = CheckAttempt(attempt_lines, case, len(output_lines[0]))
    if attempt_error is not None:
      judge_error_header = (
          "JUDGE_ERROR: " if attempt_error == _BETTER_CONTESTANT_SOLUTION_ERROR
          else "")
      return "{}Case #{}: {}".format(
          judge_error_header, case_num, attempt_error)

  return None

import sys
if __name__ == "__main__":
  if len(sys.argv) == 2 and sys.argv[1] == '-2':
    sys.exit(0)

  result = FindError(None,
                     open(sys.argv[1]).read(),
                     open(sys.argv[3]).read(),
                     open(sys.argv[2]).read())
  if result:
    print >> sys.stderr, result
    sys.exit(1)
