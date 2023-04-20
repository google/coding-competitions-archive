"""judge.py for Revenge of Gorosort."""

# Usage: `judge.py test_number`, where the argument test_number is either 0
# (test set 1), 1 (test set 2), 2 (test set 3).

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


def Shuffle(arr, partitions):
  # The real judge may implement Shuffle() in a different way and use random
  # numbers differently.
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


# Returns the number of turns used.
def RunCase(n, turns_remaining, is_last_test_case):
  def Output(line):
    print(line)
    sys.stdout.flush()

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
      tokens = input().strip().split()
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


def RunCases(t, n, max_turns):
  turns_remaining = max_turns
  for i in range(1, t + 1):
    # Reset the seed for each case for stability.
    # The real judge may generate random numbers differently than the local
    # testing tool.
    random.seed(12345 + t * t * t + i)
    try:
      turns_remaining -= RunCase(n=n, turns_remaining=turns_remaining, is_last_test_case=(i == t))
    except Error as err:
      raise Error(CASE_FAILED_ERROR(i, err))


  try:
    extra_input = raw_input()
  except Exception:
    return
  raise Error(ADDITIONAL_INPUT_ERROR(extra_input[:100]))

def main():
  assert len(sys.argv) == 2, "Bad usage. See the comment at the top of the file for usage instructions."
  index = int(sys.argv[1])
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
