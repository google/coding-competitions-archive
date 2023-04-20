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

See https://codejam.withgoogle.com/codejam/resources/faq#languages for how we
compile and run your solution in the language of your choice.

Windows users:
  Follow the instructions for Linux and Mac users if you are familiar with
  terminal tools on Windows. Otherwise, please be advised that this script might
  not work with Python 2 (it works with Python 3). In addition, if you cannot
  pass arguments to Python, you will need to modify the "cmd = sys.argv[1:]"
  line below.
"""

S = 10**5
# CASES is a list of test cases, giving the values of the gophers' taste
# levels. In this example, gophers always reorder themselves randomly,
# but in Test set 2, that might not be the case. To test other scenarios,
# substitute a reordering function other than random.shuffle on line 159.
# Note that the [1, 1, 2] case would not appear in test set 1.
CASES = [[1, 2, 3, 4, 5, 6], [1, 10**6], [1, 1, 2]]
NUM_TEST_CASES = len(CASES)
# You can set PRINT_INTERACTION_HISTORY to True to print out the interaction
# history between your code and the judge.
PRINT_INTERACTION_HISTORY = False


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


def ReadValue(line):
  t = line.split()
  if len(t) != 1:
    return "Wrong number of tokens: {}. Expected 1.".format(len(t))
  try:
    v = int(t[0])
  except:
    return "Not an integer: {}".format(t[0])
  if v < -25 or -2 < v < 1 or 10**6 < v:
    return "Value {} is out of range.".format(v)
  return v


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
  snacks = 0
  taste_levels = CASES[i]
  n = len(taste_levels)
  if PRINT_INTERACTION_HISTORY:
    print("Test Case #{}:".format(i + 1))
  JudgePrint(p, S)

  try:
    while True:
      # Detect whether the your code has finished running.
      CheckSubprocessExit(p, i + 1)
      if snacks % n == 0:
        random.shuffle(taste_levels)
      try:
        line = p.stdout.readline()
      except:
        raise Exception("Couldn't read a valid line.")
      v = ReadValue(line)
      if isinstance(v, str):
        raise Exception(v)
      if v < 0:  # The submitted value is a guess.
        if abs(v) == n:
          break  # Correct answer.
        raise Exception(
            "Wrong guess of {} gophers (true value: {})".format(abs(v), n))
      else:  # The submitted value is a snack quality level.
        snacks += 1
        if snacks > S:
          raise Exception("Used too many snacks.")
        JudgePrint(p, 1 if v >= taste_levels[snacks % n] else 0)
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
