# Usage: `local_testing_tool.py [test_number]`, where test_number is ignored.

import sys
import random

N = 100
MAX_COST = 6 * 10**8
CORRECT, WRONG = 1, -1

CASES = [tuple(range(N // 2, N + 1)) + tuple(range(1, N // 2)),
         tuple(range(1, N + 1)), tuple(range(N, 0, -1))]


class Error(Exception):
  pass


class JudgeError(Exception):
  pass


INVALID_LINE_ERROR = "Couldn't read a valid line"
TOO_LONG_LINE_ERROR = "Line too long: {} characters".format
WRONG_NUM_TOKENS_ERROR = "Wrong number of tokens, expected 1 or 3 got {}".format
NOT_INTEGER_ERROR = "Not an integer: {}".format
OUT_OF_BOUNDS_ERROR = "{} is out of bounds".format
WRONG_QUERY_ERROR = "Received wrong query: {}".format
COST_LIMIT_EXCEEDED_ERROR = "Exceeded the cost limit"
WRONG_ORDER_ERROR = "Did not sort the list"
CASE_ERROR = "Case #{} failed: {}".format
EXCEPTION_AFTER_END_ERROR = (
    "Exception raised while reading input after all cases finish.")
ADDITIONAL_INPUT_ERROR = "Additional input after all cases finish: {}".format


def ParseInteger(line):
  try:
    return int(line)
  except:
    raise Error(NOT_INTEGER_ERROR(line))


def ReadValues(line):
  if len(line) > 1000:
    raise Error(TOO_LONG_LINE_ERROR(len(line)))
  parts = line.split()
  if len(parts) not in (1, 3):
    raise Error(WRONG_NUM_TOKENS_ERROR(len(parts)))
  v = tuple([parts[0]] + [ParseInteger(parts[i]) for i in range(1, len(parts))])
  if parts[0] not in ("D", "S", "M"):
    raise Error(WRONG_QUERY_ERROR(line))
  if parts[0] == "D" and len(v) != 1:
    raise Error(WRONG_QUERY_ERROR(line))
  if parts[0] in ("S", "M"):
    if len(v) != 3:
      raise Error(WRONG_QUERY_ERROR(line))
    if v[1] >= v[2]:
      raise Error(WRONG_QUERY_ERROR(line))
  for vi in v[1:]:
    if not 1 <= vi <= N:
      raise Error(OUT_OF_BOUNDS_ERROR(vi))
  return v


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


def RunCase(case):

  def Input():
    try:
      return input()
    except:
      raise Error(INVALID_LINE_ERROR)

  case = list(case)
  n = len(case)
  cost = 0
  while True:
    v = ReadValues(Input())
    if v[0] == "D":
      if case != list(range(1, n + 1)):
        raise Error(WRONG_ORDER_ERROR)
      return CORRECT
    i = v[1] - 1
    j = v[2] - 1
    if v[0] == "S":
      case[i], case[j] = case[j], case[i]
      Output(1)
    if v[0] == "M":
      cost += (10**8 + (j - i)) // (j - i + 1)
      if cost > MAX_COST:
        raise Error(COST_LIMIT_EXCEEDED_ERROR)
      Output(case.index(min(case[i:j + 1])) + 1)


def RunCases(cases):
  Output("{} {}".format(len(cases), len(cases[0])))
  for i, case in enumerate(cases, 1):
    try:
      RunCase(case)
      Output(CORRECT)
    except Error as err:
      Output(WRONG)
      raise Error(CASE_ERROR(i, err))

  try:
    extra_input = input()
  except EOFError:
    return
  except Exception:
    raise Error(EXCEPTION_AFTER_END_ERROR)
  raise Error(ADDITIONAL_INPUT_ERROR(extra_input[:100]))


def main():
  random.seed(1025)
  try:
    RunCases(CASES)
  except Error as err:
    print(str(err)[:1000], file=sys.stderr)
    sys.exit(1)
  except Exception as exception:
    Output(WRONG)
    print(
        ("JUDGE_ERROR! Internal judge exception: {}".format(exception)
        )[:1000],
        file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
  main()
