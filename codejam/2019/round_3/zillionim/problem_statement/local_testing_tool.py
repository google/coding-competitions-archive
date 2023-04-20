# Usage: `python testing_tool.py test_number`, where the argument test_number
# is either 0 (small), 1 (large), or 2 (second large).
# This can also be run as `python3 testing_tool.py test_number`.

from __future__ import print_function
import random
import sys

# Use raw_input in Python2.
try:
  input = raw_input
except NameError:
  pass

T = 500
W = (300, 475, 499)
B = 10 ** 10
C = B * 100

INVALID_OUTPUT = -1
YOU_WIN = -2
YOU_LOSE = -3

class Error(Exception):
  pass


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


def CountValidPoints(status):
  return sum((b - a - B + 1) for a, b in status)


def IthPoint(status, i):
  """Returns the value of the i-th valid point (0-based)."""
  for j, (a, b) in enumerate(status):
    if b - a - B + 1 > i:
      return a + i
    i -= b - a - B + 1
  assert False


def RunCase():
  def Output(line):
    print(line)
    sys.stdout.flush()

  status = [(1, C + 1)]
  while True:
    if not status:
      Output(YOU_WIN)
      return True
    valid_points = CountValidPoints(status)
    p = IthPoint(status, random.randrange(valid_points))
    status = ApplyPlay(status, p)
    if not status:
      Output(YOU_LOSE)
      return False
    Output(p)
    try:
      p = ReadValue(input())
      status = ApplyPlay(status, p)
    except Error as err:
      Output(INVALID_OUTPUT)
      raise Error(err)
    except:
      Output(INVALID_OUTPUT)
      raise Error(INVALID_LINE_ERROR)


def RunCases(t, w):
  wins = 0
  for i in range(1, t + 1):
    # The implementation of randomness here is not guaranteed to match the
    # implementation of randomness in the real judge.
    random.seed(2 + i)
    try:
      win = RunCase()
    except Error as err:
      raise Error(CASE_FAILED_ERROR(i, err))
    if win:
      wins += 1
  print("All cases completed. Got {} wins out of {} total games "
        "({} needed for CORRECT)".format(wins, t, w),
        file=sys.stderr)
  try:
    extra_input = input()
  except EOFError:
    if wins < w:
      raise Error(TOO_FEW_WINS_ERROR(wins, w))
    return
  except Exception:
    raise Error(EXCEPTION_AFTER_END_ERROR)
  raise Error(ADDITIONAL_INPUT_ERROR(extra_input[:100]))


def main():
  assert len(sys.argv) == 2, "Bad usage"
  index = int(sys.argv[1])
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
