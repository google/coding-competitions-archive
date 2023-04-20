"""judge.py for the Power Arrangers interactive judge.
"""

# Usage: `judge.py test_number`, where the argument test_number is either 0
# (small) or 1 (large).

import itertools
import random
import sys


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
    return raw_input()

  def PrintOutput(self, output):
    print output
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
    for i in xrange(self.max_inspection + 1):
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
  for case_number in xrange(1, NUM_CASES + 1):
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


def TestParseContestantInput():
  case = JudgeSingleCase(150, IO())
  for value in range(1, 596):
    assert case._ParseContestantInput(str(value)) == (value, None)

  for contestant_input in [
      '0', '-1', '-514', '596', '1204', '2147483648', '-2147483648'
  ]:
    assert case._ParseContestantInput(contestant_input) == (
        None, _ERROR_MSG_INVALID_POSITION)

  for contestant_input in ['NaN', '2019CODEJAM', 'RABBIT', '']:
    assert case._ParseContestantInput(contestant_input) == (
        None, _ERROR_MSG_INCORRECT_WORD_LENGTH)

  for contestant_input in ['AAAAA', 'BCDEF', 'BADEE', 'HOUSE', 'POWER']:
    assert case._ParseContestantInput(contestant_input) == (
        None, _ERROR_MSG_INVALID_PERMUTATION)

  for permutation in itertools.permutations('ABCDE'):
    contestant_input = ''.join(permutation)
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
        return self.case.answer
      return v
    raise EOFError

  def PrintOutput(self, output):
    self.outputs.append(str(output))

  def SetCurrentCase(self, case):
    self.case = case


def TestJudgeSingleCase():
  mock_io = MockIO([str(i) for i in range(1, 101)] + ['595'])
  case = JudgeSingleCase(150, mock_io)
  # Something that's a permutation of ABCDE but is definitely wrong.
  wrong_answer = case.answer[::-1]
  mock_io.inputs.append(wrong_answer)

  err = case.Judge()
  assert err == _ERROR_MSG_WRONG_ANSWER_FORMAT_STR.format(
      wrong_answer, case.answer)

  assert len(mock_io.outputs) == 101
  assert all(len(o) == 1 and 'A' <= o <= 'E' for o in mock_io.outputs)
  for i in range(0, 100, 5):
    assert ''.join(sorted(mock_io.outputs[i:i+5])) == 'ABCDE'

  for limit in [150, 475]:
    # The answer should not be consumed.
    mock_io = MockIO(['217'] * (limit + 1) + [_ANSWER])
    case = JudgeSingleCase(limit, mock_io)
    mock_io.inputs.append(case.answer)

    err = case.Judge()
    assert err == _ERROR_MSG_MAX_INSPECTION_EXCEED
    assert len(mock_io.outputs) == limit
    assert mock_io.inputs
    assert len(set(mock_io.outputs)) == 1

    # We somehow guessed the correct answer.
    mock_io = MockIO(['217'] * limit + [_ANSWER])
    case = JudgeSingleCase(limit, mock_io)

    err = case.Judge()
    assert err is None
    assert len(mock_io.outputs) == limit + 1
    assert mock_io.outputs[-1] == _CORRECT_MSG

    # We somehow guessed the correct answer super early.
    mock_io = MockIO(['1', '2', '3', _ANSWER])
    case = JudgeSingleCase(limit, mock_io)

    err = case.Judge()
    assert err is None
    assert len(mock_io.outputs) == 4
    assert mock_io.outputs[-1] == _CORRECT_MSG


def TestJudgeAllCases():
  mock_io = MockIO(['1', _ANSWER, '2', _ANSWER, '3', 'RABBIT'])
  err = JudgeAllCases(0, mock_io)
  assert err == 'Case #3 fails:\n' + _ERROR_MSG_INCORRECT_WORD_LENGTH
  assert len(mock_io.outputs) == 6
  assert mock_io.outputs[0] == str(NUM_CASES) + ' 475'
  assert mock_io.outputs[2] == _CORRECT_MSG
  assert mock_io.outputs[4] == _CORRECT_MSG

  mock_io = MockIO(['1', '2', _ANSWER, '3', _ANSWER, '4', _ANSWER])
  err = JudgeAllCases(1, mock_io)
  assert err == 'Case #4 fails:\n' + _ERROR_MSG_READ_FAILURE
  assert len(mock_io.outputs) == 8
  assert mock_io.outputs[0] == str(NUM_CASES) + ' 150'

  mock_io = MockIO(['1', _ANSWER, _ANSWER, _ANSWER] + ['274'] * 150)
  err = JudgeAllCases(1, mock_io)
  assert err == 'Case #4 fails:\n' + _ERROR_MSG_READ_FAILURE
  assert len(mock_io.outputs) == 155
  assert mock_io.outputs[0] == str(NUM_CASES) + ' 150'

  mock_io = MockIO(['1', _ANSWER, _ANSWER, _ANSWER] + ['274'] * 151)
  err = JudgeAllCases(1, mock_io)
  assert err == 'Case #4 fails:\n' + _ERROR_MSG_MAX_INSPECTION_EXCEED
  assert len(mock_io.outputs) == 155
  assert mock_io.outputs[0] == str(NUM_CASES) + ' 150'

  mock_io = MockIO(['514', '514', '514', _ANSWER] * NUM_CASES)
  err = JudgeAllCases(1, mock_io)
  assert err is None
  assert len(mock_io.outputs) == 1 + (4 * NUM_CASES)
  assert mock_io.outputs[0] == str(NUM_CASES) + ' 150'


def Test():
  TestParseContestantInput()
  TestJudgeSingleCase()
  TestJudgeAllCases()


def main():
  if sys.argv[1] == '-2':
    Test()
  else:
    test_number = int(sys.argv[1])
    random.seed(514514 + test_number)
    io = IO()
    result = JudgeAllCases(test_number, io)
    if result is not None:
      print >> sys.stderr, result
      io.PrintOutput(_WRONG_ANSWER_MSG)
      sys.exit(1)


if __name__ == '__main__':
  main()
