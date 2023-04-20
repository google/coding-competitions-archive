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
"""A custom judge for the Go++ problem."""

__author__ = "abednego@google.com (Igor Naverniouk)"




class Error(Exception):
  pass


def ParseInput(input_file):
  """Returns the list of (B, G) pairs, one for each case.

  Args:
    input_file: entire contents of the input file

  Returns:
    A list of tuples (B, G), where B is a string of binary digits, and G is a
    non-empty list of strings of binary digits.

  Raises:
    Error: if the input cannot be parsed.
  """
  input_lines = input_file.splitlines()
  if not input_lines: raise Error("The input file is empty")
  try:
    num_cases = int(input_lines[0].strip())
  except ValueError:
    raise Error("The first line of input is not an integer")
  if len(input_lines) != 1 + num_cases * 3:
    raise Error("The number of lines should be %d, not %d" %
                (1 + num_cases * 3, len(input_lines)))
  cases = []
  for i in xrange(num_cases):
    try:
      n, l = map(int, input_lines[1 + i * 3].strip().split())
      g = input_lines[1 + i * 3 + 1].strip().split()
      b = input_lines[1 + i * 3 + 2].strip()
    except ValueError:
      raise Error("Case #%d is badly formatted" % (i + 1))
    if n < 1: raise Error("Case #%d: n is too small" % (i + 1))
    if n > 500: raise Error("Case #%d: n is too large" % (i + 1))  # With margin
    if l < 1: raise Error("Case #%d: l is too small" % (i + 1))
    if l > 500: raise Error("Case #%d: l is too large" % (i + 1))  # With margin
    if len(g) != n: raise Error("Case #%d: len(g) is wrong" % (i + 1))
    for s in g:
      if len(s) != l: raise Error("Case #%d: wrong word length" % (i + 1))
      if set(s) - set("01"):
        raise Error("Case #%d: bad character in G" % (i + 1))
    if len(b) != l: raise Error("Case #%d: wrong B length" % (i + 1))
    if set(b) - set("01"): raise Error("Case #%d: bad character in B" % (i + 1))
    cases.append((b, g))
  return cases


def CanGenerate(p, q, candidates):
  """Checks if programs p and q can generate each string from a given list.

  Args:
    p: a string of '0', '1', and '?' characters representing program 1.
    q: a string of '0', '1', and '?' characters representing program 2.
    candidates: a list of strings of binary digits representing the output.

  Returns:
    A list of booleans of the same length as candidate. The i-th item is True
    iff some interleaving of p and q can produce s.
  """
  # NOTE(petya): I've tried manually splitting candidates into blocks of
  # 62 to avoid going to the 'long' type, but it was not faster - it looks
  # like Python takes care of this pretty well.

  a, b, c = len(p), len(q), len(candidates[0])

  # k[i][j] is the number of printed characters after p[:i] and q[:j] have run.
  k = [[0 for _ in xrange(b + 1)] for _ in xrange(a + 1)]
  for i in xrange(a):
    k[i + 1][0] = k[i][0] + (1 if p[i] == "?" else 0)
  for i in xrange(a + 1):
    for j in xrange(b):
      k[i][j + 1] = k[i][j] + (1 if q[j] == "?" else 0)
  if k[a][b] != c: return False  # Wrong number of question marks.

  # Compress corresponding bits of each candidate into one bitmask.
  zero_mask = [0 for _ in xrange(c)]
  one_mask = [0 for _ in xrange(c)]
  for i, s in enumerate(candidates):
    for pos in xrange(c):
      if s[pos] == "1":
        one_mask[pos] |= 1 << i
      else:
        zero_mask[pos] |= 1 << i

  # r0[i][j] is the mask of candidates where it is possible for p[:i] and q[:j]
  # to have executed and produced s[:k[i][j]] with the register having value 0
  # at the end.
  # r1[i][j] does the same for register value 1.
  r0 = [[0 for _ in xrange(b + 1)] for _ in xrange(a + 1)]
  r1 = [[0 for _ in xrange(b + 1)] for _ in xrange(a + 1)]
  r0[0][0] = (1 << len(candidates)) - 1
  for i in xrange(a + 1):
    for j in xrange(b + 1):
      if i < a:
        if p[i] == "?":
          r0[i + 1][j] |= r0[i][j] & zero_mask[k[i][j]]
          r1[i + 1][j] |= r1[i][j] & one_mask[k[i][j]]
        else:
          (r0 if p[i] == "0" else r1)[i + 1][j] |= r0[i][j] | r1[i][j]
      if j < b:
        if q[j] == "?":
          r0[i][j + 1] |= r0[i][j] & zero_mask[k[i][j]]
          r1[i][j + 1] |= r1[i][j] & one_mask[k[i][j]]
        else:
          (r0 if q[j] == "0" else r1)[i][j + 1] |= r0[i][j] | r1[i][j]

  res_mask = r0[a][b] | r1[a][b]
  return [(res_mask & (1 << i)) != 0 for i in xrange(len(candidates))]


def CheckCase(b, g, attempt):
  """Returns None if the output for this case is correct, or a 'str' error.

  Args:
    b: The bad string
    g: The list of good strings
    attempt: contestant's output lines

  Returns:
    None on success; a string on error.
  """
  # Parse the contestant's output.
  if len(attempt) != 1: return "More than one line of output"
  if not attempt[0]: return "Empty line of output"
  is_impossible = len(attempt[0]) == 1 and attempt[0][0] == "impossible"
  expected_impossible = b in g
  if is_impossible and expected_impossible:
    return None
  if is_impossible and not expected_impossible:
    return "Said 'IMPOSSIBLE'. Gotcha."
  if not is_impossible and expected_impossible:
    return "Expected IMPOSSIBLE when B is in G."
  if len(attempt[0]) != 2: return "Invalid output line"
  p, q = attempt[0]
  if len(p) < 1 or len(q) < 1: return "Empty program"
  if len(p) + len(q) > 200: return "Programs are too long"
  if set(c for c in p + q) - set(c for c in "01?"): return "Bad character"
  if sum(1 for c in p + q if c == "?") != len(b): return "Bad number of ?s"

  # Check correctness.
  can_generate = CanGenerate(p, q, [b] + g)
  if can_generate[0]: return "Programs can generate B"
  for can_s, s in zip(can_generate[1:], g):
    if not can_s: return "Programs cannot generate %s" % s
  return None


def FindError(_, input_file, output_file, attempt):
  """Returns None if the output is correct and a 'str' error otherwise.

  Args:
    see judge.Judge.FindError().

  Returns:
    None on success; a string on error.
  """
  # Parse everything.
  try:
    cases = ParseInput(input_file)
  except Error as e:
    return "Error in IO generator: " + str(e)
  _, parsed_attempt, error = _utils_TokenizeAndSplitCases(
      output_file, attempt, len(cases))
  if error is not None:
    return "_utils_TokenizeAndSplitCases() found an error: %s" % error

  if len(cases) != len(parsed_attempt):
    return "Bug in _utils_TokenizeAndSplitCases() or ParseInput()"

  # Validate case by case.
  for case, ((b, g), attempt) in enumerate(zip(cases, parsed_attempt)):
    error = CheckCase(b, g, attempt)
    if error is not None:
      return "Error in case #%d: %s" % (case + 1, error)

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