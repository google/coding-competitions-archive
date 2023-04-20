# Usage: `judge.py test_number`, where the argument test_number is 0
# (Test Set 1) or 1 (Test Set 2).

import sys
import random

T = 100
Ns = (10, 50, 50)
Qs = (30000, 30000, 17000)
CORRECT, WRONG = 1, -1


def GenCase(n):
  r = list(range(1, n + 1))
  random.shuffle(r)
  for _ in range(2 * n):  # additional shuffling only for real judge
    i, j = random.randrange(n), random.randrange(n)
    r[i], r[j] = r[j], r[i]
  return tuple(r)


def GenCases(n):
  return tuple(GenCase(n) for _ in range(T))


def TestCases():
  assert len(Qs) == 3
  assert Qs[0] == 300 * T
  assert Qs[1] == 300 * T
  assert Qs[2] == 170 * T
  for index in range(3):
    cases = GenCases(Ns[index])
    AssertEqual(len(cases), T)
    for case in cases:
      AssertEqual(len(case), Ns[index])
      for i in range(1, Ns[index]+1):
        AssertEqual(case.count(i), 1)


def AssertEqual(expected, actual):
  assert expected == actual, ("Expected [{}], got [{}]".format(
      expected, actual))


class Error(Exception):
  pass


class JudgeError(Exception):
  pass


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
    assert expected_message == message, ("Expected error [{}], got [{}]".format(
        expected_message, message))


def AssertReturnsIO(ret, expected_output, fn, *args):
  test_output_storage = []
  AssertReturns(ret, fn, *(args + (test_output_storage,)))
  AssertEqual(expected_output, test_output_storage)


def AssertRaisesErrorIO(expected_message, expected_output, fn, *args):
  test_output_storage = []
  AssertRaisesError(expected_message, fn, *(args + (test_output_storage,)))
  AssertEqual(expected_output, test_output_storage)


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


def TestParseInteger():
  AssertReturns(1, ParseInteger, "1")
  AssertReturns(10, ParseInteger, "10")
  AssertReturns(0, ParseInteger, "0")
  AssertReturns(-1, ParseInteger, "-1")
  AssertRaisesError(NOT_INTEGER_ERROR("- 2"), ParseInteger, "- 2")
  AssertRaisesError(NOT_INTEGER_ERROR("foo"), ParseInteger, "foo")
  AssertRaisesError(NOT_INTEGER_ERROR("x"), ParseInteger, "x")


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


def TestReadValues():
  N = 50

  def ReadValuesN(line):
    return ReadValues(N, line)

  AssertReturns((1, 2, 4), ReadValuesN, "1 2 4")
  AssertReturns((50, 49, 1), ReadValuesN, "   50    049 0001")
  AssertReturns(
      tuple(range(1, 51)), ReadValuesN, " ".join(str(x) for x in range(1, 51)))
  AssertRaisesError(TOO_LONG_LINE_ERROR(1001), ReadValuesN, "x" * 1001)
  AssertRaisesError(
      WRONG_NUM_TOKENS_ERROR(N, N + 1), ReadValuesN, "x " * (N + 1))
  AssertRaisesError(
      WRONG_NUM_TOKENS_ERROR(N, N - 1), ReadValuesN, "x " * (N - 1))
  AssertRaisesError(WRONG_NUM_TOKENS_ERROR(N, 2), ReadValuesN, "x y")
  AssertRaisesError(WRONG_NUM_TOKENS_ERROR(N, 1), ReadValuesN, "  x    ")
  AssertRaisesError(WRONG_NUM_TOKENS_ERROR(N, 0), ReadValuesN, "     ")
  AssertRaisesError(WRONG_NUM_TOKENS_ERROR(N, 0), ReadValuesN, "")
  AssertRaisesError(NOT_INTEGER_ERROR("foo"), ReadValuesN, "foo 1 2")
  AssertRaisesError(NOT_INTEGER_ERROR("bar"), ReadValuesN, "1 2 bar")
  AssertRaisesError(NOT_INTEGER_ERROR("foo"), ReadValuesN, "foo 1 bar")
  AssertRaisesError(OUT_OF_BOUNDS_ERROR(51), ReadValuesN, "1 51 2")
  AssertRaisesError(OUT_OF_BOUNDS_ERROR(0), ReadValuesN, "0 1 2")
  AssertRaisesError(OUT_OF_BOUNDS_ERROR(0), ReadValuesN, "0 10000 1")
  AssertRaisesError(
      OUT_OF_BOUNDS_ERROR(10**20), ReadValuesN,
      " ".join(str(x) for x in range(1, 50)) + " 1" + ("0" * 20))
  AssertRaisesError(
      OUT_OF_BOUNDS_ERROR(0), ReadValuesN,
      " ".join(str(x) for x in range(1, 50)) + " 0")
  AssertRaisesError(
      NOT_INTEGER_ERROR("baz"), ReadValuesN,
      " ".join(str(x) for x in range(1, 50)) + " baz")


def Inv(v):
  r = list(v)
  for i in range(len(r)):
    r[v[i] - 1] = i + 1
  return tuple(r)


def TestInv():
  AssertReturns((1, 2, 3), Inv, (1, 2, 3))
  AssertReturns((2, 3, 1, 4), Inv, (3, 1, 2, 4))
  AssertReturns((3, 4, 2, 5, 1), Inv, (5, 3, 1, 2, 4))


def Mid(pos, v):
  if len(v) != 3:
    raise JudgeError("Mid called with {} values (expected 3)".format(len(v)))
  p = tuple(pos[vi - 1] for vi in v)
  min_p, max_p = min(p), max(p)
  for vi in v:
    if pos[vi - 1] not in (min_p, max_p):
      return vi


def TestMid():
  AssertReturns(2, Mid, Inv((1, 2, 3)), (1, 2, 3))
  AssertReturns(1, Mid, Inv((2, 1, 3)), (1, 2, 3))
  AssertReturns(3, Mid, Inv((1, 3, 2)), (1, 2, 3))
  AssertReturns(2, Mid, Inv((1, 3, 2, 4)), (1, 2, 4))
  AssertReturns(2, Mid, Inv((1, 3, 2, 4)), (3, 2, 4))
  AssertReturns(3, Mid, Inv((1, 3, 2, 4)), (3, 1, 4))


def ActuallyOutput(line):
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


def OutputF(test_output_storage):
  def Output(line):
    if test_output_storage is None:
      ActuallyOutput(line)
    else:
      test_output_storage.append(line)
  return Output


def RunCase(case, max_q, test_input=None, test_output_storage=None):
  def Input():
    try:
      return input() if test_input is None else test_input.pop(0)
    except:
      raise Error(INVALID_LINE_ERROR)
  Output = OutputF(test_output_storage)

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


def TestRunCase():
  AssertRaisesErrorIO(INVALID_LINE_ERROR, [], RunCase, (1, 2, 3, 4), 10, [])
  AssertRaisesErrorIO(
      WRONG_NUM_TOKENS_ERROR(4, 2), [], RunCase, (1, 2, 3, 4), 10, ["x y"])
  AssertRaisesErrorIO(
      WRONG_NUM_TOKENS_ERROR(4, 0), [], RunCase, (1, 2, 3, 4), 10, [""])
  AssertRaisesErrorIO(
      NOT_INTEGER_ERROR("x"), [3], RunCase, (1, 2, 3, 4), 10,
      ["3  1 4", "x 1 2"])
  AssertRaisesErrorIO(
      OUT_OF_BOUNDS_ERROR(0), [3], RunCase, (1, 2, 3, 4), 10,
      ["3  1 4", " 1 0 2"])
  AssertRaisesErrorIO(TOO_MANY_QUERIES_ERROR, [3, 2], RunCase, (1, 2, 3, 4), 2,
                      ["3  1 4", " 1 4 2", "1 2 3"])
  AssertRaisesErrorIO(INVALID_LINE_ERROR, [3, 2, 2], RunCase, (1, 2, 3, 4), 4,
                      ["3  1 4", " 1 4 2", "1 2 3"])
  AssertRaisesErrorIO(WRONG_ORDER_ERROR, [3, 2], RunCase, (1, 2, 3, 4), 3,
                      ["3  1 4", " 1 4 2", "1 2 4 3"])
  AssertReturnsIO(2, [3, 2], RunCase, (1, 2, 3, 4), 2,
                  ["3  1 4", " 1 4 2", "1 2 3 4"])
  AssertReturnsIO(1, [2], RunCase, (1, 2, 3, 4), 2, ["1 4 2", "1 2 3 4"])
  AssertReturnsIO(1, [2], RunCase, (1, 2, 3, 4), 2, ["1 4 2", "4 3 2 1"])


def RunCases(cases, max_q, test_input=None, test_output_storage=None):
  Output = OutputF(test_output_storage)

  Output("{} {} {}".format(len(cases), len(cases[0]), max_q))
  tot_q = 0
  for i, case in enumerate(cases, 1):
    try:
      q = RunCase(case, max_q - tot_q, test_input, test_output_storage)
      Output(CORRECT)
      tot_q += q
    except Error as err:
      Output(WRONG)
      raise Error(CASE_ERROR(i, err))

  def Input():
    if test_input is None:
      return input()
    else:
      if test_input:
        return test_input.pop(0)
      else:
        raise EOFError()

  try:
    extra_input = Input()
  except EOFError:
    return tot_q
  except Exception:  # pylint: disable=broad-except
    raise Error(EXCEPTION_AFTER_END_ERROR)
  raise Error(ADDITIONAL_INPUT_ERROR(extra_input[:100]))


def TestRunCases():
  AssertRaisesErrorIO(
      CASE_ERROR(1, INVALID_LINE_ERROR), ["1 4 10", -1], RunCases,
      [[1, 2, 3, 4]], 10, [])
  AssertRaisesErrorIO(
      CASE_ERROR(1, WRONG_NUM_TOKENS_ERROR(4, 2)), ["1 4 10", -1], RunCases,
      [(1, 2, 3, 4)], 10, ["x y"])
  AssertRaisesErrorIO(
      CASE_ERROR(1, WRONG_NUM_TOKENS_ERROR(4, 0)), ["1 4 10", -1], RunCases,
      [(1, 2, 3, 4)], 10, [""])
  AssertRaisesErrorIO(
      CASE_ERROR(1, NOT_INTEGER_ERROR("x")), ["1 4 10", 3, -1], RunCases,
      [(1, 2, 3, 4)], 10, ["3  1 4", "x 1 2"])
  AssertRaisesErrorIO(
      CASE_ERROR(1, OUT_OF_BOUNDS_ERROR(0)), ["1 4 10", 3, -1], RunCases,
      [(1, 2, 3, 4)], 10, ["3  1 4", " 1 0 2"])
  AssertRaisesErrorIO(
      CASE_ERROR(1, TOO_MANY_QUERIES_ERROR), ["1 4 2", 3, 2, -1], RunCases,
      [(1, 2, 3, 4)], 2, ["3  1 4", " 1 4 2", "1 2 3"])
  AssertRaisesErrorIO(
      CASE_ERROR(1, INVALID_LINE_ERROR), ["1 4 4", 3, 2, 2, -1], RunCases,
      [(1, 2, 3, 4)], 4, ["3  1 4", " 1 4 2", "1 2 3"])
  AssertRaisesErrorIO(
      CASE_ERROR(1, WRONG_ORDER_ERROR), ["1 4 3", 3, 2, -1], RunCases,
      [(1, 2, 3, 4)], 3, ["3  1 4", " 1 4 2", "1 2 4 3"])
  AssertReturnsIO(2, ["1 4 2", 3, 2, 1], RunCases, [(1, 2, 3, 4)], 2,
                  ["3  1 4", " 1 4 2", "1 2 3 4"])
  AssertReturnsIO(2, ["2 4 2", 3, 2, 1, 1], RunCases,
                  [(1, 2, 3, 4), (1, 2, 3, 4)], 2,
                  ["3  1 4", " 1 4 2", "1 2 3 4", "1 2 3 4"])
  AssertRaisesErrorIO(
      CASE_ERROR(2, WRONG_ORDER_ERROR), ["2 4 2", 3, 2, 1, -1], RunCases,
      [(1, 2, 3, 4),
       (1, 2, 3, 4)], 2, ["3  1 4", " 1 4 2", "4 3 2 1", "4 1 2 3"])
  AssertRaisesErrorIO(
      ADDITIONAL_INPUT_ERROR("extra"), ["2 4 2", 3, 2, 1, 1], RunCases,
      [(1, 2, 3, 4),
       (1, 2, 3, 4)], 2, ["3  1 4", " 1 4 2", "4 3 2 1", "1 2 3 4", "extra"])


def Test():
  TestCases()
  TestParseInteger()
  TestReadValues()
  TestInv()
  TestMid()
  TestRunCase()
  TestRunCases()


def main():
  assert len(sys.argv) == 2, "Bad usage"
  index = int(sys.argv[1])
  random.seed(4352 + index)
  if index == -2:
    Test()
  else:
    assert index in (0, 1, 2)
    try:
      q = RunCases(GenCases(Ns[index]), Qs[index])
      print(QUERIES_USED(q, Qs[index]), file=sys.stderr)
    except Error as err:
      print(str(err)[:1000], file=sys.stderr)
      sys.exit(1)
    except Exception as exception:
      ActuallyOutput(WRONG)
      print(("JUDGE_ERROR! Internal judge exception: {}".format(exception))
            [:1000], file=sys.stderr)
      sys.exit(1)


if __name__ == "__main__":
  main()
