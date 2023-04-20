# Usage: `local_testing_tool.py test_number`, where the argument test_number
# is either 0 (Test Set 1), 1 (Test Set 2), or 2 (Test Set 3).
import sys

# Use raw_input in Python2.
try:
  input = raw_input
except NameError:
  pass

HIT, MISS, CENTER, WRONG = "HIT", "MISS", "CENTER", "WRONG"
MAXX = 10 ** 9
MINR = (MAXX - 5, MAXX - 50, MAXX // 2)
MAXR = (MAXX - 5, MAXX - 50, MAXX)

D = 300

# These are NOT the cases the real judge uses!
# CASES[test_number] are the cases run if test_number is passed as
# command line parameter.
CASES = [[((0, 0), (10 ** 9) - 5), ((5, -5), (10 ** 9) - 5)],
         [((0, 0), (10 ** 9) - 50), ((-50, 50), (10 ** 9) - 50)],
         [((0, 50), (10 ** 9) // 2), ((0, 0), (10 ** 9))]]


class Error(Exception):
  pass


class JudgeError(Exception):
  pass


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


def Dist2(p, q):
  return ((p[0] - q[0]) ** 2) + ((p[1] - q[1]) ** 2)


def Answer(p, c, r):
  if p == c:
    return CENTER
  elif Dist2(p, c) <= r ** 2:
    return HIT
  else:
    return MISS


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


def RunCase(d, c, r, test_input=None, test_output_storage=None):
  for _ in range(d):
    try:
      line = input()
    except:
      raise Error(INVALID_LINE_ERROR)
    p = ReadValues(line)
    a = Answer(p, c, r)
    Output(a)
    if a == CENTER:
      return
  raise Error(CENTER_NOT_HIT_ERROR(d))


def RunCases(d, minr, maxr, cases, test_input=None, test_output_storage=None):
  Output("{} {} {}".format(len(cases), minr, maxr))
  for i, (c, r) in enumerate(cases, 1):
    assert minr <= r <= maxr and all(-MAXX + r <= x <= MAXX - r for x in c)
    try:
      RunCase(d, c, r, test_input=test_input,
              test_output_storage=test_output_storage)
    except Error as err:
      Output(WRONG)
      raise Error(CASE_ERROR(i, err))
  try:
    extra_input = input()
  except EOFError:
    return
  except Exception:  # pylint: disable=broad-except
    raise Error(EXCEPTION_AFTER_END_ERROR)
  raise Error(ADDITIONAL_INPUT_ERROR(extra_input[:100]))


def main():
  try:
    assert len(sys.argv) == 2
    minr, maxr, cases = (
        MINR[int(sys.argv[1])], MAXR[int(sys.argv[1])], CASES[int(sys.argv[1])])
  except:
    print("Usage: {} <test_number> where the argument test_number is " +
          "either 0 (Test Set 1), 1 (Test Set 2), or 2 (Test Set 3)".format(
              sys.argv[0]), file=sys.stderr)
    sys.exit(1)
  try:
    RunCases(D, minr, maxr, cases)
    print("Finished running all cases succesfully!", file=sys.stderr)
  except Error as err:
    print(str(err)[:1000], file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
  main()
