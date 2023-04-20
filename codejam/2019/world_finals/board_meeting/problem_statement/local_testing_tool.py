# Usage: `python testing_tool.py test_number`, where the argument test_number
# is either 0 (first test set) or 1 (second test set).
# This can also be run as `python3 testing_tool.py test_number`.

import collections
import sys

# Use raw_input in Python2.
try:
  input = raw_input
except NameError:
  pass

N_MAXS = (1, 10)
MAX_COORD = int(1e6)
MAX_REQUEST_COORD = 10 * MAX_COORD
MAX_REQUESTS = 1000

END_OF_PHASE_1 = "READY"
END_OF_PHASE_2 = "DONE"
INVALID_OUTPUT = "ERROR"

TestCase = collections.namedtuple("TestCase", ["kings", "requests"])

# Add your own cases here.
# The one included here is just an example and is not necessarily part of
# any real test set.
CASES = (
    # cases for test set 1
    [
        TestCase(kings=((0, 1),), requests=((2, 3), (0, 1), (1, 0))),
        TestCase(kings=((-1, 2),), requests=((-1, 2),))
    ],
    # cases for test set 2
    [
        TestCase(kings=((1, 2), (3, 4)), requests=((5, 6), (7, 8), (-1, -2))),
        TestCase(kings=((-1000000, 1000000),), requests=((10000000, -10000000),))
    ]
)

class Error(Exception):
  pass


WRONG_NUM_TOKENS_ERROR = (
    "Wrong number of tokens: expected {}, found {}.".format)
EXCEEDED_REQUESTS_ERROR = "Exceeded number of requests: {}.".format
OUT_OF_BOUNDS_ERROR = "Request out of bounds: ({}, {}).".format
NOT_INTEGER_ERROR = "Not an integer: {}".format
INVALID_LINE_ERROR = "Couldn't read a valid line."
CASE_FAILED_ERROR = "Case #{} failed: {}".format
WRONG_ANSWER = "Wrong answer for request {}: expected {}, found {}.".format
EXCEPTION_AFTER_END_ERROR = (
    "Exception raised while reading input after all cases finish.")
ADDITIONAL_INPUT_ERROR = "Additional input after all cases finish: {}".format


def ReadValues(line, num_tokens):
  t = line.split()
  if len(t) != num_tokens:
    raise Error(WRONG_NUM_TOKENS_ERROR(num_tokens, len(t)))
  r = []
  for s in t:
    try:
      v = int(s)
    except:
      raise Error(NOT_INTEGER_ERROR(s[:100]))
    r.append(v)
  return r


def EvaluateRequest(kings, rx, ry):
  res = 0
  for x, y in kings:
    res += max(abs(rx - x), abs(ry - y))
  return res


def RunCase(case):

  def Output(line):
    print(line)
    sys.stdout.flush()

  received_requests = 0
  while True:
    try:
      line = input()
    except:
      Output(INVALID_OUTPUT)
      raise Error(INVALID_LINE_ERROR)

    if line.strip().lower() == END_OF_PHASE_1.lower():
      break

    try:
      (x, y) = ReadValues(line, 2)
    except:
      Output(INVALID_OUTPUT)
      raise

    received_requests += 1
    if received_requests > MAX_REQUESTS:
      Output(INVALID_OUTPUT)
      raise Error(EXCEEDED_REQUESTS_ERROR(received_requests))

    if not(-MAX_REQUEST_COORD <= x <= MAX_REQUEST_COORD and
           -MAX_REQUEST_COORD <= y <= MAX_REQUEST_COORD):
      Output(INVALID_OUTPUT)
      raise Error(OUT_OF_BOUNDS_ERROR(x, y))

    Output(str(EvaluateRequest(case.kings, x, y)))

  for i, (x, y) in enumerate(case.requests):
    Output("{} {}".format(x, y))

    try:
      line = input()
    except:
      Output(INVALID_OUTPUT)
      raise Error(INVALID_LINE_ERROR)

    try:
      (v,) = ReadValues(line, 1)
    except:
      Output(INVALID_OUTPUT)
      raise

    expected = EvaluateRequest(case.kings, x, y)
    if v != expected:
      Output(INVALID_OUTPUT)
      raise Error(WRONG_ANSWER(i, expected, v))

  Output(END_OF_PHASE_2)


def RunCases(cases):
  for i, case in enumerate(cases, 1):
    try:
      RunCase(case)
    except Error as error:
      raise Error(CASE_FAILED_ERROR(i, error))

  try:
    extra_input = input()
  except EOFError:
    return
  except Exception:
    raise Error(EXCEPTION_AFTER_END_ERROR)
  raise Error(ADDITIONAL_INPUT_ERROR(extra_input[:100]))


def main():
  assert len(sys.argv) == 2
  index = int(sys.argv[1])
  try:
    cases = CASES[index]
    n_max = N_MAXS[index]
    print(len(cases), n_max, MAX_COORD, MAX_REQUESTS)
    sys.stdout.flush()
    try:
      RunCases(cases)
    except Error as error:
      print(error, file=sys.stderr)
      sys.stdout.flush()
      sys.exit(1)
  except Exception as exception:
    print(INVALID_OUTPUT)
    print('Exception:', file=sys.stderr)
    print(str(exception)[:1000], file=sys.stderr)
    sys.stdout.flush()
    sys.exit(1)


if __name__ == "__main__":
  main()
