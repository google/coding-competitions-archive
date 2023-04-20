# Usage: `judge.py test_number`, where the argument test_number is 0
# (Test Set 1) or 1 (Test Set 2).

import sys
import random

T = 100
N = 100
MAX_COST = 6 * 10**8
CORRECT, WRONG = 1, -1


def GenCase():
  r = list(range(1, N + 1))
  random.shuffle(r)
  for _ in range(2 * N):  # additional shuffling only for real judge
    i, j = random.randrange(N), random.randrange(N)
    r[i], r[j] = r[j], r[i]
  return tuple(r)


def GenCases():
  cases = []
  cases.append(list(range(1, N + 1)))  # already sorted list
  cases.append([N] + list(range(1, N)))
  cases.append(list(range(2, N + 1)) + [1])
  cases.append(list(range(N, 0, -1)))
  cases.append([N] + list(range(2, N)) + [1])
  cases.append([1] + list(range(N - 1, 1, -1)) + [N])
  cases.append(list(range(2, N + 1, 2)) + list(range(1, N + 1, 2)))
  cases.extend([GenCase() for _ in range(len(cases), T)])
  return tuple(cases)


def TestCases():
  cases = GenCases()
  AssertEqual(len(cases), T)
  for case in cases:
    AssertEqual(len(case), N)
    for i in range(1, N + 1):
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


def TestParseInteger():
  AssertReturns(1, ParseInteger, "1")
  AssertReturns(10, ParseInteger, "10")
  AssertReturns(0, ParseInteger, "0")
  AssertReturns(-1, ParseInteger, "-1")
  AssertRaisesError(NOT_INTEGER_ERROR("- 2"), ParseInteger, "- 2")
  AssertRaisesError(NOT_INTEGER_ERROR("foo"), ParseInteger, "foo")
  AssertRaisesError(NOT_INTEGER_ERROR("x"), ParseInteger, "x")


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


def TestReadValues():

  AssertReturns(("S", 2, 4), ReadValues, "S 2 4")
  AssertReturns(("M", 1, 49), ReadValues, "   M    01 0049")
  AssertRaisesError(TOO_LONG_LINE_ERROR(1001), ReadValues, "x" * 1001)
  AssertRaisesError(WRONG_NUM_TOKENS_ERROR(N + 1), ReadValues, "x " * (N + 1))
  AssertRaisesError(WRONG_NUM_TOKENS_ERROR(N - 1), ReadValues, "x " * (N - 1))
  AssertRaisesError(WRONG_NUM_TOKENS_ERROR(2), ReadValues, "x y")
  AssertRaisesError(WRONG_NUM_TOKENS_ERROR(0), ReadValues, "     ")
  AssertRaisesError(WRONG_NUM_TOKENS_ERROR(0), ReadValues, "")
  AssertRaisesError(WRONG_QUERY_ERROR("S 51 2"), ReadValues, "S 51 2")
  AssertRaisesError(WRONG_QUERY_ERROR("0 1 2"), ReadValues, "0 1 2")
  AssertRaisesError(WRONG_QUERY_ERROR("D 1 2"), ReadValues, "D 1 2")
  AssertRaisesError(OUT_OF_BOUNDS_ERROR(10**6), ReadValues, "S 5 1000000")
  AssertRaisesError(OUT_OF_BOUNDS_ERROR(0), ReadValues, "M 0 5")
  AssertRaisesError(NOT_INTEGER_ERROR("baz"), ReadValues, "S baz 5")


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


def RunCase(case, test_input=None, test_output_storage=None):

  def Input():
    try:
      return input() if test_input is None else test_input.pop(0)
    except:
      raise Error(INVALID_LINE_ERROR)

  Output = OutputF(test_output_storage)
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


def TestRunCase():
  AssertRaisesErrorIO(INVALID_LINE_ERROR, [], RunCase, (1, 2, 3, 4), [])
  AssertRaisesErrorIO(
      WRONG_NUM_TOKENS_ERROR(2), [], RunCase, (1, 2, 3, 4), ["S 1"])
  AssertRaisesErrorIO(
      WRONG_NUM_TOKENS_ERROR(0), [], RunCase, (1, 2, 3, 4), [""])
  AssertRaisesErrorIO(
      WRONG_QUERY_ERROR("D  1 4"), [], RunCase, (1, 2, 3, 4), ["D  1 4"])
  AssertRaisesErrorIO(
      OUT_OF_BOUNDS_ERROR(0), [1], RunCase, (1, 2, 3, 4), ["S  1 4", " M 0 2"])
  AssertRaisesErrorIO(
      COST_LIMIT_EXCEEDED_ERROR, [1, 2, 3, 2, 1, 2, 1, 2, 3, 2, 1, 2],
      RunCase, (1, 2, 3, 4), [
          "M 1 2", " M 2 3", " M 3 4", " M 2 3", " M 1 2", " M 2 3", "M 1 2",
          " M 2 3", " M 3 4", " M 2 3", " M 1 2", " M 2 3"
      ] + ["M 1 2"] * 10)
  # Check rounding up makes exceed budget
  AssertRaisesErrorIO(
      COST_LIMIT_EXCEEDED_ERROR, [1] * 17, RunCase,
      (1, 2, 3, 4), ["M 1 3"] * 18 + ["D"])
  # Check cost is exactly the budget
  AssertReturnsIO(
      1, [1] * 24, RunCase,
      (1, 2, 3, 4), ["M 1 4"] * 24 + ["D"])
  AssertRaisesErrorIO(
      COST_LIMIT_EXCEEDED_ERROR, [1, 2, 3, 2, 1, 2, 1, 2, 3, 2, 1, 1],
      RunCase, (1, 2, 3, 4), [
          "M 1 2", " M 2 3", " M 3 4", " M 2 3", " M 1 2", " M 2 3", "M 1 2",
          " M 2 3", " M 3 4", " M 2 3", " M 1 2", "M 1 2", "M 1 2"
      ])
  AssertRaisesErrorIO(
      WRONG_QUERY_ERROR(" S 4 2"), [1], RunCase, (1, 2, 3, 4),
      ["M  1 4", " S 4 2", "D"])
  AssertRaisesErrorIO(WRONG_ORDER_ERROR, [1, 1], RunCase, (1, 2, 3, 4),
                      ["M  1 4", " S 2 4", "D"])
  AssertReturnsIO(1, [1, 4, 1], RunCase, (1, 2, 4, 3),
                  ["M  1 4", " M 3 4", "S 3  4", "D"])
  AssertReturnsIO(1, [1, 4, 1, 1, 1, 1, 1, 1, 1, 1, 1], RunCase, (1, 2, 4, 3),
                  ["M  1 4", " M 3 4", "S 3  4", "S 1 2", "S 1 2",
                   "S 1 2", "S 1 2", "S 1 2", "S 1 2", "S 1 2", "S 1 2", "D"])
  AssertReturnsIO(
      1, [1, 2, 3, 2, 1, 2, 1, 2, 3, 2], RunCase,
      (1, 2, 3, 4), [
          "M 1 2", " M 2 3", " M 3 4", " M 2 3", " M 1 2", " M 2 3", "M 1 2",
          " M 2 3", " M 3 4", " M 2 3", "D"
      ])


def RunCases(cases, test_input=None, test_output_storage=None):
  Output = OutputF(test_output_storage)

  Output("{} {}".format(len(cases), len(cases[0])))
  for i, case in enumerate(cases, 1):
    try:
      RunCase(case, test_input, test_output_storage)
      Output(CORRECT)
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
    return
  except Exception:  # pylint: disable=broad-except
    raise Error(EXCEPTION_AFTER_END_ERROR)
  raise Error(ADDITIONAL_INPUT_ERROR(extra_input[:100]))


def TestRunCases():
  AssertRaisesErrorIO(
      CASE_ERROR(1, INVALID_LINE_ERROR), ["1 4", -1], RunCases, [[1, 2, 3, 4]],
      [])
  AssertRaisesErrorIO(
      CASE_ERROR(1, WRONG_NUM_TOKENS_ERROR(4)), ["1 4", -1], RunCases,
      [(1, 2, 3, 4)], ["S 1 2 3"])
  AssertRaisesErrorIO(
      CASE_ERROR(1, WRONG_NUM_TOKENS_ERROR(0)), ["1 4", -1], RunCases,
      [(1, 2, 3, 4)], [""])
  AssertRaisesErrorIO(
      CASE_ERROR(1, NOT_INTEGER_ERROR("x")), ["1 4", 1, -1], RunCases,
      [(1, 2, 3, 4)], ["S  1 4", "S x 2"])
  AssertRaisesErrorIO(
      CASE_ERROR(1, OUT_OF_BOUNDS_ERROR(0)), ["1 4", 1, -1], RunCases,
      [(1, 2, 3, 4)], ["M  1 4", " S 0 2"])
  AssertRaisesErrorIO(
      CASE_ERROR(1, COST_LIMIT_EXCEEDED_ERROR),
      ["1 4", 1, 3, 1, 2, 2, 1, 1, 3, 1, 2, 2, 1, 1, -1], RunCases,
      [(1, 2, 3, 4)], [
          "M 1 2", "M 3 4", "M  1 3", " M 2 4", "M 2 3", "M 1 2", "M 1 2",
          "M 3 4", "M  1 3", " M 2 4", "M 2 3", "M 1 2", "M 1 2", "M 1 2"
      ])
  AssertRaisesErrorIO(
      CASE_ERROR(1, WRONG_QUERY_ERROR("D  1 4")), ["1 4", -1], RunCases,
      [(1, 2, 3, 4)], ["D  1 4"])
  AssertRaisesErrorIO(
      CASE_ERROR(1, WRONG_ORDER_ERROR), ["1 4", 1, -1], RunCases, [(1, 2, 3, 4)],
      ["S 1 4", "D"])
  AssertRaisesErrorIO(
      CASE_ERROR(2, WRONG_ORDER_ERROR), ["2 4", 1, 1, -1], RunCases,
      [(1, 2, 3, 4), (1, 2, 3, 4)], ["D", "S 1 4", "D"])
  AssertRaisesErrorIO(
      ADDITIONAL_INPUT_ERROR("extra"), ["2 4", 1, 2, 1, 1], RunCases,
      [(1, 2, 3, 4), (1, 2, 3, 4)], ["M  1 4", " M 2 4", "D", "D", "extra"])


def Test():
  TestCases()
  TestParseInteger()
  TestReadValues()
  TestRunCase()
  TestRunCases()


def main():
  assert len(sys.argv) == 2, "Bad usage"
  index = int(sys.argv[1])
  random.seed(4352 + index)
  if index == -2:
    Test()
  else:
    assert index in (0,)
    try:
      RunCases(GenCases())
    except Error as err:
      print(str(err)[:1000], file=sys.stderr)
      sys.exit(1)
    except Exception as exception:
      ActuallyOutput(WRONG)
      print(
          ("JUDGE_ERROR! Internal judge exception: {}".format(exception)
          )[:1000],
          file=sys.stderr)
      sys.exit(1)


if __name__ == "__main__":
  main()
