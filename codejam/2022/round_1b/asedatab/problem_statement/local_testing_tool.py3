"""judge.py for asedatab."""

# Usage: `judge.py test_number`, where the argument test_number is 0 (visible)
# This can also be run as `python3 testing_tool.py test_number`.

from __future__ import print_function
import sys
import random

# Use raw_input in Python2.
try:
  input = raw_input
except NameError:
  pass

T = 100
S = 8
MAX_TURNS = 300

INVALID_OUTPUT = -1
RUN_OUT_OF_TURNS = -1

class Error(Exception):
  pass

INVALID_LINE_ERROR = "Couldn't read a valid line."
RUN_OUT_OF_TURNS_ERROR = "Run out of turns"
UNEXPECTED_LENGTH = "Expect line with length {}, but actually get {}".format
UNEPECTED_CHAR = "Input contains unexpected character {}".format
EXCEPTION_AFTER_END_ERROR = "Exception raised while reading input after all cases finish."
ADDITIONAL_INPUT_ERROR = "Additional input after all cases finish: {}".format

CASE_FAILED_ERROR = "Case #{} failed: {}".format

def ReadValue(line):
  line = line.strip()
  if len(line) != S:
    raise Error(UNEXPECTED_LENGTH(S, len(line)))
  for c in line:
    if c not in {'1', '0'}:
      raise Error(UNEPECTED_CHAR(c))
  return line

def GetNewRecord(old_record, newp):
  new_record = ""
  for i in range(S):
    new_record += '1' if old_record[i] != newp[i] else '0'
  return new_record

def GetNumberOfOne(record):
  number_of_one = 0
  for i in range(S):
    number_of_one += 1 if record[i] == '1' else 0
  return number_of_one

def RunCase():
  def Output(line):
    print(line)
    sys.stdout.flush()

  # choose a random record that is not all 0
  record = "0"*S
  while record == "0"*S:
    record = ""
    for i in range(S):
      record += chr(random.randrange(2) + ord('0'))

  for i in range(MAX_TURNS):
    try:
      line = input()
      p = ReadValue(line)
      r = random.randrange(S)
      # right rotate r is same as left rotate (S - r)
      r = S - r
      newp = p[r:] + p[:r]
      record = GetNewRecord(record, newp)
      number_of_one = GetNumberOfOne(record)
      if number_of_one == 0:
        # output 0 if the record is set to 0 and mark the test as completed.
        Output(0)
        return True
      elif i < MAX_TURNS - 1:
        # output the number of 1s in the record if it isn't the last turn
        Output(number_of_one)
      else:
        # output -1 (Run out of turns) if it is the last turn and the record
        # is not yet set to 0. Also mark the test as failed
        Output(RUN_OUT_OF_TURNS)
        return False
    except Error as err:
      Output(INVALID_OUTPUT)
      raise Error(err)
    except:
      Output(INVALID_OUTPUT)
      raise Error(INVALID_LINE_ERROR)

def RunCases(t):
  for i in range(1, t + 1):
    # The implementation of randomness here is not guaranteed to match the
    # implementation of randomness in the real judge.
    random.seed(2 + i)
    try:
      res = RunCase()
      if not res:
        raise Error(RUN_OUT_OF_TURNS_ERROR)
    except Error as err:
      raise Error(CASE_FAILED_ERROR(i, err))

  try:
    extra_input = input()
  except Exception:
    return
  raise Error(ADDITIONAL_INPUT_ERROR(extra_input[:100]))

def main():
  try:
    print(T)
    sys.stdout.flush()
    try:
      RunCases(T)
    except Error as err:
      print(str(err)[:1000], file=sys.stderr)
      sys.exit(1)
  except Exception as exception:
    print(INVALID_OUTPUT)
    sys.stdout.flush()
    print(('JUDGE_ERROR! Internal judge exception: {}'.format(exception))
          [:1000], file=sys.stderr)

if __name__ == "__main__":
  main()
