# Usage: `python3 testing_tool.py <index>` where <index> is 0, 1, or 2.

import sys
import collections
import itertools
import random
import math


# This tool is a lot slower than the real judge. Trying 2000 cases can take
# a long time with this tool.
NUM_CASES = 100
N = 50
NEED_CORRECT = (60, 78, 86)


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
SAME_TREE_TWICE_ERROR = "Using the same tree twice"
TOO_FEW_CORRECT_ERROR = "Too few correct answers: {}.".format

INVALID_OUTPUT = -1
INF = 10**5

def ReadValues(line, num_tokens, n):
  t = line.split()
  if len(t) != num_tokens:
    raise Error(WRONG_NUM_TOKENS_ERROR(num_tokens, len(t)))
  r = []
  for s in t:
    try:
      v = int(s)
    except:
      raise Error(NOT_INTEGER_ERROR(s[:100]))
    if v < 1 or v > 2 * n:
      raise Error(OUT_OF_BOUNDS_ERROR(v))
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

def Play(score_matrix, north_tree, south_tree, n):
  for i in range(2 * n):
    for j in range(2 * n):
      if i == north_tree or j == south_tree:
        score_matrix[i][j] = -INF
      elif (i < north_tree and j > south_tree) or (i > north_tree and j < south_tree):
        score_matrix[i][j] += 1

def RunCases(num_cases, n, need_correct):
  Output("{} {} {}".format(num_cases, n, need_correct))

  correct = 0
  for _ in range(num_cases):

    contestant_score, judge_score = 0, 0
    score_matrix = [[0 for _ in range(2 * n)] for _ in range(2 * n)]
    for _ in range(n):
      try:
        move = ReadValues(Input(), 2, n)
      except EOFError:
        raise Error(INVALID_LINE_ERROR)
      except Error as error:
          raise error

      north_tree, south_tree = move[0], move[1]
      north_tree -= 1
      south_tree -= 1

      if score_matrix[north_tree][south_tree] < 0:
        raise Error(SAME_TREE_TWICE_ERROR)

      contestant_score += score_matrix[north_tree][south_tree]

      Play(score_matrix, north_tree, south_tree, n)

      best_score = max(map(max, score_matrix))

      judge_score += best_score
      best_moves = [(north, south)
                    for north in range(2 * n)
                    for south in range(2 * n)
                    if score_matrix[north][south] == best_score]
      # It is not guaranteed that the judge uses the same method of picking
      # random move.
      north_tree, south_tree = random.choice(best_moves)

      Play(score_matrix, north_tree, south_tree, n)
      Output("{} {}".format(north_tree + 1, south_tree + 1))

    Output("{}".format(int(contestant_score > judge_score)))

    if contestant_score > judge_score:
      correct += 1

  try:
    extra_input = Input()
    raise Error(ADDITIONAL_INPUT_ERROR(extra_input[:100]))
  except EOFError:
    pass

  perc = 100.0 * correct / num_cases
  print(f"User got {correct} wins out of {num_cases} games ({perc}%).",
        file=sys.stderr)
  if correct < need_correct:
    raise WrongAnswer(TOO_FEW_CORRECT_ERROR(correct))


def main():
  assert len(sys.argv) == 2
  index = int(sys.argv[1])
  assert index in (0, 1, 2)
  num_cases = NUM_CASES
  n = N
  need_correct = NEED_CORRECT[index]
  random.seed(234234)  # Seed is fixed here, but not in the real judge.
  print("This is running with random seed = 234234. This will not change "
        "automatically on each run like in the real judge.",
        file=sys.stderr)
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
