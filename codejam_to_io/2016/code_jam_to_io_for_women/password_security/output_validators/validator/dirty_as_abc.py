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
"""A custom judge for "Dirty As ABC", Code Jam 2016."""

__author__ = 'tullis@google.com (Ian Tullis)'



# The various errors we can return.
ATTEMPT_FALSE_NEGATIVE_ERROR = 'Got IMPOSSIBLE when answer exists.'
BAD_HEADER_ERROR = 'Incorrect number of tokens in header.'
BAD_OUTPUT_ERROR = 'Our output is incorrect!'
DIRTY_WORD_FOUND_ERROR = 'Gasp! Dirty word %s in alphabet!'
NOT_ALPHABET_ERROR = 'Answer is not a full alphabet.'
OUTPUT_FALSE_NEGATIVE_ERROR = 'Attempt is correct for IMPOSSIBLE case.'
WRONG_NUM_LINES_ERROR = 'More than one line in output.'


def ParseInputFile(input_file):
  """Turns an input file into a list of lists of dirty words."""

  # Change everything to lowercase.
  input_lines = _utils_Tokenize(input_file, case_sensitive=False)
  num_cases = int(input_lines[0][0])
  # Every case's input is two lines long. We don't need the first line since
  # it's just the number of dirty words, for the contestant's convenience.
  return [input_lines[2 + 2 * i] for i in xrange(num_cases)]


# Constants for use in VerifyOutput and VerifyCase.
IMPOSSIBLE_OUTPUT, INCORRECT_OUTPUT, POSSIBLE_OUTPUT = 0, 1, 2


def VerifyOutput(lines, dirty_words):
  """Checks the output for a single test case.

  Args:
    lines: Tokenized lines from our I/OGen's output or a contestant's attempt.
    dirty_words: A list of dirty words for this case.

  Returns:
    A tuple with these entries:
    1. One of IMPOSSIBLE_OUTPUT, INCORRECT_OUTPUT, POSSIBLE_OUTPUT
    2. An error message (in the case of INCORRECT_OUTPUT)
  """

  if len(lines) != 1:
    return INCORRECT_OUTPUT, WRONG_NUM_LINES_ERROR

  header = lines[0]
  # After processing by TokenizeAndSplitCases, the header should have only one
  # token: the answer.
  if len(header) != 1:
    return INCORRECT_OUTPUT, BAD_HEADER_ERROR

  answer = header[0]
  # See if the answer is IMPOSSIBLE. (lowercase due to TokenizeAndSplitCases)
  if answer == 'impossible':
    return IMPOSSIBLE_OUTPUT, None

  # Act as if the case is solvable, even if we think it isn't, just in case the
  # contestant has a valid answer that we overlooked.
  alphabet_list = [chr(ord('a')+x) for x in range(26)]
  # Check the length first to avoid potentially sorting a giant output.
  if len(answer) != 26 or sorted(list(answer)) != alphabet_list:
    return INCORRECT_OUTPUT, NOT_ALPHABET_ERROR

  for dw in dirty_words:
    if dw in answer:
      return INCORRECT_OUTPUT, DIRTY_WORD_FOUND_ERROR % dw

  return POSSIBLE_OUTPUT, None


def VerifyCase(output_lines, attempt_lines, dirty_words):
  """Checks a single test case.

  Args:
    output_lines: Tokenized lines from our I/OGen's output.
    attempt_lines: Tokenized lines from the contestant's attempt.
    dirty_words: The list of dirty words for a single test case.
  Returns:
    An error, or None if there is no error.
  """

  output_res, _ = VerifyOutput(output_lines, dirty_words)
  attempt_res, attempt_error = VerifyOutput(attempt_lines, dirty_words)
  if attempt_res == INCORRECT_OUTPUT:
    return attempt_error
  if output_res == INCORRECT_OUTPUT:
    return BAD_OUTPUT_ERROR
  # both are either POSSIBLE_OUTPUT or IMPOSSIBLE_OUTPUT
  if output_res == attempt_res:
    return None
  if attempt_res == IMPOSSIBLE_OUTPUT:
    return ATTEMPT_FALSE_NEGATIVE_ERROR
  # output_res = IMPOSSIBLE_OUTPUT
  return OUTPUT_FALSE_NEGATIVE_ERROR


def FindError(unused_self, input_file, output_file, attempt):
  """See judge.Judge.FindError()."""
  dirty_word_lists = ParseInputFile(input_file)
  num_cases = len(dirty_word_lists)
  output, attempt, error = _utils_TokenizeAndSplitCases(
      output_file, attempt, num_cases)
  if error is not None:
    return error

  for case_num, (dirty_word_list, output_lines, attempt_lines) in enumerate(
      zip(dirty_word_lists, output, attempt), start=1):
    error = VerifyCase(output_lines, attempt_lines, dirty_word_list)
    if error is not None:
      return 'Case #%s: %s' % (case_num, error)

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