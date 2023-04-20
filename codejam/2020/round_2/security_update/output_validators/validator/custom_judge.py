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


"""Custom judge for Security Update, Code Jam 2020."""

from heapq import heappush, heappop
from math import ceil
import collections
import itertools

_BAD_OUTPUT_ERROR_STR = 'Our output is incorrect:'
_BAD_OUTPUT_ERROR = (_BAD_OUTPUT_ERROR_STR + ' {}').format

_BAD_FORMAT_ERROR = 'Output is not well-formatted'
_WRONG_NUMBER_OF_WEIGHTS = 'Wrong number of weights'
_UNABLE_TO_PARSE_ERROR = 'Unable to parse operation values'
_INVALID_WEIGHT_TOO_LARGE = 'Invalid weight. Must be <= 10^6'
_INVALID_WEIGHT_TOO_SMALL = 'Invalid weight. Must be >= 1'

_CaseInput = collections.namedtuple('_CaseInput', ['hints', 'edges'])


class minheap:

  def __init__(self):
    self.heap = []
    self.entries = {}
    self.count = 0

  def push(self, value, priority):
    if value in self.entries:
      self.entries[value][-1] = None
      del self.entries[value]
    self.count += 1
    entry = [priority, self.count, value]
    self.entries[value] = entry
    heappush(self.heap, entry)

  def pop(self):
    while self.heap:
      _, _, value = heappop(self.heap)
      if value is not None:
        del self.entries[value]
        return value


def ParseInputFile(input_file):
  """Turns an input file into a list of _CaseInputs."""
  input_lines = _utils_Tokenize(input_file)
  n_cases = int(input_lines.pop(0)[0])
  cases = []
  for _ in range(n_cases):
    nodes, edges = map(int, input_lines.pop(0))
    cases.append(
        _CaseInput(
            map(int, input_lines.pop(0)),
            [map(int, input_lines.pop(0)) for e in range(edges)]))
  return cases


def VerifyOutput(lines, case):
  """Checks the output for a single test case.

  Args:
    lines: Tokenized lines (either from our I/OGen's output or a contestant's
      attempt.)
    case: A _CaseInput representing a single test case.

  Returns:
    A string containing an error message if an error is found, or None of there
      are no errors.
  """

  # check lines are parsed.
  if not lines:
    return _BAD_FORMAT_ERROR

  # check first line has values
  if not lines[0]:
    return _BAD_FORMAT_ERROR

  # convert input to ints
  try:
    provided_weights = [int(token) for token in lines[0]]
  except ValueError:
    return _UNABLE_TO_PARSE_ERROR

  # check length of edges is equal to length of weights provided
  if len(provided_weights) != len(case.edges):
    return _WRONG_NUMBER_OF_WEIGHTS

  # check provided weights are within bounds
  for weight in provided_weights:
    if weight > 10**6:
      return _INVALID_WEIGHT_TOO_LARGE
    if weight <= 0:
      return _INVALID_WEIGHT_TOO_SMALL

  # set up graph
  cost = {}
  neighbors = collections.defaultdict(set)
  for (u, v), w in zip(case.edges, provided_weights):
    cost[u, v] = w
    cost[v, u] = w
    neighbors[u].add(v)
    neighbors[v].add(u)

  # run Dijkstra with a min heap to find min distance from source of all nodes
  dist = {node: float('inf') for node in range(1, len(case.hints) + 2)}
  dist[1] = 0
  Q = minheap()
  Q.push(1, 0)
  while Q.heap:
    u = Q.pop()
    for v in neighbors[u]:
      alt = dist[u] + cost[u, v]
      if alt < dist[v]:
        dist[v] = alt
        Q.push(v, alt)

  # rank the distances
  ranked_distance = zip(sorted(list(dist.values())), itertools.count())
  nth_distance = {node: rank for node, rank in reversed(ranked_distance)}

  # check that everything adhere to given hints. If not, list errors
  errors = []
  for node, hint in zip(itertools.count(2), case.hints):
    if hint > 0 and dist[node] != hint:
      errors.append('Node {} has minimum distance {}, should be {}.'.format(
          node, dist[node], hint))
    elif hint < 0 and nth_distance[dist[node]] != -hint:
      errors.append('Node {} has rank {}, should be {}.'.format(
          node, nth_distance[dist[node]], -hint))

  return ' '.join(errors) if errors else None


def VerifyCase(output_lines, attempt_lines, case):
  """Checks a single test case.

  Args:
    output_lines: Tokenized lines from our I/OGen's output.
    attempt_lines: Tokenized lines from the contestant's attempt.
    case: A CaseInput representing a single test case.

  Returns:
    An error, or None if there is no error.
  """

  output_error = VerifyOutput(output_lines, case)
  if output_error:
    return _BAD_OUTPUT_ERROR(output_error)
  attempt_error = VerifyOutput(attempt_lines, case)
  return attempt_error


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


def RunUnitTests():
  input_lines = [
      '3',
      '4 4',
      '5 10 -2',
      '1 2',
      '1 3',
      '2 4',
      '3 4',
      '6 9',
      '10 -2 -5 15 20',
      '1 2',
      '1 3',
      '2 3',
      '2 4',
      '2 5',
      '3 5',
      '3 6',
      '4 5',
      '5 6',
      '4 3',
      '1000000 -2 -3',
      '1 2',
      '2 3',
      '3 4',
  ]
  output_lines = [
      'Case #1: 5 10 1 5',
      'Case #2: 10 12 4 15 8 3 9 7 5',
      'Case #3: 1000000 1 1',
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

  # Test group 1: Judge Error, Invalid token.
  AssertEqual('Invalid generator output file: Too few cases.',
              FindError(None, input_file, '', output_file))
  AssertEqual(
      'Invalid generator output file: File does not begin with "case #1:".',
      FindError(None, input_file, modifyOutput(output_lines, 0, '1 1 1'),
                output_file))

  # Test group 2: Judge Error, output has wrong format.
  AssertEqual(
      'JUDGE_ERROR Case #1: Our output is incorrect: ' + _BAD_FORMAT_ERROR,
      FindError(None, input_file, modifyOutput(output_lines, 0, 'Case #1:'),
                output_file))

  # Test group 3: Judge Error, output is wrong.
  AssertEqual(
      'JUDGE_ERROR Case #1: Our output is incorrect: ' +
      _WRONG_NUMBER_OF_WEIGHTS,
      FindError(None, input_file, modifyOutput(output_lines, 0, 'Case #1: 1 1'),
                output_file))
  AssertEqual(
      'JUDGE_ERROR Case #1: Our output is incorrect: ' + _UNABLE_TO_PARSE_ERROR,
      FindError(None, input_file, modifyOutput(output_lines, 0, 'Case #1: a'),
                output_file))
  AssertEqual(
      'JUDGE_ERROR Case #1: Our output is incorrect: ' +
      _INVALID_WEIGHT_TOO_LARGE,
      FindError(None, input_file,
                modifyOutput(output_lines, 0, 'Case #1: 1000001 1 1 1'),
                output_file))
  AssertEqual(
      'JUDGE_ERROR Case #1: Our output is incorrect: ' +
      _INVALID_WEIGHT_TOO_SMALL,
      FindError(None, input_file,
                modifyOutput(output_lines, 0, 'Case #1: 0 1 1 1'), output_file))
  AssertEqual(
      'JUDGE_ERROR Case #1: Our output is incorrect:'
      ' Node 2 has minimum distance 6, should be 5.',
      FindError(None, input_file,
                modifyOutput(output_lines, 0, 'Case #1: 6 10 1 5'),
                output_file))
  AssertEqual(
      'JUDGE_ERROR Case #1: Our output is incorrect:'
      ' Node 4 has rank 3, should be 2.',
      FindError(None, input_file,
                modifyOutput(output_lines, 0, 'Case #1: 5 10 6 5'),
                output_file))
  AssertEqual(
      'JUDGE_ERROR Case #1: Our output is incorrect:'
      ' Node 3 has minimum distance 11, should be 10.'
      ' Node 4 has rank 3, should be 2.',
      FindError(None, input_file,
                modifyOutput(output_lines, 0, 'Case #1: 5 11 7 5'),
                output_file))

  # Test group 4: Attempt Error, Invalid token.
  AssertEqual('Invalid attempt file: Too few cases.',
              FindError(None, input_file, output_file, ''))

  # Test group 5: Attempt Error, output has wrong format.
  AssertEqual(
      'Case #1: ' + _BAD_FORMAT_ERROR,
      FindError(None, input_file, output_file,
                modifyOutput(output_lines, 0, 'Case #1:')))

  # Test group 6: Attempt Error, output is wrong.
  AssertEqual(
      'Case #1: ' + _WRONG_NUMBER_OF_WEIGHTS,
      FindError(None, input_file, output_file,
                modifyOutput(output_lines, 0, 'Case #1: 1 1')))
  AssertEqual(
      'Case #1: ' + _UNABLE_TO_PARSE_ERROR,
      FindError(None, input_file, output_file,
                modifyOutput(output_lines, 0, 'Case #1: a')))
  AssertEqual(
      'Case #1: ' + _INVALID_WEIGHT_TOO_LARGE,
      FindError(None, input_file, output_file,
                modifyOutput(output_lines, 0, 'Case #1: 1000001 1 1 1')))
  AssertEqual(
      'Case #1: ' + _INVALID_WEIGHT_TOO_SMALL,
      FindError(None, input_file, output_file,
                modifyOutput(output_lines, 0, 'Case #1: 0 1 1 1')))
  AssertEqual(
      'Case #1:'
      ' Node 2 has minimum distance 6, should be 5.',
      FindError(None, input_file, output_file,
                modifyOutput(output_lines, 0, 'Case #1: 6 10 1 5')))
  AssertEqual(
      'Case #1:'
      ' Node 4 has rank 3, should be 2.',
      FindError(None, input_file, output_file,
                modifyOutput(output_lines, 0, 'Case #1: 5 10 6 5')))
  AssertEqual(
      'Case #1:'
      ' Node 3 has minimum distance 11, should be 10.'
      ' Node 4 has rank 3, should be 2.',
      FindError(None, input_file, output_file,
                modifyOutput(output_lines, 0, 'Case #1: 5 11 7 5')))

  # Test group 7: Verifies no error on correct output.
  AssertEqual(None, FindError(None, input_file, output_file, output_file))

  print('Unit tests passed.')
  sys.exit(0)


import sys
if __name__ == '__main__':
  if sys.argv[1] == '-2':
    RunUnitTests()

  result = FindError(
      None,
      file(sys.argv[1]).read(),  # input path
      file(sys.argv[3]).read(),  # iogen output path
      file(sys.argv[2]).read())  # attempt output path
  if result:
    print >> sys.stderr, result
    sys.exit(1)
