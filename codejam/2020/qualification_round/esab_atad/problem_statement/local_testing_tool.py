# Usage: `python local_testing_tool.py test_number`, where the argument
# test_number is either 0 (Test Set 1), 1 (Test Set 2) or 2 (Test Set 3).

import itertools
import random
import sys

# Use raw_input in Python2.
try:
  input = raw_input
except NameError:
  pass

MAX_QUERIES = 150
NUM_CASES = 100

_ERROR_MSG_EXTRA_NEW_LINES = 'Input has extra newline characters.'
_ERROR_MSG_INVALID_CHARACTER = 'Input contains character other than 0 and 1.'
_ERROR_MSG_INVALID_INPUT = 'Input is neither a number or a string with correct length.'
_ERROR_MSG_INPUT_OUT_OF_RANGE = 'Input position is out of range.'
_ERROR_MSG_READ_FAILURE = 'Read for input fails.'
_ERROR_MSG_WRONG_ANSWER_FORMAT_STR = 'Wrong answer: contestant input {}, but answer is {}.'
_ERROR_MSG_MAX_QUERIES_EXCEED = 'Contestant tries to query too many times.'

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


def Reverse(s):
  return s[::-1]


def BitFlip(s):
  return ''.join(str(1 - int(c)) for c in s)


class JudgeSingleCase(object):

  def __init__(self, io, initial_arr):
    self.io = io
    self.io.SetCurrentCase(self)

    self.arr = initial_arr
    self.len = len(self.arr)

  def _ParseContestantInput(self, response):
    """Parses contestant's input.

    Parses contestant's input, which should be a number between 1 and self.len,
    or a string of length exactly self.len which contains only 0 and 1.

    Args:
      response: (str) one-line input given by the contestant.

    Returns:
      A int or str of the contestant's input.
      Also, an error string if input is invalid, otherwise None.
    """
    if ('\n' in response) or ('\r' in response):
      return None, _ERROR_MSG_EXTRA_NEW_LINES

    if len(response) == self.len:
      if any(c not in '01' for c in response):
        return None, _ERROR_MSG_INVALID_CHARACTER
      return response, None

    try:
      num = int(response)
      if not 1 <= num <= self.len:
        return None, _ERROR_MSG_INPUT_OUT_OF_RANGE
      return num, None
    except ValueError:
      return None, _ERROR_MSG_INVALID_INPUT

  def _ReadContestantInput(self):
    """Reads contestant's input.

    Reads contestant's input,  which should be a number between 1 and self.len,
    or a string of length exactly self.len which contains only 0 and 1.

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
    for i in range(MAX_QUERIES + 1):
      contestant_input, err = self._ReadContestantInput()
      if err is not None:
        return err

      if isinstance(contestant_input, str):
        if self.arr != contestant_input:
          return _ERROR_MSG_WRONG_ANSWER_FORMAT_STR.format(
              contestant_input[:2 * self.len], self.arr)
        self.io.PrintOutput(_CORRECT_MSG)
        return None

      if i == MAX_QUERIES:
        return _ERROR_MSG_MAX_QUERIES_EXCEED

      if i % 10 == 0:
        # Number of queries we've received ends with 1
        if random.randint(0, 1):
          self.arr = Reverse(self.arr)
        if random.randint(0, 1):
          self.arr = BitFlip(self.arr)
      self.io.PrintOutput(self.arr[contestant_input - 1])


def RandomBitString(b):
  return ''.join(str(random.randint(0, 1)) for _ in range(b))


def GenerateInputs(b):
  assert b in (10, 20, 100)

  cases = set()

  # Add your own cases here.
  # The one included here is just an example and is not necessarily part of
  # any real test set.
  cases.add('1' * b)

  while len(cases) < NUM_CASES:
    cases.add(RandomBitString(b))

  cases = list(cases)
  random.shuffle(cases)
  assert len(cases) == NUM_CASES
  assert all(len(case) == b for case in cases)
  assert all(all(c in '01' for c in case) for case in cases)
  return cases


def JudgeAllCases(test_number, io):
  """Sends input to contestant and judges contestant output.

  Returns:
    An error string, or None if the attempt was correct.
  """
  b = (10, 20, 100)[test_number]
  inputs = GenerateInputs(b)

  io.PrintOutput('{} {}'.format(NUM_CASES, b))
  for case_number in range(NUM_CASES):
    single_case = JudgeSingleCase(io, inputs[case_number])
    err = single_case.Judge()
    if err is not None:
      return 'Case #{} fails:\n{}'.format(case_number + 1, err)

  # Make sure nothing other than EOF is printed after all cases finish.
  try:
    response = io.ReadInput()
  except EOFError:
    return None
  except Exception:  # pylint: disable=broad-except
    return 'Exception raised while reading input after all cases finish.'
  return 'Additional input after all cases finish: {}'.format(response[:1000])


def main():
  try:
    test_number = int(sys.argv[1])
    assert test_number in (0, 1, 2)
    # Remember that the local testing tool is not guaranteed to implement
    # randomness in the same way as the actual judge.
    random.seed(123456 + test_number)
    io = IO()
    result = JudgeAllCases(test_number, io)
    if result is not None:
      print(result, file=sys.stderr)
      io.PrintOutput(_WRONG_ANSWER_MSG)
      sys.exit(1)
  except Exception as exception:
    # Hopefully this will never happen, but try to finish gracefully
    # and report a judge error in case of unexpected exception.
    io.PrintOutput(_WRONG_ANSWER_MSG)
    print('JUDGE_ERROR! Internal judge exception:', file=sys.stderr)
    print(str(exception)[:1000], file=sys.stderr)
    sys.exit(1)


if __name__ == '__main__':
  main()
