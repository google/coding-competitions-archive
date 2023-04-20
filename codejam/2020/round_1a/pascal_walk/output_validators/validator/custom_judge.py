# Copyright 2011 Google Inc. All Rights Reserved.
"""Basic utilities for custom judges."""

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
  return [
      filter(None, row.split(' ')) for row in text.split('\n') if row.strip()
  ]


def _utils_TokenizeAndSplitCases(output_file,
                                 attempt,
                                 num_cases,
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
    case_sensitive: Whether to run in case-sensitive mode (for everything except
      the word 'Case' itself).

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
      line = list(line)
      if (len(line) >= 2 and line[0].lower() == 'case' and
          line[1].startswith('#')):
        # This line is a "Case #N:" line.
        expected_case = 1 + len(split_text)
        if line[1] != ('#%d:' % expected_case):
          return None, ('Expected "case #%d:", found "%s %s".' %
                        (expected_case, line[0], line[1]))
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
  """Returns int(s) if s is an integer in the given range.

  Otherwise None.

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
  """Returns float(s) if s is a float.

  Otherwise None.

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


"""Custom judge for Pascal Walk, Code Jam 2020."""

import collections

_BAD_OUTPUT_ERROR_STR = 'Our output is incorrect:'
_BAD_OUTPUT_ERROR = (_BAD_OUTPUT_ERROR_STR + ' {}').format

_BAD_FORMAT_ERROR = 'Output is not well-formatted'
_TOO_MANY_STEPS = 'Too many steps: {}'.format
_LINE_HAS_WRONG_NUMBER_OF_ELEMENTS = 'Line {} does not have 2 values'.format
_POSITIONS_NOT_UNIQUE = 'Positions not unique'
_WRONG_STARTING_POINT = 'Wrong starting point: {}'.format
_INVALID_POSITION = 'Invalid position: {}'.format
_POSITIONS_ARE_NOT_ADJACENT = 'Position {} is not adjacent to {}'.format
_SUM_IS_TOO_LARGE = 'Sum is too large'
_SUM_IS_TOO_SMALL = 'Sum is too small: {}'.format

MAX_STEPS = 500
MAX_N = 10**9
INFINITY = MAX_N * 10  # Just something very big.
PRECOMPUTED_BINOMIAL_COEFFICIENTS = []


def PrecomputeBinomialCoefficients():
  """Fills PRECOMPUTED_BINOMIAL_COEFFICIENTS with Pascal's triangle."""
  global PRECOMPUTED_BINOMIAL_COEFFICIENTS

  d = PRECOMPUTED_BINOMIAL_COEFFICIENTS
  if d:
    return

  for r in range(MAX_STEPS + 1):
    d.append([0] * (MAX_STEPS + 1))
    d[r][0] = 1
    for k in range(1, r + 1):
      d[r][k] = min(d[r - 1][k - 1] + d[r - 1][k], INFINITY)


def BinomialCoefficient(r, k):
  """Calculates k-th number on the r-th row of Pascal's triangle.

  Assumes that all other validation steps are happened before calling this
  method. Specifically expects that r and k do not exceed MAX_STEPS.
  """
  global PRECOMPUTED_BINOMIAL_COEFFICIENTS

  if not PRECOMPUTED_BINOMIAL_COEFFICIENTS:
    PrecomputeBinomialCoefficients()

  if r > MAX_STEPS or k > MAX_STEPS:
    raise RuntimeError('Too large values for BinomialCoefficient: {}'.format(
        (r, k)))

  if r < 0 or k < 0 or k > r:
    return 0

  return PRECOMPUTED_BINOMIAL_COEFFICIENTS[r][k]


def ParseInputFile(input_file):
  """Turns an input file into a list of _CaseInputs."""
  input_lines = _utils_Tokenize(input_file)[1:]  # skip the number of test cases
  cases = []
  while input_lines:
    n = int(input_lines.pop(0)[0])
    cases.append(n)
  return cases


def VerifyOutput(lines, n):
  """Checks the output for a single test case.

  Args:
    lines: Tokenized lines (either from our IOgen's output or a contestant's
      attempt.)
    n: value of N in the current test case.

  Returns:
    None if the output is correct, or an error message.
  """
  if not lines:
    return _BAD_FORMAT_ERROR

  # Check 1st line:
  if lines[0]:
    return _BAD_FORMAT_ERROR

  # Remove empty 1st line
  lines = lines[1:]

  # Ensure that we have at least one step
  if not lines:
    return _BAD_FORMAT_ERROR

  # Check number of steps
  if len(lines) > MAX_STEPS:
    return _TOO_MANY_STEPS(len(lines))

  # Convert to int
  try:
    a = [tuple(map(int, line)) for line in lines]
  except ValueError:
    return _BAD_FORMAT_ERROR

  # Sanity check all lines
  for i, line in enumerate(a):
    # Every line contains r and k
    if len(line) != 2:
      return _LINE_HAS_WRONG_NUMBER_OF_ELEMENTS(i)
    r, k = line
    # Every (r, k) represents a position in Pascal's triangle
    if r < 1 or k < 1 or k > r:
      return _INVALID_POSITION((r, k))

  # Positions must be unique
  if len(set(a)) != len(a):
    return _POSITIONS_NOT_UNIQUE

  # Always start from the top
  if a[0] != (1, 1):
    return _WRONG_STARTING_POINT(a[0])

  # Handle first step separately
  pr = pk = 1
  s = 1

  for (r, k) in a[1:]:
    # Verify the adjacency
    ok = ((r == pr and (k == pk - 1 or k == pk + 1)) or  # On the same row
          (r == pr - 1 and (k == pk - 1 or k == pk)) or  # Going up
          (r == pr + 1 and (k == pk + 1 or k == pk)))  # Going down

    if not ok:
      return _POSITIONS_ARE_NOT_ADJACENT((r, k), (pr, pk))

    # Calculate the sum, capping it at INFINITY
    s += BinomialCoefficient(r - 1, k - 1)

    # Cut it right away if the sum is already too big
    if s > n:
      return _SUM_IS_TOO_LARGE

    pr, pk = r, k

  # Verify that the sum is correct
  if n != s:
    return _SUM_IS_TOO_SMALL(s)

  return None


def VerifyCase(output_lines, attempt_lines, n):
  """Checks a single test case.

  Args:
    output_lines: Tokenized lines from our IOgen's output.
    attempt_lines: Tokenized lines from the contestant's attempt.
    n: value of N in the current test case.

  Returns:
    An error, or None if there is no error.
  """
  output_error = VerifyOutput(output_lines, n)
  if output_error:
    return _BAD_OUTPUT_ERROR(output_error)

  attempt_error = VerifyOutput(attempt_lines, n)

  if attempt_error:
    return attempt_error

  return None


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
      je = 'JUDGE_ERROR ' if error.startswith(_BAD_OUTPUT_ERROR_STR) else ''
      return '{}Case #{}: {}'.format(je, case_num, error)

  # Everything passes.
  return None


def AssertEqual(a, b):
  if a != b:
    print('Not true that the following are equal:')
    print(a)
    print(b)
  assert a == b


def UnitTests():
  input_lines = ['3', '1', '4', '19']
  output_lines = [
      'Case #1:', '1 1', 'Case #2:', '1 1', '2 1', '2 2', '3 3', 'Case #3:',
      '1 1', '2 2', '3 2', '4 3', '5 3', '5 2', '4 1', '3 1'
  ]
  input_file = '\n'.join(input_lines)
  output_file = '\n'.join(output_lines)

  def modifyOutput(output_lines, change_at, new_value):
    """Modify a single line in output."""
    lines = list(output_lines)
    lines[change_at] = new_value
    return '\n'.join(lines)

  def addToOutput(output_lines, insert_at, new_value):
    """Add a new line to output."""
    lines = list(output_lines)
    lines.insert(insert_at, new_value)
    return '\n'.join(lines)

  def removeFromOutput(output_lines, delete_at):
    """Delete one line from output."""
    lines = list(output_lines)
    lines.pop(delete_at)
    return '\n'.join(lines)

  # Test group 1: Judge Error, Invalid token.
  AssertEqual('Invalid generator output file: Too few cases.',
              FindError(None, input_file, '', output_file))

  # Test group 2: Judge Error, output has wrong format.
  AssertEqual(
      'JUDGE_ERROR Case #1: Our output is incorrect: ' + _BAD_FORMAT_ERROR,
      FindError(None, input_file, modifyOutput(output_lines, 0, 'Case #1: 1'),
                output_file))

  AssertEqual(
      'JUDGE_ERROR Case #1: Our output is incorrect: ' + _BAD_FORMAT_ERROR,
      FindError(None, input_file, modifyOutput(output_lines, 0, 'Case #1: 1 1'),
                output_file))

  # Test group 3: Judge Error, output is wrong.
  AssertEqual(
      'JUDGE_ERROR Case #1: Our output is incorrect: ' +
      _LINE_HAS_WRONG_NUMBER_OF_ELEMENTS(0),
      FindError(None, input_file, modifyOutput(output_lines, 1, '3 2 1 4'),
                output_file))
  AssertEqual(
      'JUDGE_ERROR Case #2: Our output is incorrect: ' + _POSITIONS_NOT_UNIQUE,
      FindError(None, input_file, modifyOutput(output_lines, 6, '1 1'),
                output_file))

  # Test group 4: Attempt error, Invalid token.
  AssertEqual('Invalid attempt file: Invalid or non-ASCII characters.',
              FindError(None, input_file, output_file, chr(6)))
  AssertEqual('Invalid attempt file: Too few cases.',
              FindError(None, input_file, output_file, ''))
  AssertEqual(
      'Invalid attempt file: Expected "case #1:", found "case ##1:".',
      FindError(None, input_file, output_file,
                modifyOutput(output_lines, 0, 'Case ##1: POSSIBLE')))

  # Test group 5: Attempt Error, output has wrong format.
  AssertEqual(
      'Case #1: ' + _BAD_FORMAT_ERROR,
      FindError(None, input_file, output_file,
                removeFromOutput(output_lines, 1)))
  AssertEqual(
      'Case #1: ' + _BAD_FORMAT_ERROR,
      FindError(None, input_file, output_file,
                modifyOutput(output_lines, 1, '3 2 1.0')))
  AssertEqual(
      'Case #1: ' + _BAD_FORMAT_ERROR,
      FindError(None, input_file, output_file,
                modifyOutput(output_lines, 1, '3 2 a')))

  # Test group 6: Attempt Error, output is wrong.
  AssertEqual(
      'Case #1: ' + _LINE_HAS_WRONG_NUMBER_OF_ELEMENTS(0),
      FindError(None, input_file, output_file,
                modifyOutput(output_lines, 1, '3 2 1 4')))
  AssertEqual(
      'Case #2: ' + _LINE_HAS_WRONG_NUMBER_OF_ELEMENTS(2),
      FindError(None, input_file, output_file,
                modifyOutput(output_lines, 5, '1')))
  AssertEqual(
      'Case #2: ' + _POSITIONS_NOT_UNIQUE,
      FindError(None, input_file, output_file,
                modifyOutput(output_lines, 6, '1 1')))
  AssertEqual(
      'Case #1: ' + _INVALID_POSITION((0, 1)),
      FindError(None, input_file, output_file,
                modifyOutput(output_lines, 1, '0 1')))
  AssertEqual(
      'Case #1: ' + _INVALID_POSITION((1, 0)),
      FindError(None, input_file, output_file,
                modifyOutput(output_lines, 1, '1 0')))
  AssertEqual(
      'Case #1: ' + _INVALID_POSITION((-1, 1)),
      FindError(None, input_file, output_file,
                modifyOutput(output_lines, 1, '-1 1')))
  AssertEqual(
      'Case #1: ' + _INVALID_POSITION((1, -1)),
      FindError(None, input_file, output_file,
                modifyOutput(output_lines, 1, '1 -1')))
  AssertEqual(
      'Case #1: ' + _INVALID_POSITION((1, 2)),
      FindError(None, input_file, output_file,
                modifyOutput(output_lines, 1, '1 2')))

  wrong_output_lines = [
      'Case #1:', '2 2', 'Case #2:', '1 1', '2 1', '2 2', '3 3', 'Case #3:',
      '1 1', '2 2', '3 2', '4 3', '5 3', '5 2', '4 1', '3 1'
  ]
  AssertEqual(
      'Case #1: ' + _WRONG_STARTING_POINT((2, 2)),
      FindError(None, input_file, output_file, '\n'.join(wrong_output_lines)))

  wrong_output_lines = [
      'Case #1:', '1 1', 'Case #2:', '1 1', '2 1', '2 2', '3 3', 'Case #3:',
      '1 1', '2 2', '3 2', '4 3', '5 3', '5 2', '4 1', '4 2'
  ]
  AssertEqual(
      'Case #3: ' + _SUM_IS_TOO_LARGE,
      FindError(None, input_file, output_file, '\n'.join(wrong_output_lines)))

  wrong_output_lines = [
      'Case #1:', '1 1', 'Case #2:', '1 1', '2 1', '2 2', '3 3', 'Case #3:',
      '1 1', '2 2', '3 2', '4 3', '5 3', '5 2', '4 1'
  ]
  AssertEqual(
      'Case #3: ' + _SUM_IS_TOO_SMALL(18),
      FindError(None, input_file, output_file, '\n'.join(wrong_output_lines)))

  wrong_output_lines = [
      'Case #1:', '1 1', 'Case #2:', '1 1', '2 1', '2 2', '3 3', 'Case #3:',
      '1 1', '2 2', '3 2', '4 3', '5 3'
  ]
  for p in ((4, 1), (4, 4), (5, 1), (5, 5), (6, 1), (6, 2), (6, 5)):
    AssertEqual(
        'Case #3: ' + _POSITIONS_ARE_NOT_ADJACENT(p, (5, 3)),
        FindError(None, input_file, output_file,
                  '\n'.join(wrong_output_lines + ['{} {}'.format(*p)])))

  too_many_steps = [
      'Case #1:',
      '1 1',
      'Case #2:',
      '1 1',
      '2 1',
      '2 2',
      '3 3',
      'Case #3:',
  ] + ['{} {}'.format(x + 1, x + 1) for x in range(MAX_STEPS + 1)]
  AssertEqual(
      'Case #3: ' + _TOO_MANY_STEPS(501),
      FindError(None, input_file, output_file, '\n'.join(too_many_steps)))

  overflowing = [
      'Case #1:',
      '1 1',
      'Case #2:',
      '1 1',
      '2 1',
      '3 2',
      'Case #3:',
  ] + ['{} {}'.format(x + 1, (x + 2) // 2) for x in range(MAX_STEPS)]
  AssertEqual('Case #3: ' + _SUM_IS_TOO_LARGE,
              FindError(None, input_file, output_file, '\n'.join(overflowing)))

  # Test group 7: Correct output
  AssertEqual(None, FindError(None, input_file, output_file, output_file))

  max_steps_input_file = '\n'.join(['1', '500'])
  max_steps_output_file = '\n'.join(
      ['Case #1:'] + ['{} {}'.format(x + 1, x + 1) for x in range(MAX_STEPS)])
  AssertEqual(
      None,
      FindError(None, max_steps_input_file, max_steps_output_file,
                max_steps_output_file))

  # Test group 8: Verifies Pascal triangle calculation

  AssertEqual(1, BinomialCoefficient(0, 0))
  AssertEqual(0, BinomialCoefficient(0, 1))
  AssertEqual(0, BinomialCoefficient(0, -1))
  for r in range(1, MAX_STEPS + 1):
    for k in range(MAX_STEPS + 1):
      expected = min(
          INFINITY,
          BinomialCoefficient(r - 1, k - 1) + BinomialCoefficient(r - 1, k))
      AssertEqual(expected, BinomialCoefficient(r, k))

  print('Unit tests passed')
  sys.exit(0)


import sys
if __name__ == '__main__':
  if sys.argv[1] == '-2':
    UnitTests()

  result = FindError(
      None,
      file(sys.argv[1]).read(),  # input path
      file(sys.argv[3]).read(),  # iogen output path
      file(sys.argv[2]).read())  # attempt output path
  if result:
    print >> sys.stderr, result
    sys.exit(1)
