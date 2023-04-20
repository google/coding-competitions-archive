"""judge.py for the ESAb ATAd interactive judge.
"""

# Usage: `judge.py test_number`, where the argument test_number is either 0
# (Test Set 1), 1 (Test Set 2) or 2 (Test Set 3).

import itertools
import random
import sys


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

  cases.add('0' * b)
  cases.add('01' * (b // 2))
  cases.add('0' * (b // 2) + '1' * (b // 2))
  if b > 10:
    cases.add(('0' * 10 + '1' * 10) * (b // 20))

  for p in [2, 4, 10, 20]:
    if b % p != 0:
      continue
    for _ in range(4):
      r = RandomBitString(b // p)
      cases.add(r * p)
      r = RandomBitString(b // p)
      cases.add((r + Reverse(r)) * (p // 2))
      r = RandomBitString(b // p)
      cases.add((r + BitFlip(Reverse(r))) * (p // 2))


  for p in range(0, b, 10):
    for d in range(0, 2):
      x = p + d
      s = RandomBitString(b // 2)
      s1 = s + Reverse(s)
      cases.add(s1[0:x] + BitFlip(s1[x]) + s1[x+1:])
      s2 = s + Reverse(BitFlip(s))
      cases.add(s2[0:x] + BitFlip(s1[x]) + s2[x+1:])

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


def TestParseContestantInput():
  for b in [10, 20, 100]:
    case = JudgeSingleCase(IO(), '0' * b)
    for value in range(1, b + 1):
      assert case._ParseContestantInput(str(value)) == (value, None)

    for contestant_input in [
        '0', '-1', '-514', '596', '1204', str(10**30), str(-10**31)
    ]:
      assert case._ParseContestantInput(contestant_input) == (
          None, _ERROR_MSG_INPUT_OUT_OF_RANGE)

    for contestant_input in ['NaN', '0CODEJAM', 'RABBIT', '']:
      assert case._ParseContestantInput(contestant_input) == (
          None, _ERROR_MSG_INVALID_INPUT)

    for contestant_input in ['A' * b, '0' * (b - 1) + '2', ' ' * b]:
      assert case._ParseContestantInput(contestant_input) == (
          None, _ERROR_MSG_INVALID_CHARACTER)

    for _ in range(100):
      contestant_input = RandomBitString(b)
      assert case._ParseContestantInput(contestant_input) == (contestant_input,
                                                              None)


_ANSWER = object()


class MockIO(object):

  def __init__(self, inputs):
    self.inputs = inputs
    self.outputs = []
    self.case = None

  def ReadInput(self):
    if self.inputs:
      v = self.inputs.pop(0)
      if v is _ANSWER:
        assert self.case is not None
        return self.case.arr
      return v
    raise EOFError

  def PrintOutput(self, output):
    self.outputs.append(str(output))

  def SetCurrentCase(self, case):
    self.case = case


def TestJudgeSingleCase():
  for b in [10, 20, 100]:
    mock_io = MockIO(
        list(
            itertools.chain.from_iterable(
                [str(random.randint(1, b))] * 10 for _ in range(12))))
    ans = RandomBitString(b)
    case = JudgeSingleCase(mock_io, ans)
    wrong_answer = BitFlip(ans[0]) + ans[1:]
    mock_io.inputs.append(wrong_answer)

    err = case.Judge()
    assert err == _ERROR_MSG_WRONG_ANSWER_FORMAT_STR.format(
        wrong_answer, case.arr)

    assert len(mock_io.outputs) == 120
    assert all(o in '01' for o in mock_io.outputs)
    for i, c in enumerate(mock_io.outputs):
      # The array shouldn't change while number of queries doesn't end with 1.
      assert c == mock_io.outputs[i // 10 * 10]

    # The answer should not be consumed.
    mock_io = MockIO(['1'] * (MAX_QUERIES + 1) + [_ANSWER])
    case = JudgeSingleCase(mock_io, ans)

    err = case.Judge()
    assert err == _ERROR_MSG_MAX_QUERIES_EXCEED
    assert len(mock_io.outputs) == MAX_QUERIES
    assert mock_io.inputs

    # We somehow guessed the correct answer.
    mock_io = MockIO(['1'] * MAX_QUERIES + [_ANSWER])
    case = JudgeSingleCase(mock_io, ans)

    err = case.Judge()
    assert err is None
    assert len(mock_io.outputs) == MAX_QUERIES + 1
    assert mock_io.outputs[-1] == _CORRECT_MSG

    # We somehow guessed the correct answer super early.
    mock_io = MockIO(['1', '2', '3', _ANSWER])
    case = JudgeSingleCase(mock_io, ans)

    err = case.Judge()
    assert err is None
    assert len(mock_io.outputs) == 4
    assert mock_io.outputs[-1] == _CORRECT_MSG


def TestJudgeAllCases():
  mock_io = MockIO(['1', _ANSWER, '2', _ANSWER, '3', 'RABBIT'])
  err = JudgeAllCases(0, mock_io)
  assert err == 'Case #3 fails:\n' + _ERROR_MSG_INVALID_INPUT
  assert len(mock_io.outputs) == 6
  assert mock_io.outputs[0] == '{} 10'.format(NUM_CASES)
  assert mock_io.outputs[2] == _CORRECT_MSG
  assert mock_io.outputs[4] == _CORRECT_MSG

  mock_io = MockIO(['1', _ANSWER, '2', _ANSWER, '3', 'RABBIT'])
  err = JudgeAllCases(1, mock_io)
  assert err == 'Case #3 fails:\n' + _ERROR_MSG_INVALID_INPUT
  assert len(mock_io.outputs) == 6
  assert mock_io.outputs[0] == '{} 20'.format(NUM_CASES)
  assert mock_io.outputs[2] == _CORRECT_MSG
  assert mock_io.outputs[4] == _CORRECT_MSG

  mock_io = MockIO(['1', '2', _ANSWER, '3', _ANSWER, '4', _ANSWER])
  err = JudgeAllCases(2, mock_io)
  assert err == 'Case #4 fails:\n' + _ERROR_MSG_READ_FAILURE
  assert len(mock_io.outputs) == 8
  assert mock_io.outputs[0] == '{} 100'.format(NUM_CASES)

  mock_io = MockIO(['1', _ANSWER, _ANSWER, _ANSWER] + ['12'] * MAX_QUERIES)
  err = JudgeAllCases(2, mock_io)
  assert err == 'Case #4 fails:\n' + _ERROR_MSG_READ_FAILURE
  assert len(mock_io.outputs) == MAX_QUERIES + 5
  assert mock_io.outputs[0] == '{} 100'.format(NUM_CASES)

  mock_io = MockIO(['1', _ANSWER, _ANSWER, _ANSWER] + ['12'] * (MAX_QUERIES + 1))
  err = JudgeAllCases(2, mock_io)
  assert err == 'Case #4 fails:\n' + _ERROR_MSG_MAX_QUERIES_EXCEED
  assert len(mock_io.outputs) == MAX_QUERIES + 5
  assert mock_io.outputs[0] == '{} 100'.format(NUM_CASES)

  mock_io = MockIO(['42', '42', '42', _ANSWER] * NUM_CASES)
  err = JudgeAllCases(2, mock_io)
  assert err is None
  assert len(mock_io.outputs) == 1 + (4 * NUM_CASES)
  assert mock_io.outputs[0] == '{} 100'.format(NUM_CASES)


def Test():
  TestParseContestantInput()
  TestJudgeSingleCase()
  TestJudgeAllCases()


def main():
  if sys.argv[1] == '-2':
    Test()
  else:
    try:
      test_number = int(sys.argv[1])
      random.seed(1204 + test_number)
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
