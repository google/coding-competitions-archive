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
"""Custom judge for A Whole New Word, Code Jam 2018."""

__author__ = 'johngs@google.com (Jonathan Irvin Gunawan)'

import collections


_BAD_IMPOSSIBLE_CLAIM_ERROR = (
    'Solution claims a word does not exist while our solution finds one')
_BAD_FORMAT_ERROR = 'Output is not a single string'
_BAD_OUTPUT_ERROR = 'Our output is incorrect: {0}'.format
_BAD_POSSIBLE_CLAIM_ERROR = _BAD_OUTPUT_ERROR(
    'Solution shows that a word exists while our solution does not find one')
_BAD_STRING_CHAR_NOT_FOUND_ERROR = (
    'The {0}-th character is not found in the list of given words').format
_BAD_STRING_FOUND_ERROR = 'Output is found in the list of given words'
_BAD_STRING_LENGTH_ERROR = 'Output is not L-character word or a dash'

"""Parsed information for a single test case.

Attributes:
  n: The number of words.
  l: The length of each word.
  words: A set of l-uppercase-letter words.
  available_letter: A list of length l. available_letter[i] is a set of letters
                    which are available on the index i.
"""
_CaseInput = collections.namedtuple('_CaseInput',
                                    ['n', 'l', 'words', 'available_letters'])


def ParseInputFile(input_file):
  """Turns an input file into a list of _CaseInputs."""
  input_lines = _utils_Tokenize(input_file)[1:]  # skip the number of cases
  cases = []
  while input_lines:
    words = set()
    available_letters = []
    n, l = [int(x) for x in input_lines.pop(0)]
    for i in xrange(l):
      available_letters.append(set())
    for _ in xrange(n):
      line = input_lines.pop(0)
      words.add(line[0].lower())
      for i in xrange(l):
        available_letters[i].add(line[0].lower()[i])
    cases.append(_CaseInput(n, l, words, available_letters))
  return cases


def VerifyOutput(lines, case, expected_word_exists):
  """Checks the output for a single test case.

  Args:
    lines: Tokenized lines (either from our I/OGen's output or a contestant's
        attempt.)
    case: A _CaseInput representing a single test case.
    expected_word_exists: Whether a word exists based on our output. We assume
        that our output's is correct.

  Returns:
    A tuple of two values:
        1. None if the output is correct, or an error message.
        2. Whether there is a word if the output is correct, or None.
  """
  if (not lines) or (len(lines) != 1) or (len(lines[0]) != 1):
    return _BAD_FORMAT_ERROR, None

  output = lines[0][0]
  word_exists = True

  if output == '-':
    word_exists = False
  else:
    if len(output) != case.l:
      return _BAD_STRING_LENGTH_ERROR, None
    if output in case.words:
      return _BAD_STRING_FOUND_ERROR, None
    for i in xrange(case.l):
      if output[i] not in case.available_letters[i]:
        return _BAD_STRING_CHAR_NOT_FOUND_ERROR(i), None

  if expected_word_exists is not None:
    if (expected_word_exists) and (not word_exists):
      return _BAD_IMPOSSIBLE_CLAIM_ERROR, None
    if (not expected_word_exists) and (word_exists):
      return _BAD_POSSIBLE_CLAIM_ERROR, None

  return None, word_exists


def VerifyCase(output_lines, attempt_lines, case):
  """Checks a single test case.

  Args:
    output_lines: Tokenized lines from our I/OGen's output.
    attempt_lines: Tokenized lines from the contestant's attempt.
    case: A CaseInput representing a single test case.
  Returns:
    An error, or None if there is no error.
  """

  output_error, solution_exists = VerifyOutput(output_lines, case, None)
  if output_error is not None:
    return _BAD_OUTPUT_ERROR(output_error)
  attempt_error, _ = VerifyOutput(attempt_lines, case, solution_exists)
  return attempt_error


def FindError(unused_self, input_file, output_file, attempt_file):
  """See judge.Judge.FindError()."""
  input_cases = ParseInputFile(input_file)
  num_cases = len(input_cases)
  output_cases, attempt_cases, error = _utils_TokenizeAndSplitCases(output_file,
                                                                   attempt_file,
                                                                   num_cases)
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
  if sys.argv[1] == '-2':
    sys.exit(0)
  result = FindError(None,
                     file(sys.argv[1]).read(),
                     file(sys.argv[3]).read(),
                     file(sys.argv[2]).read())
  if result:
    print >> sys.stderr, result
    sys.exit(1)
