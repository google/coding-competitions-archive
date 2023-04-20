# Usage: `python testing_tool.py` (without the backticks)
# This can also be run as `python3 testing_tool.py`.
import random
import sys

# Use raw_input in Python2.
try:
  input = raw_input
except NameError:
  pass

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

def Won(vases):
  min_cnt = min(len(vase) for vase in vases)
  win_vases_idx = [i for i, vase in enumerate(vases)
                   if len(vase) == min_cnt]
  if len(win_vases_idx) > 1:
    print("failed case: vases {} all have {} tokens, so "
          "nobody wins.".format([v + 1 for v in win_vases_idx], min_cnt),
          file=sys.stderr)
    return False

  win_vase_idx = win_vases_idx[0]
  win_vase = vases[win_vase_idx]
  for p in win_vase:
    if win_vase.count(p) > 1:
      print("failed case: winning vase {} had more than "
            "one token for player {}.".format(win_vase_idx + 1, p),
            file=sys.stderr)
      return False

  if npeople not in win_vase:
    print("failed case: I don't have a token in the "
          "winning vase {}".format(win_vase_idx + 1),
          file=sys.stderr)
    return False
  return True

def FormatVase(v):
  return ' '.join(map(str,[len(v)]+sorted(v)))

class JudgeSingleCase:

  def __init__(self, case):
    self.choices = [random.randint(1, nvases) for _ in range(npeople-1)]
    self.vases = [[] for _ in range(nvases)]

  def Judge(self):
    """Judge one single case; should only be called once per test case.

    Returns:
      A bool indicating whether the player won.
      Also, an error string if an I/O rule was violated, otherwise None.
    """
    for i in range(1,npeople+1):
      # Print the current person.
      print(i)
      sys.stdout.flush()

      # Person i inserts their token, if that is not the player.
      if i <= npeople-1:
        self.vases[self.choices[i-1]-1].append(i)

      # Read and parse input.
      try:
        contestant_input = input()
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
        print(FormatVase(self.vases[vase-1]))
        sys.stdout.flush()

    return Won(self.vases), None

def JudgeAllCases():
  """Sends input to contestant and judges contestant output.

  Returns:
    An error string, or None if the attempt was correct.
  """
  print(total_num_cases)
  sys.stdout.flush()
  correct = 0
  for case_number in range(total_num_cases):
    sys.stdout.flush()
    single_case = JudgeSingleCase(case_number)
    won, err = single_case.Judge()
    if err is not None:
      print(_WRONG_ANSWER_MSG)
      sys.stdout.flush()
      return "Case #{} fails:\n{}".format(case_number+1, err)
    if won:
      correct = correct+1
  # Make sure nothing other than EOF is printed after all cases finish.
  try:
    response = input()
  except EOFError:
    print("Got {}/{}".format(correct, total_num_cases), file=sys.stderr)
    if correct < total_successes_required:
      return "Too few cases succeeded: {}/{}, need {}\n".format(
          correct, total_num_cases, total_successes_required)
    return None
  except Exception:
    return "Exception raised while reading input after all cases finish."
  return "Additional input after all cases finish: {}".format(response[:1000])

def main():
  # The real judge does not necessarily implement randomness in the same way.
  random.seed(2)
  result = JudgeAllCases()
  if result is not None:
    print(result, file=sys.stderr)
    sys.exit(1)

if __name__ == "__main__":
  main()
