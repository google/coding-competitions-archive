"""judge.py for the Lollipop Shop interactive judge.
"""

# Usage: `judge.py seed`, where the argument seeds the random number generator.

import random
import sys

total_num_cases = 50
maxn = 200

_ERROR_MSG_EXTRA_NEW_LINES = "Input has extra newline characters."
_ERROR_MSG_INCORRECT_ARG_NUM = "Input does not have exactly 1 token."
_ERROR_MSG_INVALID_TOKEN = "Input has invalid token."
_ERROR_MSG_OUT_OF_RANGE = "Input is out of range."
_ERROR_MSG_READ_FAILURE = "Read for input fails."

_WRONG_ANSWER_MSG = "-1"

class JudgeSingleCase:

  def __init__(self, case):
    self.flavor_probabilities = [0.005 + 0.095 * random.random() for _ in xrange(maxn)]
    self.prefs = [[flavor for flavor in xrange(maxn)
                   if random.random() < self.flavor_probabilities[flavor]]
                  for customer in xrange(maxn)]

  def rec(self, w):
    if self.used[w]:
      return False
    self.used[w] = True
    for x in self.prefs[w]:
      if self.mb[x]==-1 or self.rec(self.mb[x]):
        self.ma[w]=x
        self.mb[x]=w
        return True
    return False

  def match(self):
    self.ma = [-1]*maxn
    self.mb = [-1]*maxn
    ret = 0
    for i in xrange(maxn):
      w = -1
      for x in self.prefs[w]:
        if self.mb[x]==-1:
          if w == -1 or self.flavor_probabilities[x] < self.flavor_probabilities[w]:
            w = x
      if w != -1:
        self.ma[i] = w
        self.mb[w] = i
        ret = ret+1
    for i in xrange(maxn):
      if self.ma[i]==-1:
        self.used = [False]*maxn
        if self.rec(i):
          ret = ret+1
    return ret

  def _parse_contestant_input(self, response):
    """Parses contestant's input.

    Parse contestant's input which should be one integer, within [-1, maxn).

    Args:
      response: (str) one-line input given by the contestant.

    Returns:
      (int, string): the integer sent by the contestant, and the error
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
    try:
      guess = int(token)
    except Exception:
      return (self.__lo, _ERROR_MSG_INVALID_TOKEN)
    if (guess < -1) or (guess >= maxn):
      return (self.__lo, _ERROR_MSG_OUT_OF_RANGE)
    return (guess, None)

  def Judge(self):
    """Judge one single case; should only be called once per test case.

    Returns:
      An error string, or None if the attempt was correct.
    """
    opt = self.match()
    score = 0
    used = [False]*maxn
    for i in xrange(maxn):
      line = self.prefs[i]
      print ' '.join(map(str,[len(line)]+line))
      sys.stdout.flush()
      try:
        contestant_input = raw_input()
      except Exception:
        return False, _ERROR_MSG_READ_FAILURE
      guess, err = self._parse_contestant_input(contestant_input)
      if err is not None:
        return False, err
      if guess == -1:
        continue
      if used[guess]:
        return False, "Flavor already sold"
      used[guess] = True
      if guess not in line:
        return False, "Flavor disliked"
      score = score + 1
    return score >= opt-opt/10, None


def JudgeAllCases():
  """Sends input to contestant and judges contestant output.

  Returns:
    An error string, or None if the attempt was correct.
  """
  print total_num_cases
  sys.stdout.flush()
  correct = 0
  for case_number in xrange(total_num_cases):
    print maxn
    sys.stdout.flush()
    single_case = JudgeSingleCase(case_number)
    enough, err = single_case.Judge()
    if err is not None:
      return "Case #{} fails:\n{}".format(case_number+1, err)
    if enough:
      correct = correct+1
  # Make sure nothing other than EOF is printed after all cases finish.
  try:
    response = raw_input()
  except EOFError:
    print >> sys.stderr, "Got {}/{}".format(correct, total_num_cases)
    if correct < total_num_cases:
      return "Too few cases succeeded: {}/{}\n".format(correct, total_num_cases)
    return None
  except Exception:  # pylint: disable=broad-except
    return "Exception raised while reading input after all cases finish."
  return "Additional input after all cases finish: {}".format(response[:1000])


def main():
  if sys.argv[1] == "-2":
    print >> sys.stderr, "self-test not implemented"
  else:
    random.seed(126)
    result = JudgeAllCases()
    if result is not None:
      print >> sys.stderr, result
      print _WRONG_ANSWER_MSG
      sys.stdout.flush()
      sys.exit(1)


if __name__ == "__main__":
  main()
