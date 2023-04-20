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
# Copyright 2011 Google Inc. All Rights Reserved.

"""A custom judge for the Equal Sums problem."""

__author__ = 'darthur@google.com (David Arthur)'

import logging



def ParseInput(input_file):
  """Given the input file, returns the numbers for each test case."""
  lines = input_file.splitlines()
  result = []
  for line in lines[1:]:
    numbers = [int(word) for word in line.split()[1:]]
    result.append(set(numbers))
  return result


def ParseSubset(tokenized_line, case_number, number_set):
  """Converts a list of strings into a set of numbers, and validates.

  Validation means checking that each number appears in number_set, and does
  not appear twice within tokenized_line.

  Args:
    tokenized_line: A line of text, as returned by Tokenize.
    case_number: What test case this line corresponds to. Used only for
      formatting error messages.
    number_set: The set of all numbers available for use.

  Returns:
    On success: number_set, None is returned.
    On failure: None, error_message is returned.
  """
  result = set()
  for word in tokenized_line:
    value = _utils_ToInteger(word)
    if value is None:
      return None, 'In case #%d, %s is not an integer.' % (case_number, word)
    if value not in number_set:
      return None, 'In case #%d, %d is not in the input.' % (case_number, value)
    if value in result:
      return None, 'In case #%d, %d is used twice.' % (case_number, value)
    result.add(value)
  return result, None


def JudgeCase(case_number, number_set, is_possible, case_attempt):
  """Judges the tokenized output of one input case.

  Args:
    case_number: The number we saw in 'Case #N:'. Used only in error messages.
    number_set: The set of numbers available to used for this test case.
    is_possible: Whether this test case is possible to find an equal sum for.
    case_attempt: The user's output attempt for this case, as returned by
      TokenizeAndSplitCases.

  Returns:
    An error string, or None if the attempt was correct.
  """
  if case_attempt[0]:
    return 'Case header has extra tokens for case #%d.' % case_number

  # Handle impossible.
  if (len(case_attempt) >= 2 and
      len(case_attempt[1]) == 1 and
      case_attempt[1][0] == 'impossible'):
    if len(case_attempt) != 2:
      return 'Case #%d should have two lines.' % case_number
    elif is_possible:
      return 'Case #%d incorrectly declared impossible.' % case_number
    else:
      return None

  # Get the second content line.
  if len(case_attempt) != 3:
    return 'Case #%d should have three lines.' % case_number

  # Parse everything.
  subset1, error = ParseSubset(case_attempt[1], case_number, number_set)
  if error: return error
  subset2, error = ParseSubset(case_attempt[2], case_number, number_set)
  if error: return error
  if subset1 == subset2:
    return 'Duplicate subsets in case #%d.' % case_number

  # Check the sum.
  sum1 = sum(subset1)
  sum2 = sum(subset2)
  if sum1 != sum2:
    return 'Sums (%d, %d) not equal in case #%d.' % (sum1, sum2, case_number)
  return None


def FindError(unused_self, input_file, output_file, attempt):
  """See judge.Judge.FindError()."""

  # Parse the generator input/output.
  parsed_input = ParseInput(input_file)
  parsed_output, parsed_attempt, error = _utils_TokenizeAndSplitCases(
      output_file, attempt, len(parsed_input))
  if error is not None: return error

  # Try each test case.
  for tc in xrange(len(parsed_input)):
    number_set = parsed_input[tc]
    case_output = parsed_output[tc]
    case_attempt = parsed_attempt[tc]
    if (len(case_output) != 1 or
        len(case_output[0]) != 1 or
        (case_output[0][0] != 'possible' and
         case_output[0][0] != 'impossible')):
      error = 'Invalid generator output for case #%d.' % (tc + 1)
      logging.error(error)
      return error
    result = JudgeCase(tc + 1, number_set, case_output[0][0] == 'possible',
                       case_attempt)
    if result is not None: return result

  # Huge success!
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
