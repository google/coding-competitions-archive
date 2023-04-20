"""judge.py for the number guessing interactive judge.
"""

# Usage: `judge.py test_number`, where the argument test_number is either 0
# (small), 1 (large) or -2 (test mode).

import random
import sys

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


class JudgeSingleCase:

  def __init__(self, answer, lo, hi, max_num_tries):
    self.__answer = answer  # the number that is being guessed
    self.__lo = lo  # answer > lo
    self.__hi = hi  # answer <= hi
    self.__max_num_tries = max_num_tries  # max number of tries

  def _parse_contestant_input(self, response):
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
    for _ in xrange(self.__max_num_tries):
      try:
        contestant_input = raw_input()
      except Exception:
        return _ERROR_MSG_READ_FAILURE
      guess, err = self._parse_contestant_input(contestant_input)
      if err is not None:
        return err
      if guess == self.__answer:
        print _CORRECT_MSG
        sys.stdout.flush()
        return None
      elif guess < self.__answer:
        print _TOO_SMALL_MSG
        sys.stdout.flush()
      else:
        print _TOO_BIG_MSG
        sys.stdout.flush()
    return _QUERY_LIMIT_EXCEEDED_MSG


class JudgeSingleCaseTest:

  @staticmethod
  def TestParseContestantInput():
    """Test _parse_contestant_input using assert.
    """
    case = JudgeSingleCase(10, 0, 20, 20)
    for contestant_input in ["\r2", "2\r", "\n 2 ", "3 \n\n"]:
      assert case._parse_contestant_input(contestant_input)[
          1] == _ERROR_MSG_EXTRA_NEW_LINES
    for contestant_input in [
        "", " 10 20  ", "  200 30 \t 3 \t", "5 6 7 8", "  \t ", "9 9 9"
    ]:
      assert case._parse_contestant_input(contestant_input)[
          1] == _ERROR_MSG_INCORRECT_ARG_NUM
    for contestant_input in ["2.3", "abcd", "!?!?", "a", "100", "2.0"]:
      assert case._parse_contestant_input(contestant_input)[
          1] == _ERROR_MSG_INVALID_TOKEN
    for contestant_input in ["0", "-1", "21", "99"]:
      assert case._parse_contestant_input(contestant_input)[
          1] == _ERROR_MSG_OUT_OF_RANGE
    for (contestant_input, expected_result) in zip(
        ["\t\t 10", "  18 ", "\t9\t", "  \t10     ", "10\t  ", "10", "1", "20"],
        [10, 18, 9, 10, 10, 10, 1, 20]):
      assert case._parse_contestant_input(contestant_input) == (expected_result,
                                                                None)

  @staticmethod
  def Test():
    """Runs all unit tests.
    """
    JudgeSingleCaseTest.TestParseContestantInput()


def JudgeAllCases():
  """Sends input to contestant and judges contestant output.

  Returns:
    An error string, or None if the attempt was correct.
  """
  test_number = int(sys.argv[1])
  total_num_cases = 20
  a = 0
  b = (30, 10**9)[test_number]
  max_num_tries = 30
  print total_num_cases
  sys.stdout.flush()
  for case_number in xrange(1, total_num_cases + 1):
    print a, b
    print max_num_tries
    sys.stdout.flush()
    random.seed(case_number + 101)
    answer = random.randint(a + 1, b)
    single_case = JudgeSingleCase(answer, a, b, max_num_tries)
    err = single_case.Judge()
    if err is not None:
      return "Case #{} fails:\n{}".format(case_number, err)
  # Make sure nothing other than EOF is printed after all cases finish.
  try:
    response = raw_input()
  except EOFError:
    return None
  except Exception:  # pylint: disable=broad-except
    return "Exception raised while reading input after all cases finish."
  return "Additional input after all cases finish: {}".format(response[:1000])


def main():
  if int(sys.argv[1]) == -2:
    result = JudgeSingleCaseTest.Test()
  else:
    result = JudgeAllCases()
    if result is not None:
      print >> sys.stderr, result
      print _WRONG_ANSWER_MSG
      sys.stdout.flush()
      sys.exit(1)


if __name__ == "__main__":
  main()
