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
"""A custom judge for "Senate Evacuation", Code Jam 2016.

Statement is at:
//recruiting/contest_data/codejam/gcj_2016/senate_evacuation/statement.html
"""

import copy


# The various errors we can return.
_ABSOLUTE_MAJORITY_ACHIEVED = 'An absolute majority was achieved.'
_EVACUATION_INCOMPLETE = 'Evacuation incomplete.'
_INVALID_PARTY = 'Party {0} not valid ({1} parties in total).'.format
_INVALID_STEP_LENGTH = 'Step with length not in {1,2}.'
_MORE_THAN_ONE_LINE = 'More than one line in output.'
_PARTY_ALREADY_FINISHED = 'Party {0} already finished evacuating.'.format


def _ParseInputFile(input_file):
  """Turns an input file into a list of cases.

  Args:
    input_file: (str) the full text of the input file (including newlines).

  Returns:
    A list of lists of integers representing tests read from input_file.
    Each list of integers represents exactly one test case. The i-th integer
    of each list represents the number of senators of the i-th party.
  """

  input_lines = _utils_Tokenize(input_file)
  num_cases = int(input_lines[0][0])

  result = []
  for i in xrange(num_cases):
    # Every input case is two lines long. We ignore the first because it is
    # equal to the number of tokens in the second one.
    result.append([int(x) for x in input_lines[2 + 2*i]])
  return result


def _VerifyCase(attempt_lines, case):
  """Checks a single test case.

  Args:
    attempt_lines: Tokenized lines from the contestant's attempt.
    case: A list of integers representing a single test case.
  Returns:
    An error (full string or format function, see constants at the top of
    the file), or None if there is no error. We use this way of error handling
    following judge.Judge.FindError() format.
  """
  if len(attempt_lines) != 1:
    return _MORE_THAN_ONE_LINE

  party_sizes = copy.deepcopy(case)
  num_parties = len(party_sizes)
  sum_party_sizes = sum(party_sizes)

  for step in attempt_lines[0]:
    if len(step) < 1 or len(step) > 2:
      return _INVALID_STEP_LENGTH

    for party_chr in step:
      # The tokenizer will convert everything to lowercase.
      party = ord(party_chr) - ord('a')
      if party < 0 or party >= num_parties:
        return _INVALID_PARTY(party_chr, num_parties)

      if party_sizes[party] < 1:
        return _PARTY_ALREADY_FINISHED(party_chr)

      party_sizes[party] -= 1

    sum_party_sizes -= len(step)
    for party_size in party_sizes:
      if party_size*2 > sum(party_sizes):
        return _ABSOLUTE_MAJORITY_ACHIEVED

  if sum(party_sizes) > 0:
    return _EVACUATION_INCOMPLETE

  return None


def FindError(unused_self, input_file, output_file, attempt):
  """Implementation for Senate Evacuation of judge.Judge.FindError()."""
  input_cases = _ParseInputFile(input_file)
  _, attempt, error = _utils_TokenizeAndSplitCases(
      output_file, attempt, len(input_cases))
  if error:
    return error

  for case_num, (case, attempt_lines) in enumerate(
      zip(input_cases, attempt), start=1):
    error = _VerifyCase(attempt_lines, case)
    if error:
      return 'Case #%s: %s' % (case_num, error)

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
