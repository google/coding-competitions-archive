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
# Copyright 2013 Google Inc. All Rights Reserved.

"""A custom judge for the Pogo problem."""

__author__ = 'hackson@google.com (Hackson Leung)'

import logging
import re



VALID_PATTERN = re.compile(r'^[news]*$')
SMALL_DATASET_SIZE = 50
STEPS_LIMIT = 500
# For testing purposes only
FORCE_LARGE_DATASET_MODE = False
SAMPLE_CASE = [[3, 4], [-3, 4]]


def SetForcingLargeDatasetMode(enable):
  """For testing purposes that force checking test cases in large dataset mode.
     Then we save the hassle in generating real number of test cases so as to
     trigger the judge mode switching.
  """
  global FORCE_LARGE_DATASET_MODE
  FORCE_LARGE_DATASET_MODE = enable


def MaxAllowedSteps(num_test_cases, num_steps_judge):
  """Determines the maximum number of steps allowed for user's attempted case.

  Arg:
    num_test_cases: The number of test cases that serves as the main switch of
      checking criteria.
    num_steps_judge: The judge's (minimum) number of steps for the case.

  Returns:
    The maximum number of steps allowed. For the definition of maximum number of
    steps, see the description in JudgeCase. In small input set, we always have
    a larger value defined by STEPS_LIMIT.
  """
  global FORCE_LARGE_DATASET_MODE
  if num_test_cases <= SMALL_DATASET_SIZE and not FORCE_LARGE_DATASET_MODE:
    return STEPS_LIMIT

  return num_steps_judge


def ParseInput(input_file):
  """Given the input file, returns the numbers for each test case."""
  lines = input_file.splitlines()
  return [[int(coord) for coord in line.split()] for line in lines[1:]]


def JudgeCase(case_number, destination_point, case_attempt, minimum_steps,
              maximum_steps):
  """Judges the tokenized output of one input case.

  Args:
    case_number: The number we saw in 'Case #N:'. Used only in error messages.
    destination_point: The coordinates of the destination for this test case.
    case_attempt: The user's output attempt for this case, as returned by
      TokenizeAndSplitCases.
    minimum_steps: The minimum steps in judge's output for this case. User's
      output attempt must always have number of steps at least this value. If
      the number of steps is less than this value and it can reach the
      destination point, then it is possible that the solution in IOGen is
      wrong. A warning will be issued. For the case of having value larger than
      minimum_steps, it will be handled by maximum_steps, see below.
    maximum_steps: The maximum allowed steps for this case. User's output
      attempt must have number of steps not exceeding this value. Otherwise we
      treat it as incorrect. Note that the correctness is under the assumption
      that it is a valid solution, i.e. it reaches the destination point.

  Returns:
    An error string, or None if the attempt was correct.
  """
  case_steps = len(case_attempt[0][0])
  # Check if it fits in the maximum allowed steps.
  if case_steps > maximum_steps:
    return ('Expected to move at most %d steps, but it took %d steps in case '
            '#%d, which is too much.' %
            (maximum_steps, case_steps, case_number))

  pos_x, pos_y, jump_size = 0, 0, 1
  for move in case_attempt[0][0]:
    if move == 'n':
      pos_y += jump_size
    elif move == 'e':
      pos_x += jump_size
    elif move == 'w':
      pos_x -= jump_size
    else:
      pos_y -= jump_size
    jump_size += 1

  if [pos_x, pos_y] != destination_point:
    return ('Expected to be at (%d, %d), but arrived at (%d, %d) in case #%d.' %
            (destination_point[0], destination_point[1], pos_x, pos_y,
             case_number))

  # This is a valid solution, now check if it could be a more optimal solution.
  if case_steps < minimum_steps:
    error = ('[WARNING] Expected to have minimum of %d steps, but it took %d '
             'steps in case #%d, which is better. Check IOGen please.' %
             (minimum_steps, case_steps, case_number))
    logging.error(error)
    return error

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
    point = parsed_input[tc]
    case_output = parsed_output[tc]
    case_attempt = parsed_attempt[tc]
    if (len(case_output) != 1 or
        len(case_output[0]) != 1 or
        VALID_PATTERN.match(case_output[0][0]) is None):
      error = 'Invalid generator output for case #%d.' % (tc + 1)
      logging.error(error)
      return error

    minimum_steps = 0 if parsed_input == SAMPLE_CASE else len(case_output[0][0])

    # Determine if we are judging small or large dataset
    maximum_steps = MaxAllowedSteps(len(parsed_input), minimum_steps)

    if (len(case_attempt) != 1 or
        len(case_attempt[0]) != 1 or
        VALID_PATTERN.match(case_attempt[0][0]) is None):
      error = 'Invalid output for case #%d.' % (tc + 1)
      return error
    else:
      result = JudgeCase(tc + 1, point, case_attempt, minimum_steps,
                         maximum_steps)
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
