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


"""Custom judge for Letter Blocks

Judges contestants' solutions for Letter Blocks
"""

import random

IMPOSSIBLE = 'IMPOSSIBLE'


def ParseInputFile(input_file):
  input_lines = _utils_Tokenize(input_file)
  n_cases = int(next(input_lines.pop(0)))
  cases = []
  for _ in range(n_cases):
    if len(input_lines) == 0:
      return 'num cases ({}) exceeds actual given cases'.format(n_cases), None
    n_strings = int(next(input_lines.pop(0)))
    strings = list(input_lines.pop(0))
    assert len(strings) == n_strings
    cases.append(strings)
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
    judge_error = judge_case(case, attempt_lines[0][0], output_lines[0][0])
    if judge_error:
      return 'Case #{}: {}'.format(case_num, judge_error)

  # Everything passes.
  return None


from itertools import groupby

INTERNAL_ERROR_PREFIX = 'INTERNAL_ERROR for {}: '.format
ATTEMPT_ERROR_PREFIX = 'WRONG_ANSWER for {}: '.format

WRONGLY_DECLARED_IMPOSSIBLE = ('Declared IMPOSSIBLE, but a valid tower can be'
                               ' made.')
WRONGLY_DECLARED_POSSIBLE = 'Case is impossible, but {} was given'.format
INVALID_TOWER = 'Invalid tower: {}'.format
OUTPUT_DOES_NOT_FIT_INPUT = (
    'The output {} cannot be formed from the input (missing some elements or'
    ' contains some extra elements)').format
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


# Returns true if `attempt_output` is a right output for the case's input,
# which is given in `input_strings`.
def judge_case(input_strings, attempt_output, io_output):

  if io_output == IMPOSSIBLE:
    if attempt_output == IMPOSSIBLE:
      return None
    if not is_valid_tower(attempt_output):
      return (ATTEMPT_ERROR_PREFIX(input_strings)
              + WRONGLY_DECLARED_POSSIBLE(attempt_output))
    if not can_words_form_string(input_strings, attempt_output):
      return (ATTEMPT_ERROR_PREFIX(input_strings)
              + WRONGLY_DECLARED_POSSIBLE(attempt_output))
    return INTERNAL_ERROR_PREFIX(input_strings) + WRONGLY_DECLARED_IMPOSSIBLE

  # Judge's answer is possible. Verify judge's answer before proceeding to
  # judgement.
  if not is_valid_tower(io_output):
    return INTERNAL_ERROR_PREFIX(input_strings) + INVALID_TOWER(io_output)
  if not can_words_form_string(input_strings, io_output):
    return (INTERNAL_ERROR_PREFIX(input_strings)
            + OUTPUT_DOES_NOT_FIT_INPUT(io_output))

  if not is_valid_tower(attempt_output):
    return ATTEMPT_ERROR_PREFIX(input_strings) + INVALID_TOWER(attempt_output)
  if not can_words_form_string(input_strings, attempt_output):
    return ATTEMPT_ERROR_PREFIX(input_strings) + OUTPUT_DOES_NOT_FIT_INPUT(
        attempt_output, input_strings)

  return None

def build_starts_pures(words):
  starts, pures = {}, {}
  for word in words:
    char = word[0]
    if len(set(list(word))) == 1:  # `word` is "pure" (i.e. made of only 1 char)
      if char not in pures:
        pures[char] = []
      pures[char].append(word)
    else:
      starts[char] = [word]
  return starts, pures


def can_words_form_string(words, string):
  starts, pures = build_starts_pures(words)
  string_partition = []

  index = 0
  while index < len(string):
    curr_char = string[index]
    if curr_char not in pures and curr_char not in starts:
      return False
    dict_to_use = pures if (curr_char in pures) else starts
    for substring in dict_to_use[curr_char]:
      string_partition.append(substring)
      index += len(substring)
    dict_to_use.pop(curr_char)

  if len(starts) != 0 or len(pures) != 0 or index != len(string):
    return False

  assert sorted(string_partition) == sorted(words)
  assert ''.join(string_partition) == string
  return True


def is_valid_tower(word):
  distinct_group_chars = [list(c)[0] for _, c in groupby(word)]
  return len(distinct_group_chars) == len(set(distinct_group_chars))

# ---- Start of unit testing infra ----
def build_random_valid_tower(max_appearance_per_char):
  tower = ''
  for i in range(0, 26):
    if random.randint(1, 3) == 1:  # 2/3 probability using a char.
      continue
    char = chr(ord('A') + i)
    tower += char * random.randint(1, max_appearance_per_char)
  return tower


def randomly_split(string, max_substring_length):
  substrings = []
  index = 0
  while index < len(string):
    next_substring_size = random.randint(1, max_substring_length)
    substrings.append(string[index:index + next_substring_size])
    index += next_substring_size
  if index < len(string):
    substrings.append(string[index:])
  assert ''.join(substrings) == string
  return substrings


def can_words_form_string_test(max_appearance_per_char, max_substring_length):
  random_valid_tower = build_random_valid_tower(max_appearance_per_char)
  random_split = randomly_split(random_valid_tower, max_substring_length)
  random.shuffle(random_split)
  validation = can_words_form_string(random_split, random_valid_tower)
  assert validation, 'Failed test: {}=>{}'.format(random_split,
                                                  random_valid_tower)


def run_can_words_form_string_tests():
  for i in [10, 20, 50, 100]:
    for j in [1, 4, 8, 15]:
      can_words_form_string_test(i, j)


def AssertEqual(a, b):
  if a != b:
    print('Not true that the following are equal:')
    print(a)
    print(b)
  assert a == b


def run_unit_tests():
  input_lines = [
      '6', '1', 'A', '3', 'A B C', '2', 'AB AB', '5', 'BCD B DE A D', '1',
      'AKA', '3', 'A B BA'
  ]
  output_lines = [
      'Case #1: A', 'Case #2: ABC', 'Case #3: IMPOSSIBLE', 'Case #4: ABBCDDDE',
      'Case #5: IMPOSSIBLE', 'Case #6: BBAA'
  ]

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
      'num cases (6) exceeds actual given cases',
      FindError(None, make_file(input_lines[0:3]), make_file(output_lines),
                make_file(output_lines)))

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
                make_file(sub(output_lines, 0, 'Case #2: IMPOSSIBLE')),
                make_file(output_lines)))

  AssertEqual(
      ("Case #1: INTERNAL_ERROR for ['A']: Declared IMPOSSIBLE, but a valid"
      " tower can be made."),
      FindError(None, make_file(input_lines),
                make_file(sub(output_lines, 0, 'Case #1: IMPOSSIBLE')),
                make_file(output_lines)))

  AssertEqual(
      ("Case #3: WRONG_ANSWER for ['AB', 'AB']: Case is impossible, but ABAB"
      " was given"),
      FindError(None, make_file(input_lines), make_file(output_lines),
                make_file(sub(output_lines, 2, 'Case #3: ABAB'))))
  AssertEqual(
      "Case #3: INTERNAL_ERROR for ['AB', 'AB']: Invalid tower: ABAB",
      FindError(None, make_file(input_lines),
                make_file(sub(output_lines, 2, 'Case #3: ABAB')),
                make_file(output_lines)))
  AssertEqual(
      ("Case #2: INTERNAL_ERROR for ['A', 'B', 'C']: The output ABCC cannot be"
      " formed from the input (missing some elements or contains some extra"
      " elements)"),
      FindError(None, make_file(input_lines),
                make_file(sub(output_lines, 1, 'Case #2: ABCC')),
                make_file(output_lines)))

  AssertEqual(
      "Case #6: WRONG_ANSWER for ['A', 'B', 'BA']: Invalid tower: ABAB",
      FindError(None, make_file(input_lines), make_file(output_lines),
                make_file(sub(output_lines, 5, 'Case #6: ABAB'))))

  AssertEqual(
      ("Case #2: WRONG_ANSWER for ['A', 'B', 'C']: The output ABCC cannot be"
      " formed from the input (missing some elements or contains some extra"
      " elements)"),
      FindError(None, make_file(input_lines),
                make_file(output_lines),
                make_file(sub(output_lines, 1, 'Case #2: ABCC'))))

  print('Unit tests pass!')


# ---- End of unit testing infra ----

import sys

if __name__ == '__main__':
  if sys.argv[1] == '-2':
    run_can_words_form_string_tests()
    run_unit_tests()
  else:
    result = FindError(None,
                       open(sys.argv[1]).read(),
                       open(sys.argv[3]).read(),
                       open(sys.argv[2]).read())
    if result:
      print(sys.stderr, result)
      sys.exit(1)
