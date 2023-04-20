"""judge.py for the Self-Naming Network interactive judge.
"""

# Usage: `judge.py test_number`, where the argument test_number is either 0
# (small), 1 (large) or -2 (test mode).

import random
import sys


def ReadNLines(n):
  try:
    return [raw_input() for _ in xrange(n)]
  except:
    return "There weren't {} lines to read".format(n)


def ReadIntList(n, l, u, line):
  t = line.split()
  if len(t) != n:
    return "Wrong number of tokens: {}. Expected {}.".format(len(t), n)
  try:
    xs = map(int, t)
  except:
    return "A token in {} is not an integer.".format(t)
  for x in xs:
    if x < l or x > u:
      return "Integer {} is not in range [{}-{}].".format(x, l, u)
  return xs


def TestReadIntList():
  assert ReadIntList(3, 1, 3, "1 2 3") == [1, 2, 3]
  assert ReadIntList(3, -1, 3, "-1 2 1") == [-1, 2, 1]
  assert ReadIntList(1, 1, 3, "1") == [1]
  assert ReadIntList(3, 1, 3, "1 2") == "Wrong number of tokens: 2. Expected 3."
  assert ReadIntList(3, 1, 3, "") == "Wrong number of tokens: 0. Expected 3."
  assert ReadIntList(3, 1, 3, " 1 2 3") == [1, 2, 3]
  assert ReadIntList(3, 1, 3, "1 2 3 ") == [1, 2, 3]
  assert ReadIntList(3, 1, 3, "1 2  3") == [1, 2, 3]
  assert ReadIntList(3, 1, 3, "1 2 x") == (
      "A token in ['1', '2', 'x'] is not an integer.")
  assert ReadIntList(3, 1, 3, "1 x 3") == (
      "A token in ['1', 'x', '3'] is not an integer.")
  assert ReadIntList(3, 1, 3, "x 2 3") == (
      "A token in ['x', '2', '3'] is not an integer.")
  assert ReadIntList(3, 1, 3, "\t 2 3") == (
      "Wrong number of tokens: 2. Expected 3.")
  assert ReadIntList(3, 1, 3, "1 10 2") == (
      "Integer 10 is not in range [1-3].")
  assert ReadIntList(3, 2, 3, "1 2 3") == (
      "Integer 1 is not in range [2-3].")
  assert ReadIntList(3, -1, 3, "1 2 -2") == (
      "Integer -2 is not in range [-1-3].")


def ReadN(l, u, line):
  t = ReadIntList(1, l, u, line)
  if isinstance(t, str):
    return t
  return t[0]


def TestReadN():
  assert ReadN(10, 12, "10") == 10
  assert ReadN(10, 12, "11") == 11
  assert ReadN(10, 12, "12") == 12
  assert ReadN(10, 12, "11 ") == 11
  assert ReadN(10, 12, " 11") == 11
  assert isinstance(ReadN(10, 12, "1 1"), str)
  assert isinstance(ReadN(10, 12, "a11"), str)
  assert isinstance(ReadN(10, 12, "11a"), str)
  assert isinstance(ReadN(10, 12, "9"), str)
  assert isinstance(ReadN(10, 12, "13"), str)


def ReadGraph(lines):
  n = len(lines) / 2
  g = [set() for _ in xrange(n)]
  for l in lines:
    t = ReadIntList(2, 1, n, l)
    if isinstance(t, str):
      return t
    a, b = t
    if a == b:
      return "Node {} has a self-loop.".format(a)
    g[a - 1].add(b - 1)
    g[b - 1].add(a - 1)
  for i in xrange(n):
    if len(g[i]) != 4:
      return "Node {} has degree {} instead of 4.".format(i+1, len(g[i]))
  return g


def TestReadGraph():
  assert ReadGraph(["1 2", "1 3", "1 4", "1 5", "2 3", "2 4", "2 5", "3 4",
                    "3 5", "4 5"]) == [set([1,2,3,4]), set([0,2,3,4]),
                                       set([0,1,3,4]), set([0,1,2,4]),
                                       set([0,1,2,3])]
  assert ReadGraph(["1 2", "3 1", "5 4", "1 5", "2 4", "3 2", "2 5", "3 5",
                    "4 3", "4 1"]) == [set([1,2,3,4]), set([0,2,3,4]),
                                       set([0,1,3,4]), set([0,1,2,4]),
                                       set([0,1,2,3])]
  assert ReadGraph(["1 2", "1 3", "1 4", "1 5", "2 3", "2 4", "2 5", "3 4",
                    "3 5", "4 1"]) == "Node 4 has degree 3 instead of 4."
  assert ReadGraph(["1 2", "1 3", "1 4", "1 5", "2 3", "2 4", "2 5", "3 1",
                    "3 2", "4 5"]) == "Node 3 has degree 2 instead of 4."
  assert ReadGraph(["1 2", "1 3", "1 4", "1 5", "2 3", "2 4", "2 5", "3 3",
                    "3 5", "4 5"]) == "Node 3 has a self-loop."
  assert isinstance(ReadGraph(["1 2", "1 3", "1 4", "1 5", "2 3", "2 4", "2 5",
                               "3 3", "3 5", "4 10"]), str)
  assert isinstance(ReadGraph(["1 2", "1 3", "1 4", "1 5", "2 3", "2 4", "2 5",
                               "3 3", "3 5", "x 5"]), str)
  assert isinstance(ReadGraph(["1 2", "1 3", "1 4", "1 5", "2 3", "2 4", "2 5",
                               "3 3", "35", "4 5"]), str)
  assert ReadGraph(["1 2", "1 2", "1 2", "1 2", "3 4", "3 4", "3 4", "3 4",
                    "5 6", "5 6", "5 6", "5 6"]) == (
      "Node 1 has degree 1 instead of 4.")
  assert ReadGraph(["1 1", "1 1", "2 2", "2 2", "3 3", "3 3", "4 4", "4 4",
                    "5 5", "5 5", "6 6", "6 6"]) == (
      "Node 1 has a self-loop.")


def IsConnected(g):
  n = len(g)
  c = range(n)
  for i in xrange(n):
    for j in g[i]:
      if c[i] != c[j]:
        oi = c[i]
        for k in xrange(n):
          if c[k] == oi:
            c[k] = c[j]
  return len(set(c)) == 1


def TestIsConnected():
  assert IsConnected([set()]) == True
  assert IsConnected([set([1]), set([0]), set()]) == False
  assert IsConnected([set([1, 2]), set([0]), set([0])]) == True
  assert IsConnected([set([1, 2, 3]), set([0, 3]), set([0]),
                      set([0, 1])]) == True
  assert IsConnected([set([2]), set([3]), set([0]), set([1])]) == False
  assert IsConnected([set([2, 3]), set([3]), set([0]), set([0, 1])]) == True


def ReadPermutation(n, line):
  p = ReadIntList(n, 1, n, line)
  if isinstance(p, str):
    return p
  if len(set(p)) != n:
    return "Repeated integers in {}.".format(p)
  return [x - 1 for x in p]


def TestReadPermutation():
  assert ReadPermutation(3, "1 2 3") == [0, 1, 2]
  assert ReadPermutation(4, "4 2 1 3") == [3, 1, 0, 2]
  assert ReadPermutation(1, "1") == [0]
  assert ReadPermutation(3, "1 2 1") == "Repeated integers in [1, 2, 1]."
  assert isinstance(ReadPermutation(3, "1 2"), str)
  assert isinstance(ReadPermutation(3, "1 x 2"), str)
  assert isinstance(ReadPermutation(3, "1 0 2"), str)
  assert isinstance(ReadPermutation(3, "1 2 13"), str)


def ApplyPermutation(p, g):
  n = len(g)
  h = [set() for _ in xrange(n)]
  for i in xrange(n):
    for j in g[i]:
      h[p[i]].add(p[j])
  return h


def TestApplyPermutation():
  g1 = [set([1]), set([0]), set()]
  g2 = [set([1, 2]), set([0]), set([0])]
  g3 = [set([1, 2, 3]), set([0, 3]), set([0]), set([0, 1])]
  for g in g1, g2, g3:
    assert ApplyPermutation(range(len(g)), g) == g
  p = [1, 0, 2]
  assert ApplyPermutation(p, g1) == g1
  assert ApplyPermutation(p, g2) == [set([1]), set([0, 2]), set([1])]
  p = [1, 2, 0]
  assert ApplyPermutation(p, g1) == [set(), set([2]), set([1])]
  assert ApplyPermutation(p, g2) == [set([1]), set([0, 2]), set([1])]
  p = [1, 3, 2, 0]
  assert ApplyPermutation(p, g3) == [set([1, 3]), set([0, 2, 3]), set([1]),
                                     set([0, 1])]


def RandomPermutation(n):
  p = range(n)
  random.shuffle(p)
  # To make this different from the randomization method used publicly in the
  # local testing tool, do some swaps. This does not break our "uniformly at
  # random" guarantee.
  for _ in xrange(10):
    i1, i2 = random.sample(xrange(n), 2)
    p[i1], p[i2] = p[i2], p[i1]
  return p


def RunCase(l, u):
  print l, u
  sys.stdout.flush()
  lines = ReadNLines(1)
  if isinstance(lines, str):
    return lines
  n = ReadN(l, u, lines[0])
  if isinstance(n, str):
    return n
  lines = ReadNLines(2 * n)
  if isinstance(lines, str):
    return lines
  g = ReadGraph(lines)
  if isinstance(g, str):
    return g
  if not IsConnected(g):
    return "Graph not connected"
  p = RandomPermutation(n)
  h = ApplyPermutation(p, g)
  print n
  for i in xrange(n):
    for j in sorted(list(h[i])):
      if i < j:
        print i + 1, j + 1
  sys.stdout.flush()
  lines = ReadNLines(1)
  if isinstance(lines, str):
    return lines
  q = ReadPermutation(n, lines[0])
  if isinstance(q, str):
    return q
  if p != q:
    return "Received permutation {} != expected {}".format(q, p)


def RunCases(cases):
  for i, (l, u) in enumerate(cases, 1):
    result = RunCase(l, u)
    if result:
      return "Case #{} failed: {}".format(i, result)
  try:
    extra_input = raw_input()
  except EOFError:
    return None
  except Exception:  # pylint: disable=broad-except
    return "Exception raised while reading input after all cases finish."
  return "Additional input after all cases finish: {}".format(extra_input[:100])


def Test():
  TestReadIntList()
  TestReadN()
  TestReadGraph()
  TestIsConnected()
  TestReadPermutation()
  TestApplyPermutation()


def main():
  random.seed(31415)
  assert len(sys.argv) == 2
  index = int(sys.argv[1])
  if index == -2:
    Test()
  else:
    cases = ([(10, 50)] * 30, [(x, x) for x in [10, 11, 16, 25] * 2 +
                                                range(29, 51, 1)])[index]
    assert len(cases) == 30
    random.shuffle(cases)
    print 30
    result = RunCases(cases)
    if result:
      print >> sys.stderr, result
      sys.stdout.flush()
      sys.exit(1)


if __name__ == "__main__":
  main()
