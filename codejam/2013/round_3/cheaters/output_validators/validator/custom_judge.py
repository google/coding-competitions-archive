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
"""Default judge for neverland tasks."""

__author__ = "ajyang@google.com (Joyce Yang)"

import re



# Copy-pasted from recruiting/codejam/app/judge.py
# Not inheriting from Judge ( like in judge.py for simplicity (the super class
# doesn't do anything useful right now).
class DefaultJudge(object):
  """The judge that should be used by default for all problems.

  For an exhaustive list of examples, see tests/judge_unittest.py.
  In short, this judge tolerates the following differences.
  (1) Any amount of whitespace (defined as spaces and tabs) is treated as
      a single space.
  (2) Leading and trailing whitespace is ignored.
  (3) Blank lines (lines consisting of only whitespace) are ignored.
      (Windows, Mac, and Linux carriage returns / linefeeds handled the same.)
  (4) Floating point numbers are compared with relative and absolute precision
      of 1e-6. More precisely, if the correct answer has a floating point
      number (or an integer), then the judge expects a floating point
      number (or an integer) from the contestant's answer and compares the two.
      If the answer is within the relative OR absolute difference of 1e-6, the
      numbers are considered the same. Identical non-digit characters are
      removed from the beginning and end of tokens before comparison, so that
      "answer=5.0kg" will match "answer=4.999999999999kg".
  (5) The above floating-point comparison will not take place unless there is
      a decimal point in the output file.
  (6) Case insensitive by default.

  FindError() works in linear time.
  """

  def __init__(self, handle_floats=True, epsilon=1e-6, extra_precise=False,
               case_sensitive=False):
    self.handle_floats = handle_floats
    if extra_precise:
      epsilon *= 0.05
    else:
      epsilon *= 1.1
    self.epsilon = epsilon
    self.extra_precise = extra_precise
    self.case_sensitive = case_sensitive

  @staticmethod
  def ShortenToken(token):
    """Shortens too long token before presenting it to the admin.

    Args:
      token: (str) A string to be shortened.

    Returns:
      The shortened token
    """
    if len(token) > 20:
      return token[:17] + "..."
    else:
      return token

  def __CompareTokens(self, expected, received):
    """Returns a string error message, or None if there are no errors.

    Args:
      expected: (str) The token from the correct output.
      received: (str) The token from the contestant's output.
    """
    expected_orig = expected
    received_orig = received
    if not self.case_sensitive:
      expected = expected.lower()
      received = received.lower()
    if expected == received:
      return None
    reason = "expected {} and received {}.".format(
        self.ShortenToken(expected_orig), self.ShortenToken(received_orig))
    if not self.handle_floats:
      return reason
    # Remove the common prefix, in case we're dealing with floating-point
    # numbers like USD0.05.
    for index in xrange(min(len(expected), len(received))):
      if (expected[index] != received[index] or "0" <= expected[index] <= "9" or
          expected[index] == "."):
        expected = expected[index:]
        received = received[index:]
        break
    else:  # one is a prefix of the other
      return reason
    # Remove the common suffix, in case we're dealing with floating-point
    # numbers like 100.0m/s.
    for index in xrange(1, min(len(expected), len(received)) + 1):
      if expected[-index] != received[-index] or "0" <= expected[-index] <= "9":
        expected = expected[:len(expected) - index + 1]
        received = received[:len(received) - index + 1]
        break
    else:  # one is a suffix of the other
      return reason
    # The following code handles approximate equality for floating-point
    # numbers.  It must be kept in sync with similar logic in
    # recruiting/codejam/contest_validator/contest_validator.py.
    if not (self.IsNumeric(expected) and self.IsNumeric(received)):
      return reason
    if not self.IsApproximatelyEqual(float(expected), float(received),
                                     self.epsilon):
      extra_precise_text = (
          self.extra_precise and
          " The judge is set to be extra precise for the contest validator." or
          "")
      return "{} and {} are not approximately equal. (eps = {}){}".format(
          self.ShortenToken(expected_orig), self.ShortenToken(received_orig),
          self.epsilon, extra_precise_text)
    return None

  def __CompareRows(self, row1, row2):
    """Returns a string error message, or None if there are no errors.

    Args:
      row1: ([str]) The tokenized row of the correct output.
      row2: ([str]) The tokenized row of the contestant's output.
    """
    num_tokens = min(len(row1), len(row2))
    err = None
    for token1, token2 in zip(row1[:num_tokens], row2[:num_tokens]):
      err = self.__CompareTokens(token1, token2)
      if err is not None:
        break
    if len(row1) == len(row2):
      return err
    else:
      if err is None:
        if len(row1) < len(row2):
          err = "the correct line is a prefix of the contestant's line."
        else:
          err = "the contestant's line is a prefix of the correct line."
      return "expected {} token(s), and received {}. First difference: {}".format(
          len(row1), len(row2), err)

  # pylint: disable=unused-argument
  def FindError(self, input_file, output_file, attempt):
    """Returns a string error message, or None if there are no errors.

    Args:
      input_file: (str) The input file.
      output_file: (str) The correct output.
      attempt: A contestant's output that we are verifying.
    """
    rows1 = _utils_Tokenize(output_file)
    rows2 = _utils_Tokenize(attempt)
    if rows1 is None:
      return ("Wrong answer: the reference output file contains non-whitespace "
              "characters outside ASCII range 32-126.")
    if rows2 is None:
      return ("Wrong answer: the contestant's output file contains "
              "non-whitespace characters outside ASCII range 32-126.")

    # If the output files contain different number of lines, we pad the shorter
    # one with empty lines.
    if len(rows1) < len(rows2):
      rows1 += [[] for _ in xrange(len(rows2) - len(rows1))]
    elif len(rows2) < len(rows1):
      rows2 += [[] for _ in xrange(len(rows1) - len(rows2))]

    case_count = 0
    for row1, row2, row_count in zip(rows1, rows2, range(len(rows1))):
      if (len(row2) >= 2 and
          ((self.case_sensitive and row2[0] == "Case") or
           row2[0].lower() == "case") and
          re.match(R"^#\d+:$", row2[1])):
        case_count += 1
      err = self.__CompareRows(row1, row2)
      if err is not None:
        return "Wrong answer: line %d, case %d, %s" % (
            1 + row_count, case_count, err)

    return None

  @staticmethod
  def IsNumeric(x):
    return _utils_ToFloat(x) is not None

  @staticmethod
  def IsApproximatelyEqual(x, y, epsilon):
    """Checks if x and y are approximately equal (within distance epsilon).

    Args:
      x: (float) First value to be compared.
      y: (float) Second value to be compared.
      epsilon: (float) The tolerance of the comparison. By default, 'epsilon' is
        1.1e-6, which is like 1e-6, but errs on the side of false positives.

    Returns:
      True iff y is within relative or absolute 'epsilon' of x. Returns False
      if x or y can't be cast to a float (even if x == y).
    """
    if not (DefaultJudge.IsNumeric(x) and DefaultJudge.IsNumeric(y)):
      return False

    # Check absolute precision.
    if -epsilon <= x - y <= epsilon:
      return True

    # Are x or y too close to zero?
    if -epsilon <= x <= epsilon or -epsilon <= y <= epsilon:
      return False

    # Check relative precision.
    return (-epsilon <= (x - y) / x <= epsilon or
            -epsilon <= (x - y) / y <= epsilon)

import sys
if __name__ == "__main__":
  if sys.argv[1] == "-2":
    sys.exit(0)
  judge = DefaultJudge(epsilon=1e-06, extra_precise=False)
  result = judge.FindError(
      file(sys.argv[1]).read(),
      file(sys.argv[3]).read(),
      file(sys.argv[2]).read())
  if result:
    print >> sys.stderr, result
    sys.exit(1)
