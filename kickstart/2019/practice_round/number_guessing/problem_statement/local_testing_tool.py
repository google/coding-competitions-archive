"""Number Guessing interactive judge."""

# Usage: `testing_tool.py test_number`, where the argument test_number is
# either 0 (first test set) or 1 (second test set).

from __future__ import print_function
import random
import sys

# Use raw_input in Python2.
try:
  input = raw_input
except NameError:
  pass

_ERROR_MSG_EXTRA_NEW_LINES = "Input has extra newline characters."
_ERROR_MSG_INCORRECT_ARG_NUM = "Input does not have exactly 1 token."
_ERROR_MSG_INVALID_TOKEN = "Input has invalid token."
_ERROR_MSG_OUT_OF_RANGE = "Input is out of range."
_ERROR_MSG_READ_FAILURE = "Read for input fails."

_CORRECT_MSG = "CORRECT"
_QUERY_LIMIT_EXCEEDED_MSG = "Query Limit Exceeded."
_TOO_BIG_MSG = "TOO_BIG"
_TOO_SMALL_MSG = "TOO_SMALL"
_WRONG_ANSWER_MSG = "WRONG_ANSWER"

CASES = ([1, 30], [1, 42, 10**9])  # fill in your own cases

B_VALUE = (30, 10**9)


def Output(line):
  print(line)
  sys.stdout.flush()


class JudgeSingleCase:

  def __init__(self, answer, lo, hi, max_num_tries):
    self.__answer = answer  # the number that is being guessed
    self.__lo = lo  # answer > lo
    self.__hi = hi  # answer <= hi
    self.__max_num_tries = max_num_tries  # max number of tries

  def ReadValues(self, response):
    """Parses contestant's input.

    Parse contestant's input which should be one integer, within (lo, hi].

    Args:
      response: (str) one-line input given by the contestant.

    Returns:
      (int, string): the integer guess sent by the contestant, and the error
      string in case of error.
      If the parsing succeeds, the return value should be (int, None).
      If the parsing fails, the return value should be (None, str).
    """
    if ("\n" in response) or ("\r" in response):
      return (self.__lo, _ERROR_MSG_EXTRA_NEW_LINES)
    tokens = response.split()
    if len(tokens) != 1:
      return (self.__lo, _ERROR_MSG_INCORRECT_ARG_NUM)
    token = tokens[0]
    if len(token) > len(str(self.__hi)):
      return (self.__lo, _ERROR_MSG_INVALID_TOKEN)
    try:
      guess = int(token)
    except Exception:
      return (self.__lo, _ERROR_MSG_INVALID_TOKEN)
    if (guess <= self.__lo) or (guess > self.__hi):
      return (self.__lo, _ERROR_MSG_OUT_OF_RANGE)
    return (guess, None)

  def Judge(self):
    """Judge one single case; should only be called once per test case.

    Returns:
      An error string, or None if the attempt was correct.
    """
    for _ in range(self.__max_num_tries):
      try:
        contestant_input = input()
      except Exception:
        return _ERROR_MSG_READ_FAILURE
      guess, err = self.ReadValues(contestant_input)
      if err is not None:
        return err
      if guess == self.__answer:
        Output(_CORRECT_MSG)
        return None
      elif guess < self.__answer:
        Output(_TOO_SMALL_MSG)
      else:
        Output(_TOO_BIG_MSG)
    return _QUERY_LIMIT_EXCEEDED_MSG


def RunCases(B, cases):
  """Sends input to contestant and judges contestant output.

  Returns:
    An error string, or None if the attempt was correct.
  """

  A = 0
  N = 30
  T = len(cases)
  Output(T)

  for case_number, answer in enumerate(cases, 1):
    Output("{} {}".format(A, B))
    Output(N)
    single_case = JudgeSingleCase(answer, A, B, N)
    err = single_case.Judge()
    if err is not None:
      return "Case #{} ({}) failed:\n{}".format(case_number, answer, err)
  # Ensure there is no additional output beyond the testcases.
  try:
    response = input()
  except EOFError:
    return None
  except Exception:  # pylint: disable=broad-except
    return "Exception raised while reading input after all cases finish."
  return "Additional input after all cases finish: {}".format(response[:1000])


def main():
  random.seed(30)
  assert len(sys.argv) == 2
  index = int(sys.argv[1])
  cases = CASES[index]
  random.shuffle(cases)
  b = B_VALUE[index]
  result = RunCases(b, cases)
  if result is not None:
    print(result, file=sys.stderr)
    Output(_WRONG_ANSWER_MSG)
    sys.exit(1)


if __name__ == "__main__":
  main()
