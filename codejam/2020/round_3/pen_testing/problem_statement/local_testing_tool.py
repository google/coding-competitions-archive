# Usage: `python testing_tool.py test_number`, where the argument test_number
# is either 0 (first test set), 1 (second test set) or 2 (third test set).
# This can also be run as `python3 testing_tool.py test_number`.

import sys
import collections
import itertools
import random
import math

# Use raw_input in Python2.
try:
  input = raw_input
except NameError:
  pass

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


def Input():
  try:
    return input()
  except EOFError:
    raise
  except:
    raise Error(INVALID_LINE_ERROR)


def Output(line):
  try:
    print(line)
    sys.stdout.flush()
  except:
    try:
      sys.stdout.close()
    except:
      pass


def RunCases(num_cases, n, need_correct):
  Output("{} {} {}".format(num_cases, n, need_correct))

  remaining = [
      list(range(n))
      for _ in range(num_cases)]
  # It is not guaranteed that the judge uses the same method of random number
  # generation.
  for i in range(num_cases):
    random.shuffle(remaining[i])

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


def main():
  assert len(sys.argv) == 2
  index = int(sys.argv[1])
  num_cases = NUM_CASES[index]
  n = N
  need_correct = NEED_CORRECT[index]
  try:
    RunCases(num_cases, n, need_correct)
  except Error as error:
    Output(INVALID_OUTPUT)
    print(error, file=sys.stderr)
    sys.exit(1)
  except WrongAnswer as error:
    print(error, file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
  main()
