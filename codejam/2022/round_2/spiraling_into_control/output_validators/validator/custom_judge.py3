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
                                 case_sensitive=True):
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


"""Custom judge for Spiraling Into Control

Judges contestants' solutions for Spiraling Into Control
"""

import math

IMPOSSIBLE = 'IMPOSSIBLE'


def ParseInputFile(input_file):
  input_lines = _utils_Tokenize(input_file)
  n_cases = int(next(input_lines.pop(0)))
  cases = []
  for _ in range(n_cases):
    if len(input_lines) == 0:
      return 'num cases ({}) exceeds actual given cases'.format(n_cases), None
    cases.append([int(x) for x in list(input_lines.pop(0))])
  return None, cases


def FindError(unused_self, input_file, output_file, attempt_file):
  """See judge.Judge.FindError()."""
  error, input_cases = ParseInputFile(input_file)
  if error:
    return error
  num_cases = len(input_cases)
  output_cases, attempt_cases, error = _utils_TokenizeAndSplitCases(
      output_file, attempt_file, num_cases)
  if error is not None:
    return error

  for case_num, (case, output_lines, attempt_lines) in enumerate(
      zip(input_cases, output_cases, attempt_cases), start=1):
    judge_error = judge_case(case, attempt_lines, output_lines)
    if judge_error:
      return 'Case #{}: {}'.format(case_num, judge_error)

  # Everything passes.
  return None


INTERNAL_ERROR_PREFIX = 'INTERNAL_ERROR for {}: '.format
ATTEMPT_ERROR_PREFIX = 'WRONG_ANSWER for {}: '.format

WRONGLY_DECLARED_IMPOSSIBLE = 'Declared IMPOSSIBLE, but has solution {}'.format
WRONGLY_DECLARED_POSSIBLE = 'Case is impossible, but {} was given'.format
WRONG_IMPOSSIBLE_FORMAT = 'Declared IMPOSSIBLE, but has extra stuff.'
INVALID_FIRST_LINE = 'Invalid first line: {}'.format
INVALID_NUM_SHORTCUTS = 'Invalid number of shortcuts: {}'.format
WRONG_NUM_LINES = 'Declared {} shortcuts but gave {} lines'.format
MALFORMED_SHORTCUT = 'Malformed shortcut: {}'.format
INVALID_SHORTCUT = 'Invalid shortcut: {}'.format
WRONG_SHORTCUT_ORDER = 'Shortcuts are not in order: saw {} after {}'.format
WRONG_PATH_LENGTH = 'Wanted {} moves, got {}'.format
"""
Judges a case based on the case's input, the IO gen's output, and the
attempt's output.

Returns a tuple of two elements:
    - First element is None if the attempt is successful, or an error message if
      the attempt is not successful.
    - Second element is always False if the first element is None. If not, it's
      true if the error caused is due to internal error (judge or IO gen is the
      cause)
"""


# Returns true if `attempt_output` is a correct output for the case's input,
# which is given in `case_info`.
def judge_case(case_info, attempt_output, io_output):
  n, k = case_info
  if io_output[0][0] == IMPOSSIBLE:
    if attempt_output[0][0] == IMPOSSIBLE:
      if (len(attempt_output[0]) != 1) or (len(attempt_output) > 1):
        return (ATTEMPT_ERROR_PREFIX('{} {}'.format(n, k))
              + WRONG_IMPOSSIBLE_FORMAT)
      return None
    if find_error(n, k, attempt_output):
      return (ATTEMPT_ERROR_PREFIX('{} {}'.format(n, k))
              + WRONGLY_DECLARED_POSSIBLE(attempt_output))
    return (INTERNAL_ERROR_PREFIX('{} {}'.format(n, k))
            + WRONGLY_DECLARED_IMPOSSIBLE(attempt_output))

  # Judge's answer is possible. Verify judge's answer before proceeding to
  # judgement.
  err = find_error(n, k, io_output)
  if err:
    return INTERNAL_ERROR_PREFIX('{} {}'.format(n, k)) + err

  err = find_error(n, k, attempt_output)
  if err:
    return ATTEMPT_ERROR_PREFIX('{} {}'.format(n, k)) + err

  return None

def num_to_loc(num, n):
  # Counts square rings starting from the center. e.g.,
  #
  # 22222
  # 21112
  # 21012
  # 21112
  # 22222
  #
  # This is safe (i.e. we don't need to worry about getting e.g. 3.00000000001
  # which ceilings up to 4) because the integers that can come out of this
  # computation (and the math.sqrt() values that produce them) have exact
  # floating-point representations.
  # For example, when N = 5, num = 41, we get 0.5 * sqrt(50-41) - 0.5
  # = 0.5 * 3 - 0.5 = 1.
  ring = math.ceil(0.5 * math.sqrt(n**2 + 1 - num) - 0.5)
  upper_left = n**2 - 8 * ((ring)*(ring+1)) // 2
  diff = num - upper_left
  if diff <= ring * 2:
    return (n//2 - ring, n//2 - ring + diff)
  elif diff <= ring * 4:
    return (n//2 - ring + (diff - ring * 2), n//2 + ring)
  elif diff <= ring * 6:
    return (n//2 + ring, n//2 + ring - (diff - ring * 4))
  else:
    return (n//2 + ring - (diff - ring * 6), n//2 - ring)


def adjacent(s, f, n):
  rs, cs = num_to_loc(s, n)
  rf, cf = num_to_loc(f, n)
  rdiff = abs(rs-rf)
  cdiff = abs(cs-cf)
  return (rdiff == 1 and cdiff == 0) or (rdiff == 0 and cdiff == 1)


def find_error(n, k, output):
  if len(output[0]) != 1:
    return INVALID_FIRST_LINE(output[0])
  if output[0][0] == IMPOSSIBLE:
    return WRONGLY_DECLARED_IMPOSSIBLE('')
  try:
    num_shortcuts = int(output[0][0])
  except ValueError as ve:
    return INVALID_FIRST_LINE(output[0])
  if num_shortcuts < 1 or num_shortcuts > n-1:
    return INVALID_NUM_SHORTCUTS(num_shortcuts)
  shortcut_lines = output[1:]
  if len(shortcut_lines) != num_shortcuts:
    return WRONG_NUM_LINES(num_shortcuts, len(shortcut_lines))
  shortcuts = []
  for shortcut_line in shortcut_lines:
    if len(shortcut_line) != 2:
      return MALFORMED_SHORTCUT(shortcut_line)
    try:
      shortcut = [int(x) for x in shortcut_line]
    except ValueError:
      return MALFORMED_SHORTCUT(shortcut_line)
    shortcuts.append(shortcut)
  path_length = n**2-1
  max_room_so_far = 1
  for shortcut in shortcuts:
    s, f = shortcut
    if s < 1 or s > n*n or f < 1 or f > n*n:
      return INVALID_SHORTCUT(shortcut)
    savings = f - s - 1
    if savings <= 0:
      return INVALID_SHORTCUT(shortcut)
    if not adjacent(s, f, n):
      return INVALID_SHORTCUT(shortcut)
    if s < max_room_so_far:
      return WRONG_SHORTCUT_ORDER(s, max_room_so_far)
    path_length -= savings
    max_room_so_far = f
  if path_length != k:
    return WRONG_PATH_LENGTH(k, path_length)
  return None


# ---- Start of unit testing infra ----

import random

def AssertEqual(a, b):
  if a != b:
    print('Not true that the following are equal:')
    print(a)
    print(b)
  assert a == b


# Copied from tullis_bfs.py.
def make_spiral(n):
  g = [[0 for _ in range(n)] for __ in range(n)]
  dirs = [(0, 1), (1, 0), (0, -1), (-1, 0)]
  curr_dir = 0
  rdev, cdev = dirs[curr_dir]
  r, c = 0, 0
  for num in range(1, n*n + 1):
    g[r][c] = num
    if not (
        0 <= r + rdev < n and 0 <= c + cdev < n and g[r+rdev][c+cdev] == 0):
      curr_dir = (curr_dir + 1) % 4
      rdev, cdev = dirs[curr_dir]
    r, c = r + rdev, c + cdev
  return g


def run_num_to_loc_tests():
  for n in (3, 5, 7, 9, 19, 39, 99):
    s = make_spiral(n)
    for num in range(1, n**2 + 1):
      r, c = num_to_loc(num, n)
      assert s[r][c] == num, 'num_to_loc({}) gave ({}, {}), which is {}'.format(
          num, r, c, s[r][c])
  # The 99999999 case is needed to detect a faulty version of the formula
  # that uses math.sqrt(n**2 - num), forgetting +1.
  cases = [10**i - 1 for i in range(1, 9)]
  for i in range(1000):
    cases.append(1 + 2 * random.randint(100, 4998))
  for n in cases:
    for num, r, c in ((1, 0, 0),
                      (2, 0, 1),
                      (n-1, 0, n-2),
                      (n, 0, n-1),
                      (n+1, 1, n-1),
                      (n+(n-2), n-2, n-1),
                      (n+(n-1), n-1, n-1),
                      (n+(n), n-1, n-2),
                      (n+(n-1)+(n-2), n-1, 1),
                      (n+(n-1)+(n-1), n-1, 0),
                      (n+(n-1)+(n), n-2, 0),
                      (n+(n-1)+(n-1)+(n-3), 2, 0),
                      (n+(n-1)+(n-1)+(n-2), 1, 0),
                      (n+(n-1)+(n-1)+(n-1), 1, 1),
                      (n*n, n//2, n//2),
                      (n*n-1, n//2, n//2 - 1),
                      (n*n-2, n//2+1, n//2 - 1),
                      (n*n-3, n//2+1, n//2),
                      (n*n-4, n//2+1, n//2+1),
                      (n*n-5, n//2, n//2+1),
                      (n*n-6, n//2-1, n//2+1),
                      (n*n-7, n//2-1, n//2),
                      (n*n-8, n//2-1, n//2-1),
                      (n*n-9, n//2-1, n//2-2),
                      (n*n-10, n//2, n//2-2)):
      rr, cc = num_to_loc(num, n)
      assert (rr, cc) == (r, c), (
        "num_to_loc({}, {}): wanted ({}, {}), got ({}, {})".format(
           num, n, r, c, rr, cc))


def run_adjacent_tests():
  for n in range(3, 21, 2):
    s = make_spiral(n)
    for r in range(n):
      for c in range(n):
        curr_num = s[r][c]
        neighbors = set()
        non_neighbors = set()
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
          nr, nc = r + dr, c + dc
          if 0 <= nr < n and 0 <= nc < n:
            neighbors.add(s[nr][nc])
        for xr in range(n):
          for xc in range(n):
            other_num = s[xr][xc]
            if other_num not in neighbors:
              non_neighbors.add(other_num)
        for num in neighbors:
          assert adjacent(curr_num, num, n), (
              'N = {}: {} and {} should have been adjacent'.format(
                  curr_num, num))
        for num in non_neighbors:
          assert not adjacent(curr_num, num, n), (
              'N = {}: {} and {} should not have been adjacent'.format(
                  curr_num, num))


def run_unit_tests():
  input_lines = ['4', '3 2', '3 3', '5 4', '5 1']
  output_lines = ['Case #1: 1', '1 8', 'Case #2: IMPOSSIBLE',
                  'Case #3: 2', '3 18', '18 25', 'Case #4: IMPOSSIBLE']

  def make_file(lines):
    return '\n'.join(lines)

  def sub(lst, i, new_at_i):
    lst_copy = list(lst)
    lst_copy[i] = new_at_i
    return lst_copy

  AssertEqual(
      None,
      FindError(None, make_file(input_lines), make_file(output_lines),
                make_file(output_lines)))

  AssertEqual(
      'Invalid generator output file: Too many cases.',
      FindError(None, make_file(sub(input_lines[0:3], 0, '2')),
                make_file(output_lines), make_file(output_lines)))

  AssertEqual(
      'Invalid generator output file: Too few cases.',
      FindError(None, make_file(input_lines),
                make_file(output_lines[:1]),
                make_file(output_lines)))

  AssertEqual(
      'Invalid attempt file: Too few cases.',
      FindError(None, make_file(input_lines),
                make_file(output_lines),
                make_file(output_lines[:1])))

  AssertEqual(
      'Invalid generator output file: Expected "case #1:", found "Case #2:".',
      FindError(None, make_file(input_lines),
                make_file(sub(output_lines, 0, 'Case #2: 1')),
                make_file(output_lines)))

  AssertEqual(
      'Case #1: WRONG_ANSWER for 3 2: Declared IMPOSSIBLE, but has solution ',
      FindError(None, make_file(input_lines),
                make_file(output_lines),
                make_file(['Case #1: IMPOSSIBLE'] + output_lines[2:])))

  AssertEqual(
      ("Case #1: INTERNAL_ERROR for 3 2: Declared IMPOSSIBLE, but has "
       "solution [['1'], ['1', '8']]"),
      FindError(None, make_file(input_lines),
                make_file(['Case #1: IMPOSSIBLE'] + output_lines[2:]),
                make_file(output_lines)))

  AssertEqual(
      ("Case #4: WRONG_ANSWER for 5 1: Case is impossible, "
      	     "but [['1'], ['1', '2']] was given"),
      FindError(None, make_file(input_lines), make_file(output_lines),
                make_file(output_lines[:-1] + ['Case #4: 1'] + ['1 2'])))

  AssertEqual(
      ("Case #1: INTERNAL_ERROR for 3 2: Invalid first line: ['oh', 'no']"),
      FindError(None, make_file(input_lines),
                make_file(sub(output_lines, 0, 'Case #1: oh no')),
                make_file(output_lines)))

  AssertEqual(
      ('Case #4: WRONG_ANSWER for 5 1: '
       'Declared IMPOSSIBLE, but has extra stuff.'),
      FindError(None, make_file(input_lines), make_file(output_lines),
                make_file(output_lines + ['1 8'])))

  AssertEqual(
      ('Case #2: WRONG_ANSWER for 3 3: '
       'Declared IMPOSSIBLE, but has extra stuff.'),
      FindError(None, make_file(input_lines), make_file(output_lines),
                make_file(sub(output_lines, 2, 'Case #2: IMPOSSIBLE AF'))))

  AssertEqual(
      ("Case #1: WRONG_ANSWER for 3 2: Invalid first line: ['oh', 'no']"),
      FindError(None, make_file(input_lines),
                make_file(output_lines),
                make_file(sub(output_lines, 0, 'Case #1: oh no'))))

  AssertEqual(
      ('Case #1: WRONG_ANSWER for 3 2: Invalid first line: []'),
      FindError(None, make_file(input_lines),
                make_file(output_lines),
                make_file(sub(output_lines, 0, 'Case #1:'))))

  AssertEqual(
      ("Case #1: WRONG_ANSWER for 3 2: Invalid first line: ['lots']"),
      FindError(None, make_file(input_lines),
                make_file(output_lines),
                make_file(sub(output_lines, 0, 'Case #1: lots'))))

  AssertEqual(
      ('Case #1: WRONG_ANSWER for 3 2: Invalid number of shortcuts: 0'),
      FindError(None, make_file(input_lines),
                make_file(output_lines),
                make_file(sub(output_lines, 0, 'Case #1: 0'))))

  AssertEqual(
      ('Case #1: WRONG_ANSWER for 3 2: Invalid number of shortcuts: 3'),
      FindError(None, make_file(input_lines),
                make_file(output_lines),
                make_file(sub(output_lines, 0, 'Case #1: 3'))))

  AssertEqual(
      ('Case #1: WRONG_ANSWER for 3 2: Declared 1 shortcuts but gave 2 lines'),
      FindError(None, make_file(input_lines),
                make_file(output_lines),
                make_file(output_lines[0:2] + ['1 8'] + output_lines[2:])))

  AssertEqual(
      ('Case #1: WRONG_ANSWER for 3 2: Declared 2 shortcuts but gave 1 lines'),
      FindError(None, make_file(input_lines),
                make_file(output_lines),
                make_file(['Case #1: 2'] + ['1 8'] + output_lines[2:])))

  AssertEqual(
      ("Case #1: WRONG_ANSWER for 3 2: Malformed shortcut: ['18']"),
      FindError(None, make_file(input_lines),
                make_file(output_lines),
                make_file(sub(output_lines, 1, '18'))))

  AssertEqual(
      ("Case #1: WRONG_ANSWER for 3 2: Malformed shortcut: ['1', '2', '3']"),
      FindError(None, make_file(input_lines),
                make_file(output_lines),
                make_file(sub(output_lines, 1, '1 2 3'))))

  AssertEqual(
      ("Case #1: WRONG_ANSWER for 3 2: Malformed shortcut: ['one', 'eight']"),
      FindError(None, make_file(input_lines),
                make_file(output_lines),
                make_file(sub(output_lines, 1, 'one eight'))))

  for s, f in ((0, 8), (9, 8), (1, -1), (1, 9), (1, 1), (1, 2), (8, 9)):
    AssertEqual(
        ('Case #1: WRONG_ANSWER for 3 2: Invalid shortcut: '
         '[{}, {}]'.format(s, f)),
        FindError(None, make_file(input_lines),
                  make_file(output_lines),
                  make_file(sub(output_lines, 1, '{} {}'.format(s, f)))))

  for s, f in ((18, 3), (19, 4), (18, 2), (18, 4), (18, 20), (18, 24),
               (18, 17), (18, 19), (18, 1)):
    AssertEqual(
        ('Case #3: WRONG_ANSWER for 5 4: Invalid shortcut: '
         '[{}, {}]'.format(s, f)),
        FindError(None, make_file(input_lines),
                  make_file(output_lines),
                  make_file(sub(output_lines, 5, '{} {}'.format(s, f)))))

  for s1, f1, s2, f2, exp1, exp2 in ((18, 25, 3, 18, 3, 25),
                                     (3, 18, 3, 18, 3, 18),
                                     (3, 18, 4, 19, 4, 18),
                                     (3, 18, 2, 17, 2, 18)):
    AssertEqual(
        ('Case #3: WRONG_ANSWER for 5 4: Shortcuts are not in order: saw '
         '{} after {}'.format(exp1, exp2)),
        FindError(None, make_file(input_lines),
                  make_file(output_lines),
                  make_file(output_lines[0:4] + ['{} {}'.format(s1, f1)]
                            + ['{} {}'.format(s2, f2)] + output_lines[6:])))

  for s1, f1, s2, f2, pl in ((1, 16, 20, 25, 6),
                             (6, 19, 22, 25, 10)):
    AssertEqual(
        ('Case #3: WRONG_ANSWER for 5 4: Wanted 4 moves, '
         'got {}'.format(pl)),
        FindError(None, make_file(input_lines),
                  make_file(output_lines),
                  make_file(output_lines[0:4] + ['{} {}'.format(s1, f1)]
                            + ['{} {}'.format(s2, f2)] + output_lines[6:])))

  for pl, s, f in ((10, 3, 18), (12, 7, 20), (14, 11, 22), (16, 15, 24),
                   (18, 18, 25), (20, 20, 25), (22, 22, 25)):
    AssertEqual(
        None,
        FindError(None, make_file(['1', '5 {}'.format(pl)]),
                    make_file(['Case #1: 1', '{} {}'.format(s, f)]),
                    make_file(['Case #1: 1', '{} {}'.format(s, f)])))

  for s1, f1, s2, f2 in ((1, 16, 17, 24), (1, 16, 18, 25), (2, 17, 18, 25)):
    AssertEqual(
        None,
        FindError(None, make_file(input_lines),
                  make_file(output_lines),
                  make_file(output_lines[0:4] + ["{} {}".format(s1, f1)]
                            + ["{} {}".format(s2, f2)] + output_lines[6:])))
  print('Unit tests pass!')



# ---- End of unit testing infra ----

import sys

if __name__ == '__main__':
  if sys.argv[1] == '-2':
    run_num_to_loc_tests()
    run_adjacent_tests()
    run_unit_tests()
  else:
    result = FindError(None,
                       open(sys.argv[1]).read(),
                       open(sys.argv[3]).read(),
                       open(sys.argv[2]).read())
    if result:
      print(sys.stderr, result)
      sys.exit(1)
