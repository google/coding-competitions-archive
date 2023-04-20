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

"""A custom judge for the House Of Kittens problem."""

__author__ = 'darthur@google.com (David Arthur)'




class CaseInput(object):
  """Holds information for a single test case.

  Args:
    num_points: The number of points on the input polygon.
    faces: The faces that the input polygon has been divided into. Each face is
      a sorted list of indices in the range [0, num_points).
  """

  def __init__(self, num_points, faces):
    self.num_points = num_points
    self.faces = faces


def ExtractFaces(vertex_edges, start_pos, end_pos):
  """Returns all faces of the given region of the polygon.

  There should be an edge between start_pos and end_pos. We will sub-divide
  the polygon consisting of (start_pos, start_pos+1, ..., end_pos) into faces,
  and return the result.

  As a side-effect, this function clears vertex_edges.

  Args:
    vertex_edges: vertex_edges[u] contains the list of vertices v such that
      (u, v) is a diagonal and v > u. The list is sorted for each u, and all
      numbers are 0-indexed. Additionally, edges from start_pos to vertices
      greater than end_pos should be omitted from vertex_edges.
    start_pos: See above. Also 0-indexed.
    end_pos: See above. Also 0-indexed.
  Returns:
    A list of faces, each represented as a list of 0-indexed vertices.
  """
  pos = start_pos
  all_faces = []
  this_face = [start_pos]

  while pos != end_pos:
    if vertex_edges[pos]:
      new_end_pos = vertex_edges[pos].pop(-1)
      all_faces.extend(ExtractFaces(vertex_edges, pos, new_end_pos))
      assert not vertex_edges[pos]
      pos = new_end_pos
    else:
      pos += 1
    this_face.append(pos)

  all_faces.append(this_face)
  return all_faces


def ParseCase(input_lines):
  """Returns a CaseInput from three input lines."""
  num_points, unused_num_edges = [int(w) for w in input_lines[0].split()]
  edge_start = [int(w) - 1 for w in input_lines[1].split()]
  edge_end = [int(w) - 1 for w in input_lines[2].split()]

  vertex_edges = [[] for i in xrange(num_points)]
  for i, start in enumerate(edge_start):
    vertex_edges[start].append(edge_end[i])
  for vertex_edge_list in vertex_edges:
    vertex_edge_list.sort()

  polygons = ExtractFaces(vertex_edges, 0, num_points - 1)
  return CaseInput(num_points, polygons)


def ParseInputFile(input_file):
  """Returns a list of CaseInputs from the input file as a text string."""
  input_lines = input_file.splitlines()
  num_cases = int(input_lines[0])
  result = []
  for i in xrange(num_cases):
    result.append(ParseCase(input_lines[3 * i + 1 : 3 * i + 4]))
  return result


def FindError(unused_self, input_file, unused_output_file, attempt):
  """Returns None if the output is correct and a 'str' error otherwise.

  Args:
    see judge.Judge.FindError().
  """
  input_cases = ParseInputFile(input_file)
  num_cases = len(input_cases)

  tokenized_output = _utils_Tokenize(attempt, False)
  if tokenized_output is None:
    return 'Output file contains invalid or non-ASCII characters.'
  if len(tokenized_output) != 2 * num_cases:
    return 'Incorrect number of output file lines.'

  for test_case in xrange(1, num_cases + 1):
    input_case = input_cases[test_case - 1]
    num_colors = min([len(face) for face in input_case.faces])
    line1, line2 = tokenized_output[2 * test_case - 2 : 2 * test_case]

    # Check line1.
    if (len(line1) != 3 or
        line1[0] != 'case' or
        line1[1] != ('#%d:' % test_case)):
      return 'Case header is broken for case #%d' % test_case
    if _utils_ToInteger(line1[2]) != num_colors:
      return 'Incorrect number of colors for case #%d' % test_case

    # Get the polygon colors.
    polygon_colors = []
    if len(line2) != input_case.num_points:
      return 'Incorrect number of points on line 2 for case #%d' % test_case
    for token in line2:
      int_token = _utils_ToInteger(token)
      if int_token is None or not 1 <= int_token <= num_colors:
        return 'Invalid color %s for case #%d' % (token, test_case)
      polygon_colors.append(int_token)

    # Validate the polygon colors.
    for i, face in enumerate(input_case.faces):
      if len(set(polygon_colors[v] for v in face)) != num_colors:
        return 'Missing color in face #%d for case #%d' % (i + 1, test_case)

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
