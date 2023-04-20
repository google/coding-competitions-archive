# Copyright 2011 Google Inc. All Rights Reserved.
"""Basic utilities for custom judges."""

import sys


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
  return list(filter(None, row.split(' '))
              for row in text.split('\n')
              if row.strip())



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


"""Custom judge for Simple Polygon, Kick Start."""

import collections

MIN_XY = 0
MAX_XY = 10**9

_BAD_OUTPUT_ERROR_STR = 'Our output is incorrect:'
_BAD_OUTPUT_ERROR = (_BAD_OUTPUT_ERROR_STR + ' {}').format

_BAD_FORMAT_ERROR = 'Output is not well-formatted'
_COLLINEAR_ERROR = 'Vertices contain collinear edges'
_SELF_INTERSECTING_ERROR = 'Polygon is self-intersecting'
_WRONG_ANSWER = 'The answer is not equivalent to A/2'

"""Parsed information for a single test case."""
_CaseInput = collections.namedtuple('_CaseInput', ['N', 'A'])
_Vertex = collections.namedtuple('_Vertex', ['X', 'Y'])
_Segment = collections.namedtuple('_Segment', ['A', 'B'])


def ParseInputFile(input_file):
  """Turns an input file into a list of _CaseInputs."""
  # skip the number of cases (line 0)
  input_lines = _utils_Tokenize(input_file)[1:]
  cases = []
  for input_line in input_lines:
    N, A = map(int, input_line)
    cases.append(_CaseInput(N, A))
  return cases


def VerifyOutput(lines, case):
  """Checks the output for a single test case.

  Args:
    lines: Tokenized lines (either from our I/OGen's output or a contestant's
      attempt.)
    case: A _CaseInput representing a single test case.

  Returns:
    None if the output is correct, or an error message.
  """
  if len(lines) > 1:
    if len(lines[0]) != 1 or lines[0][0] != 'POSSIBLE':
      return _BAD_FORMAT_ERROR

    if len(lines) != case.N + 1:
      return _BAD_FORMAT_ERROR

    for line in lines[1:]:
      if (len(line) != 2 or
          _utils_ToInteger(line[0], MIN_XY, MAX_XY) is None or
          _utils_ToInteger(line[1], MIN_XY, MAX_XY) is None):
        return _BAD_FORMAT_ERROR

    vertices = ConvertLinesToVertices(lines[1:])
    if IsCollinear(vertices):
      return _COLLINEAR_ERROR

    segments = ConvertVerticesToSegments(vertices)
    if IsSelfIntersecting(segments):
      return _SELF_INTERSECTING_ERROR

  if len(lines) == 1:
    if len(lines[0]) != 1 or lines[0][0] != 'IMPOSSIBLE':
      return _BAD_FORMAT_ERROR

  return None


def IsCollinear(vertices):
  """Returns whether any 3 sequential vertices are collinear.

  For every 3 vertices, checks if the area (i.e. a triangle) is > 0. If the are
  is equal to 0, they are collinear.
  """
  a = vertices[-2]
  b = vertices[-1]
  for c in vertices:
    area = GetDoublePolygonArea([a, b, c], 3)
    if area == 0:
      return True
    a, b = b, c

  return False


def IsSelfIntersecting(segments):
  """Returns whether any of the line segments intersect with each other.

  Each segment is compared with every other segment O(n^2).
  """
  for i in range(len(segments)):
    # Neighboring segments are skipped since they should share a common
    # point and `IsCollinear` fn should capture if they overlap.
    for j in range(i + 2, len(segments)):
      # Skip the first and last segment since they should share a common vertex
      if i == 0 and j == len(segments) - 1: continue

      if CheckIntersection(segments[i], segments[j]):
        return True

  return False


def CheckIntersection(segment_a, segment_b):
  """Returns whether two segments intersect.

  Ref: https://www.geeksforgeeks.org/check-if-two-given-line-segments-intersect/
  """

  def _IsPointOnSegment(p, q, r):
    """Returns whether point r lies on segment (p, q)."""
    return (q.X <= max(p.X, r.X) and q.X >= min(p.X, r.X) and
            q.Y <= max(p.Y, r.Y) and q.Y >= min(p.Y, r.Y))

  def _GetOrientation(p, q, r):
    """Returns the orientation of points p, q, and r.

    Returns:
      0 if collinear
      1 if clockwise
      -1 if counter-clockwise
    """
    val = ((q.Y - p.Y) * (r.X - q.X)) - \
          ((q.X - p.X) * (r.Y - q.Y))
    if val == 0: return 0
    return 1 if val > 0 else -1

  p1, q1 = segment_a
  p2, q2 = segment_b

  o1 = _GetOrientation(p1, q1, p2)
  o2 = _GetOrientation(p1, q1, q2)
  o3 = _GetOrientation(p2, q2, p1)
  o4 = _GetOrientation(p2, q2, q1)

  if o1 != o2 and o3 != o4: return True
  if o1 == 0 and _IsPointOnSegment(p1, p2, q1): return True
  if o2 == 0 and _IsPointOnSegment(p1, q2, q1): return True
  if o3 == 0 and _IsPointOnSegment(p2, p1, q2): return True
  if o4 == 0 and _IsPointOnSegment(p2, q1, q2): return True

  return False


def ConvertLinesToVertices(lines):
  """Converts a set of lines to vertices.

  Ordering of lines is kept the same. Converts each line to an _Vertex objects.
  """
  return [_Vertex(_utils_ToInteger(v[0]), _utils_ToInteger(v[1]))
          for v in lines]


def ConvertVerticesToSegments(vertices):
  """Converts a set of vertices to segments.

  Ordering of segments is kept the same. Segments are created from neighboring
  vertices into _Segment objects.
  """
  return [_Segment(vertices[i], vertices[i + 1])
          for i in range(len(vertices) - 1)] + \
      [_Segment(vertices[-1], vertices[0])]


def GetDoublePolygonArea(vertices, n):
  """Returns double the area of the polygon for a given test case.

  Ref: https://en.wikipedia.org/wiki/Shoelace_formula
  """
  area = 0
  j = n - 1
  for i in range(n):
    area += ((vertices[j].X + vertices[i].X) *
             (vertices[j].Y - vertices[i].Y))
    j = i

  return abs(area)


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
  if output_error is not None:
    return _BAD_OUTPUT_ERROR(output_error)

  attempt_error = VerifyOutput(attempt_lines, case)
  if attempt_error is not None:
    return attempt_error

  return None


def FindError(unused_self, input_file, output_file, attempt_file):
  """See judge.Judge.FindError()."""
  input_cases = ParseInputFile(input_file)
  num_cases = len(input_cases)
  output_cases, attempt_cases, error = _utils_TokenizeAndSplitCases(
      output_file, attempt_file, num_cases, True)
  if error is not None:
    return error

  for case_num, (case, output_lines, attempt_lines) in enumerate(
      zip(input_cases, output_cases, attempt_cases), start=1):
    error = VerifyCase(output_lines, attempt_lines, case)
    if error is not None:
      je = 'JUDGE_ERROR ' if error.startswith(_BAD_OUTPUT_ERROR_STR) else ''
      return '{}Case #{}: {}'.format(je, case_num, error)

    # Check IMPOSSIBLE case
    if len(attempt_lines) == 1:
      if (attempt_lines[0][0] != output_lines[0][0] or
          attempt_lines[0][0] != 'IMPOSSIBLE'):
        return _WRONG_ANSWER + ' (got: %s, expected: %s)' % (
          attempt_lines[0][0], output_lines[0][0])

    # Check POSSIBLE case
    else:
      vertices = ConvertLinesToVertices(attempt_lines[1:])
      actual_area = GetDoublePolygonArea(vertices, case.N)
      expected_area = case.A

      if actual_area != expected_area:
        return _WRONG_ANSWER + ' (got: %s, expected: %s)' % (
          actual_area, expected_area)

  # Everything passes.
  return None


class SimplePolygonUnitTest():

  def assertIsNone(self, a):
    assert a is None

  def assertEqual(self, a, b):
    assert a == b, (a, b)

  def assertStartsWith(self, a, b):
    assert a.startswith(b), (a, b)

  input_file = """
2
4 36
5 2
""".lstrip()

  output_file = """
Case #1: POSSIBLE
2 9
6 9
8 6
0 6
Case #2: IMPOSSIBLE
""".lstrip()

  alternative_input_file = """
1
8 48
""".lstrip()

  alternative_output_file = """
Case #1: POSSIBLE
10 10
10 12
12 14
14 14
16 12
14 10
14 8
12 8
""".lstrip()

  def testCorrectAnswerDoesNotCauseError(self):
    self.assertIsNone(
        FindError(None, self.input_file, self.output_file, self.output_file))

  def testCorrectAlternativeAnswerDoesNotCauseError(self):
    self.assertIsNone(
        FindError(None,
                  self.alternative_input_file,
                  self.alternative_output_file,
                  self.alternative_output_file))

  def testAlternativeCorrectAnswerDoesNotCauseError(self):
    self.assertIsNone(
        FindError(
            None, self.input_file, self.output_file, """
Case #1: POSSIBLE
2 7
6 7
8 4
0 4
Case #2: IMPOSSIBLE
""".lstrip()))

  def testConcaveAlternativeAnswerDoesNotCauseError(self):
    self.assertIsNone(
        FindError(None,
                  self.alternative_input_file,
                  self.alternative_output_file,
                  """
Case #1: POSSIBLE
10 10
10 12
12 14
14 14
16 10
14 12
12 12
16 2
""".lstrip()))

  def testAboveBoundsCorrectAnswerCausesError(self):
    self.assertEqual(
        'Case #1: ' + _BAD_FORMAT_ERROR,
        FindError(
            None, self.input_file, self.output_file, """
Case #1: POSSIBLE
1000000002 1000000007
1000000006 1000000007
1000000008 1000000004
1000000000 1000000004
Case #2: IMPOSSIBLE
""".lstrip()))

  def testBelowBoundsCorrectAnswerCausesError(self):
    self.assertEqual(
        'Case #1: ' + _BAD_FORMAT_ERROR,
        FindError(
            None, self.input_file, self.output_file, """
Case #1: POSSIBLE
0 5
6 5
6 2
-2 2
Case #2: IMPOSSIBLE
""".lstrip()))

  def testIncorrectAnswerCausesError(self):
    self.assertStartsWith(
        FindError(
            None, self.input_file, self.output_file, """
Case #1: POSSIBLE
1 11
6 13
5 4
0 3
Case #2: IMPOSSIBLE
""".lstrip()), _WRONG_ANSWER)

  def testIncorrectAnswerWithLargeAreaCausesError(self):
    # Area is 2^32 + 16
    self.assertStartsWith(
        FindError(
            None, """
1
4 16
""".lstrip(),
"""
Case #1: POSSIBLE
0 0
0 8
1 8
1 0
""".lstrip(), """
Case #1: POSSIBLE
0 0
0 268435457
8 268435457
8 0
""".lstrip()), _WRONG_ANSWER)

  def testCollinearNeighboringPointsCausesError(self):
    self.assertEqual(
        'Case #1: ' + _COLLINEAR_ERROR,
        FindError(
            None, """
1
4 16
""".lstrip(), """
Case #1: POSSIBLE
0 0
0 4
2 4
2 0
""".lstrip(), """
Case #1: POSSIBLE
0 0
0 2
0 4
4 4
""".lstrip()))

  def testParallelSegmentsDoNotCauseError(self):
    # [(0, 4), (4, 4)] + [(4, 8), (0, 8)]
    self.assertIsNone(
        FindError(
            None, self.alternative_input_file, self.alternative_output_file, """
Case #1: POSSIBLE
0 0
0 4
4 4
4 8
0 8
6 9
6 1
2 3
""".lstrip()))

  def testSameConsecutiveVerticesCausesError(self):
    # Vertices (16, 12) are duplicates.
    self.assertEqual(
        'Case #1: ' + _COLLINEAR_ERROR,
        FindError(
            None, self.alternative_input_file, self.alternative_output_file, """
Case #1: POSSIBLE
10 10
10 12
12 14
14 14
16 12
16 12
14 8
12 9
""".lstrip()))

  def testCollinearSegmentsDoNotCauseError(self):
    # [(2, 10), (2, 6)] + [(2, 4), (2, 0)]
    self.assertIsNone(
        FindError(
            None, self.alternative_input_file, self.alternative_output_file, """
Case #1: POSSIBLE
0 0
0 10
2 10
2 6
4 6
4 4
2 4
2 0
""".lstrip()))

  def testCounterClockwiseAnswerDoesNotCausesError(self):
    self.assertIsNone(
        FindError(
            None, self.alternative_input_file, self.alternative_output_file, """
Case #1: POSSIBLE
2 0
2 4
4 4
4 6
2 6
2 10
0 10
0 0
""".lstrip()))

  def testSelfIntersectingAnswerCausesError(self):
    self.assertEqual(
        'Case #1: ' + _SELF_INTERSECTING_ERROR,
        FindError(
            None, self.input_file, self.output_file, """
Case #1: POSSIBLE
2 7
6 7
0 6
8 6
Case #2: IMPOSSIBLE
""".lstrip()))

  def testSelfIntersectingByVertexOnVertexCausesError(self):
    # Vertex (10, 10) collides with vertex (10, 10)
    self.assertEqual(
        'Case #1: ' + _SELF_INTERSECTING_ERROR,
      FindError(
          None, self.alternative_input_file, self.alternative_output_file, """
Case #1: POSSIBLE
10 10
10 12
12 14
14 14
16 12
10 10
14 8
8 6
""".lstrip()))

  def testSelfIntersectingByVertexOnSegmentCausesError(self):
    # Vertex (10, 11) collides with segment [(10, 10), (10, 12)]
    self.assertEqual(
        'Case #1: ' + _SELF_INTERSECTING_ERROR,
      FindError(
          None, self.alternative_input_file, self.alternative_output_file, """
Case #1: POSSIBLE
10 10
10 12
12 14
14 14
16 12
10 11
14 8
7 6
""".lstrip()))

  def testEmptyAttemptCausesError(self):
    self.assertEqual('Invalid attempt file: Too few cases.',
                     FindError(None, self.input_file, self.output_file, ''))

  def testBadHeaderCausesError(self):
    self.assertEqual(
        'Invalid attempt file: Expected "case #1:", found "Case ##1:".',
        FindError(None, self.input_file, self.output_file,
                  'Case ##1: IMPOSSIBLE'))

  def testBadFormatCausesError(self):
    self.assertEqual(
        'Case #1: ' + _BAD_FORMAT_ERROR,
        FindError(
            None, self.input_file, self.output_file, """
Case #1:
Case #2: IMPOSSIBLE
""".lstrip()))

    self.assertEqual(
        'Case #1: ' + _BAD_FORMAT_ERROR,
        FindError(
            None, self.input_file, self.output_file, """
Case #1: POSSIBLE
Case #2: IMPOSSIBLE
""".lstrip()))

    self.assertEqual(
        'Case #1: ' + _BAD_FORMAT_ERROR,
        FindError(
            None, self.input_file, self.output_file, """
Case #1: POSSIBLE 0 7 4 7 6 4 6 4
Case #2: IMPOSSIBLE
""".lstrip()))

  def testMissingCaseCausesError(self):
    self.assertEqual(
        'Invalid attempt file: Too few cases.',
        FindError(
            None, self.input_file, self.output_file, """
Case #1: POSSIBLE
""".lstrip()))


def RunUnitTests():
  test = SimplePolygonUnitTest()
  test_methods = [
      method_name for method_name in dir(test)
      if callable(getattr(test, method_name)) and method_name.startswith('test')
  ]
  for test_method in test_methods:
    print(test_method)
    getattr(test, test_method)()

  print('SimplePolygonUnitTest passes.')
  sys.exit(0)


if __name__ == '__main__':
  if sys.argv[1] == '-2':
    RunUnitTests()

  result = FindError(None,
                     open(sys.argv[1]).read(),
                     open(sys.argv[3]).read(),
                     open(sys.argv[2]).read())
  if result:
    print(result, file=sys.stderr)
    sys.exit(1)
