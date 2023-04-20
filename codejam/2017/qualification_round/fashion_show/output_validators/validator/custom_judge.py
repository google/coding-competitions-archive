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
"""Custom judge for Fashion Show, Code Jam 2017."""

__author__ = 'tullis@google.com (Ian Tullis)'

import collections


# The various errors we can return.
_BAD_GRID_ERROR = 'Grid error in {0} {1}'.format
_BAD_HEADER_ERROR = 'Wrong number/types of tokens in header.'
_BAD_MODEL_ERROR = 'Wrong format or parameters for a model.'
_BAD_OUTPUT_ERROR = 'Our output is incorrect: {0}'.format
_BAD_REPLACEMENT_ERROR = (
    'Replaced an o or used a non-o replacement at coords ({0}, {1}).'.format)
_BAD_SCORE_CLAIM_ERROR = (
    'Solution didn\'t claim the right score')
_DUPLICATE_MODIFICATION_ERROR = (
    'Changes to the grid modify the same coordinates ({0}, {1}) twice.'.format)
_INCONSISTENT_SCORE_ERROR = 'Solution didn\'t achieve the score it claimed.'
_WRONG_NUM_LINES_ERROR = 'Number of lines does not match header.'


"""Parsed information for a single test case.

Attributes:
  n: The dimension of the square grid.
  preplaced_models: A list of tuples of the form (type, r, c); each represents
     one preplaced model in the grid.
  preplaced_dict: A double dictionary corresponding to the grid;
     preplaced_dict[r][c] gives the type of the model that is there.
  score_so_far: The number of style points from the preplaced models.
"""
_CaseInput = collections.namedtuple(
    '_CaseInput', ['n', 'preplaced_models', 'preplaced_dict', 'score_so_far'])


def ParseInputFile(input_file):
  """Turns an input file into a list of _CaseInputs."""
  input_lines = _utils_Tokenize(input_file)[1:]  # skip the number of cases
  cases = []
  while input_lines:
    models = []
    preplaced_dict = {}
    score_so_far = 0
    n, m = [int(x) for x in input_lines.pop(0)]
    for _ in range(m):
      line = input_lines.pop(0)
      t, r, c = line
      score_so_far += 2 if t == 'o' else 1
      r = int(r)
      c = int(c)
      models.append((t, r, c))
      if r not in preplaced_dict:
        preplaced_dict[r] = {}
      preplaced_dict[r][c] = t
    cases.append(_CaseInput(n, tuple(models), preplaced_dict, score_so_far))
  return cases


def _IsLegal(n, models):
  """Determines whether a grid is legal.

  Assumes that the input passed in consists only of valid model types with
  valid, non-duplicate locations.

  Note that this does NOT test whether a grid has an optimal score.

  Args:
    n: The dimensions of the grid.
    models: A list of tuples: the models on the grid.
        Each tuple is of the form (t, r_i, c_i).

  Returns:
    None if the grid is legal, or an error string otherwise.
  """
  rows, cols, updiags, downdiags = set(), set(), set(), set()
  for m in models:
    t, r, c = m
    if t != '+':
      if r in rows:
        return _BAD_GRID_ERROR('row', r)
      if c in cols:
        return _BAD_GRID_ERROR('column', c)
      rows.add(r)
      cols.add(c)
    if t != 'x':
      # Up-diagonals start with 0 for the top left cell, then 1 for the
      # cells below and to the right of that, and so on.
      u = r + c - 2
      # Down-diagonals start with 0 for the bottom left cell, then 1 for the
      # cells above and to the right of that, and so on.
      d = n - 1 - r + c
      if u in updiags:
        return _BAD_GRID_ERROR('up-diagonal', u)
      if d in downdiags:
        return _BAD_GRID_ERROR('down-diagonal', d)
      updiags.add(u)
      downdiags.add(d)
  return None


def VerifyOutput(lines, case, expected_score):
  """Checks the output for a single test case.

  Args:
    lines: Tokenized lines (either from our I/OGen's output or a contestant's
        attempt.)
    case: A _CaseInput representing a single test case.
    expected_score: The score from our output. We assume that our output's
        score is correct (delegating it to the I/OGen solution to get that
        right.)

  Returns:
    A tuple of two values:
        1. None if the output is correct, or an error message.
        2. The score if the output is correct, or None.
  """
  if (not lines) or len(lines[0]) != 2:
    return _BAD_HEADER_ERROR, None
  try:
    claimed_score = int(lines[0][0])
    new_models = int(lines[0][1])
  except ValueError:
    return _BAD_HEADER_ERROR, None
  if expected_score and claimed_score < expected_score:
    return _BAD_SCORE_CLAIM_ERROR, None
  if new_models != len(lines[1:]):
    return _WRONG_NUM_LINES_ERROR, None
  models = list(case.preplaced_models)
  cells_modified = set()
  actual_score = case.score_so_far
  for line in lines[1:]:
    if len(line) != 3:
      return _BAD_MODEL_ERROR, None
    t, r, c = line
    # We can safely assume that t is a string since it has been through the
    # tokenizer.
    if t not in '+xo':
      return _BAD_MODEL_ERROR, None
    try:
      r = int(r)
      c = int(c)
    except ValueError:
      return _BAD_MODEL_ERROR, None
    if r < 1 or r > case.n or c < 1 or c > case.n:
      return _BAD_MODEL_ERROR, None
    if (r, c) in cells_modified:
      return _DUPLICATE_MODIFICATION_ERROR(r, c), None
    cells_modified.add((r, c))
    if r in case.preplaced_dict and c in case.preplaced_dict[r]:
      if t != 'o':
        return _BAD_REPLACEMENT_ERROR(r, c), None
      existing_type = case.preplaced_dict[r][c]
      if existing_type == 'o':
        return _BAD_REPLACEMENT_ERROR(r, c), None
      models.remove((existing_type, r, c))
      models.append(('o', r, c))
      actual_score += 1
    else:
      actual_score += 2 if t == 'o' else 1
      models.append((t, r, c))
  if actual_score != claimed_score:
    return _INCONSISTENT_SCORE_ERROR, None
  err = _IsLegal(case.n, models)
  if err:
    return err, None
  if expected_score and (actual_score > expected_score):
    return (_BAD_OUTPUT_ERROR(
        'We expected score {}; they got valid score {}'.format(
            expected_score, actual_score)),
            None)
  return None, actual_score


def VerifyCase(output_lines, attempt_lines, case):
  """Checks a single test case.

  Args:
    output_lines: Tokenized lines from our I/OGen's output.
    attempt_lines: Tokenized lines from the contestant's attempt.
    case: A CaseInput representing a single test case.
  Returns:
    An error, or None if there is no error.
  """

  output_error, expected_score = VerifyOutput(output_lines, case, None)
  if output_error is not None:
    return _BAD_OUTPUT_ERROR(output_error)
  attempt_error, _ = VerifyOutput(attempt_lines, case, expected_score)
  return attempt_error


def FindError(unused_self, input_file, output_file, attempt):
  """See judge.Judge.FindError()."""
  input_cases = ParseInputFile(input_file)
  num_cases = len(input_cases)
  output, attempt, error = _utils_TokenizeAndSplitCases(output_file, attempt,
                                                       num_cases)
  if error is not None:
    return error

  for case_num, (case, output_lines, attempt_lines) in enumerate(
      zip(input_cases, output, attempt), start=1):
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
