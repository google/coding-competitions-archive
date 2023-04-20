"""judge.py for the Pottery Lottery interactive judge.
"""

# Usage: `judge.py seed`, where the argument seeds the random number generator.

import random
import sys

total_num_cases = 250
total_successes_required = 225

npeople = 100
nvases = 20

_ERROR_MSG_EXTRA_NEW_LINES = "Input has extra newline characters."
_ERROR_MSG_INCORRECT_ARG_NUM = "Input does not have exactly 1 token."
_ERROR_MSG_INVALID_TOKEN = "Input has invalid token."
_ERROR_MSG_OUT_OF_RANGE = "Input is out of range."
_ERROR_MSG_READ_FAILURE = "Read for input fails."

_WRONG_ANSWER_MSG = "-1"

def ParseContestantInput(response, nvases, npeople):
  """Parses contestant's input.

  Parse contestant's input which should be two integers:
    A vase number within [1, nvases]
    A person number within [1, npeople], or 0 to look

  Args:
    response: (str) one-line input given by the contestant.

  Returns:
    (int, int, string): the two integers sent by the contestant, and the error
    string in case of error.
    If the parsing succeeds, the return value should be (int, int, None).
    If the parsing fails, the return value should be (None, None, str).
  """
  if ("\n" in response) or ("\r" in response):
    return (None, None, _ERROR_MSG_EXTRA_NEW_LINES)
  tokens = response.split()
  if len(tokens) != 2:
    return (None, None, _ERROR_MSG_INCORRECT_ARG_NUM)

  try:
    vase = int(tokens[0])
  except Exception:
    return (None, None, _ERROR_MSG_INVALID_TOKEN)

  try:
    person = int(tokens[1])
  except Exception:
    return (None, None, _ERROR_MSG_INVALID_TOKEN)

  if (vase < 1) or (vase > nvases) or (person < 0) or (person > npeople):
    return (None, None, _ERROR_MSG_OUT_OF_RANGE)
  return (vase, person, None)


def TestReadContestantInput():
  assert ParseContestantInput("", 5, 8) == (None, None, _ERROR_MSG_INCORRECT_ARG_NUM)
  assert ParseContestantInput(" ", 5, 8) == (None, None, _ERROR_MSG_INCORRECT_ARG_NUM)
  assert ParseContestantInput("1", 5, 8) == (None, None, _ERROR_MSG_INCORRECT_ARG_NUM)
  assert ParseContestantInput("1 2 3", 5, 8) == (None, None, _ERROR_MSG_INCORRECT_ARG_NUM)
  assert ParseContestantInput("3 y", 5, 8) == (None, None, _ERROR_MSG_INVALID_TOKEN)
  assert ParseContestantInput("x 6", 5, 8) == (None, None, _ERROR_MSG_INVALID_TOKEN)
  assert ParseContestantInput("3 6", 5, 8) == (3, 6, None)
  assert ParseContestantInput("3  6", 5, 8) == (3, 6, None)
  assert ParseContestantInput(" 3 6", 5, 8) == (3, 6, None)
  assert ParseContestantInput("3 6 ", 5, 8) == (3, 6, None)
  assert ParseContestantInput("5 8", 5, 8) == (5, 8, None)
  assert ParseContestantInput("3 0", 5, 8) == (3, 0, None)
  assert ParseContestantInput("0 6", 5, 8) == (None, None, _ERROR_MSG_OUT_OF_RANGE)
  assert ParseContestantInput("6 6", 5, 8) == (None, None, _ERROR_MSG_OUT_OF_RANGE)
  assert ParseContestantInput("3 -1", 5, 8) == (None, None, _ERROR_MSG_OUT_OF_RANGE)
  assert ParseContestantInput("3 9", 5, 8) == (None, None, _ERROR_MSG_OUT_OF_RANGE)

def Won(vases):
  min_cnt = min(len(vase) for vase in vases)
  win_vases_idx = [i for i, vase in enumerate(vases)
                   if len(vase) == min_cnt]
  if len(win_vases_idx) > 1:
    print >> sys.stderr, ("failed case: vases {} all have {} tokens, so " +
        "nobody wins.").format([v + 1 for v in win_vases_idx], min_cnt)
    return False

  win_vase_idx = win_vases_idx[0]
  win_vase = vases[win_vase_idx]
  for p in win_vase:
    if win_vase.count(p) > 1:
      print >> sys.stderr, ("failed case: winning vase {} had more than " +
          "one token for player {}.").format(win_vase_idx + 1, p)
      return False

  if npeople not in win_vase:
    print >> sys.stderr, ("failed case: I don't have a token in the " +
        "winning vase {}").format(win_vase_idx + 1)
    return False
  return True

def TestWon():
  assert Won([[1,2,3],[100]]) == True
  assert Won([[1,2],[3,100]]) == False
  assert Won([[1],[2,3,100]]) == False
  assert Won([[1,2,3,4],[5,5,100]]) == False
  assert Won([[1,2,3,4],[5,100,100]]) == False

def FormatVase(v):
  return ' '.join(map(str,[len(v)]+sorted(v)))

def TestFormatVase():
  assert FormatVase([]) == "0"
  assert FormatVase([100]) == "1 100"
  assert FormatVase([1,2]) == "2 1 2"
  assert FormatVase([3,4,2,1,5]) == "5 1 2 3 4 5"

class JudgeSingleCase:

  def __init__(self, case):
    self.choices = [random.randint(1, nvases) for _ in xrange(npeople-1)]
    random.shuffle(self.choices)  # Change randomization scheme for security.
    self.vases = [[] for _ in xrange(nvases)]

  def Judge(self):
    """Judge one single case; should only be called once per test case.

    Returns:
      A bool indicating whether the player won.
      Also, an error string if an I/O rule was violated, otherwise None.
    """
    for i in xrange(1,npeople+1):
      # Print the current person.
      print i
      sys.stdout.flush()

      # Person i inserts their token, if that is not the player.
      if i <= npeople-1:
        self.vases[self.choices[i-1]-1].append(i)

      # Read and parse input.
      try:
        contestant_input = raw_input()
      except Exception:
        return False, _ERROR_MSG_READ_FAILURE
      vase, person, err = ParseContestantInput(contestant_input, nvases, npeople)
      if err is not None:
        return False, err

      # Do player's move.
      if person > 0:
        # Inserting a forged token, or player's own token on the last day
        if i == npeople and person != npeople:
          return False, "The player must place their own token on the last day!"
        self.vases[vase-1].append(person)
        if i == npeople:
          self.choices.append(vase)
      else:
        # Examine a vase
        if i == npeople:
          return False, "The player can't examine a vase on the last day!"
        print FormatVase(self.vases[vase-1])
        sys.stdout.flush()

    return Won(self.vases), None


def JudgeAllCases():
  """Sends input to contestant and judges contestant output.

  Returns:
    An error string, or None if the attempt was correct.
  """
  print total_num_cases
  sys.stdout.flush()
  correct = 0
  for case_number in xrange(total_num_cases):
    sys.stdout.flush()
    single_case = JudgeSingleCase(case_number)
    won, err = single_case.Judge()
    if err is not None:
      print _WRONG_ANSWER_MSG
      sys.stdout.flush()
      return "Case #{} fails:\n{}".format(case_number+1, err)
    if won:
      correct = correct+1
  # Make sure nothing other than EOF is printed after all cases finish.
  try:
    response = raw_input()
  except EOFError:
    print >> sys.stderr, "Got {}/{}".format(correct, total_num_cases)
    if correct < total_successes_required:
      return "Too few cases succeeded: {}/{}, need {}\n".format(
          correct, total_num_cases, total_successes_required)
    return None
  except Exception:  # pylint: disable=broad-except
    return "Exception raised while reading input after all cases finish."
  return "Additional input after all cases finish: {}".format(response[:1000])

def Test():
  TestReadContestantInput()
  TestWon()
  TestFormatVase()

def main():
  if sys.argv[1] == "-2":
    Test()
  else:
    random.seed(412435 + int(sys.argv[1]))
    result = JudgeAllCases()
    if result is not None:
      print >> sys.stderr, result
      sys.exit(1)

if __name__ == "__main__":
  main()
