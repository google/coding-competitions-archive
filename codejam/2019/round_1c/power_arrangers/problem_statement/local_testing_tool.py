# Usage: `python testing_tool.py test_number`, where the argument test_number is
# either 0 (first test set) or 1 (second test set).
# This can also be run as `python3 testing_tool.py test_number`.
import itertools
import random
import sys

# Use raw_input in Python2.
try:
  input = raw_input
except NameError:
  pass

NUM_CASES = 50

_ERROR_MSG_EXTRA_NEW_LINES = 'Input has extra newline characters.'
_ERROR_MSG_INVALID_POSITION = 'Input is not a valid position.'
_ERROR_MSG_INCORRECT_WORD_LENGTH = 'Input is not of length 5.'
_ERROR_MSG_INVALID_PERMUTATION = 'Input is not a permutation of ABCDE.'
_ERROR_MSG_READ_FAILURE = 'Read for input fails.'
_ERROR_MSG_MAX_INSPECTION_EXCEED = 'Contestant tries to inspect figures too many times.'
_ERROR_MSG_WRONG_ANSWER_FORMAT_STR = 'Wrong answer: contestant input {}, but answer is {}.'

_CORRECT_MSG = 'Y'
_WRONG_ANSWER_MSG = 'N'


class IO(object):

  def ReadInput(self):
    return input()

  def PrintOutput(self, output):
    print(output)
    sys.stdout.flush()

  def SetCurrentCase(self, case):
    pass


class JudgeSingleCase(object):

  def __init__(self, max_inspection, io):
    self.io = io
    self.io.SetCurrentCase(self)
    self.max_inspection = max_inspection
    permutations = [''.join(p) for p in itertools.permutations('ABCDE')]
    random.shuffle(permutations)
    self.answer = permutations.pop()
    self.figures = ''.join(permutations)

  def _ParseContestantInput(self, response):
    """Parses contestant's input.

    Parses contestant's input, which should be a number between 1 and 595, or a
    string of length 5 which is a permutation of 'A'-'E'.

    Args:
      response: (str) one-line input given by the contestant.

    Returns:
      A int or str of the contestant's input.
      Also, an error string if input is invalid, otherwise None.
    """
    if ('\n' in response) or ('\r' in response):
      return None, _ERROR_MSG_EXTRA_NEW_LINES

    try:
      num = int(response)
      if not 1 <= num <= len(self.figures):
        return None, _ERROR_MSG_INVALID_POSITION
      return num, None
    except ValueError:
      if len(response) != 5:
        return None, _ERROR_MSG_INCORRECT_WORD_LENGTH
      if ''.join(sorted(response)) != 'ABCDE':
        return None, _ERROR_MSG_INVALID_PERMUTATION
      return response, None

  def _ReadContestantInput(self):
    """Reads contestant's input.

    Reads contestant's input, which should be a number between 1 and 595, or a
    string of length 5 which is a permutation of 'A'-'E'.

    Returns:
      A int or str of the contestant's input.
      Also, an error string if input is invalid, otherwise None.
    """
    try:
      contestant_input = self.io.ReadInput()
    except Exception:
      return None, _ERROR_MSG_READ_FAILURE

    return self._ParseContestantInput(contestant_input)

  def Judge(self):
    """Judges one single case; should only be called once per test case.

    Returns:
      An error string if an I/O rule was violated or the answer was incorrect,
      otherwise None.
    """
    for i in range(self.max_inspection + 1):
      contestant_input, err = self._ReadContestantInput()
      if err is not None:
        return err

      if isinstance(contestant_input, str):
        if self.answer != contestant_input:
          return _ERROR_MSG_WRONG_ANSWER_FORMAT_STR.format(
              contestant_input, self.answer)
        self.io.PrintOutput(_CORRECT_MSG)
        return None

      if i == self.max_inspection:
        return _ERROR_MSG_MAX_INSPECTION_EXCEED

      self.io.PrintOutput(self.figures[contestant_input - 1])


def JudgeAllCases(test_number, io):
  """Sends input to contestant and judges contestant output.

  Returns:
    An error string, or None if the attempt was correct.
  """
  max_inspection = [475, 150][test_number]

  io.PrintOutput('{} {}'.format(NUM_CASES, max_inspection))
  for case_number in range(1, NUM_CASES + 1):
    single_case = JudgeSingleCase(max_inspection, io)
    err = single_case.Judge()
    if err is not None:
      return 'Case #{} fails:\n{}'.format(case_number, err)

  # Make sure nothing other than EOF is printed after all cases finish.
  try:
    response = io.ReadInput()
  except EOFError:
    return None
  except Exception:  # pylint: disable=broad-except
    return 'Exception raised while reading input after all cases finish.'
  return 'Additional input after all cases finish: {}'.format(response[:1000])


def main():
  test_number = int(sys.argv[1])
  # We have provided one implementation of randomness here, but it is not
  # necessarily what will be used in the real judge.
  random.seed(2 + test_number)
  io = IO()
  result = JudgeAllCases(test_number, io)
  if result is not None:
    print(result, file=sys.stderr)
    io.PrintOutput(_WRONG_ANSWER_MSG)
    sys.exit(1)


if __name__ == '__main__':
  main()
