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
"""A custom judge for "Slides", Code Jam 2016."""

__author__ = 'tullis@google.com (Ian Tullis)'

import collections



# The various errors we can return.
_ATTEMPT_FALSE_NEGATIVE_ERROR = 'Got IMPOSSIBLE when answer exists.'
_BAD_HEADER_ERROR = 'Incorrect number of tokens, or wrong data, in header.'
_BAD_LINE_ERROR = 'Wrong number of tokens / length / characters in output line.'
_BAD_OUTPUT_ERROR = 'Our output is incorrect!'
_CYCLE_ERROR = 'Cycle causes infinite possibilities.'
_ONE_ON_DIAGONAL_ERROR = 'One along diagonal.'
_OUTPUT_FALSE_NEGATIVE_ERROR = 'Attempt is correct for IMPOSSIBLE case.'
_SLIDE_FROM_END_ERROR = 'Slide originating in last building.'
_WRONG_NUM_LINES_ERROR = 'Wrong number of lines in output.'
_WRONG_NUM_PATHS_ERROR = 'Expected %d paths but got %d.'


# Constants for use in _VerifyOutput and _VerifyCase.
# These classify answers to test cases, which may come from our own I/OGen or
# from contestants.
_IMPOSSIBLE = 0  # The given answer is "IMPOSSIBLE".
_INCORRECT = 1  # An answer is claimed, but is incorrect.
_POSSIBLE = 2  # An answer is claimed, and is correct.


# Constant ceiling to keep the calculation of number of paths bounded.
# It's larger than any possible desired value of M. (This is needed because
# small cycles can cause the numbers to blow up very quickly.)
_CEILING = 10**19


class _CaseInput(collections.namedtuple('_CaseInput', ('b', 'm'))):
  """Parsed information for a single test case.

  Attributes:
    b: The B parameter (number of buildings) for the test case.
    m: The M parameter (desired number of paths) for the test case.
  """


def _ParseInputFile(input_file):
  """Turns an input file of one-line test cases into a list of _CaseInputs."""

  input_lines = _utils_Tokenize(input_file)
  return [_CaseInput(int(b), int(m)) for b, m in input_lines[
      1:int(input_lines[0][0]) + 1]]


def _GetNumPaths(slides_matrix):
  """Checks the number of paths from the start building to the end building.

  Returns the actual number of paths from building 1 to building B (which
  may be 0 if B is unreachable from 1), or returns -1 if a cycle is part of
  at least one path leading from 1 to B (which results in infinite paths).
  We use a path-counting version of Floyd-Warshall.

  Args:
     slides_matrix: A list of B lists with B integers each. The jth value on
         the ith line is 1 if there is a slide from building i to building j,
         and 0 otherwise.

  Returns:
    min(actual number of paths, _CEILING), or -1, as described above.
  """

  num_buildings = len(slides_matrix)
  for k in xrange(num_buildings):
    new_slides_matrix = [[0]*num_buildings for _ in xrange(num_buildings)]
    for i in xrange(num_buildings):
      for j in xrange(num_buildings):
        new_slides_matrix[i][j] = min(
            slides_matrix[i][j] + slides_matrix[i][k]*slides_matrix[k][j],
            _CEILING)
    slides_matrix = new_slides_matrix

  for i in xrange(num_buildings):
    if (slides_matrix[0][i] > 0 and slides_matrix[i][i] > 0
        and slides_matrix[i][num_buildings - 1] > 0):
      return -1

  return slides_matrix[0][-1]


def _VerifyOutput(lines, case):
  """Checks the output for a single test case.

  We act as if the case is solvable, even if we think it isn't, just in case
  the contestant has a valid answer that we overlooked.

  Args:
    lines: Tokenized lines (either from our I/OGen's output or a contestant's
        attempt).
    case: A _CaseInput representing a single test case.

  Returns:
    A tuple with these entries:
    1. One of _IMPOSSIBLE, _INCORRECT, or _POSSIBLE, as described above.
    2. An error message (in the case of _INCORRECT), or None otherwise.
  """

  header = lines[0]
  # After processing by TokenizeAndSplitCases, the header should have only one
  # token: either 'possible' or 'impossible'.
  if len(header) != 1:
    return _INCORRECT, _BAD_HEADER_ERROR
  is_possible = header[0]
  if is_possible not in {'possible', 'impossible'}:
    return _INCORRECT, _BAD_HEADER_ERROR
  # IMPOSSIBLE is lowercased here because the output text has been lowercased
  # by TokenizeAndSplitCases.
  if is_possible == 'impossible':
    return _IMPOSSIBLE, None

  raw_answer = lines[1:]
  if len(raw_answer) != case.b:
    return _INCORRECT, _WRONG_NUM_LINES_ERROR

  for line_tokens in raw_answer:
    if len(line_tokens) != 1:
      return _INCORRECT, _BAD_LINE_ERROR
    line = line_tokens[0]
    if len(line) != case.b or line.count('0') + line.count('1') != case.b:
      return _INCORRECT, _BAD_LINE_ERROR

  answer = [[int(entry) for entry in row[0]] for row in raw_answer]

  if 1 in answer[-1]:
    return _INCORRECT, _SLIDE_FROM_END_ERROR

  for i in xrange(case.b):
    if answer[i][i] == 1:
      return _INCORRECT, _ONE_ON_DIAGONAL_ERROR

  paths = _GetNumPaths(answer)
  if paths == -1:
    return _INCORRECT, _CYCLE_ERROR
  elif paths != case.m:
    return _INCORRECT, _WRONG_NUM_PATHS_ERROR % (case.m, paths)

  return _POSSIBLE, None


def _VerifyCase(output_lines, attempt_lines, case):
  """Checks a single test case.

  Args:
    output_lines: Tokenized lines from our I/OGen's output.
    attempt_lines: Tokenized lines from the contestant's attempt.
    case: A CaseInput representing a single test case.
  Returns:
    An error, or None if there is no error.
  """

  output_res, _ = _VerifyOutput(output_lines, case)
  attempt_res, attempt_error = _VerifyOutput(attempt_lines, case)
  if attempt_res == _INCORRECT:
    return attempt_error
  if output_res == _INCORRECT:
    return _BAD_OUTPUT_ERROR
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
  input_cases = _ParseInputFile(input_file)
  num_cases = len(input_cases)
  output, attempt, error = _utils_TokenizeAndSplitCases(
      output_file, attempt, num_cases)
  if error is not None:
    return error

  for case_num, (case, output_lines, attempt_lines) in enumerate(
      zip(input_cases, output, attempt), start=1):
    error = _VerifyCase(output_lines, attempt_lines, case)
    if error is not None:
      return 'Case #%s: %s' % (case_num, error)

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
