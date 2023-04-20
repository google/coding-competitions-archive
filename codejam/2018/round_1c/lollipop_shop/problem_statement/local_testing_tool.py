""" Python script for local testing (compatible with both Python 2 and Python 3)

Disclaimer: this is a way to test your solutions, but it is NOT the real judging
system. The judging system behavior might be different.
"""
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

# CASES is a list of test cases.  They were not generated the same way as the
# real data.
#
# Each case contains a list of flavor preferences for each customer.
#
# For example, in the first case, there are 3 customers.  The first customer
# likes flavors 1 and 2, the second customer likes flavors 0 and 2, and the
# third customer likes all three flavors.
#
# MAX contains the maximum number of lollipops it is possible to sell for each
# test case in CASES.
CASES = [[[1,2],[0,2],[0,1,2]],
  [[0,1],[]],
  [[1,3],[0,2],[1,3],[0,2]],
  [[0,1,2,4],[1,3,4],[0,1,4],[1,2,3,4],[1]],
  [[2],[4],[1,4],[0,2],[0,3]]]
MAX = [3,1,4,5,5]
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
  case = CASES[i]
  N = len(case)
  if PRINT_INTERACTION_HISTORY:
    print("Test Case #{}:".format(i + 1))
  JudgePrint(p, "{}".format(N))
  used = [False] * N
  sold = 0
  for j in range(N):
    line = case[j]
    JudgePrint(p, ' '.join(map(str,[len(line)]+line)))
    # Detect whether the your code has finished running.
    CheckSubprocessExit(p, i + 1)

    user_input = None
    try:
      user_input = p.stdout.readline()
      q = int(user_input)
    except:
      # Note that your code might finish after the first CheckSubprocessExit
      # check above but before the readline(), so we will need to again check
      # whether your code has finished.
      CheckSubprocessExit(p, i + 1)
      exit_msg = ""
      if user_input == "":
        exit_msg = ("Read an empty string for the flavor. This might happen "
                    "because your code exited early, or printed an extra "
                    "newline character.")
      elif user_input is None:
        exit_msg = (
            "Unable to read the flavor. This might happen because your "
            "code exited early, printed an extra new line character, or did "
            "not print the output correctly.")
      else:
        exit_msg = ("Failed to read the flavor. Expected an integer ending "
                    "with one new line character. Read \"{}\" (quotes added to "
                    "isolate your output) instead.").format(user_input)
      WrongAnswerExit(p, i + 1, exit_msg)
    if PRINT_INTERACTION_HISTORY:
      print("Judge reads:", q)
    if (q < -1) or (q >= N):
      WrongAnswerExit(p, i + 1, "Flavor {} is out of range!".format(q))
    if q != -1:
      if q not in line:
        WrongAnswerExit(p, i + 1, "Flavor {} was not liked by the customer!".format(q))
      if used[q]:
        WrongAnswerExit(p, i + 1, "Flavor {} was already sold!".format(q))
      used[q] = True
      sold = sold + 1
  print("Case {}/{}: sold {} out of a possible {} lollipops.".format(i+1, NUM_TEST_CASES, sold, MAX[i]))

extra_output = p.stdout.readline()
WaitForSubprocess(p)
if extra_output != "":
  print("Wrong Answer because of extra output:")
  sys.stdout.write(extra_output)
  sys.exit(-1)
