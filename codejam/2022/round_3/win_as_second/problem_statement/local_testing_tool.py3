# "Win As Second" local testing tool.
#
# Usage: `python3 testing_tool.py test_number`, where the argument test_number
# is 0 (Test Set 1) or 1 (Test Set 2).

import random
import sys


MIN_N = [30, 31]
MAX_N = [30, 40]
M = 50


class Error(Exception):
  pass


WRONG_NUM_TOKENS_ERROR = (
    "Wrong number of tokens: expected {}, found {}.".format)
NOT_INTEGER_ERROR = "Not an integer: {}.".format
OUT_OF_BOUNDS_ERROR = "Request out of bounds: {}.".format
INVALID_LINE_ERROR = "Couldn't read a valid line."
ADDITIONAL_INPUT_ERROR = "Additional input after all cases finish: {}.".format
CYCLE_ERROR = "The chosen edges form a cycle after edge {}-{}".format
UELI_WON_ERROR = "Ueli won"
ALREADY_RED_ERROR = "Trying to color vertex {} that is already red".format
NOT_NEIGHBOR_ERROR = (
    "Trying to color vertex {} that is not a neighbor of vertex {}"
    " that was colored first".format)


def ReadValues(line):
  t = line.split()
  return t


def ConvertToInt(token, min, max):
    try:
      v = int(token)
    except:
      raise Error(NOT_INTEGER_ERROR(token[:100]))
    if v < min or v > max:
      raise Error(OUT_OF_BOUNDS_ERROR(v))
    return v


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


def ReadKInts(k, min, max):
  try:
    line = Input()
  except EOFError:
    raise Error(INVALID_LINE_ERROR)
  tokens = ReadValues(line)
  if len(tokens) != k:
    raise Error(WRONG_NUM_TOKENS_ERROR(k, len(tokens)))
  values = [ConvertToInt(token, min, max) for token in tokens]
  return values


def CanWinInOneMove(adj, alive):
  n = len(alive)
  alive_count = alive.count(True)
  for main in range(n):
    if alive[main]:
      got = 1
      for other in adj[main]:
        if alive[other]:
          got += 1
      if got == alive_count:
        return True
  return False


def GetRandomMove(adj, alive):
  n = len(alive)
  main = random.choice([i for i in range(n) if alive[i]])
  res = [main]
  for other in adj[main]:
    if alive[other] and random.choice([False, True]):
      res.append(other)
  return res


def RunCases(min_n, max_n):
  Output(f"{max_n - min_n + 1}")
  for n in range(min_n, max_n + 1):
    Output(f"{n}")

    component = list(range(n))
    adj = [[] for _ in range(n)]
    for _ in range(n - 1):
      p, q = ReadKInts(2, 1, n)
      p -= 1
      q -= 1
      cp = component[p]
      cq = component[q]
      if cp == cq:
        raise Error(CYCLE_ERROR(p + 1, q + 1))
      for i in range(n):
        if component[i] == cp:
          component[i] = cq
      adj[p].append(q)
      adj[q].append(p)

    Output(f"{M}")
    for _ in range(M):
      alive = [True] * n
      while any(x for x in alive):
        if CanWinInOneMove(adj, alive):
          raise Error(UELI_WON_ERROR)
        us = GetRandomMove(adj, alive)
        for x in us:
          assert alive[x]
          alive[x] = False
        Output(f"{len(us)}")
        Output(" ".join([f"{x + 1}" for x in us]))
        (k,) = ReadKInts(1, 1, n)
        them = ReadKInts(k, 1, n)
        them = [x - 1 for x in them]
        for x in them:
          if not alive[x]:
            raise Error(ALREADY_RED_ERROR(x + 1))
          alive[x] = False
          if x != them[0]:
            if not any(x == y for y in adj[them[0]]):
              raise Error(NOT_NEIGHBOR_ERROR(x + 1, them[0] + 1))

  try:
    extra_input = Input()
    raise Error(ADDITIONAL_INPUT_ERROR(extra_input[:100]))
  except EOFError:
    pass


def main():
  if len(sys.argv) == 2:
    dataset_index = int(sys.argv[1])
    if dataset_index == -2:
      sys.exit(0)
    file_mode = False
  elif len(sys.argv) == 3:
    # Note: this mode is used if you submit the local testing tool as the
    # judge in the "Test run" mode.
    file_mode = True
    dataset_index = int(sys.argv[1])
    error_file = open(sys.argv[2], 'w')
  else:
    assert False, 'Please pass a single test_number argument'

  min_n = MIN_N[dataset_index]
  max_n = MAX_N[dataset_index]
  random.seed(12345)
  try:
    RunCases(min_n, max_n)
  except Error as error:
    print(error, file=sys.stderr)
    Output("-1")
    if file_mode:
      print("status: INVALID", file=error_file)
      print("status_message: 'unused'", file=error_file)
      error_file.close()
      sys.exit(0)
    else:
      sys.exit(1)

  if file_mode:
    print("status: VALID", file=error_file)
    error_file.close()


if __name__ == "__main__":
  main()
