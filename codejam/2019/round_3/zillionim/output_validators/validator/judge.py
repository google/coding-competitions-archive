"""judge.py for Zillionim."""

# Usage: `judge.py test_number`, where the argument test_number is either 0
# (small), 1 (large), 2 (second large) or -2 (test mode).

from __future__ import print_function
import sys
import random

T = 500
W = (300, 475, 499)
B = 10 ** 10
C = B * 100

INVALID_OUTPUT = -1
YOU_WIN = -2
YOU_LOSE = -3

class Error(Exception):
  pass


class JudgeError(Exception):
  pass


def AssertEqual(expected, actual):
  assert expected == actual, (
      "Expected [{}], got [{}]".format(expected, actual))


def AssertReturns(expected, fn, *args):
  result = fn(*args)
  AssertEqual(expected, result)


def AssertRaisesError(expected_message, fn, *args):
  try:
    fn(*args)
    assert False, (
        "Expected error [{}], but there was none".format(expected_message))
  except Error as error:
    message = str(error)
    assert expected_message == message, (
        "Expected error [{}], got [{}]".format(expected_message, message))


def AssertReturnsIO(expected_return, expected_output, fn, *args):
  test_output_storage = []
  AssertReturns(expected_return, fn, *(args + (test_output_storage,)))
  AssertEqual(expected_output, test_output_storage)


def AssertRaisesErrorIO(expected_message, expected_output, fn, *args):
  test_output_storage = []
  AssertRaisesError(expected_message, fn, *(args + (test_output_storage,)))
  AssertEqual(expected_output, test_output_storage)


INVALID_LINE_ERROR = "Couldn't read a valid line."
TOO_LONG_LINE = "Too long line: {}".format
NOT_INTEGER_ERROR = "Not an integer: {}".format
INVALID_PLAY_ERROR = "Tried to play {} on status {}".format
CASE_FAILED_ERROR = "Case #{} failed: {}".format
TOO_FEW_WINS_ERROR = "Too few wins {}: expected {}".format
EXCEPTION_AFTER_END_ERROR = (
    "Exception raised while reading input after all cases finish.")
ADDITIONAL_INPUT_ERROR = "Additional input after all cases finish: {}".format


def ReadValue(line):
  if len(line) > 100:
    raise Error(TOO_LONG_LINE(len(line)))
  if len(line.split()) > 1:  # int("- 2") works in Python2 but not in Python3.
    raise Error(NOT_INTEGER_ERROR(line))
  try:
    r = int(line)
  except:
    raise Error(NOT_INTEGER_ERROR(line))
  return r


def TestReadValue():
  AssertReturns(1, ReadValue, "1")
  AssertReturns(10, ReadValue, " 10 ")
  AssertReturns(0, ReadValue, "0")
  AssertReturns(-1, ReadValue, " -1")
  AssertRaisesError(NOT_INTEGER_ERROR("- 2"), ReadValue, "- 2")
  AssertRaisesError(NOT_INTEGER_ERROR("foo"), ReadValue, "foo")
  AssertRaisesError(NOT_INTEGER_ERROR("1 1"), ReadValue, "1 1")
  AssertRaisesError(NOT_INTEGER_ERROR("-1 1"), ReadValue, "-1 1")
  AssertRaisesError(TOO_LONG_LINE(1000), ReadValue, "x" * 1000)


def ApplyPlay(status, p):
  """status is a list of pairs [a, b) stating coins a,a+1,...,b-1 are still
     there, such that status[i][1] < status[i][0] - 1 and b-a >= B for all
     pairs. It returns another status with the same format removing coins
     p, p+1, ..., p+B-1."""
  new_status = []
  found_valid = False
  for a, b in status:
    if a <= p <= b - B:
      found_valid = True
      if p - a >= B:
        new_status.append((a, p))
      if b - (p + B) >= B:
        new_status.append((p + B, b))
    else:
      new_status.append((a, b))
  if not found_valid:
    raise Error(INVALID_PLAY_ERROR(p, status))
  return new_status

def TestApplyPlay():
  AssertReturns([], ApplyPlay, [(1, B + 1)], 1)
  AssertReturns([], ApplyPlay, [(1, B + B)], 1)
  AssertReturns([], ApplyPlay, [(1, B + B)], B)
  AssertReturns([(1, B + 1)], ApplyPlay, [(1, B + B + 1)], B + 1)
  AssertReturns([(B + 1, B + B + 1)], ApplyPlay, [(1, B + B + 1)], 1)
  AssertReturns([(1, B + 1), (B + B + 1, B + B + B + 1)], ApplyPlay,
                [(1, B + B + B + 1)], B + 1)
  AssertReturns([(B + B, B + B + B + 1)], ApplyPlay, [(1, B + B + B + 1)], B)
  AssertReturns([(1, B + 2)], ApplyPlay, [(1, B + B + B + 1)], B + 2)
  AssertReturns([(B + 3, B + B + B + 5), (B + B + B + 7, B + B + B + B + 9)],
                ApplyPlay, [(1, B + 1), (B + 3, B + B + B + 5),
                            (B + B + B + 7, B + B + B + B + 9)], 1)
  AssertReturns([(1, B + 1), (B + 3, B + B + B + 5)],
                ApplyPlay, [(1, B + 1), (B + 3, B + B + B + 5),
                            (B + B + B + 7, B + B + B + B + 9)], B + B + B + 9)
  AssertReturns([(1, B + 1), (B + 3, B + B + 4),
                 (B + B + B + 4, B + B + B + B + 5),
                 (B + B + B + B + 7, B + B + B + B + B + 9)],
                ApplyPlay, [(1, B + 1), (B + 3, B + B + B + B + 5),
                            (B + B + B + B + 7, B + B + B + B + B + 9)], B + B + 4)
  status = [(1, B + 1), (B + 3, B + B + B + B + 5),
            (B + B + B + B + 7, B + B + B + B + B + 9)]
  AssertRaisesError(INVALID_PLAY_ERROR(0, status), ApplyPlay, status, 0)
  AssertRaisesError(INVALID_PLAY_ERROR(B + B + B + B + 10, status), ApplyPlay,
                    status, B + B + B + B + 10)
  AssertRaisesError(INVALID_PLAY_ERROR(3, status), ApplyPlay, status, 3)
  AssertRaisesError(INVALID_PLAY_ERROR(B + 2, status), ApplyPlay, status, B + 2)


def CountValidPoints(status):
  return sum((b - a - B + 1) for a, b in status)


def TestCountValidPoints():
  AssertReturns(1, CountValidPoints, [(1, B + 1)])
  AssertReturns(2, CountValidPoints, [(1, B + 2)])
  AssertReturns(5, CountValidPoints, [(1, B + 2), (B + 3, B + B + 5)])


def IthPoint(status, i):
  """Returns the value of the i-th valid point (0-based)."""
  for j, (a, b) in enumerate(status):
    if b - a - B + 1 > i:
      return a + i
    i -= b - a - B + 1
  assert False


def TestIthPoint():
  AssertReturns(1, IthPoint, [(1, B + 1)], 0)
  AssertReturns(1, IthPoint, [(1, B + 2)], 0)
  AssertReturns(2, IthPoint, [(1, B + 2)], 1)
  AssertReturns(B + 3, IthPoint, [(1, B + 2), (B + 3, B + B + 5)], 2)
  AssertReturns(B + 5, IthPoint, [(1, B + 2), (B + 3, B + B + 5)], 4)
  AssertReturns(B + 5, IthPoint, [(1, B + 2), (B + 3, B + B + 5),
                                  (B + B + 7, B + B + B + 9)], 4)
  AssertReturns(B + 5, IthPoint, [(1, B + 2), (B + 3, B + B + 5),
                                  (B + B + 7, B + B + B + 9)], 4)
  AssertReturns(B + B + 7, IthPoint, [(1, B + 2), (B + 3, B + B + 5),
                                      (B + B + 7, B + B + B + 9)], 5)
  AssertReturns(B + B + 8, IthPoint, [(1, B + 2), (B + 3, B + B + 5),
                                      (B + B + 7, B + B + B + 9)], 6)


def RunCase(test_input=None, test_rnd=None, test_output_storage=None):
  def Input():
    return raw_input() if test_input is None else test_input.pop(0)

  def NextRandom(x):
    if test_rnd is None:
      return random.randrange(x)
    else:
      r = test_rnd.pop(0)
      assert 0 <= r < x, "Wrong random value: {} not in [0,{})".format(r, x)
      return r

  def Output(line):
    if test_input is None:
      print(line)
      sys.stdout.flush()
    else:
      test_output_storage.append(line)

  status = [(1, C + 1)]
  while True:
    if not status:
      Output(YOU_WIN)
      return True
    try:
      valid_points = CountValidPoints(status)
      p = IthPoint(status, NextRandom(valid_points))
      status = ApplyPlay(status, p)
    except Error as err:
      raise JudgeError(err)
    if not status:
      Output(YOU_LOSE)
      return False
    Output(p)
    try:
      line = Input()
      p = ReadValue(line)
      status = ApplyPlay(status, p)
    except Error as err:
      Output(INVALID_OUTPUT)
      raise Error(err)
    except:
      Output(INVALID_OUTPUT)
      raise Error(INVALID_LINE_ERROR)


def TestRunCase():
  # Fake smaller values for easier testing.
  global B, C
  orig = B, C
  B = 3
  C = 15
  AssertRaisesErrorIO(INVALID_LINE_ERROR, [2, INVALID_OUTPUT], RunCase, [], [1])
  AssertRaisesErrorIO(NOT_INTEGER_ERROR("x"), [2, INVALID_OUTPUT], RunCase,
                      ["x"], [1])
  AssertRaisesErrorIO(TOO_LONG_LINE(101), [2, INVALID_OUTPUT], RunCase,
                      ["0" * 101], [1])
  AssertRaisesErrorIO(INVALID_PLAY_ERROR(3, [(5, C + 1)]),
                      [2, INVALID_OUTPUT], RunCase, ["3"], [1])
  AssertRaisesErrorIO(INVALID_PLAY_ERROR(0, [(5, C + 1)]),
                      [2, INVALID_OUTPUT], RunCase, ["0"], [1])
  AssertRaisesErrorIO(INVALID_PLAY_ERROR(-1, [(5, C + 1)]),
                      [2, INVALID_OUTPUT], RunCase, ["-1"], [1])
  AssertRaisesErrorIO(INVALID_PLAY_ERROR(C - B + 2, [(5, C + 1)]),
                      [2, INVALID_OUTPUT], RunCase, [str(C - B + 2)], [1])
  AssertRaisesErrorIO(INVALID_PLAY_ERROR(2 * C, [(5, C + 1)]),
                      [2, INVALID_OUTPUT], RunCase, [str(2 * C)], [1])
  AssertRaisesErrorIO(INVALID_PLAY_ERROR(C - 4, [(9, C - 2)]),
                      [2, C - 2, INVALID_OUTPUT], RunCase, ["6", str(C - 4)],
                      [1, 4])
  AssertReturnsIO(True, [2, 13, YOU_WIN], RunCase, ["6", "10"], [1, 4])
  AssertReturnsIO(False, [2, YOU_LOSE], RunCase, ["6"], [1, 2])
  AssertReturnsIO(False, [6, YOU_LOSE], RunCase, ["2"], [5, 2])
  AssertReturnsIO(False, [1, 7, YOU_LOSE], RunCase, ["4", "10"], [0, 0, 0])
  AssertReturnsIO(True, [1, 7, YOU_WIN], RunCase, ["4", "11"], [0, 0])
  AssertReturnsIO(True, [1, 7, YOU_WIN], RunCase, ["11", "4"], [0, 3])
  B, C = orig


def RunCases(t, w, test_input=None, test_rnd=None, test_output_storage=None):
  wins = 0
  for i in range(1, t + 1):
    # Reset the seed for each case for stability.
    random.seed(45282 + t * t * t + w * t + i)
    try:
      win = RunCase(test_input=test_input, test_rnd=test_rnd,
                    test_output_storage=test_output_storage)
    except Error as err:
      raise Error(CASE_FAILED_ERROR(i, err))
    if win:
      wins += 1
  print("All cases completed. Got {} wins out of {} total games "
        "({} needed for CORRECT)".format(wins, t, w),
        file=sys.stderr)
  def Input():
    if test_input is None:
      return raw_input()
    else:
      if test_input:
        return test_input.pop(0)
      else:
        raise EOFError()

  try:
    extra_input = Input()
  except EOFError:
    if wins < w:
      raise Error(TOO_FEW_WINS_ERROR(wins, w))
    return
  except Exception:  # pylint: disable=broad-except
    raise Error(EXCEPTION_AFTER_END_ERROR)
  raise Error(ADDITIONAL_INPUT_ERROR(extra_input[:100]))

def TestRunCases():
  # Fake smaller values for easier testing.
  global B, C
  orig = B, C
  B = 3
  C = 15
  AssertRaisesErrorIO(CASE_FAILED_ERROR(1, INVALID_LINE_ERROR),
                      [2, INVALID_OUTPUT], RunCases, 1, 0, [], [1])
  AssertRaisesErrorIO(CASE_FAILED_ERROR(1, NOT_INTEGER_ERROR("x")),
                      [2, INVALID_OUTPUT], RunCases, 1, 0, ["x"], [1])
  AssertRaisesErrorIO(CASE_FAILED_ERROR(1, TOO_LONG_LINE(101)),
                      [2, INVALID_OUTPUT], RunCases, 1, 0, ["0" * 101], [1])
  AssertRaisesErrorIO(CASE_FAILED_ERROR(1, INVALID_PLAY_ERROR(3, [(5, C + 1)])),
                      [2, INVALID_OUTPUT], RunCases, 1, 0, ["3"], [1])
  AssertRaisesErrorIO(CASE_FAILED_ERROR(2, INVALID_LINE_ERROR),
                      [2, YOU_LOSE, 1, INVALID_OUTPUT], RunCases, 2, 1, ["6"],
                      [1, 2, 0])
  AssertRaisesErrorIO(TOO_FEW_WINS_ERROR(0, 1), [2, YOU_LOSE], RunCases, 1, 1,
                      ["6"], [1, 2])
  AssertReturnsIO(None, [2, YOU_LOSE], RunCases, 1, 0, ["6"], [1, 2])
  AssertReturnsIO(None, [1, 7, YOU_WIN], RunCases, 1, 1, ["4", "11"], [0, 0])
  AssertReturnsIO(None, [1, 7, YOU_WIN, 1, 7, YOU_WIN], RunCases, 2, 2,
                  ["4", "11", "4", "11"], [0, 0, 0, 0])
  AssertRaisesErrorIO(TOO_FEW_WINS_ERROR(1, 2), [1, 7, YOU_WIN, 1, 7, YOU_LOSE],
                      RunCases, 2, 2, ["4", "11", "4", "10"], [0, 0, 0, 0, 0])
  AssertRaisesErrorIO(ADDITIONAL_INPUT_ERROR("extra"),
                      [1, 7, YOU_WIN, 1, 7, YOU_LOSE], RunCases, 2, 2,
                      ["4", "11", "4", "10", "extra"], [0, 0, 0, 0, 0])
  AssertRaisesErrorIO(ADDITIONAL_INPUT_ERROR("x" * 100),
                      [1, 7, YOU_WIN, 1, 7, YOU_WIN], RunCases, 2, 2,
                      ["4", "11", "4", "11", "x" * 1000], [0, 0, 0, 0])
  B, C = orig


def Test():
  TestReadValue()
  TestApplyPlay()
  TestCountValidPoints()
  TestIthPoint()
  TestRunCase()
  TestRunCases()


def main():
  assert len(sys.argv) == 2, "Bad usage"
  index = int(sys.argv[1])
  if index == -2:
    Test()
  else:
    try:
      w = W[index]
      print(T, w)
      sys.stdout.flush()
      try:
        RunCases(T, w)
      except Error as err:
        print(str(err)[:1000], file=sys.stderr)
        sys.exit(1)
    except Exception as exception:
      print(INVALID_OUTPUT)
      sys.stdout.flush()
      print(('JUDGE_ERROR! Internal judge exception: {}'.format(exception))
            [:1000], file=sys.stderr)


if __name__ == "__main__":
  main()
