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
"""A custom judge for Neigh-bors, Code Jam 2017."""

__author__ = 'tullis@google.com (Ian Tullis)'

import collections


# The various errors we can return.
_ATTEMPT_FALSE_NEGATIVE_ERROR = 'Got IMPOSSIBLE when answer exists.'
_BAD_CASE_FORMAT_ERROR = 'Wrong number of tokens in header or lines in case.'
_BAD_NEIGHBOR_ERROR = (
    'Neighbors {0} and {1} (indexes {2} and {3}) share a hair color.'.format)
_BAD_OUTPUT_ERROR = 'Our output is invalid: {0}'.format
_OUTPUT_FALSE_NEGATIVE_ERROR = 'Attempt correct for supposedly IMPOSSIBLE case.'
_WRONG_COLOR_DISTRIBUTION_ERROR = 'Colors do not match given distribution.'
_WRONG_LENGTH_ERROR = 'Wrong number of stalls.'

# Constants for use in VerifyOutput and VerifyCase.
# These classify answers to test cases, which may come from our own I/OGen or
# from contestants.
_IMPOSSIBLE = 0  # The given answer is "IMPOSSIBLE".
_INCORRECT = 1  # An answer is claimed, but is incorrect.
_POSSIBLE = 2  # An answer is claimed, and is correct.

# Allowed neighbors for a given color.
_OK_NEIGHBORS = {
    'r': 'ygb', 'o': 'b', 'y': 'rbv', 'g': 'r', 'b': 'roy', 'v': 'y'}


"""Parsed information for a single test case.

Attributes:
  n: The N input (total number of unicorns).
  r: The R input (number of unicorns with red manes).
  o: The O input (number of unicorns with orange manes).
  y: The Y input (number of unicorns with yellow manes).
  g: The G input (number of unicorns with green manes).
  b: The B input (number of unicorns with blue manes).
  v: The V input (number of unicorns with violet manes).
"""
_CaseInput = collections.namedtuple(
    '_CaseInput', ['n', 'r', 'o', 'y', 'g', 'b', 'v'])


def ParseInputFile(input_file):
  """Turns an input file into a list of _CaseInputs."""
  input_lines = _utils_Tokenize(input_file)
  return [_CaseInput(*[int(x) for x in line]) for line in input_lines[1:]]


def VerifyOutput(lines, case):
  """Checks the output for a single test case.

  Act as if the case is solvable, even if we think it isn't, just in case the
  contestant has a valid answer that we overlooked.

  Args:
    lines: Tokenized lines (either from our I/OGen's output or a contestant's
        attempt.)
    case: A CaseInput representing a single test case.

  Returns:
    A tuple with these entries:
    1. One of _IMPOSSIBLE, _INCORRECT, or _POSSIBLE
    2. An error message (in the case of _INCORRECT)
  """
  if len(lines) != 1 or len(lines[0]) != 1:
    return _INCORRECT, _BAD_CASE_FORMAT_ERROR
  ans = lines[0][0]
  if ans == 'impossible':
    return _IMPOSSIBLE, None
  if len(ans) != case.n:
    return _INCORRECT, _WRONG_LENGTH_ERROR

  if ''.join(sorted(ans)) != (
      'b' * case.b + 'g' * case.g + 'o' * case.o + 'r' * case.r + 'v' * case.v
      + 'y' * case.y):
    return _INCORRECT, _WRONG_COLOR_DISTRIBUTION_ERROR

  ans += ans[0]  # Pad the answer with a copy of the start for convenience.
  for i in range(len(ans)-1):
    if ans[i+1] not in _OK_NEIGHBORS[ans[i]]:
      return _INCORRECT, _BAD_NEIGHBOR_ERROR(
          ans[i], ans[i + 1], i, (i + 1) % case.n)

  return _POSSIBLE, None


def VerifyCase(output_lines, attempt_lines, case):
  """Checks a single test case.

  Args:
    output_lines: Tokenized lines from our I/OGen's output.
    attempt_lines: Tokenized lines from the contestant's attempt.
    case: A CaseInput representing a single test case.
  Returns:
    An error, or None if there is no error.
  """

  output_res, output_error = VerifyOutput(output_lines, case)
  attempt_res, attempt_error = VerifyOutput(attempt_lines, case)
  if attempt_res == _INCORRECT:
    return attempt_error
  if output_res == _INCORRECT:
    return _BAD_OUTPUT_ERROR(output_error)
  if output_res == _IMPOSSIBLE:
    if attempt_res == _IMPOSSIBLE:
      return None
    else:
      return _OUTPUT_FALSE_NEGATIVE_ERROR
  else:
    if attempt_res == _IMPOSSIBLE:
      return _ATTEMPT_FALSE_NEGATIVE_ERROR
    else:
      return None


def FindError(unused_self, input_file, output_file, attempt):
  """See judge.Judge.FindError()."""
  input_cases = ParseInputFile(input_file)
  num_cases = len(input_cases)
  output, attempt, error = _utils_TokenizeAndSplitCases(
      output_file, attempt, num_cases)
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
  if len(sys.argv) == 2 and sys.argv[1] == '-2':
    sys.exit(0)

  result = FindError(None,
                     open(sys.argv[1]).read(),
                     open(sys.argv[3]).read(),
                     open(sys.argv[2]).read())
  if result:
    print >> sys.stderr, result
    sys.exit(1)
