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
"""Custom judge for Napkin Folding, Code Jam 2019."""

__author__ = 'tbuzzelli@google.com (Timothy Buzzelli)'

import collections


_BAD_FOLDING_PATTERN_ERROR = 'Solution is not a valid neat folding pattern'
_BAD_FORMAT_ERROR = ('Solution does not output either POSSIBLE or IMPOSSIBLE '
                     'or is formatted incorrectly')
_BAD_IMPOSSIBLE_CLAIM_ERROR = (
    'Solution claims no neat folding pattern exists while our solution finds one'
)
_BAD_OUTPUT_ERROR = 'Our output is invalid: {}'.format
_BAD_POSSIBLE_CLAIM_ERROR = (
    'Solution claims a folding pattern exists when there is not one')
_BAD_NUM_SEGMENT_TOKENS_ERROR = 'Badly formatted segment.'
_WRONG_NUM_LINES_ERROR = 'Wrong number of lines'

_IMPOSSIBLE_KEYWORD = 'impossible'
_POSSIBLE_KEYWORD = 'possible'
"""Parsed information for a single test case.

Attributes:
  n: The number of vertices in the polygon.
  k: The number of regions in the folded polygon.
"""
_CaseInput = collections.namedtuple('_CaseInput', ['n', 'k'])


def ParseInputFile(input_file):
  """Turns an input file into a list of _CaseInputs."""
  input_lines = _utils_Tokenize(input_file)  # skip the number of cases
  num_cases = int(input_lines[0][0])
  idx = 1
  cases = []
  for _ in xrange(num_cases):
    cases.append(_CaseInput(int(input_lines[idx][0]), int(input_lines[idx][1])))
    idx = idx + int(input_lines[idx][0]) + 1
  return cases


def NormalizeFoldingPattern(folding_pattern):
  """Normalizes a folding pattern.

  Args:
    folding_pattern: Tokenized lines representing a folding pattern.

  Returns:
    First return value:
      A sorted list of strings with each string being one segment with A and B
      ordered in a normalized way, or None if there is an error.
    Second return value:
      The type of error, if there is an error.
  """
  res = []
  for segment in folding_pattern:
    if not segment or len(segment) != 4:
      return None, _BAD_NUM_SEGMENT_TOKENS_ERROR
    ax, ay, bx, by = segment
    if ax > bx or (ax == bx and ay > by):
      ax, ay, bx, by = bx, by, ax, ay
    res.append(ax + '_' + ay + '_' + bx + '_' + by)
  res.sort()
  return res, None


def VerifyCase(output_lines, attempt_lines, case):
  """Checks a single test case.

  Note: The output created by the I/OGen DOES NOT follow the expected output.
  To make judging easier, the I/OGen first outputs the number of valid folding
  patterns that are possible and then it prints all of them. Therefore, only
  need to check that the participant's output matches one of these valid folding
  patterns (after sorting).

  Args:
    output_lines: Tokenized lines from our I/OGen's output.
    attempt_lines: Tokenized lines from the contestant's attempt.
    case: A CaseInput representing a single test case.

  Returns:
    An error, or None if there is no error.
  """

  # This is here to let us compare exhaustive solutions like darcybest_all.cc
  # with the I/OGen's exhaustive output.
  if output_lines == attempt_lines:
    return None

  if len(attempt_lines) < 1 or len(attempt_lines[0]) != 1:
    return _BAD_FORMAT_ERROR

  if output_lines[0][0] == _IMPOSSIBLE_KEYWORD:
    if attempt_lines[0][0] == _POSSIBLE_KEYWORD:
      return _BAD_POSSIBLE_CLAIM_ERROR
    if attempt_lines[0][0] != _IMPOSSIBLE_KEYWORD:
      return _BAD_FORMAT_ERROR
    if len(attempt_lines) != 1:
      return _WRONG_NUM_LINES_ERROR
    return None

  if attempt_lines[0][0] == _IMPOSSIBLE_KEYWORD:
    return _BAD_IMPOSSIBLE_CLAIM_ERROR
  if attempt_lines[0][0] != _POSSIBLE_KEYWORD:
    return _BAD_FORMAT_ERROR
  attempt_segments = attempt_lines[1:]
  # For a pattern with K regions, there should be K-1 segments.
  if len(attempt_segments) != case.k - 1:
    return _WRONG_NUM_LINES_ERROR

  attempt_folding_pattern, err = NormalizeFoldingPattern(attempt_segments)
  if err:
    return err
  for i in range(int(output_lines[1][0])):
    output_folding_pattern, err = NormalizeFoldingPattern(
        output_lines[
            (2 + i * (case.k - 1)):(2 + (i + 1) * (case.k - 1))])
    if err:
      return _BAD_OUTPUT_ERROR(err)
    # Any one match is sufficient.
    if attempt_folding_pattern == output_folding_pattern:
      return None

  return _BAD_FOLDING_PATTERN_ERROR


def FindError(unused_self, input_file, output_file, attempt_file):
  """See judge.Judge.FindError()."""
  input_cases = ParseInputFile(input_file)
  num_cases = len(input_cases)
  output_cases, attempt_cases, error = _utils_TokenizeAndSplitCases(
      output_file, attempt_file, num_cases)
  if error is not None:
    return error

  for case_num, (case, output_lines, attempt_lines) in enumerate(
      zip(input_cases, output_cases, attempt_cases), start=1):
    error = VerifyCase(output_lines, attempt_lines, case)
    if error is not None:
      return 'Case #{}: {}'.format(case_num, error)

  # Everything passes.
  return None

import sys
if __name__ == "__main__":
  result = FindError(None,
                     file(sys.argv[1]).read(),
                     file(sys.argv[3]).read(),
                     file(sys.argv[2]).read())
  if result:
    print >> sys.stderr, result
    sys.exit(1)