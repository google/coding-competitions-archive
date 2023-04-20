"""judge.py for DatBae interactive judge.
"""

# Usage: `judge.py test_number`, where the argument test_number is either 0
# (small), 1 (large) or -2 (test mode).

import random
import sys
import re

_ERROR_MSG_EXTRA_NEW_LINES = "Input has extra newline characters."
_ERROR_MSG_INCORRECT_ARG_NUM = "Answer has wrong number of tokens."
_ERROR_MSG_NOT_SORTED = "Worker IDs in answer must be sorted."
_ERROR_MSG_NOT_UNIQUE = "Worker IDs in answer must be distinct."
_ERROR_MSG_INVALID_TOKEN = "Input has invalid token."
_ERROR_MSG_OUT_OF_RANGE = "Input includes an out-of-range value."
_ERROR_MSG_READ_FAILURE = "Read for input fails."

_QUERY_LIMIT_EXCEEDED_MSG = "Query Limit Exceeded."
_WRONG_ANSWER_MSG = "Wrong Answer."

_ERROR_MSG_INTERNAL_FAILURE = ("The judge failed due to an internal error. "
                               "This should not happen, please raise an issue "
                               "to the Code Jam team.")


class Case:

  def __init__(self, bad_set, N, F, input=raw_input):
    self.__bad_set = set(bad_set) # The set of broken computers
    self.__N = N # The total number of computers
    self.__max_num_tries = F # The number of allowed guesses
    self.__raw_input = input

  def _parse_contestant_query(self, bitstring):
    """Tries to parse a contestant's input as if it were a query bitstring.

    Returns:
      (string, string): The first argument is the bitstring, the second is
      the error string in case of error.
      If the parsing succeeds, the return value should be (str, None).
      If the parsing fails, the return value should be (None, str).
    """
    # Must be of length exactly N
    if len(bitstring) != self.__N:
      return (None, _ERROR_MSG_INVALID_TOKEN)
    # Bitstring must contain only 0 and 1
    if not all([x in '01' for x in bitstring]):
      return (None, _ERROR_MSG_INVALID_TOKEN)
    return (bitstring, None)

  def _parse_contestant_answer(self, tokens):
    """Tries to parse a contestant's input as if it were answering a testcase.

    Returns:
      (list string): The first argument is the answer, the second is
      the error string in case of error.
      If the parsing succeeds, the return value should be (list, None).
      If the parsing fails, the return value should be (None, str).
    """
    if len(tokens) != len(self.__bad_set):
      return (None, _ERROR_MSG_INCORRECT_ARG_NUM)
    try:
      contestant_answer = map(int, tokens)
    except Exception:
      return (None, _ERROR_MSG_INVALID_TOKEN)

    if sorted(contestant_answer) != contestant_answer:
      return (None, _ERROR_MSG_NOT_SORTED)

    if len(set(contestant_answer)) != len(contestant_answer):
      return (None, _ERROR_MSG_NOT_UNIQUE)

    for x in contestant_answer:
      if (x < 0) or (x >= self.__N):
        return (None, _ERROR_MSG_OUT_OF_RANGE)

    return (contestant_answer, None)


  def _parse_contestant_input(self, response):
    """Parses contestant's input.

    Parse contestant's input which should be either a string of N bits or
    a list of len(bad_set) space-separated integers.

    Args:
      response: (str or list) one-line of input given by the contestant.

    Returns:
      (int or list, string): The bitstring sent by the contestant if making
      a query, or a list of ints if the contestant is answering the test case.
      the second argument is an error string in case of error.
      If the parsing succeeds, the return value should be (int or list, None).
      If the parsing fails, the return value should be (None, str).
    """
    if ("\n" in response) or ("\r" in response):
      return None, _ERROR_MSG_EXTRA_NEW_LINES
    if not re.match("^[\s0-9-]+$", response):
      return None, _ERROR_MSG_INVALID_TOKEN
    tokens = response.split()
    if len(tokens) == 1 and len(tokens[0]) == self.__N:
      # If there is exactly one token and it has length N, it must be a query.
      # A number with N digits has to be at least 10**N which is always > N,
      # so there is no way for a valid answer to be mistaken as a query.
      return self._parse_contestant_query(tokens[0])
    else:
      # It's not a query, so it must parse as an answer.
      return self._parse_contestant_answer(tokens)

  def _answer_query(self, bitstring):
    answer = ""
    for i in xrange(self.__N):
      if i not in self.__bad_set:
        answer += bitstring[i]
    return answer

  def Judge(self):
    """Judge one single case; should only be called once per test case.

    Returns:
      An error string, or None if the attempt was correct.
    """
    print self.__N, len(self.__bad_set), self.__max_num_tries
    sys.stdout.flush()
    # +1 for the answer they have to give
    for queries in xrange(self.__max_num_tries + 1):
      try:
        contestant_input = self.__raw_input()
      except Exception:
        return _ERROR_MSG_READ_FAILURE
      contestant_input, err = self._parse_contestant_input(contestant_input)
      if err is not None:
        return err
      if type(contestant_input) is str:
        # Query
        if queries == self.__max_num_tries:
          # Too many queries
          return _QUERY_LIMIT_EXCEEDED_MSG
        else:
          print self._answer_query(contestant_input)
          sys.stdout.flush()
      else:
        # Answer
        assert(type(contestant_input) is list)
        if set(contestant_input) == self.__bad_set:
          # Testcase answered correctly
          print 1
          sys.stdout.flush()
          return None
        else:
          return _WRONG_ANSWER_MSG
    return _QUERY_LIMIT_EXCEEDED_MSG

def getTestCases(test_number):
  # Trigger an assertion failure for testing purposes
  if test_number == 1234:
    assert False

  MIN_N = 2
  MAX_N = 1024
  MAX_B = 15
  F = (10, 5)[test_number]

  cases = []
  def C(bad_list, N):
    assert(MIN_N <= N <= MAX_N)
    assert(1 <= len(bad_list) <= MAX_B)
    assert(F == (10, 5)[test_number])
    assert(0 <= min(bad_list) and max(bad_list) < N)
    assert(len(set(bad_list)) == len(bad_list))
    cases.append(Case(sorted(bad_list), N, F))

  def randCase(B, N):
    C(random.sample(range(0, N), B), N)

  def offset(B, N, start, jump=1):
    C([start + i*jump for i in xrange(B)], N)

  # Some simple small cases
  C([1, 2, 3, 4], 5)
  C([0, 1, 2, 3], 5)
  C([0], 5)
  C([0, 4], 5)
  C([0, 2, 4], 5)

  # Min cases
  C([0], 2)
  C([1], 2)

  # Lots of broken computers
  C(range(0, MAX_B), MAX_B+1)
  C(range(1, MAX_B+1), MAX_B+1)
  C(range(0, MAX_B/2) + range(MAX_B/2+1, MAX_B), MAX_B+1)

  # Few broken computers
  C([6], 12)
  C([3], 5)
  C([MAX_N-1], MAX_N)
  C([0], MAX_N)


  # Some random cases with one broken computer
  randCase(1, MAX_N)
  randCase(1, int(MAX_N*0.95))
  for _ in xrange(5):
    randCase(1, random.randint(2, MAX_N))

  # Some random cases with lots of broken computers
  randCase(MAX_B, MAX_N)
  randCase(MAX_B, int(MAX_B*1.4))
  randCase(MAX_B, int(MAX_B*2))
  for _ in xrange(5):
    B = random.randint(2, MAX_B)
    randCase(B, random.randint(B+1, MAX_N))

  # Offset cases
  offset(MAX_B, MAX_N, 0,  1)
  offset(MAX_B, MAX_N, MAX_N-MAX_B,  1)
  offset(MAX_B, MAX_N, 12, 12)
  offset(6, MAX_N, 800)
  offset(10, MAX_N, 101)
  for x in [1, 5, 31, 32, 33, 400]:
    offset(MAX_B, MAX_N, x, MAX_B-1)
    offset(MAX_B, MAX_N, x, MAX_B)
    offset(MAX_B, MAX_N, x, MAX_B+1)
    offset(MAX_B, MAX_N, x, MAX_B*2)
  for _ in xrange(5):
    offset(MAX_B, MAX_N, random.randint(0, 200), random.randint(1, 50))
  for _ in xrange(20):
    offset(MAX_B, MAX_N, random.randint(0, MAX_N-MAX_B))

  # Fill the remaining with random max cases
  while(len(cases) < 100):
    randCase(MAX_B, MAX_N)

  assert len(cases) <= 100
  return cases


def JudgeAllCases(test_number):
  """Sends input to contestant and judges contestant output.

  In the case of any error (other than extra input after all testcases are
  finished), -1 is printed to stdout.

  Returns:
    An error string, or None if the attempt was correct.
  """
  try:
    cases = getTestCases(test_number)
  except Exception:
    return _ERROR_MSG_INTERNAL_FAILURE

  print len(cases)
  sys.stdout.flush()
  for idx, case in enumerate(cases):
    err = case.Judge()
    if err is not None:
      print -1
      sys.stdout.flush()
      return "Case #{} fails:\n{}".format(idx+1, err)

  # Make sure nothing other than EOF is printed after all cases finish.
  try:
    response = raw_input()
  except EOFError:
    return None
  except Exception:  # pylint: disable=broad-except
    return "Exception raised while reading input after all cases finish."
  return "Additional input after all cases finish: {}".format(response[:1000])


def runUnitTests():
  print "Running unit tests"
  # Test _parse_contestant_query
  c = Case([], 5, None)
  assert c._parse_contestant_query("11111") == ("11111", None)
  assert c._parse_contestant_query("00000") == ("00000", None)
  assert c._parse_contestant_query("01010") == ("01010", None)

  assert c._parse_contestant_query("111") == (None, _ERROR_MSG_INVALID_TOKEN)
  assert c._parse_contestant_query("000000") == (None, _ERROR_MSG_INVALID_TOKEN)
  assert c._parse_contestant_query("1111A") == (None, _ERROR_MSG_INVALID_TOKEN)

  # Test _parse_contestant_answer
  c = Case([1, 3], 5, None)
  assert c._parse_contestant_answer(["1", "3"]) == ([1, 3], None)
  assert c._parse_contestant_answer(["0", "4"]) == ([0, 4], None)
  assert c._parse_contestant_answer(["3", "3"]) ==\
      (None, _ERROR_MSG_NOT_UNIQUE)
  assert c._parse_contestant_answer(["-1", "1"]) ==\
      (None, _ERROR_MSG_OUT_OF_RANGE)
  assert c._parse_contestant_answer(["1", "5"]) ==\
      (None, _ERROR_MSG_OUT_OF_RANGE)
  assert c._parse_contestant_answer(["2", "0"]) ==\
      (None, _ERROR_MSG_NOT_SORTED)
  assert c._parse_contestant_answer(["3", "1"]) ==\
      (None, _ERROR_MSG_NOT_SORTED)
  assert c._parse_contestant_answer(["1"]) ==\
      (None, _ERROR_MSG_INCORRECT_ARG_NUM)
  assert c._parse_contestant_answer(["1", "2", "3"]) ==\
      (None, _ERROR_MSG_INCORRECT_ARG_NUM)
  assert c._parse_contestant_answer(["1", "ASDF"]) ==\
      (None, _ERROR_MSG_INVALID_TOKEN)
  c = Case([0], 2, None)
  assert c._parse_contestant_answer(["0"]) == ([0], None)
  assert c._parse_contestant_answer(["1"]) == ([1], None)

  # Test _parse_contestant_input
  c = Case([1, 3], 5, None)
  assert c._parse_contestant_input("1 3") == ([1, 3], None)
  assert c._parse_contestant_input("11010") == ("11010", None)
  assert c._parse_contestant_input("0 \t 1") == ([0, 1], None)
  c = Case([1], 2, None)
  assert c._parse_contestant_input("0") == ([0], None)
  assert c._parse_contestant_input("1") == ([1], None)
  assert c._parse_contestant_input("10") == ("10", None)
  assert c._parse_contestant_input("11") == ("11", None)
  assert c._parse_contestant_input("01") == ("01", None)

  assert c._parse_contestant_input("13") ==\
      (None, _ERROR_MSG_INVALID_TOKEN)


  case = Case([1, 3], 5, None)
  for contestant_input in ["\r2", "2\r", "\n 2 ", "3 \n\n"]:
    assert case._parse_contestant_input(contestant_input)[
        1] == _ERROR_MSG_EXTRA_NEW_LINES
  for contestant_input in ["abcd", "!?!?", "a", "1, 2", "2.0", "2.4"]:
    assert case._parse_contestant_input(contestant_input)[
        1] == _ERROR_MSG_INVALID_TOKEN
  for contestant_input in\
      ["\t\t 0 1", "  0  1 ", "\t0\t 1", "  \t0   1  ", "0 1\t  ", "0 1"]:
    assert case._parse_contestant_input(contestant_input) == ([0, 1], None)

  class FakeInput():
    def __init__(self, lines):
      self.__lines = lines
      self.__idx = 0

    def next_line(self):
      s = self.__lines[self.__idx]
      self.__idx += 1
      return s

  # Correct answer with varying number of queries
  assert Case([1, 3], 5, 5, FakeInput([
      "1 3"
  ]).next_line).Judge() == None
  assert Case([1, 3], 5, 5, FakeInput([
      "00111",
      "11001",
      "10101",
      "1 3"
  ]).next_line).Judge() == None
  assert Case([1, 3], 5, 5, FakeInput([
      "00111",
      "00111",
      "00111",
      "00111",
      "00111",
      "1 3"
  ]).next_line).Judge() == None

  # Incorrect answers for various reasons
  assert Case([1, 3], 5, 5, FakeInput([
      "-1 0"
  ]).next_line).Judge() == _ERROR_MSG_OUT_OF_RANGE
  assert Case([1, 3], 5, 5, FakeInput([
      "1 1"
  ]).next_line).Judge() == _ERROR_MSG_NOT_UNIQUE
  assert Case([1, 3], 5, 5, FakeInput([
      "3 1"
  ]).next_line).Judge() == _ERROR_MSG_NOT_SORTED
  assert Case([1, 3], 5, 5, FakeInput([
      "1 2 3"
  ]).next_line).Judge() == _ERROR_MSG_INCORRECT_ARG_NUM

  # Too many queries
  assert Case([1, 3], 5, 5, FakeInput([
      "01100",
      "01100",
      "01100",
      "01100",
      "01100",
      "01100",
      "1 3"
  ]).next_line).Judge() == _QUERY_LIMIT_EXCEEDED_MSG

  # Ensure the judge fails gracefully in the event of a failure in generating
  # test data
  assert JudgeAllCases(1234) == _ERROR_MSG_INTERNAL_FAILURE


def main():
  random.seed(821397)
  if int(sys.argv[1]) == -2:
    runUnitTests()
  else:
    test_number = int(sys.argv[1])
    result = JudgeAllCases(test_number)
    if result is not None:
      print >> sys.stderr, result
      sys.exit(1)


if __name__ == "__main__":
  main()
