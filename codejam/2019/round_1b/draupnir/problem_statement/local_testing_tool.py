"""Draupnir interactive judge.
"""

# Usage: `python testing_tool.py test_number`, where the argument test_number is
# either 0 (first test set) or 1 (second test set).
# This can also be run as `python3 testing_tool.py test_number`.
import sys

# Use raw_input in Python2.
try:
  input = raw_input
except NameError:
  pass

CASES = (((1, 2, 3, 4, 5, 6), (1, 1, 1, 1, 1, 1)),
         ((1, 2, 3, 4, 5, 6), (1, 1, 1, 1, 1, 1))) # set your own cases
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


def ComputeDay(s, d):
  rings_per_day = list(s)
  for i in range(1, d + 1):
    for j in range(1, 7):
      if i % j == 0:
        rings_per_day[j - 1] += rings_per_day[j - 1]
        rings_per_day[j - 1] %= MOD
  return rings_per_day


def RunCase(w, case, test_input=None):
  outputs = []

  def Input():
    return input()

  def Output(line):
    print(line)
    sys.stdout.flush()

  for ex in range(w + 1):
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


def RunCases(w, cases):
  for i, case in enumerate(cases, 1):
    result, _ = RunCase(w, case)
    if result:
      return "Case #{} ({}) failed: {}".format(i, case, result)
  try:
    extra_input = input()
  except EOFError:
    return None
  except Exception:  # pylint: disable=broad-except
    return "Exception raised while reading input after all cases finish."
  return "Additional input after all cases finish: {}".format(extra_input[:100])


def main():
  assert len(sys.argv) == 2
  index = int(sys.argv[1])
  cases = CASES[index]
  w = WS[index]
  print(len(cases), w)
  sys.stdout.flush()
  result = RunCases(w, cases)
  if result:
    print(result, file=sys.stderr)
    sys.stdout.flush()
    sys.exit(1)


if __name__ == "__main__":
  main()
