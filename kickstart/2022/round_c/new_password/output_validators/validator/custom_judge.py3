# Copyright 2011 Google Inc. All Rights Reserved.
"""Basic utilities for custom judges."""

import fractions
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


"""Custom judge for New Password, Kick Start."""

import collections

_BAD_OUTPUT_ERROR_STR = 'Our output is incorrect:'
_BAD_OUTPUT_ERROR = (_BAD_OUTPUT_ERROR_STR + ' {}').format

_BAD_FORMAT_ERROR = 'Output is not well-formatted'
_WRONG_ANSWER = 'The answer is not correct'
_ANSWER_HAS_INVALID_CHARACTERS = 'Answer has invalid characters'
_ANSWER_IS_TOO_SHORT = 'Answer has less than 7 characters'
_ANSWER_IS_TOO_LONG = 'Answer is not of the minimum possible length'
_ANSWER_IS_MISSING_DIGITS = 'Answer is missing digits'
_ANSWER_IS_MISSING_LOWERCASE_ALPHABET = 'Answer is missing lowercase alphabet'
_ANSWER_IS_MISSING_UPPERCASE_ALPHABET = 'Answer is missing uppercase alphabet'
_ANSWER_IS_MISSING_SPECIAL_CHARACTER = 'Answer is missing special character'
_OLD_PASSWORD_IS_NOT_PREFIX_OF_ANSWER = 'Old password is not prefix of answer'
_SPECIAL_CHARACTERS = ['#', '@', '*', '&']

"""Parsed information for a single test case."""
_CaseInput = collections.namedtuple('_CaseInput', ['original_password'])


def ParseInputFile(input_file):
  """Turns an input file into a list of _CaseInputs."""
  # skip the number of cases (line 0)
  input_lines = _utils_Tokenize(input_file)[1:]
  cases = []
  for i in range(1, len(input_lines), 2):
    cases.append(_CaseInput(list(input_lines[i])[0]))
  return cases

def getMinimumLengthOfNewPassword(old_password):
  hasDigit = False
  hasSpecialCharacter = False
  hasLowercaseAlphabet = False
  hasUppercaseAlphabet = False

  minimum_length = len(old_password)

  for c in old_password:
    if c.isdigit():
      hasDigit = True
    if c in _SPECIAL_CHARACTERS:
      hasSpecialCharacter = True
    if c.islower():
      hasLowercaseAlphabet = True
    if c.isupper():
      hasUppercaseAlphabet = True

  if hasDigit == False:
    minimum_length += 1

  if hasSpecialCharacter == False:
    minimum_length += 1

  if hasLowercaseAlphabet == False:
    minimum_length += 1

  if hasUppercaseAlphabet == False:
    minimum_length += 1

  return max(minimum_length, 7)

def VerifyOutput(lines, case):
  """Checks the output for a single test case.

  Args:
    lines: Tokenized lines (either from our I/OGen's output or a contestant's
      attempt.)
    case: A _CaseInput representing a single test case.

  Returns:
    None if the output is correct, or an error message.
  """

  if len(lines) != 1 and len(lines[0]) != 1:
    return _BAD_FORMAT_ERROR

  new_password = lines[0][0]
  if new_password.startswith(case.original_password) == False:
    return _OLD_PASSWORD_IS_NOT_PREFIX_OF_ANSWER

  if len(new_password) < 7:
    return _ANSWER_IS_TOO_SHORT

  if len(new_password) > getMinimumLengthOfNewPassword(case.original_password):
    return _ANSWER_IS_TOO_LONG

  hasDigit = False
  hasSpecialCharacter = False
  hasLowercaseAlphabet = False
  hasUppercaseAlphabet = False

  for c in new_password:
    if c.isdigit():
      hasDigit = True
    elif c in _SPECIAL_CHARACTERS:
      hasSpecialCharacter = True
    elif c.islower():
      hasLowercaseAlphabet = True
    elif c.isupper():
      hasUppercaseAlphabet = True
    else:
      return _ANSWER_HAS_INVALID_CHARACTERS

  if hasDigit == False:
    return _ANSWER_IS_MISSING_DIGITS

  if hasSpecialCharacter == False:
    return _ANSWER_IS_MISSING_SPECIAL_CHARACTER

  if hasLowercaseAlphabet == False:
    return _ANSWER_IS_MISSING_LOWERCASE_ALPHABET

  if hasUppercaseAlphabet == False:
    return _ANSWER_IS_MISSING_UPPERCASE_ALPHABET

  return None


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


def FindError(input_file, output_file, attempt_file):
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

  # Everything passes.
  return None


class NewPasswordUnitTest():

  def assertIsNone(self, a):
    assert a is None

  def assertEqual(self, a, b):
    assert a == b, (a, b)

  def assertStartsWith(self, a, b):
    assert a.startswith(b), (a, b)

  input_file = """
9
3
2@B
3
&b3
3
4cC
3
d&D
9
@@@eeeEEE
9
fffYYY555
9
FFF666***
9
777###ggg
7
1a@&*#A
""".lstrip()

  output_file = """
Case #1: 2@Bhijk
Case #2: &b3HIJK
Case #3: 4cC@&*#
Case #4: d&D8900
Case #5: @@@eeeEEE8
Case #6: fffYYY555&
Case #7: FFF666***m
Case #8: 777###gggV
Case #9: 1a@&*#A
""".lstrip()

  def testCorrectAnswerDoesNotCauseError(self):
    self.assertIsNone(
        FindError(self.input_file, self.output_file, self.output_file))


  def testCorrectAnswerDifferentPasswordDoesNotCauseError(self):
    self.assertIsNone(
        FindError(self.input_file, self.output_file, """
Case #1: 2@B2@Bx
Case #2: &b3&b3H
Case #3: 4cC4cC*
Case #4: d&Dd&D8
Case #5: @@@eeeEEE7
Case #6: fffYYY555*
Case #7: FFF666***k
Case #8: 777###gggZ
Case #9: 1a@&*#A
""".lstrip()))

  def testEmptyAttemptCausesError(self):
    self.assertEqual('Invalid attempt file: Too few cases.',
                     FindError(self.input_file, self.output_file, ''))

  def testBadHeaderCausesError(self):
    self.assertEqual(
        'Invalid attempt file: Expected "case #1:", found "Case ##1:".',
        FindError(self.input_file, self.output_file,
                  'Case ##1: 1a@$*#A'))

    self.assertEqual(
        'Invalid attempt file: File does not begin with "case #1:".',
        FindError(
            self.input_file, self.output_file, """
1a@$*#A
""".lstrip()))

  def testMissingCaseCausesError(self):
    self.assertEqual(
        'Invalid attempt file: Too few cases.',
        FindError(
            self.input_file, self.output_file, """
Case #1: 2@B2@Bx
""".lstrip()))

  def testAnswerIsNotPrefixOfOldPassword(self):
    self.assertEqual(
        'Case #1: ' + _OLD_PASSWORD_IS_NOT_PREFIX_OF_ANSWER,
        FindError("""
1
2
2wS@
""".lstrip(), """
Case #1: 2wS@@Bx
""".lstrip(), """
Case #1: 2@B2@Bx
""".lstrip()))

  def testAnswerIsTooShort(self):
    self.assertEqual(
        'Case #1: ' + _ANSWER_IS_TOO_SHORT,
        FindError("""
1
2
2wS@
""".lstrip(), """
Case #1: 2wS@@Bx
""".lstrip(), """
Case #1: 2wS@@B
""".lstrip()))

  def testAnswerIsTooLong(self):
    self.assertEqual(
        'Case #1: ' + _ANSWER_IS_TOO_LONG,
        FindError("""
1
9
@@@eeeEEE
""".lstrip(), """
Case #1: @@@eeeEEE7
""".lstrip(), """
Case #1: @@@eeeEEE78
""".lstrip()))

  def testAnswerHasInvalidCharacters(self):
    self.assertEqual(
        'Case #1: ' + _ANSWER_HAS_INVALID_CHARACTERS,
        FindError("""
1
4
2wS@
""".lstrip(), """
Case #1: 2wS@@Bx
""".lstrip(), """
Case #1: 2wS@@B-
""".lstrip()))

  def testAnswerIsMissingDigits(self):
    self.assertEqual(
        'Case #1: ' + _ANSWER_IS_MISSING_DIGITS,
        FindError("""
1
9
@@@eeeEEE
""".lstrip(), """
Case #1: @@@eeeEEE7
""".lstrip(), """
Case #1: @@@eeeEEE&
""".lstrip()))

  def testAnswerIsMissingSpecialCharacters(self):
    self.assertEqual(
        'Case #1: ' + _ANSWER_IS_MISSING_SPECIAL_CHARACTER,
        FindError("""
1
4
22eeRR
""".lstrip(), """
Case #1: 22eeRR&
""".lstrip(), """
Case #1: 22eeRR5
""".lstrip()))

  def testAnswerIsMissingLowercaseAlphabet(self):
    self.assertEqual(
        'Case #1: ' + _ANSWER_IS_MISSING_LOWERCASE_ALPHABET,
        FindError("""
1
4
22&*RR
""".lstrip(), """
Case #1: 22&*RRy
""".lstrip(), """
Case #1: 22&*RRR
""".lstrip()))

  def testAnswerIsMissingUppercaseAlphabet(self):
    self.assertEqual(
        'Case #1: ' + _ANSWER_IS_MISSING_UPPERCASE_ALPHABET,
        FindError("""
1
4
777###ggg
""".lstrip(), """
Case #1: 777###gggZ
""".lstrip(), """
Case #1: 777###ggg@
""".lstrip()))


def RunUnitTests():
  test = NewPasswordUnitTest()
  test_methods = [
      method_name for method_name in dir(test)
      if callable(getattr(test, method_name)) and method_name.startswith('test')
  ]
  for test_method in test_methods:
    print(test_method)
    getattr(test, test_method)()

  print('NewPasswordUnitTest passes.')
  sys.exit(0)


if __name__ == '__main__':
  if sys.argv[1] == '-2':
    RunUnitTests()

  result = FindError(open(sys.argv[1]).read(),
                     open(sys.argv[3]).read(),
                     open(sys.argv[2]).read())
  if result:
    print(result, file=sys.stderr)
    sys.exit(1)
