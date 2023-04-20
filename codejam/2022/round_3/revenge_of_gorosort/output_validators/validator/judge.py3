"""judge.py for Revenge of Gorosort."""

# Usage: `judge.py test_number`, where the argument test_number is either 0
# (test set 1), 1 (test set 2), 2 (test set 3), or -2 (test mode).

import sys
import random

T_ARR = [1000, 1000, 1000]
N_ARR = [100, 100, 100]
K_ARR = [16500, 12500, 11500]

NOT_YET_SORTED = 0
IS_SORTED = 1
INVALID_OUTPUT = -1
RUN_OUT_OF_TURNS = -1

class Error(Exception):
  pass

INVALID_LINE_ERROR = "Couldn't read a valid line."
RAN_OUT_OF_TURNS_ERROR = "Ran out of turns."
UNEXPECTED_LENGTH_ERROR = "Expected line with {} tokens, but actually got {}".format
INVALID_INTEGER_ERROR = "Got an incorrectly formatted integer"
INVALID_PARTITION_VALUE_ERROR = "Expected partition value in range [{}, {}], but actually got {}".format
EXCEPTION_AFTER_END_ERROR = "Exception raised while reading input after all cases finish."
ADDITIONAL_INPUT_ERROR = "Additional input after all cases finish: {}".format

CASE_FAILED_ERROR = "Case #{} failed: {}".format

def AssertEqual(expected, actual):
  assert expected == actual, (
      "Expected [{}], got [{}]".format(expected, actual))

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

def AssertReturnsIO(expected_return, expected_output, fn, *args):
  test_output_storage = []
  AssertReturns(expected_return, fn, *(args + (test_output_storage,)))
  AssertEqual(expected_output, test_output_storage)


def AssertRaisesErrorIO(expected_message, expected_output, fn, *args):
  test_output_storage = []
  AssertRaisesError(expected_message, fn, *(args + (test_output_storage,)))
  AssertEqual(expected_output, test_output_storage)

def Shuffle(arr, partitions):
  for partition in partitions:
    vals = [arr[i] for i in partition]
    random.shuffle(vals)
    for i in range(len(partition)):
      arr[partition[i]] = vals[i]


def IsSorted(arr):
  for i in range(len(arr) - 1):
    if arr[i] > arr[i + 1]:
      return False
  return True


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


# Returns the number of turns used.
def RunCase(n, turns_remaining, is_last_test_case, test_input=None, test_output_storage=None):
  def Input():
    return input() if test_input is None else test_input.pop(0)

  def Output(line):
    if test_input is None:
      ActuallyOutput(line)
    else:
      test_output_storage.append(line)

  arr = list(range(1, n + 1))
  while IsSorted(arr):
    random.shuffle(arr)

  turns_used = 0
  while True:
    turns_used += 1
    # Print the array
    Output(" ".join([str(x) for x in arr]))

    # Read the partitions
    partitions_map = {}
    try:
      tokens = Input().strip().split()
      if len(tokens) != n:
        raise Error(UNEXPECTED_LENGTH_ERROR(n, len(tokens)))
      for i in range(n):
        # Any token with more than 50 characters is assumed to not be a valid integer
        if len(tokens[i]) > 50:
          raise Error(INVALID_INTEGER_ERROR)
        x = int(tokens[i])
        if x < 1 or x > n:
          raise Error(INVALID_PARTITION_VALUE_ERROR(1, n, x))
        if x not in partitions_map:
          partitions_map[x] = []
        partitions_map[x].append(i)
    except Error as err:
      Output(INVALID_OUTPUT)
      raise Error(err)
    except Exception as err:
      Output(INVALID_OUTPUT)
      raise Error(INVALID_LINE_ERROR)

    # Shuffle the array using the partitions
    Shuffle(arr, list(partitions_map.values()))

    if turns_used == turns_remaining and (not is_last_test_case or not IsSorted(arr)):
      Output(RUN_OUT_OF_TURNS)
      raise Error(RAN_OUT_OF_TURNS_ERROR)

    # If the array is sorted, return the number of turns we used.
    if IsSorted(arr):
      Output(IS_SORTED)
      return turns_used
    # Otherwise, output that the array is not yet sorted.
    Output(NOT_YET_SORTED)


def TestRunCase():
  # TODO(tbuzzelli): Add test cases.
  return

def RunCases(t, n, max_turns, test_input=None, test_rnd=None, test_output_storage=None):
  turns_remaining = max_turns
  for i in range(1, t + 1):
    # Reset the seed for each case for stability.
    random.seed(82718 + t * t * t + i)
    try:
      turns_remaining -= RunCase(n=n, turns_remaining=turns_remaining, is_last_test_case=(i == t), test_input=test_input, test_output_storage=test_output_storage)
    except Error as err:
      raise Error(CASE_FAILED_ERROR(i, err))

  def Input():
    if test_input is None:
      return raw_input()
    else:
      if test_input:
        return test_input.pop(0)
      else:
        raise EOFError()

  try:
    extra_input = Input()
  except Exception:  # pylint: disable=broad-except
    return
  raise Error(ADDITIONAL_INPUT_ERROR(extra_input[:100]))

def TestRunCases():
  # TODO(tbuzzelli): Add test cases.
  return

def Test():
  TestRunCase()
  TestRunCases()

def main():
  assert len(sys.argv) == 2, "Bad usage"
  index = int(sys.argv[1])
  if index == -2:
    Test()
  else:
    T = T_ARR[index]
    N = N_ARR[index]
    K = K_ARR[index]
    try:
      print("{} {} {}".format(T, N, K))
      sys.stdout.flush()
      try:
        RunCases(T, N, K)
      except Error as err:
        print(str(err)[:1000], file=sys.stderr)
        sys.exit(1)
    except Exception as exception:
      print(INVALID_OUTPUT)
      sys.stdout.flush()
      print(('JUDGE_ERROR! Internal judge exception: {}'.format(exception))
            [:1000], file=sys.stderr)

if __name__ == "__main__":
  main()
