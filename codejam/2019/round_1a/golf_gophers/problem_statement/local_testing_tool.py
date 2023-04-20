"""Golf Gophers interactive judge.
"""

# Usage: `python testing_tool.py test_number`, where the argument test_number is
# either 0 (first test set) or 1 (second test set).
# This can also be run as `python3 testing_tool.py test_number`.
import random
import sys

# Use raw_input in Python2.
try:
  input = raw_input
except NameError:
  pass

CASES = ([1, 2, 3],
         [1, 2, 3]) # fill in your own cases
QS = (365, 7)
MAX_GOPHERS = (100, 10 ** 6)

WRONG_ANSWER, CORRECT_ANSWER = -1, 1

EXCEEDED_QUERIES_ERROR = "Exceeded number of queries: {}.".format
INVALID_LINE_ERROR = "Couldn't read a valid line."
NOT_INTEGER_ERROR = "Not an integer: {}".format
NUM_BLADES_OUT_OF_RANGE_ERROR = "Num blades {} is out of range [2-18].".format
NUM_GOPHERS_OUT_OF_RANGE_ERROR = "Num gophers {} is out of range [1-{}].".format
WRONG_NUM_TOKENS_ERROR = "Wrong number of tokens: {}. Expected 1 or 18.".format
WRONG_GUESS_ERROR = "Wrong guess: {}. Expected: {}.".format


def ReadValues(line, mg=None):
  t = line.split()
  if len(t) != 1 and len(t) != 18:
    return WRONG_NUM_TOKENS_ERROR(len(t))
  r = []
  for s in t:
    try:
      v = int(s)
    except:
      return NOT_INTEGER_ERROR(s if len(s) < 100 else s[:100])
    r.append(v)
  if len(r) == 1:
    if not (1 <= r[0] <= mg):
      return NUM_GOPHERS_OUT_OF_RANGE_ERROR(r[0], mg)
  else:
    for ri in r:
      if not (2 <= ri <= 18):
        return NUM_BLADES_OUT_OF_RANGE_ERROR(ri)
  return r


def GopherChoices(g):
  r = [0] * 18
  for _ in range(g):
    r[random.randrange(18)] += 1
  return r


def RunCase(qs, mg, case, test_input=None):
  outputs = []

  def Input():
    return input()

  def Output(line):
    print(line)
    sys.stdout.flush()

  for ex in range(qs + 1):
    try:
      line = Input()
    except:
      Output(WRONG_ANSWER)
      return INVALID_LINE_ERROR, outputs
    v = ReadValues(line, mg)
    if isinstance(v, str):
      Output(WRONG_ANSWER)
      return v, outputs
    if len(v) == 18:
      if ex == qs:
        Output(WRONG_ANSWER)
        return EXCEEDED_QUERIES_ERROR(qs), outputs
      else:
        r = GopherChoices(case)
        for i in range(18):
          r[i] %= v[i]
        Output(" ".join(map(str, r)))
    else:
      if v[0] != case:
        Output(WRONG_ANSWER)
        return WRONG_GUESS_ERROR(v[0], case), outputs
      else:
        Output(CORRECT_ANSWER)
        return None, outputs


def RunCases(qs, mg, cases):
  for i, case in enumerate(cases, 1):
    result, _ = RunCase(qs, mg, case)
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
  random.seed(2)
  assert len(sys.argv) == 2
  index = int(sys.argv[1])
  cases = CASES[index]
  qs = QS[index]
  mg = MAX_GOPHERS[index]
  random.shuffle(cases)
  print(len(cases), qs, mg)
  sys.stdout.flush()
  result = RunCases(qs, mg, cases)
  if result:
    print(result, file=sys.stderr)
    sys.stdout.flush()
    sys.exit(1)


if __name__ == "__main__":
  main()
