import random
import sys

def RandomPermutation(n):
  r = list(range(n))
  random.shuffle(r)
  return r

def WriteL(*args):
  print(*args, flush=True)

def ReadInt(min, max):
  while True:
    c = sys.stdin.read(1)
    if not c.isspace(): break
  s = str(c)
  while True:
    c = sys.stdin.read(1)
    if c.isspace():
      break
    s += c
  r = int(s)
  if r < min or r > max:
    raise ValueError
  return r

def ReadGraph(n, m):
  return [(ReadInt(1, n) - 1, ReadInt(1, n) - 1) for _ in range(m)]

def WriteGraph(g):
  for e in g:
    WriteL(e[0] + 1, e[1] + 1)

def NormalizedEdge(e):
  if e[0] < e[1]: return e[1], e[0]
  return e

def NormalizedGraph(g):
  for i in range(len(g)):
    g[i] = NormalizedEdge(g[i])
  return sorted(g)

def IsSimple(g):
  for e in g:
    if e[0] == e[1]: return False
  for i in range(len(g) - 1):
    if g[i] == g[i + 1]: return False
  return True

def PermutedGraph(g, p):
  return [(p[e[0]], p[e[1]]) for e in g]

MAX_C = 100000;

def RunCase(C, L):
  WriteL(C, L)
  g = NormalizedGraph(ReadGraph(C, L))


  perm = RandomPermutation(C)
  perm_g = NormalizedGraph(PermutedGraph(g, perm));
  WriteGraph(perm_g)

  path = [ReadInt(1, C) - 1 for _ in range(C)]

  if not IsSimple(g):
    print("Got non-simple graph.", file=sys.stderr)
    return False
  if len(set(path)) != C:
    print("Path is not a ring.", file=sys.stderr)
    return False
  perm_g_edges = set(perm_g)
  for i in range(C):
    e = NormalizedEdge((path[i], path[(i + 1) % C]))
    if e not in perm_g_edges:
      print("Path edge not in permuted graph.", file=sys.stderr)
      return False
  return True

def RunCases(cases):
  WriteL(len(cases))
  res = [RunCase(*case) for case in cases]
  return res.count(True)

cases = [(4, 5), (6, 10)]
correct = RunCases(cases)
print(f"Solved {correct} cases correctly out of {len(cases)} total.",
      file=sys.stderr)
sys.exit(correct < len(cases))
