"""judge.py for Digit Blocks."""

# Usage: `judge.py test_number`, where the argument test_number is either 0
# (Test Set 1), 1 (Test Set 2) or -2 (test mode).

import hashlib
import sys
import time

NUM_CASES = 50
NUM_TOWERS = 20
HEIGHT = 15
S_NUMERATOR = 19131995794056374423098756540547899023413702180946652049981241292126018545306904350366099321347119078652032583488867227895217431806297911694310429334039514156462579697671476886724907447289719647706123340311407317731009795521253453701078446252610184655049627322081301971215320298108283424216000000000000000000000000000
S_DENOMINATOR = 10 ** 300


def GetBoundary(p, q):
  # x >= NUM_CASES * (p / q) * (S_NUMERATOR / S_DENOMINATOR)
  # x >= NUM_CASES * p * S_NUMERATOR / (q * S_DENOMINATOR)
  return (NUM_CASES * p * S_NUMERATOR + q * S_DENOMINATOR - 1) // (q * S_DENOMINATOR)


NEED_AT_LEAST = [860939810732536850, 937467793908762347]
assert NEED_AT_LEAST[0] == GetBoundary(9, 10)
assert NEED_AT_LEAST[1] == GetBoundary(98, 100)


class Error(Exception):
  pass


def AssertEqual(expected, actual):
  assert expected == actual, ("Expected [{}], got [{}]".format(
      expected, actual))


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


WRONG_NUM_TOKENS_ERROR = (
    "Wrong number of tokens: expected {}, found {}.".format)
NOT_INTEGER_ERROR = "Not an integer: {}.".format
INVALID_LINE_ERROR = "Couldn't read a valid line."
ADDITIONAL_INPUT_ERROR = "Additional input after all cases finish: {}.".format
OUT_OF_BOUNDS_ERROR = "Tower number out of bounds: {}.".format
TOWER_ALREADY_FULL_ERROR = "Tower {} is already full.".format
TOO_SMALL_SUM_ERROR = "Too small sum: {}.".format

INVALID_OUTPUT = "-1"
TOO_SMALL = "-1"
ALL_CORRECT = "1"


# In the local_testing_tool, replace the random number
# generation method with Python built-in Random and seed generation method
# to just use time.time() without "^ value".
def GenerateSeed():
  return int(1e9 * time.time()) ^ 543657846317584631


class RNG(object):
  """Uses SHA-256 of consecutive integers to get random numbers."""

  def __init__(self, seed):
    self.counter = seed

  def Next(self):
    self.counter += 1
    hasher = hashlib.sha256()
    hasher.update(self.counter.to_bytes(32, byteorder='big'))
    digest = hasher.digest()
    assert 32 == len(digest)
    return int.from_bytes(digest, byteorder='big')


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


def ActuallyOutput(line):
  try:
    print(line)
    sys.stdout.flush()
  except:
    # We ignore errors to avoid giving an error if the contestants' program
    # finishes after writing all required output, but without reading all our
    # responses.
    try:
      sys.stdout.close()
    except:
      pass


def RunCase(input_fn, output_fn, num_towers, height, rng):
  towers = [''] * num_towers
  for step in range(num_towers * height):
    digit = str(rng.Next() % 10)
    output_fn(digit)
    try:
      (pos,) = ReadValues(input_fn(), 1)
    except EOFError:
      output_fn(INVALID_OUTPUT)
      raise Error(INVALID_LINE_ERROR)
    except Error as error:
      output_fn(INVALID_OUTPUT)
      raise error

    if pos < 1 or pos > num_towers:
      output_fn(INVALID_OUTPUT)
      raise Error(OUT_OF_BOUNDS_ERROR(pos))
    pos -= 1
    if len(towers[pos]) >= height:
      output_fn(INVALID_OUTPUT)
      raise Error(TOWER_ALREADY_FULL_ERROR(pos + 1))
    towers[pos] = digit + towers[pos]

  return sum(int(x) for x in towers)


def RunCases(num_cases, num_towers, height, need_correct, seed, test_input=None,
             test_output_storage=None):
  def Input():
    try:
      if test_input is None:
        return input()
      else:
        if test_input:
          return test_input.pop(0)
        else:
          raise EOFError()
    except EOFError:
      raise
    except:
      raise Error(INVALID_LINE_ERROR)

  def Output(line):
    if test_input is None:
      ActuallyOutput(line)
    else:
      test_output_storage.append(line)

  Output("{} {} {} {}".format(num_cases, num_towers, height, need_correct))

  rng = RNG(seed)
  total_score = 0
  for case_id in range(num_cases):
    total_score += RunCase(Input, Output, num_towers, height, rng)

  if total_score < need_correct:
    Output(TOO_SMALL)
    raise Error(TOO_SMALL_SUM_ERROR(total_score))
  Output(ALL_CORRECT)

  try:
    extra_input = Input()
    Output(INVALID_OUTPUT)
    raise Error(ADDITIONAL_INPUT_ERROR(extra_input[:100]))
  except EOFError:
    pass


def Test():
  # Test NOT_INTEGER_ERROR
  AssertRaisesErrorIO(
      NOT_INTEGER_ERROR("hello"), ["1 1 1 1", "6", "-1"], RunCases, 1, 1, 1, 1,
      1, ["hello"])
  # Test wrong number of tokens 0
  AssertRaisesErrorIO("Wrong number of tokens: expected 1, found 0.",
                      ["1 1 1 1", "6", "-1"], RunCases, 1, 1, 1, 1, 1, [""])
  # Test wrong number of tokens 2
  AssertRaisesErrorIO("Wrong number of tokens: expected 1, found 2.",
                      ["1 1 1 1", "6", "-1"], RunCases, 1, 1, 1, 1, 1, ["1 2"])
  # Test ADDITIONAL_INPUT_ERROR
  AssertRaisesErrorIO(
      ADDITIONAL_INPUT_ERROR("1"), ["1 1 1 1", "6", "1", "-1"], RunCases, 1, 1,
      1, 1, 1, ["1", "1"])
  # Test TOO_SMALL_SUM_ERROR
  AssertRaisesErrorIO(
      TOO_SMALL_SUM_ERROR(6), ["1 1 1 7", "6", "-1"], RunCases, 1, 1, 1, 7, 1,
      ["1"])
  # Test too small index
  AssertRaisesErrorIO(
      OUT_OF_BOUNDS_ERROR(0), ["1 2 2 7", "6", "-1"], RunCases, 1, 2, 2, 7, 1,
      ["0"])
  # Test too big index
  AssertRaisesErrorIO(
      OUT_OF_BOUNDS_ERROR(3), ["1 2 2 7", "6", "-1"], RunCases, 1, 2, 2, 7, 1,
      ["3"])
  # Test TOWER_ALREADY_FULL_ERROR
  AssertRaisesErrorIO(
      TOWER_ALREADY_FULL_ERROR(1), ["1 2 2 7", "6", "2", "9", "9", "-1"],
      RunCases, 1, 2, 2, 7, 1, ["1", "1", "2", "1"])
  # Test multiple cases TOO_SMALL_SUM_ERROR
  AssertRaisesErrorIO(
      TOO_SMALL_SUM_ERROR(221),
      ["2 2 2 222", "6", "2", "9", "9", "6", "0", "2", "7", "-1"], RunCases, 2,
      2, 2, 222, 1, ["1", "1", "2", "2", "2", "1", "1", "2"])
  # Test multiple cases TOWER_ALREADY_FULL_ERROR
  AssertRaisesErrorIO(
      TOWER_ALREADY_FULL_ERROR(1),
      ["2 2 2 222", "6", "2", "9", "9", "6", "0", "2", "-1"], RunCases, 2, 2, 2,
      222, 1, ["1", "1", "2", "2", "1", "1", "1"])
  # Test multiple cases correct
  AssertReturnsIO(None,
                  ["2 2 2 221", "6", "2", "9", "9", "6", "0", "2", "7", "1"],
                  RunCases, 2, 2, 2, 221, 1,
                  ["1", "1", "2", "2", "2", "1", "1", "2"])
  return


def main():
  assert len(sys.argv) == 2
  index = int(sys.argv[1])
  if index == -2:
    Test()
  else:
    seed = GenerateSeed()
    print('Seed: ', seed, file=sys.stderr)
    try:
      try:
        RunCases(NUM_CASES, NUM_TOWERS, HEIGHT, NEED_AT_LEAST[index], seed)
      except Error as error:
        print(error, file=sys.stderr)
        sys.exit(1)
    except Exception as exception:
      # Hopefully this will never happen, but try to finish gracefully
      # and report a judge error in case of unexpected exception.
      ActuallyOutput(INVALID_OUTPUT)
      print('JUDGE_ERROR! Internal judge exception:', file=sys.stderr)
      print(str(type(exception)), file=sys.stderr)
      print(str(exception)[:1000], file=sys.stderr)
      sys.exit(1)


if __name__ == "__main__":
  main()
