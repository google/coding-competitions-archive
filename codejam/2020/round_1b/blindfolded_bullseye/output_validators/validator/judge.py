# Usage: `judge.py test_number`, where the argument test_number is either 0
# (Test Set 1), 1 (Test Set 2) or 2 (Test Set 3).
import sys
import random

# Use raw_input in Python2.
try:
  input = raw_input
except NameError:
  pass

HIT, MISS, CENTER, WRONG = "HIT", "MISS", "CENTER", "WRONG"
MAXX = 10 ** 9
MINR = (MAXX - 5, MAXX - 50, MAXX // 2)
MAXR = (MAXX - 5, MAXX - 50, MAXX)

T = 20
D = 300


def GenCases(tsi):
  # 3 cases with center close to origin, 2 with large radius and 1 with min
  # radius.
  m = MINR[tsi]
  cases = [((random.randrange(-2, 2), random.randrange(-2, 2)),
           m + (0, random.randrange(2, 8))[tsi // 2]) for _ in range(2)]
  cases.append(((random.randrange(-5, 5), random.randrange(-5, 5)), m))
  # 16 cases with small radius, 8 close to corners and 9 at random locations.
  if tsi < 2:
    rs = [m for _ in range(17)]
  else:
    # case to catch triangulations that fail to find 3 points (suggested by Darcy)
    cases.append(((m, 0), m))
    rs = [m, m + 1] + list(random.sample(range(m + 2, m + 100), k=14))
  random.shuffle(rs)
  for i in range(8):
    r = rs[i]
    x = MAXX - r - random.randrange((2, 3, 100)[tsi])
    y = MAXX - r - random.randrange((3, 4, 1000)[tsi])
    if random.choice((True, False)):
      x, y = y, x
    if i % 2 == 0:
      x = -x
    if i % 4 < 2:
      y = -y
    cases.append(((x, y), r))
  for r in rs[8:]:
    cases.append(((random.randrange(-MAXX + r, MAXX - r + 1),
                   random.randrange(-MAXX + r, MAXX - r + 1)), r))
  return cases


CASES = tuple(GenCases(i) for i in range(3))


def TestCases():
  AssertEqual(len(MINR), 3)
  AssertEqual(len(CASES), 3)
  assert MINR[0] == MAXR[0]
  assert MINR[1] == MAXR[1]
  for minr, maxr, cases in zip(MINR, MAXR, CASES):
    assert(len(cases) == T)
    for (x, y), r in cases:
      assert minr <= r <= maxr
      assert -MAXX + r <= x <= MAXX - r
      assert -MAXX + r <= y <= MAXX - r


def AssertEqual(expected, actual):
  assert expected == actual, (
      "Expected [{}], got [{}]".format(expected, actual))


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
    assert expected_message == message, (
        "Expected error [{}], got [{}]".format(expected_message, message))


def AssertFinishesIO(expected_output, fn, *args):
  test_output_storage = []
  AssertReturns(None, fn, *(args + (test_output_storage,)))
  AssertEqual(expected_output, test_output_storage)


def AssertRaisesErrorIO(expected_message, expected_output, fn, *args):
  test_output_storage = []
  AssertRaisesError(expected_message, fn, *(args + (test_output_storage,)))
  AssertEqual(expected_output, test_output_storage)


INVALID_LINE_ERROR = "Couldn't read a valid line"
TOO_LONG_LINE_ERROR = "Line too long: {} characters".format
WRONG_NUM_TOKENS_ERROR = "Wrong number of tokens, expected 2 got {}".format
NOT_INTEGER_ERROR = "Not an integer: {}".format
OUT_OF_BOUNDS_ERROR = "{} is out of bounds".format
CENTER_NOT_HIT_ERROR = "Center not hit in {} attempts".format
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
  if len(line) > 100:
    raise Error(TOO_LONG_LINE_ERROR(len(line)))
  parts = line.split()
  if len(parts) != 2:
    raise Error(WRONG_NUM_TOKENS_ERROR(len(parts)))
  x = ParseInteger(parts[0])
  y = ParseInteger(parts[1])
  if not -MAXX <= x <= MAXX:
    raise Error(OUT_OF_BOUNDS_ERROR(x))
  if not -MAXX <= y <= MAXX:
    raise Error(OUT_OF_BOUNDS_ERROR(y))
  return x, y


def TestReadValues():
  AssertReturns((1, 1), ReadValues, "1 1")
  AssertReturns((10, -10), ReadValues, "   10    -10 ")
  AssertReturns((0, 0), ReadValues, "-0 0")
  AssertReturns((-10 ** 9, 10 ** 9), ReadValues, "-1000000000 1000000000")
  AssertRaisesError(TOO_LONG_LINE_ERROR(101), ReadValues, "x" * 101)
  AssertRaisesError(WRONG_NUM_TOKENS_ERROR(3), ReadValues, "x y z")
  AssertRaisesError(WRONG_NUM_TOKENS_ERROR(1), ReadValues, "  x    ")
  AssertRaisesError(WRONG_NUM_TOKENS_ERROR(0), ReadValues, "     ")
  AssertRaisesError(WRONG_NUM_TOKENS_ERROR(0), ReadValues, "")
  AssertRaisesError(NOT_INTEGER_ERROR("foo"), ReadValues, "foo 1")
  AssertRaisesError(NOT_INTEGER_ERROR("bar"), ReadValues, "1 bar")
  AssertRaisesError(NOT_INTEGER_ERROR("foo"), ReadValues, "foo bar")
  AssertRaisesError(OUT_OF_BOUNDS_ERROR(10 ** 9 + 1), ReadValues,
                    "1 1000000001")
  AssertRaisesError(OUT_OF_BOUNDS_ERROR(-10 ** 9 - 1), ReadValues,
                    "-1000000001 1")
  AssertRaisesError(OUT_OF_BOUNDS_ERROR(-10 ** 9 - 1), ReadValues,
                    "-1000000001 1000000001")


def Dist2(p, q):
  return ((p[0] - q[0]) ** 2) + ((p[1] - q[1]) ** 2)


def Answer(p, c, r):
  if p == c:
    return CENTER
  elif Dist2(p, c) <= r ** 2:
    return HIT
  else:
    return MISS


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


def RunCase(d, c, r, test_input=None, test_output_storage=None):
  def Input():
    try:
      return input() if test_input is None else test_input.pop(0)
    except:
      raise Error(INVALID_LINE_ERROR)

  Output = OutputF(test_output_storage)

  for _ in range(d):
    p = ReadValues(Input())
    a = Answer(p, c, r)
    Output(a)
    if a == CENTER:
      return
  raise Error(CENTER_NOT_HIT_ERROR(d))


def TestRunCase():
  AssertRaisesErrorIO(INVALID_LINE_ERROR, [], RunCase, 2, (0, 0), 10, [])
  AssertRaisesErrorIO(WRONG_NUM_TOKENS_ERROR(3), [], RunCase, 2, (0, 0), 10,
                      ["  x  y  z"])
  AssertRaisesErrorIO(WRONG_NUM_TOKENS_ERROR(0), [], RunCase, 2, (0, 0), 10,
                      [""])
  AssertRaisesErrorIO(NOT_INTEGER_ERROR("x"), [MISS], RunCase, 2, (0, 0), 10,
                      ["-15 -15", "x y"])
  AssertRaisesErrorIO(OUT_OF_BOUNDS_ERROR(10 ** 9 + 1), [HIT], RunCase, 2,
                      (0, 0), 10, ["1 0", "1 1000000001"])
  AssertRaisesErrorIO(CENTER_NOT_HIT_ERROR(2), [HIT, MISS],
                      RunCase, 2, (0, 0), 10, ["1 0", "1 1000000000"])
  AssertFinishesIO([HIT, MISS, CENTER], RunCase, 3, (0, 0), 10,
                   ["1 0", "1 1000000000", "0 0"])
  AssertFinishesIO([CENTER], RunCase, 1, (-10 ** 9, 10 ** 9), 10,
                   ["  -1000000000   1000000000   "])
  AssertFinishesIO([MISS, MISS, MISS, HIT, HIT, HIT, CENTER],
                   RunCase, 100, (1, 2), 10,
                   ["-10 2", "6 -7", "-6 -6", "8 9", "7 -6", "-9 2", "1 2"])


def RunCases(d, minr, maxr, cases, test_input=None, test_output_storage=None):
  Output = OutputF(test_output_storage)

  Output("{} {} {}".format(len(cases), minr, maxr))
  for i, (c, r) in enumerate(cases, 1):
    assert minr <= r <= maxr and all(-MAXX + r <= x <= MAXX - r for x in c)
    try:
      RunCase(d, c, r, test_input=test_input,
              test_output_storage=test_output_storage)
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
  AssertRaisesErrorIO(CASE_ERROR(1, INVALID_LINE_ERROR), ["1 10 20", WRONG],
                      RunCases, 2, 10, 20, [((0, 0), 10)], [])
  AssertRaisesErrorIO(CASE_ERROR(2, WRONG_NUM_TOKENS_ERROR(3)),
                      ["2 10 11", CENTER, WRONG], RunCases, 2, 10, 11,
                      [((0, 0), 10), ((0, 0), 10)], ["0 0", "  x  y  z"])
  AssertFinishesIO(["1 10 10", HIT, MISS, CENTER], RunCases, 3, 10, 10,
                   [((0, 0), 10)], ["1 0", "1 1000000000", "0 0"])
  AssertFinishesIO(["2 5 15", CENTER, MISS, MISS, MISS, HIT, HIT, HIT, CENTER],
                   RunCases, 100, 5, 15,
                   [((-10 ** 9 + 10, 10 ** 9 - 10), 10), ((0, 0), 10)],
                   ["  -999999990   999999990   ", "-11 0", "5 -9", "-7 -8",
                   "7 7", "6 -8", "-10 0", "0 0"])
  AssertRaisesErrorIO(ADDITIONAL_INPUT_ERROR("extra"),
                      ["2 7 100", CENTER, MISS, MISS, MISS, HIT, HIT, HIT,
                       CENTER],
                      RunCases, 100, 7, 100,
                      [((-10 ** 9 + 10, 10 ** 9 - 10), 10), ((0, 0), 10)],
                      ["  -999999990   999999990   ", "-11 0", "5 -9",
                       "-7 -8", "7 7", "6 -8", "-10 0", "0 0", "extra"])

def Test():
  TestCases()
  TestParseInteger()
  TestReadValues()
  TestRunCase()
  TestRunCases()


def main():
  assert len(sys.argv) == 2, "Bad usage"
  index = int(sys.argv[1])
  random.seed(4252352)
  if index == -2:
    Test()
  else:
    try:
      RunCases(D, MINR[index], MAXR[index], CASES[index])
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
