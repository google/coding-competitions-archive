# Usage: `local_testing_tool.py test_number`, where the argument test_number
# is 0 (Test Set 1), 1 (Test Set 2) or 2 (Test Set 3).

import sys
import random

T = 100
Ns = (10, 50, 50)
Qs = (30000, 30000, 17000)
CORRECT, WRONG = 1, -1


def GenCase(n):
  r = list(range(1, n + 1))
  random.shuffle(r)
  return tuple(r)


def GenCases(n):
  return tuple(GenCase(n) for _ in range(T))


class Error(Exception):
  pass


class JudgeError(Exception):
  pass


INVALID_LINE_ERROR = "Couldn't read a valid line"
TOO_LONG_LINE_ERROR = "Line too long: {} characters".format
WRONG_NUM_TOKENS_ERROR = "Wrong number of tokens, expected 3 or {} got {}".format
NOT_INTEGER_ERROR = "Not an integer: {}".format
OUT_OF_BOUNDS_ERROR = "{} is out of bounds".format
REPEATED_INTEGERS_ERROR = "Received repeated integers: {}".format
TOO_MANY_QUERIES_ERROR = "Queried too many times"
WRONG_ORDER_ERROR = "Guessed wrong order"
CASE_ERROR = "Case #{} failed: {}".format
EXCEPTION_AFTER_END_ERROR = (
    "Exception raised while reading input after all cases finish.")
ADDITIONAL_INPUT_ERROR = "Additional input after all cases finish: {}".format
QUERIES_USED = "Total Queries Used: {}/{}".format


def ParseInteger(line):
  try:
    return int(line)
  except:
    raise Error(NOT_INTEGER_ERROR(line))


def ReadValues(n, line):
  if len(line) > 1000:
    raise Error(TOO_LONG_LINE_ERROR(len(line)))
  parts = line.split()
  if len(parts) not in (3, n):
    raise Error(WRONG_NUM_TOKENS_ERROR(n, len(parts)))
  v = tuple(ParseInteger(parts[i]) for i in range(len(parts)))
  for vi in v:
    if not 1 <= vi <= n:
      raise Error(OUT_OF_BOUNDS_ERROR(vi))
  if len(set(v)) != len(v):
    raise Error(REPEATED_INTEGERS_ERROR(v))
  return v


def Inv(v):
  r = list(v)
  for i in range(len(r)):
    r[v[i] - 1] = i + 1
  return tuple(r)


def Mid(pos, v):
  if len(v) != 3:
    raise JudgeError("Mid called with {} values (expected 3)".format(len(v)))
  p = tuple(pos[vi - 1] for vi in v)
  min_p, max_p = min(p), max(p)
  for vi in v:
    if pos[vi - 1] not in (min_p, max_p):
      return vi


def Output(line):
  try:
    print(line)
    sys.stdout.flush()
  except:
    # If we let stdout be closed by the end of the program, then an unraisable
    # broken pipe exception will happen, and we won't be able to finish
    # normally.
    try:
      sys.stdout.close()
    except:
      pass


def RunCase(case, max_q):

  def Input():
    try:
      return input()
    except:
      raise Error(INVALID_LINE_ERROR)

  pos = Inv(case)
  q = 0
  while True:
    v = ReadValues(len(case), Input())
    if len(v) == len(case):
      if v != case and v != tuple(reversed(case)):
        raise Error(WRONG_ORDER_ERROR)
      return q
    if q >= max_q:
      raise Error(TOO_MANY_QUERIES_ERROR)
    q += 1
    Output(Mid(pos, v))


def RunCases(cases, max_q):
  Output("{} {} {}".format(len(cases), len(cases[0]), max_q))
  tot_q = 0
  for i, case in enumerate(cases, 1):
    try:
      q = RunCase(case, max_q - tot_q)
      Output(CORRECT)
      tot_q += q
    except Error as err:
      Output(WRONG)
      raise Error(CASE_ERROR(i, err))

  try:
    extra_input = input()
  except EOFError:
    return tot_q
  except Exception:  # pylint: disable=broad-except
    raise Error(EXCEPTION_AFTER_END_ERROR)
  raise Error(ADDITIONAL_INPUT_ERROR(extra_input[:100]))


def main():
  assert len(sys.argv) == 2, "Bad usage"
  index = int(sys.argv[1])
  random.seed(1234 + index)
  assert index in (0, 1, 2)
  try:
    q = RunCases(GenCases(Ns[index]), Qs[index])
    print(QUERIES_USED(q, Qs[index]), file=sys.stderr)
  except Error as err:
    print(str(err)[:1000], file=sys.stderr)
    sys.exit(1)
  except Exception as exception:
    Output(WRONG)
    print(
        ("JUDGE_ERROR! Internal judge exception: {}".format(exception))[:1000],
        file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
  main()
