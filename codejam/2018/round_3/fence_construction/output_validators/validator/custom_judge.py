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
"""A custom judge for "Fence Construction", Code Jam 2018."""

__author__ = "trankevin@google.com (Kevin Tran)"

import math


# Errors
INVALID_PERMUTATION_SIZE = "Permutation contains the wrong number of elements"
NOT_PERMUTATION = "Permutation does not contain each integer once"
ORDER_NOT_SATISFIED = "The first K fences are not built in the correct order"

OUTPUT_HAS_TOO_MANY_LINES = "Contestant output must have only one line"
FAILED_TO_PARSE_OUTPUT = "Could not parse the contestant's output"

CANNOT_BE_BUILT = "The fences cannot be built in this order"


def ParseInputFile(input_file):
  """Parses an input text into individual test cases.

  Assumes that the input text is valid according to the problem statement.

  Args:
    input_file: str, the raw contents of an input text file.

  Returns:
    A list of testcases. Each testcase is a tuple of (K, fences),
  """
  input_lines = _utils_Tokenize(input_file)
  testcases = []
  cases = int(input_lines[0][0])
  line_at = 1
  for _ in xrange(cases):
    num_f, k = map(int, input_lines[line_at])
    fences = []
    for _ in xrange(num_f):
      line_at += 1
      f = tuple(map(int, input_lines[line_at]))
      fences.append(f)
    testcases.append((k, fences))
    line_at += 1
  return testcases


def CheckPermutation(case, perm):
  """Given a list of integers, checks if it is a valid permutation.

  The permutation is checked to see if it satisfies the requested
  ordering in the problem. Does not check the solution is feasible
  (that's done in CheckCorrectness).

  Args:
    case: The parsed testcase
    perm: A list of integers representing the permutation

  Returns:
    None if the permutation satisfies the requirements, otherwise
    it returns an error string.
  """
  k, fences = case
  if len(fences) != len(perm):
    return INVALID_PERMUTATION_SIZE
  if sorted(perm) != range(1, len(fences)+1):
    return NOT_PERMUTATION
  last_seen = 0
  for x in perm:
    if x == last_seen+1:
      last_seen += 1
  if last_seen < k:
    return ORDER_NOT_SATISFIED
  return None


def ParseListOfInts(tokens):
  """Parse a list of ints from the list of tokens.

  Args:
    tokens: the list of string tokens for one case returned by
      TokenizeAndSplitCases

  Returns:
    (perm, None), where perm is the parsed permutation.
    If parsing fails, returns (None, error), where error is the error string.
  """
  try:
    if len(tokens) != 1:
      return None, OUTPUT_HAS_TOO_MANY_LINES
    ints = map(int, tokens[0])
  except ValueError:
    return None, FAILED_TO_PARSE_OUTPUT

  return ints, None


def CheckCorrectness(case, perm):
  """Checks if a parsed solution is correct.

  Args:
    case: tuple of (K, fence)
    perm: list of fence IDs (one indexed)

  Returns:
    None, if the solution is valid. OTherwise, returns
    an error string
  """
  _, fences = case
  for i in range(len(perm)):
    perm[i] -= 1
  soln = Solve(perm, fences)
  if soln is None:
    return CANNOT_BE_BUILT
  return None


def VerifyCase(case, perm):
  """Checks a single test case.

  Args:
    case: tuple of (K, fence), representing a testcase
    perm: list of fence IDs (one indexed) representing the
      solution to be checked

  Returns:
    An error string, or None if there is no error.
  """

  error = CheckPermutation(case, perm)
  if error:
    return error
  return CheckCorrectness(case, perm)


def FindError(unused_self, input_file, output_file, attempt):
  """See judge.Judge.FindError()."""
  input_cases = ParseInputFile(input_file)

  _, attempt, error = _utils_TokenizeAndSplitCases(output_file, attempt,
                                                  len(input_cases))
  if error:
    return error

  for case_num, (input_case, attempt_lines) in enumerate(
      zip(input_cases, attempt),
      start=1):
    perm, error = ParseListOfInts(attempt_lines)
    if error is not None:
      return "Case #{}: {}".format(case_num, error)

    error = VerifyCase(input_case, perm)
    if error is not None:
      return "Case #{}: {}".format(case_num, error)

  # Everything passes.
  return None

def Add(p, pi, x, y):
  """Add a new point (x, y).

  Args:
    p: index -> point.
    pi: point -> index.
    x: x-coordinate of new point.
    y: y-coordinate of new point.
  """
  if (x, y) not in pi:
    pi[(x, y)] = len(p)
    p.append((x, y))


def Faces(a, ao):
  """Find all faces given adjacency list of points.

  Args:
    a: a[i] = indices of points adjacent to i-th point.
    ao: ao[i] = map point -> index in a.

  Returns:
    List of faces.
  """
  s = set()
  r = []
  for oi in xrange(len(a)):
    for oj in xrange(len(a[oi])):
      if (oi, a[oi][oj]) not in s:
        i, j = oi, oj
        l = []
        while True:
          # print i, p[i], "-", a[i][j], p[a[i][j]]
          assert (i, a[i][j]) not in s, "Seen edge twice"
          l.append((i, a[i][j]))
          s.add((i, a[i][j]))
          ni = a[i][j]
          nj = (ao[ni][i] + 1) % len(a[ni])
          if ni == oi and nj == oj:
            break
          i, j = ni, nj
        # print l
        r.append(l)
  return r


def Solve(k, e):
  """Find a valid permutation with given prefix.

  Args:
    k: prefix of solution.
    e: list of edges.

  Returns:
    A valid permutation.
    Throws exception if no valid permutation found.
  """
  assert k
  # point -> int
  pi = {}
  # int -> point
  p = []
  # point ids to fence id
  ei = {}
  for i, (x, y, z, w) in enumerate(e):
    Add(p, pi, x, y)
    Add(p, pi, z, w)
    ei[(pi[(x, y)], pi[(z, w)])] = i
    ei[(pi[(z, w)], pi[(x, y)])] = i
  n = len(p)
  # point -> list of adjacent points
  a = [[] for _ in xrange(n)]
  # point -> index in a
  ao = [{} for _ in xrange(n)]
  for (x, y, z, w) in e:
    a[pi[(x, y)]].append(pi[(z, w)])
    a[pi[(z, w)]].append(pi[(x, y)])
  for i in xrange(n):
    orig = p[i]
    a[i].sort(key=lambda i: math.atan2(p[i][1] - orig[1], p[i][0] - orig[0]))
    for j in xrange(len(a[i])):
      ao[i][a[i][j]] = j
  # List of polygons
  f = [set([ei[x] for x in fi]) for fi in Faces(a, ao)]
  # print f
  wf = [[] for _ in xrange(len(e))]
  for fi, fiv in enumerate(f):
    for i in fiv:
      wf[i].append(fi)
  # print wf
  s = set([k[-1]])
  q = set([k[-1]])
  r = []
  while q:
    i = -1
    if i not in q:
      for j in q:
        if j not in k or j == k[-1]:
          i = j
          break  # Get any unordered fence or the next one in the order
    # Invalid
    if i == -1:
      break
    if k and i == k[-1]:
      k.pop()
    r.append(i)
    for fi in wf[i]:
      for j in f[fi]:
        if j not in s:
          q.add(j)
          s.add(j)
    q.remove(i)
  if len(r) != len(e) or len(k) != 0:
    return None
  return list(reversed([x + 1 for x in r]))

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
