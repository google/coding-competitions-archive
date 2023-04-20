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
# Copyright 2015 Google Inc. All Rights Reserved.

"""A custom judge for the Coin Jam problem."""

__author__ = 'tullis@google.com (Ian Tullis)'



INVALID_OUTPUT_ERROR = 'Output file contains invalid or non-ASCII characters.'
OUTPUT_TOO_SHORT_ERROR = 'Output file does not contain at least 2 lines.'
BROKEN_HEADER_ERROR = 'Case header is broken for case #%d.'
WRONG_NUM_JAMCOINS_ERROR = 'Wrong number of jamcoins.'
WRONG_NUM_VALUES_ERROR = 'Incorrect number of values on output line #%d.'
REPEATED_JAMCOIN_ERROR = 'Repeated jamcoin: %s.'
WRONG_JAMCOIN_LENGTH_ERROR = 'Expected length %d for jamcoin %s.'
WRONG_JAMCOIN_START_END_ERROR = 'Jamcoin %s does not start and end with 1.'
BAD_JAMCOIN_CHARACTER_ERROR = 'Jamcoin %s has a character other than 0 or 1.'
BAD_DIVISOR_ERROR = 'Error turning divisor %s into integer 2 or greater.'
SELF_DIVISOR_ERROR = 'Divisor %d equals jamcoin %s in base %d.'
INVALID_DIVISOR_ERROR = 'Divisor %d doesn\'t divide jamcoin %s (%d in base %d).'


def ParseInputFile(input_file):
  input_lines = input_file.splitlines()
  num_cases = int(input_lines[0])
  result = []
  for i in xrange(num_cases):
    result.append([int(v) for v in input_lines[i + 1].strip().split()])
  return result


def ToBase(s, b):
  """Turns a string (of 0s and 1s) into a base b number."""
  ans = 0
  val = 1
  for i in range(len(s)-1, -1, -1):
    ans += val * int(s[i])
    val *= b
  return ans


def CheckJamcoin(jamcoin, divisors):
  """Returns None if jamcoin is valid and a 'str' error otherwise."""
  for i in range(len(divisors)):
    base = 2+i
    coin_in_base = ToBase(jamcoin, base)
    if coin_in_base == divisors[i]:
      return SELF_DIVISOR_ERROR % (divisors[i], jamcoin, base)
    if coin_in_base % divisors[i] != 0:
      return INVALID_DIVISOR_ERROR % (divisors[i], jamcoin, coin_in_base, base)
  return None


def FindError(unused_self, input_file, unused_output_file, attempt):
  """See judge.Judge.FindError()."""
  input_cases = ParseInputFile(input_file)
  num_cases = len(input_cases)

  tokenized_output = _utils_Tokenize(attempt, False)
  if tokenized_output is None:
    return INVALID_OUTPUT_ERROR
  if len(tokenized_output) <= 1:
    return OUTPUT_TOO_SHORT_ERROR

  # In practice, there will only be one test case for this problem. This
  # assumption is hardcoded in here, although I'm leaving the outer loop
  # just in case.
  for test_case in xrange(1, num_cases + 1):
    # Check the first line.
    line1 = tokenized_output[0]
    if (len(line1) != 2 or
        line1[0] != 'case' or
        line1[1] != ('#%d:' % test_case)):
      return BROKEN_HEADER_ERROR % test_case

    coin_length, num_coins_needed = input_cases[test_case-1]

    if len(tokenized_output[1:]) != num_coins_needed:
      return WRONG_NUM_JAMCOINS_ERROR

    jamcoins_seen = {}

    for c in range(1, len(tokenized_output)):
      line = tokenized_output[c]
      # Should be 10 values per line: one jamcoin and divisors in 9 bases.
      if len(line) != 10:
        return WRONG_NUM_VALUES_ERROR % c
      jamcoin, divisors = line[0], line[1:]
      if jamcoin in jamcoins_seen:
        return REPEATED_JAMCOIN_ERROR % jamcoin
      if len(jamcoin) != coin_length:
        return WRONG_JAMCOIN_LENGTH_ERROR % (coin_length, jamcoin)
      if jamcoin[0] != '1' or jamcoin[-1] != '1':
        return WRONG_JAMCOIN_START_END_ERROR % jamcoin
      for d in jamcoin[1:-1]:
        if d != '0' and d != '1':
          return BAD_JAMCOIN_CHARACTER_ERROR % jamcoin
      for i in range(len(divisors)):
        d_int = _utils_ToInteger(divisors[i], minimum_value=2)
        if d_int is None:
          return BAD_DIVISOR_ERROR % divisors[i]
        divisors[i] = d_int
      err = CheckJamcoin(jamcoin, divisors)
      if err is not None:
        return err
      jamcoins_seen[jamcoin] = True

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
