"""judge.py for the Draupnir interactive judge.
"""

# Usage: `judge.py test_number`, where the argument test_number is either 0
# (small), 1 (large) or -2 (test mode).


import sys

# REMOVE FOR LOCAL_TESTING_TOOL
import itertools
import random

def GenerateCases(test_index):
  random.seed(926153 + test_index)
  cases = [tuple(ri for _ in xrange(6)) for ri in (1, 100)]
  for i in xrange(6):
    one_or_two = 1 + ((i & 1) ^ test_index)
    case = [0] * 6
    case[i] = one_or_two
    cases.append(tuple(case))
    case = [100] * 6
    case[i] -= one_or_two
    cases.append(tuple(case))
  assert len(cases) == 14
  cases += [tuple(random.randrange(0, 5) + pi * 96 for pi in p)
            for p in set(itertools.permutations([0, 0, 0, 1, 1, 1]))]
  assert len(cases) == 34
  cases += [tuple(random.randrange(1, 5) for _ in xrange(6))
            for __ in xrange(5)]
  cases += [tuple(random.randrange(96, 101) for _ in xrange(6))
            for __ in xrange(5)]
  assert len(cases) == 44
  while len(cases) < 50:
    cases.append(tuple(random.randrange(20, 81) for _ in xrange(6)))
  random.shuffle(cases)
  return cases

# FINISH REMOVE FOR LOCAL_TESTING_TOOL, AND SET CASES BELOW
CASES = (GenerateCases(0), GenerateCases(1))
WS = (6, 2)

MAX_DAY = 500
WRONG_ANSWER, CORRECT_ANSWER = -1, 1
MOD = 2 ** 63


DAY_OUT_OF_RANGE_ERROR = "Day {} is out of range.".format
EXCEEDED_QUERIES_ERROR = "Exceeded number of queries: {}.".format
INVALID_LINE_ERROR = "Couldn't read a valid line."
NOT_INTEGER_ERROR = "Not an integer: {}".format
RING_AMOUNT_OUT_OF_RANGE_ERROR = "Ring amount {} is out of range.".format
WRONG_NUM_TOKENS_ERROR = "Wrong number of tokens: {}. Expected 1 or 6.".format
WRONG_GUESS_ERROR = "Wrong guess: {}. Expected: {}.".format


def ReadValues(line):
  t = line.split()
  if len(t) != 1 and len(t) != 6:
    return WRONG_NUM_TOKENS_ERROR(len(t))
  r = []
  for s in t:
    try:
      v = int(s)
    except:
      return NOT_INTEGER_ERROR(s if len(s) < 100 else s[:100])
    r.append(v)
  if len(r) == 1:
    if not (1 <= r[0] <= MAX_DAY):
      return DAY_OUT_OF_RANGE_ERROR(r[0])
  else:
    for ri in r:
      if ri < 0:
        return RING_AMOUNT_OUT_OF_RANGE_ERROR(ri)
  return r


def TestReadValues():
  assert ReadValues("1") == [1]
  assert ReadValues("500") == [500]
  assert ReadValues(" 2  ") == [2]
  assert ReadValues(" 0  ") == DAY_OUT_OF_RANGE_ERROR(0)
  assert ReadValues("501") == DAY_OUT_OF_RANGE_ERROR(501)
  assert ReadValues("-5") == DAY_OUT_OF_RANGE_ERROR(-5)
  assert ReadValues("0 1 2 3 4 5") == range(6)
  assert ReadValues(("999999999999 " * 6)) == [999999999999] * 6
  assert ReadValues("1 2 3 4 5 -1") == RING_AMOUNT_OUT_OF_RANGE_ERROR(-1)
  assert ReadValues("0 -2 3 4 5 -1") == RING_AMOUNT_OUT_OF_RANGE_ERROR(-2)
  for v, expected in (("1 1", WRONG_NUM_TOKENS_ERROR(2)),
                      ("   ", WRONG_NUM_TOKENS_ERROR(0)),
                      ("", WRONG_NUM_TOKENS_ERROR(0)),
                      ("1 1 1 1 1 1 1", WRONG_NUM_TOKENS_ERROR(7)),
                      ("a11", NOT_INTEGER_ERROR("a11")),
                      ("11a", NOT_INTEGER_ERROR("11a")),
                      ("abcdefghij" * 11,
                       NOT_INTEGER_ERROR("abcdefghij" * 10))):
    result = ReadValues(v)
    assert result == expected, (
      "TestReadValue({}): expected {}, got {}".format(
        v, expected, result))


def ComputeDay(s, d):
  return [(s[i] * (2 ** min(63, d / (i + 1)))) % MOD for i in xrange(len(s))]

def TestComputeDay():
  assert ComputeDay([1, 1, 1, 1, 1, 1], 1) == [2, 1, 1, 1, 1, 1]
  assert ComputeDay([1, 1, 1, 1, 1, 1], 2) == [4, 2, 1, 1, 1, 1]
  assert ComputeDay([1, 1, 1, 1, 1, 1], 3) == [8, 2, 2, 1, 1, 1]
  assert ComputeDay([1, 1, 1, 1, 1, 1], 4) == [16, 4, 2, 2, 1, 1]
  assert ComputeDay([1, 1, 1, 1, 1, 1], 5) == [32, 4, 2, 2, 2, 1]
  assert ComputeDay([1, 1, 1, 1, 1, 1], 6) == [64, 8, 4, 2, 2, 2]
  assert ComputeDay([1, 1, 1, 1, 1, 1], 7) == [128, 8, 4, 2, 2, 2]
  assert ComputeDay([1, 2, 3, 4, 5, 6], 7) == [128, 16, 12, 8, 10, 12]
  assert ComputeDay([1, 1, 1, 1, 1, 1], 14) == [2 ** 14, 128, 16, 8, 4, 4]
  assert ComputeDay([1, 2, 3, 4, 5, 6], 14) == [2 ** 14, 256, 48, 32, 20, 24]
  assert ComputeDay([1, 1, 1, 1, 1, 1], 62)[:2] == [2 ** 62, 2 ** 31]
  assert ComputeDay([1, 1, 1, 1, 1, 1], 63)[:2] == [0, 2 ** 31]
  assert ComputeDay([1, 1, 1, 1, 1, 1], 64)[:2] == [0, 2 ** 32]
  assert ComputeDay([1, 1, 1, 1, 1, 1], 125)[:2] == [0, 2 ** 62]
  assert ComputeDay([1, 1, 1, 1, 1, 1], 126)[:2] == [0, 0]
  assert ComputeDay([1, 1, 1, 1, 1, 1], 127)[:2] == [0, 0]


def RunCase(w, case, test_input=None):
  outputs = []

  def Input():
    if test_input is None:
      return raw_input()
    else:
      return test_input.pop(0)

  def Output(line):
    if test_input is None:
      print line
      sys.stdout.flush()
    else:
      outputs.append(line)

  for ex in xrange(w + 1):
    try:
      line = Input()
    except:
      Output(WRONG_ANSWER)
      return INVALID_LINE_ERROR, outputs
    v = ReadValues(line)
    if isinstance(v, str):
      Output(WRONG_ANSWER)
      return v, outputs
    if len(v) == 1:
      if ex == w:
        Output(WRONG_ANSWER)
        return EXCEEDED_QUERIES_ERROR(w), outputs
      else:
        Output(sum(ComputeDay(case, v[0])) % MOD)
    else:
      if tuple(v) != tuple(case):
        Output(WRONG_ANSWER)
        return WRONG_GUESS_ERROR(v, case)[:100], outputs
      else:
        Output(CORRECT_ANSWER)
        return None, outputs


def TestRunCase():
  for w, case, inputs, exp_outputs, exp_result in (
      (4, range(6), [], [-1], INVALID_LINE_ERROR),
      (4, range(6), ["HELLO"], [-1], NOT_INTEGER_ERROR("HELLO")),
      (4, range(6), ["1 2"], [-1], WRONG_NUM_TOKENS_ERROR(2)),
      (4, range(6), ["0 1 2 3 4 5 6"], [-1], WRONG_NUM_TOKENS_ERROR(7)),
      (4, range(6), ["0 1 2 3 4 5"], [1], None),
      (4, range(6), ["0 1 2 3 4 6"], [-1],
       WRONG_GUESS_ERROR(range(5) + [6], range(6))),
      (4, range(6), [" ".join([str(10 ** 16)] * 6)], [-1],
       WRONG_GUESS_ERROR([10 ** 16] * 6, range(6))[:100]),
      (4, range(6), ["1"] * 4 + ["0 1 2 3 4 5"], [15] * 4 + [1], None),
      (4, range(6), ["1"] * 5 + ["0 1 2 3 4 5"], [15] * 4 + [-1],
       EXCEEDED_QUERIES_ERROR(4)),
      (4, range(6), ["1", "2", "4", "3", "0 1 2 3 4 5"], [15, 16, 23, 18, 1], None),
      (4, [0] * 5 + [3], ["1", "5", "6", "0 0 0 0 0 3"], [3, 3, 6, 1], None),
      (4, [3, 5] + [0] * 4, ["62", "63", "125", "126", "3 5 0 0 0 0"], [2 ** 62 + 5 * (2 ** 31), 5 * (2 ** 31), 2 ** 62, 0, 1], None)):
    result, outputs = RunCase(w, case, test_input=inputs[:])
    assert (result, outputs) == (exp_result, exp_outputs), (
      "TestRunCase(w={}, case={}, test_input={}): "
      "expected {}, got {}".format(
        w, case, inputs, (exp_result, exp_outputs), (result, outputs)))


def ValidateCases():
  assert len(WS) == len(CASES) == 2  # 2 test sets
  for cases in CASES:
    assert len(set(cases)) == 50
    for case in cases:
      assert len(case) == 6
      assert sum(case) > 0
      for ri in case:
        assert 0 <= ri <= 100
        assert int(ri) == ri


def RunCases(w, cases):
  for i, case in enumerate(cases, 1):
    result, _ = RunCase(w, case)
    if result:
      return "Case #{} ({}) failed: {}".format(i, case, result)
  try:
    extra_input = raw_input()
  except EOFError:
    return None
  except Exception:  # pylint: disable=broad-except
    return "Exception raised while reading input after all cases finish."
  return "Additional input after all cases finish: {}".format(extra_input[:100])


def Test():
  TestReadValues()
  TestComputeDay()
  TestRunCase()
  ValidateCases()


def main():
  assert len(sys.argv) == 2
  index = int(sys.argv[1])
  if index == -2:
    Test()
  else:
    cases = CASES[index]
    w = WS[index]
    print len(cases), w
    sys.stdout.flush()
    result = RunCases(w, cases)
    if result:
      print >> sys.stderr, result
      sys.stdout.flush()
      sys.exit(1)


if __name__ == "__main__":
  main()
