"""judge.py for Pen Testing."""

# Usage: `judge.py test_number`, where the argument test_number is either 0
# (small), 1 (large) or -2 (test mode).

import hashlib
import sys
import collections
import itertools
import random
import math
import time

NUM_CASES = [20000, 20000, 100000]
N = 15
NEED_CORRECT = [10900, 12000, 63600]


class Error(Exception):
  pass

class WrongAnswer(Exception):
  pass


WRONG_NUM_TOKENS_ERROR = (
    "Wrong number of tokens: expected {}, found {}.".format)
NOT_INTEGER_ERROR = "Not an integer: {}.".format
INVALID_LINE_ERROR = "Couldn't read a valid line."
ADDITIONAL_INPUT_ERROR = "Additional input after all cases finish: {}.".format
OUT_OF_BOUNDS_ERROR = "Request out of bounds: {}.".format
TOO_MANY_ROUNDS_ERROR = "Too many rounds"
SAME_PEN_TWICE_ERROR = "Taking the same pen twice"
TOO_FEW_CORRECT_ERROR = "Too few correct answers: {}.".format

INVALID_OUTPUT = -1
SUCCESSFUL = 1
NO_MORE_INK = 0
DID_NOT_WRITE = 0


def GenerateSeed():
  return int(1e9 * time.time()) ^ 226386487361623781


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


def Shuffle(arr, rng):
  for j in range(len(arr)):
    k = rng.Next() % (j + 1)
    tmp = arr[j]
    arr[j] = arr[k]
    arr[k] = tmp


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


def RunCases(num_cases, n, need_correct, seed, test_input=None,
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

  Output("{} {} {}".format(num_cases, n, need_correct))

  remaining = [
      list(range(n))
      for _ in range(num_cases)]
  rng = RNG(seed)
  for i in range(num_cases):
    Shuffle(remaining[i], rng)

  max_rounds = n * (n + 1) // 2
  num_rounds = 0

  while True:
    try:
      moves = ReadValues(Input(), num_cases)
    except EOFError:
      raise Error(INVALID_LINE_ERROR)

    for move in moves:
      if move < 0 or move > n:
        raise Error(OUT_OF_BOUNDS_ERROR(move))
    if all(move == 0 for move in moves):
      break
    num_rounds += 1
    if num_rounds > max_rounds:
      raise Error(TOO_MANY_ROUNDS_ERROR)
    results = []
    for move, rem in zip(moves, remaining):
      if move == 0:
        results.append(DID_NOT_WRITE)
      else:
        move -= 1
        got = rem[move]
        if got > 0:
          results.append(SUCCESSFUL)
          rem[move] = got - 1
        else:
          results.append(NO_MORE_INK)
    Output(' '.join(str(result) for result in results))

  try:
    guesses = ReadValues(Input(), 2 * num_cases)
  except EOFError:
    raise Error(INVALID_LINE_ERROR)

  correct = 0
  for v1, v2, rem in zip(guesses[0::2], guesses[1::2], remaining):
    if v1 < 1 or v1 > n:
      raise Error(OUT_OF_BOUNDS_ERROR(v1))
    if v2 < 1 or v2 > n:
      raise Error(OUT_OF_BOUNDS_ERROR(v2))
    if v1 == v2:
      raise Error(SAME_PEN_TWICE_ERROR)
    v1 -= 1
    v2 -= 1
    if rem[v1] + rem[v2] >= n:
      correct += 1

  try:
    extra_input = Input()
    raise Error(ADDITIONAL_INPUT_ERROR(extra_input[:100]))
  except EOFError:
    pass

  if correct < need_correct:
    raise WrongAnswer(TOO_FEW_CORRECT_ERROR(correct))


def AssertEqual(expected, actual):
  assert expected == actual, (
      "Expected [{}], got [{}]".format(expected, actual))


def AssertRaisesError(expected_message, fn, *args, **kwargs):
  try:
    fn(*args, **kwargs)
    assert False, (
        "Expected error [{}], but there was none".format(expected_message))
  except Error as error:
    message = str(error)
    assert expected_message == message, (
        "Expected error [{}], got [{}]".format(expected_message, message))


def AssertRaisesWrongAnswer(expected_message, fn, *args, **kwargs):
  try:
    fn(*args, **kwargs)
    assert False, (
        "Expected error [{}], but there was none".format(expected_message))
  except WrongAnswer as wa:
    message = str(wa)
    assert expected_message == message, (
        "Expected error [{}], got [{}]".format(expected_message, message))


def TestReadValues():
  AssertEqual([1, -2, 3], ReadValues("1 -2 3", 3))
  AssertEqual([1, 2, 3], ReadValues("1        2   \t\t    3", 3))
  AssertRaisesError(WRONG_NUM_TOKENS_ERROR(1, 0), ReadValues, "", 1)
  AssertRaisesError(WRONG_NUM_TOKENS_ERROR(2, 1), ReadValues, "1", 2)
  AssertRaisesError(WRONG_NUM_TOKENS_ERROR(2, 3), ReadValues, "1 2 3", 2)
  AssertRaisesError(NOT_INTEGER_ERROR("two"), ReadValues, "1 two", 2)
  AssertRaisesError(NOT_INTEGER_ERROR("1.0"), ReadValues, "1.0", 1)
  # Check truncation.
  AssertRaisesError(NOT_INTEGER_ERROR("a"*100), ReadValues, "a"*100 + "b", 1)


# Cases use N >= 3, because it's impossible to succeed for N = 2!
def TestRunCases():
  # The cases in this group take advantage of what the answers for this seed
  # happen to be.
  RunCases(1, 3, 1, 123, test_input=["0", "1 2"], test_output_storage=[])
  # Order of pens within a test case answer is irrelevant.
  RunCases(1, 3, 1, 123, test_input=["0", "2 1"], test_output_storage=[])
  AssertRaisesWrongAnswer(TOO_FEW_CORRECT_ERROR(0), RunCases, 1, 3, 1, 123,
                          test_input=["0", "1 3"],
                          test_output_storage=[])
  AssertRaisesWrongAnswer(TOO_FEW_CORRECT_ERROR(0), RunCases, 1, 3, 1, 123,
                          test_input=["0", "2 3"],
                          test_output_storage=[])
  RunCases(2, 3, 2, 123, test_input=["0 0", "1 2 1 3"], test_output_storage=[])
  AssertRaisesWrongAnswer(TOO_FEW_CORRECT_ERROR(1), RunCases, 2, 3, 2, 123,
                          test_input=["0 0", "1 2 1 2"],
                          test_output_storage=[])
  AssertRaisesWrongAnswer(TOO_FEW_CORRECT_ERROR(1), RunCases, 2, 3, 2, 123,
                          test_input=["0 0", "1 3 1 3"],
                          test_output_storage=[])
  AssertRaisesWrongAnswer(TOO_FEW_CORRECT_ERROR(0), RunCases, 2, 3, 2, 123,
                          test_input=["0 0", "1 3 1 2"],
                          test_output_storage=[])
  AssertRaisesWrongAnswer(TOO_FEW_CORRECT_ERROR(0), RunCases, 2, 3, 2, 123,
                          test_input=["0 0", "2 3 2 3"],
                          test_output_storage=[])

  # I don't think it's possible to get the INVALID_LINE_ERROR on line 111 via
  # testing.
  # Other ways to get it: just stop giving input too early...
  AssertRaisesError(INVALID_LINE_ERROR, RunCases, 1, 3, 1, 123,
                    test_input=["1", "2", "3"],
                    test_output_storage=[])
  # ...or fail to give an answer after signaling that you want to give one.
  AssertRaisesError(INVALID_LINE_ERROR, RunCases, 1, 3, 1, 123,
                    test_input=["1", "2", "3", "0"],
                    test_output_storage=[])

  AssertRaisesError(ADDITIONAL_INPUT_ERROR("1"), RunCases, 1, 2, 1, 123,
                    test_input=["0", "1 2", "1"],
                    test_output_storage=[])

  AssertRaisesError(OUT_OF_BOUNDS_ERROR("-1"), RunCases, 1, 3, 1, 123,
                    test_input=["-1", "0", "1 2"],
                    test_output_storage=[])
  AssertRaisesError(OUT_OF_BOUNDS_ERROR("987654321"), RunCases, 1, 3, 1, 123,
                    test_input=["987654321", "0", "1 2"],
                    test_output_storage=[])
  AssertRaisesError(OUT_OF_BOUNDS_ERROR("0"), RunCases, 1, 3, 1, 123,
                    test_input=["0", "0 2"],
                    test_output_storage=[])
  AssertRaisesError(OUT_OF_BOUNDS_ERROR("4"), RunCases, 1, 3, 1, 123,
                    test_input=["0", "1 4"],
                    test_output_storage=[])

  # Use exactly as many rounds as allowed. Conveniently use the pen that was
  # empty to begin with...
  RunCases(1, 3, 1, 123,
           test_input=["3", "3", "3", "3", "3", "3", "0", "1 2"],
  	   test_output_storage=[])
  # One more round than allowed.
  AssertRaisesError(TOO_MANY_ROUNDS_ERROR, RunCases, 1, 3, 1, 123,
                    test_input=["3", "3", "3", "3", "3", "3", "3", "0", "1 2"],
                    test_output_storage=[])

  AssertRaisesError(SAME_PEN_TWICE_ERROR, RunCases, 1, 3, 1, 123,
                    test_input=["0", "1 1"],
                    test_output_storage=[])

  # Using either of the pens with ink makes us fail, since we don't have enough left overall.
  AssertRaisesWrongAnswer(TOO_FEW_CORRECT_ERROR(0), RunCases, 1, 3, 1, 123,
                          test_input=["1", "0", "2 3"],
                          test_output_storage=[])
  AssertRaisesWrongAnswer(TOO_FEW_CORRECT_ERROR(0), RunCases, 1, 3, 1, 123,
                          test_input=["2", "0", "2 3"],
                          test_output_storage=[])

  # Try to answer without signaling 0 first.
  AssertRaisesError(WRONG_NUM_TOKENS_ERROR(1, 2), RunCases, 1, 3, 1, 123,
                    test_input=["1 2"],
                    test_output_storage=[])
  # Try to proceed to the next case without answering.
  AssertRaisesError(WRONG_NUM_TOKENS_ERROR(4, 2), RunCases, 2, 3, 2, 123,
                    test_input=["0 0", "1 2"],
                    test_output_storage=[])

  # Only a line of all 0s triggers the judgment step.
  # (This contrives to always use the empty pen, to keep the answer correct)
  RunCases(2, 3, 2, 123,
           test_input=["0 2", "3 0", "0 2", "3 0", "0 2", "3 0", "0 0", "1 2 1 3"],
           test_output_storage=[])
  # The ink values are 2 1 0.
  tos = []
  AssertRaisesWrongAnswer(TOO_FEW_CORRECT_ERROR(0), RunCases, 1, 3, 1, 123,
                          test_input=["1", "2", "3", "1", "2", "3", "0", "1 2"],
                          test_output_storage=tos)
  AssertEqual(["1 3 1", "1", "1", "0", "1", "0", "0"], tos)
  # Check that the system prints 0 when no pen is chosen in a case.
  # The first pen has 2 units in Case 1 and 1 unit in Case 2.
  tos = []
  AssertRaisesWrongAnswer(TOO_FEW_CORRECT_ERROR(0), RunCases, 2, 3, 2, 123,
    test_input=["0 1", "1 0", "0 1", "1 0", "0 1", "1 0", "0 0", "1 2 1 2"],
    test_output_storage=tos)
  AssertEqual(["2 3 2", "0 1", "1 0", "0 0", "1 0", "0 0", "0 0"], tos)
  # In Case 1, the ink values are 2 1 3 0. In Case 2, they're 0 2 3 1.
  tos = []
  AssertRaisesWrongAnswer(
      TOO_FEW_CORRECT_ERROR(0), RunCases, 2, 4, 2, 123,
      test_input=["1 1", "1 1", "1 1", "2 2", "2 2", "2 2", "3 3", "3 3", "3 3", "4 4", "0 0", "1 2 3 4"],
      test_output_storage=tos)
  AssertEqual(
      ["2 4 2", "1 0", "1 0", "0 0", "1 1", "0 1", "0 0", "1 1", "1 1", "1 1", "0 1"], tos)


def Test():
  TestReadValues()
  TestRunCases()


def main():
  assert len(sys.argv) == 2
  index = int(sys.argv[1])
  if index == -2:
    Test()
  else:
    seed = GenerateSeed()
    print('Seed: ', seed, file=sys.stderr)
    try:
      num_cases = NUM_CASES[index]
      n = N
      need_correct = NEED_CORRECT[index]
      try:
        RunCases(num_cases, n, need_correct, seed)
      except Error as error:
        ActuallyOutput(INVALID_OUTPUT)
        print(error, file=sys.stderr)
        sys.exit(1)
      except WrongAnswer as error:
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
