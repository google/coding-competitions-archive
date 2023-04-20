"""War of the Words interactive judge.
"""

# Usage: `testing_tool.py test_number`, where the argument test_number
# is either 0 (first test set) or 1 (second test set)

import random
import sys

total_num_cases = 50

nrounds = 100
nwords = 100000

_ERROR_MSG_EXTRA_NEW_LINES = "Input has extra newline characters."
_ERROR_MSG_INCORRECT_WORD_LENGTH = "Input word is not of length 5."
_ERROR_MSG_INVALID_WORD = "Input has invalid character in word."
_ERROR_MSG_READ_FAILURE = "Read for input fails."

_WRONG_ANSWER_MSG = "-1"


def NumToWord(x):
  assert 0 <= x < nwords
  return ''.join(chr(ord('A') + int(c)) for c in '{:05d}'.format(x))


def WordToNum(s):
  assert len(s) == 5
  assert all('A' <= c <= 'J' for c in s)
  return int(''.join(str(ord(c) - ord('A')) for c in s))


class IO(object):

  def ReadInput(self):
    return raw_input()

  def PrintOutput(self, output):
    print output
    sys.stdout.flush()


class JudgeSingleCase(object):

  def __init__(self, io):
    self.io = io

    # rank[0] is the highest-ranked word.
    self.rank = range(nwords)
    random.shuffle(self.rank)

    self.rank_rev = [-1 for i in xrange(nwords)]
    for i in xrange(nwords):
      self.rank_rev[self.rank[i]] = i

  def _ParseContestantInput(self, response):
    """Parses contestant's input.

    Parses contestant's input, which should be a string of length 5 with only
    'A'~'J'.

    Args:
      response: (str) one-line input given by the contestant.

    Returns:
      str: the error string in case of error.
      If the parsing succeeds, the return value should be None.
    """
    if ("\n" in response) or ("\r" in response):
      return _ERROR_MSG_EXTRA_NEW_LINES

    if len(response) != 5:
      return _ERROR_MSG_INCORRECT_WORD_LENGTH

    if any(not ('A' <= c <= 'J') for c in response):
      return _ERROR_MSG_INVALID_WORD

    return None

  def _ReadContestantInput(self):
    """Reads contestant's input.

    Reads contestant's input, which should be a string of length 5 with only
    'A'~'J'.

    Returns:
      A string of the contestant's input.
      Also, an error string if input is invalid, otherwise None.
    """
    try:
      contestant_input = self.io.ReadInput()
    except Exception:
      return None, _ERROR_MSG_READ_FAILURE

    err = self._ParseContestantInput(contestant_input)
    if err is not None:
      return None, err

    return contestant_input, None

  def _CompareRanks(self, rank1, rank2):
    if rank1 < rank2 and not (rank1 == 0 and rank2 == nwords - 1):
      return True

    if rank1 == nwords - 1 and rank2 == 0:
      return True

    return False

  def _CompareWords(self, word1, word2):
    return self._CompareRanks(self.rank_rev[WordToNum(word1)],
                              self.rank_rev[WordToNum(word2)])

  def _GetBetterRankRange(self, rank):
    if rank == 0:
      return (nwords - 1, nwords)
    elif rank == nwords - 1:
      return (1, rank)
    else:
      return (0, rank)

  def Judge(self):
    """Judges one single case; should only be called once per test case.

    Returns:
      Number of points gotten.
      Also an error string if an I/O rule was violated, otherwise None.
    """
    points = 0

    word, err = self._ReadContestantInput()
    if err is not None:
      return None, err
    word_rank = self.rank_rev[WordToNum(word)]

    for i in xrange(nrounds):
      robot_rank = random.randrange(*self._GetBetterRankRange(word_rank))
      robot_word = self.rank[robot_rank]
      self.io.PrintOutput(NumToWord(robot_word))

      word, err = self._ReadContestantInput()
      if err is not None:
        return None, err

      word_rank = self.rank_rev[WordToNum(word)]
      round_points = int(self._CompareRanks(word_rank, robot_rank))
      points += round_points

    return points, None


def JudgeAllCases(test_number, io):
  """Sends input to contestant and judges contestant output.

  Returns:
    An error string, or None if the attempt was correct.
  """
  min_points = 25 if test_number == 0 else 50
  failed_cases = []

  io.PrintOutput('{} {}'.format(total_num_cases, min_points))
  for case_number in xrange(1, total_num_cases + 1):
    single_case = JudgeSingleCase(io)
    points, err = single_case.Judge()
    if err is not None:
      return 'Case #{} fails:\n{}'.format(case_number, err)
    if points < min_points:
      failed_cases.append(case_number)

  if failed_cases:
    return 'Cases {} failed with too few points.'.format(failed_cases)

  # Make sure nothing other than EOF is printed after all cases finish.
  try:
    response = io.ReadInput()
  except EOFError:
    return None
  except Exception:
    return 'Exception raised while reading input after all cases finish.'
  return 'Additional input after all cases finish: {}'.format(response[:1000])


def main():
  test_number = int(sys.argv[1])
  # We have provided one implementation of randomness here, but it is not
  # necessarily what will be used in the real judge.
  random.seed(2 + test_number)
  result = JudgeAllCases(test_number, IO())
  if result is not None:
    print >> sys.stderr, result
    print _WRONG_ANSWER_MSG
    sys.stdout.flush()
    sys.exit(1)

if __name__ == '__main__':
  main()
