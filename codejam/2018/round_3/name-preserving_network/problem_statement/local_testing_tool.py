""" Python script for local testing (compatible with both Python 2 and Python 3)

Disclaimer: this is a way to test your solutions, but it is NOT the real judging
system. The judging system behavior might be different.
"""
import random
import subprocess
import sys

USAGE_MSG = """
Usage:
Linux and Mac users:
  From your terminal, run
    python testing_tool.py command_to_run_your_script_or_executable
  Note that command_to_run_your_script_or_executable is read as a list of
  arguments, so you should NOT wrap it with quotation marks.

Examples:
C++, after compilation:
  python testing_tool.py ./my_binary
Python:
  python testing_tool.py python my_code.py
Java, after compilation:
  python testing_tool.py java my_main_class_name

See https://code.google.com/codejam/resources/faq#languages for how we compile
and run your solution in the language of your choice.

Windows users:
  Follow the instructions for Linux and Mac users if you are familiar with
  terminal tools on Windows. Otherwise, please be advised that this script might
  not work with Python 2 (it works with Python 3). In addition, if you cannot
  pass arguments to Python, you will need to modify the "cmd = sys.argv[1:]"
  line below.
"""

# CASES is a list of test cases, giving the values of L and U.
# Note that the [21, 21] case would not appear in test set 1.
CASES = [[10, 50], [10, 50], [21, 21]]
NUM_TEST_CASES = len(CASES)
# You can set PRINT_INTERACTION_HISTORY to True to print out the interaction
# history between your code and the judge.
PRINT_INTERACTION_HISTORY = True


"""Helper functions"""
def JudgePrint(p, s):
  # Print the judge output to your code's input stream. Log this interaction
  # to console (stdout) if PRINT_INTERACTION_HISTORY is True.
  print(s, file=p.stdin)
  p.stdin.flush()
  if PRINT_INTERACTION_HISTORY:
    print("Judge prints:", s)


def PrintSubprocessResults(p):
  # Print the return code and stderr output for your code.
  print("Your code finishes with exit status {}.".format(p.returncode))
  code_stderr_output = p.stderr.read()
  if code_stderr_output:
    print("The stderr output of your code is:")
    sys.stdout.write(code_stderr_output)
  else:
    print("Your code doesn't have stderr output.")


def WaitForSubprocess(p):
  # Wait for your code to finish and print the stderr output of your code for
  # debugging purposes.
  if p.poll() is None:
    print("Waiting for your code to finish...")
    p.wait()
  PrintSubprocessResults(p)


def CheckSubprocessExit(p, case_id):
  # Exit if your code finishes in the middle of a test case.
  if p.poll() is not None:
    print("Your code exited early, in the middle of Case #{}.".format(case_id))
    PrintSubprocessResults(p)
    sys.exit(-1)


def WrongAnswerExit(p, case_id, error_msg):
  print("Case #{} failed: {}".format(case_id, error_msg))
  try:
    JudgePrint(p, "-1")
  except IOError:
    print("Failed to print -1 because your code finished already.")
  WaitForSubprocess(p)
  sys.exit(-1)


def ReadIntList(n, l, u, line):
  t = line.split()
  if len(t) != n:
    return "Wrong number of tokens: {}. Expected {}.".format(len(t), n)
  try:
    xs = [int(x) for x in t]
  except:
    return "A token in {} is not an integer.".format(t)
  for x in xs:
    if x < l or x > u:
      return "Integer {} is not in range [{}-{}].".format(x, l, u)
  return xs

def ReadN(l, u, line):
  t = ReadIntList(1, l, u, line)
  if isinstance(t, str):
    return t
  return t[0]

def ReadGraph(lines):
  n = len(lines) // 2
  g = [set() for _ in range(n)]
  for l in lines:
    t = ReadIntList(2, 1, n, l)
    if isinstance(t, str):
      return t
    a, b = t
    if a == b:
      return "Computer {} has a self-loop.".format(a)
    g[a - 1].add(b - 1)
    g[b - 1].add(a - 1)
  for i in range(n):
    if len(g[i]) != 4:
      return "Computer {} has {} links instead of 4.".format(i+1, len(g[i]))
  return g

def IsConnected(g):
  n = len(g)
  c = list(range(n))
  for i in range(n):
    for j in g[i]:
      if c[i] != c[j]:
        oi = c[i]
        for k in range(n):
          if c[k] == oi:
            c[k] = c[j]
  return len(set(c)) == 1

def ReadPermutation(n, line):
  p = ReadIntList(n, 1, n, line)
  if isinstance(p, str):
    return p
  if len(set(p)) != n:
    return "Repeated integers in {}.".format(p)
  return [x - 1 for x in p]

def ApplyPermutation(p, g):
  n = len(g)
  h = [set() for _ in range(n)]
  for i in range(n):
    for j in g[i]:
      h[p[i]].add(p[j])
  return h

def RandomPermutation(n):
  p = list(range(n))
  random.shuffle(p)
  return p

"""Main function begins"""
# Retrieve the command to run your code from the arguments.
# If you cannot pass arguments to Python when running this testing tool, please
# replace sys.argv[1:] with the command list to run your code.
# e.g. C++ users: cmd = ["./my_binary"]
#      Python users: cmd = [sys.executable, "my_code.py"]
#      Java users: cmd = ["java", "my_main_class_name"]
cmd = sys.argv[1:]
assert cmd, "There should be at least one argument." + USAGE_MSG
if (cmd[0] == "-h") or (cmd[0] == "-help") or (cmd[0] == "--h") or (
    cmd[0] == "--help"):
  print(USAGE_MSG)
  sys.exit(0)

# Run your code in a separate process. You can debug your code by printing to
# stderr inside your code, or adding print statements in this testing tool.
# Note that your stderr output will be printed by this testing tool only after
# your code finishes, e.g. if your code hangs, you wouldn't get your stderr
# output.
try:
  p = subprocess.Popen(
      cmd,
      stdin=subprocess.PIPE,
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE,
      bufsize=1,
      universal_newlines=True)
except Exception as e:
  print("Failed to start running your code. Error:")
  print(e)
  sys.exit(-1)

JudgePrint(p, NUM_TEST_CASES)
for i in range(NUM_TEST_CASES):
  L, U = CASES[i]
  if PRINT_INTERACTION_HISTORY:
    print("Test Case #{}:".format(i + 1))
  JudgePrint(p, "{} {}".format(L, U))
  try:
    CheckSubprocessExit(p, i + 1)
    n = ReadN(L, U, p.stdout.readline())
    if PRINT_INTERACTION_HISTORY:
      print("Judge reads:", n)
    if isinstance(n, str):
      raise Exception("Invalid number of computers.")
    links = []
    for _ in range(2 * n):
      CheckSubprocessExit(p, i + 1)
      link = p.stdout.readline()
      if PRINT_INTERACTION_HISTORY:
        print("Judge reads:", link.strip())
      links.append(link)
    g = ReadGraph(links)
    if isinstance(g, str):
      raise Exception("Links do not form a valid network.")
    if not IsConnected(g):
      raise Exception("The network of computers is not connected.")
    perm = RandomPermutation(n)
    h = ApplyPermutation(perm, g)
    JudgePrint(p, "{}".format(n))
    for y in range(n):
      for z in sorted(list(h[y])):
        if y < z:
          JudgePrint(p, "{} {}".format(y + 1, z + 1))
    CheckSubprocessExit(p, i + 1)
    resp = p.stdout.readline()
    if PRINT_INTERACTION_HISTORY:
      print("Judge reads:", resp.strip())
    resp_perm = ReadPermutation(n, resp)
    if isinstance(resp_perm, str):
      raise Exception("Invalid permutation.")
    if resp_perm != perm:
      raise Exception("The permutation you gave is not the one the judge used.")
  except Exception as e:
    # Note that your code might finish after the first CheckSubprocessExit
    # check above but before the readline(), so we will need to again check
    # whether your code has finished.
    CheckSubprocessExit(p, i + 1)
    WrongAnswerExit(p, i + 1, e)

extra_output = p.stdout.readline()
WaitForSubprocess(p)
if extra_output != "":
  print("Wrong Answer because of extra output:")
  sys.stdout.write(extra_output)
  sys.exit(-1)
