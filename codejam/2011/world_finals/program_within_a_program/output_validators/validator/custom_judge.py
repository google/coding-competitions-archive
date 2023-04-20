# Copyright 2011 Google Inc. All Rights Reserved.

"""Basic utilities for custom judges."""

__author__ = 'darthur@google.com (David Arthur)'

import logging


# Copied from judge.py
def _utils_Tokenize(text, case_sensitive=True):
  """Converts a block of text into a two-dimensional array of strings.

  Args:
    text: A block of text, probably either a contestant or generator output.
    case_sensitive: Whether all text should be converted to lower-case.

  Returns:
    A two-dimensional array of strings. There is one element for each non-blank
    row in the output, and there is one inner element for each token on that
    row. If text contains any characters outside ASCII range 32-126 (with the
    exception of tabs, carriage returns, and line feeds), None is returned.
  """
  if not case_sensitive:
    text = text.lower()
  text = text.replace('\t', ' ').replace('\r', '\n')
  for char in text:
    if not (32 <= ord(char) <= 126) and char != '\n':
      return None
  return [filter(None, row.split(' ')) for row in text.split('\n')
          if row.strip()]


def _utils_TokenizeAndSplitCases(output_file, attempt, num_cases,
                          case_sensitive=False):
  """Tokenizes the generator output file and attempt file by case number.

  This is similar to Tokenize except that:
    - It applies to both output_file and attempt.
    - The results are 3-dimensional vectors split by case number, and with the
      "Case #N:" tokens removed.
    - There could be empty rows due to the previous.
    - The number of cases in the output file and attempt must match num_cases.
    - An error string is returned if something is incorrect.

  Args:
    output_file: The output file, as given in FindError.
    attempt: The attempt file, as given in FindError.
    num_cases: The number of cases in the input file.
    case_sensitive: Whether to run in case-sensitive mode (for everything
      except the word 'Case' itself).

  Returns:
    On success, tokenized_output, tokenized_attempt, None is returned. Each of
    these are 3-dimensional arrays of tokens, sorted by case number, line
    number, and token. On failure, None, None, error is returned.
  """

  def ProcessOneFile(text, num_cases):
    """Similar to TokenizeAndSplitCases except applied to only one file."""

    # Tokenize and validate ASCII-ness. Case insensitive checking allows, for
    # example, contestants to output "case #N:" instead of "Case #N:".

    tokenized_text = _utils_Tokenize(text, case_sensitive=case_sensitive)
    if tokenized_text is None:
      return None, 'Invalid or non-ASCII characters.'

    # Build our result in split text.
    split_text = []
    # Even if case-sensitivity is on, allow the contestant to use any form of
    # 'case', since some contestants may have gotten accustomed to the
    # older, more flexible rules.
    for line in tokenized_text:
      if (len(line) >= 2 and
          line[0].lower() == 'case' and
          line[1].startswith('#')):
        # This line is a "Case #N:" line.
        expected_case = 1 + len(split_text)
        if line[1] != ('#%d:' % expected_case):
          return None, ('Expected "case #%d:", found "%s %s".'
                        % (expected_case, line[0], line[1]))
        if expected_case > num_cases:
          return None, 'Too many cases.'
        split_text.append([line[2:]])
      else:
        # This line is any other kind of line.
        if not split_text:
          return None, 'File does not begin with "case #1:".'
        split_text[-1].append(line)

    # At the end, make sure we had enough cases.
    if len(split_text) < num_cases:
      return None, 'Too few cases.'
    return split_text, None

  # Parse the generator output file. If something is wrong here, log an error.
  split_output, error = ProcessOneFile(output_file, num_cases)
  if error:
    error = 'Invalid generator output file: %s' % error
    logging.error(error)
    return None, None, error

  # Parse the user output file attempt.
  split_attempt, error = ProcessOneFile(attempt, num_cases)
  if error:
    error = 'Invalid attempt file: %s' % error
    return None, None, error
  return split_output, split_attempt, None


def _utils_ToInteger(s, minimum_value=None, maximum_value=None):
  """Returns int(s) if s is an integer in the given range. Otherwise None.

  The range is inclusive. Also, leading zeroes and negative zeros are not
  allowed.

  Args:
    s: A string to convert to an integer.
    minimum_value: If not-None, then s must be at least this value.
    maximum_value: If not-None, then s must be at most this value.

  Returns:
    An integer in the given range or None.
  """
  try:
    value = int(s)
    if len(s) > 1 and s.startswith('0'):
      return None
    if s.startswith('-0'):
      return None
    if minimum_value is not None and value < minimum_value:
      return None
    if maximum_value is not None and value > maximum_value:
      return None
    return value
  except ValueError:
    return None


def _utils_ToFloat(s):
  """Returns float(s) if s is a float. Otherwise None.

  Disallows infinities and nans.

  Args:
    s: A string to convert to a float.

  Returns:
    An float or None.
  """
  try:
    x = float(s)
    if x not in [float('inf'), float('-inf')] and x == x:  # not NaN
      return x
    else:
      return None
  except ValueError:
    return None
# Copyright 2011 Google Inc. All Rights Reserved.

"""A custom judge for the Program Within A Program problem."""

__author__ = 'darthur@google.com (David Arthur)'

import logging



def ParseInput(input_file):
  """Given the input file, returns expected positions for each test case."""
  int_values = [int(w) for w in input_file.split()]
  return int_values[1:]


def ParseExpectedOutput(output_file):
  """Given the output file, returns the values stored within.

  The output file is meaningless except that it encodes the constraints that we
  will hold the contestants to. That way, we can change the constraints from the
  generator instead of having to touch the verifier.

  Args:
    output_file: The verifier's output as a simple string. Format is expected to
      be "max_instructions max_moves min_memory_value max_memory_value\n"
      "Case #1: \nCase #2: \n"..."Case #NUMCASES: \n".
      The "Case #" part isn't used by the judge, but is needed so that
      submissions won't be rejected.

  Returns:
    All output file values as integers in the order given.
  """
  first_line = output_file[:output_file.find("\n")]
  return [int(w) for w in first_line.split()]


def ParseAttempt(attempt, num_cases, max_instructions,
                 min_memory_value, max_memory_value):
  """Converts the contestant's output into a list of instruction maps.

  Args:
    attempt: The contestant's output as a simple string.
    num_cases: The number of test cases that should have an output.
    max_instructions: The maximum number of robot instructions that is allowed
        for each test case.
    min_memory_value: All memory values (robot state or tape value) must be at
        least this high.
    max_memory_value: All memory values (robot state or tape value) must be at
        most this high.

  Returns:
    If the contestant's output is valid, then (instruction_map_list, '') is
    returned. InstructionMapList is a list with num_cases elements. Each element
    is a dictionary with at most max_instructions elements in the format:
      (state, tape_value) -> (action, new_state, new_tape_value)
    All states and tape values are integers between min_memory_value and
    max_memory_value inclusive. action is 'W', 'E', or 'S'. This dictionary
    represents the robot instructions for one test case.

    If the contestant's output is invalid, then (None, error_message) is
    returned, where error_message explains what is wrong with the output.
  """
  tokenized_output = _utils_Tokenize(attempt, False)
  if tokenized_output is None:
    return None, 'Output file contains invalid or non-ASCII characters.'
  imap_list = []
  line_number = 0

  # Loop through each test case.
  for test_case in xrange(1, num_cases + 1):
    # Read the number of instructions in the test case and verify the file
    # contains the whole instruction set.
    if line_number >= len(tokenized_output):
      return None, 'Output ended before case #%d' % test_case
    if len(tokenized_output[line_number]) != 3:
      return None, ('Wrong number of tokens on count line #%d'
                    % (line_number + 1))
    if (tokenized_output[line_number][0] != 'case' or
        tokenized_output[line_number][1] != ('#%d:' % test_case)):
      return None, 'Badly formatted case number on line #%d' % (line_number + 1)
    num_instructions = _utils_ToInteger(tokenized_output[line_number][2],
                                       0, max_instructions)
    if num_instructions is None:
      return None, 'Invalid instruction count on line #%d' % (line_number + 1)
    line_number += 1
    if line_number + num_instructions > len(tokenized_output):
      return None, 'Output ended in the middle of case #%d' % test_case
    imap = {}
    imap_list.append(imap)

    # Read this instruction set.
    lines = tokenized_output[line_number : line_number + num_instructions]
    for tokenized_line in lines:
      # Read this instruction.
      if len(tokenized_line) not in (4, 6):
        return None, ('Wrong number of tokens on instruction line #%d'
                      % (line_number + 1))
      if tokenized_line[2] != '->':
        return None, 'Missing -> token on line #%d' % (line_number + 1)
      action = tokenized_line[3]
      if action not in ('w', 'e', 'r'):
        return None, 'Invalid action on line #%d' % (line_number + 1)
      state = _utils_ToInteger(tokenized_line[0], min_memory_value,
                              max_memory_value)
      tape = _utils_ToInteger(tokenized_line[1], min_memory_value,
                             max_memory_value)
      if action == 'r':
        if len(tokenized_line) != 4:
          return None, ('Wrong number of tokens on instruction line #%d'
                        % (line_number + 1))
        state2, tape2 = 0, 0
      else:
        if len(tokenized_line) != 6:
          return None, ('Wrong number of tokens on instruction line #%d'
                        % (line_number + 1))
        state2 = _utils_ToInteger(tokenized_line[4],
                                 min_memory_value, max_memory_value)
        tape2 = _utils_ToInteger(tokenized_line[5],
                                min_memory_value, max_memory_value)
      if state is None or tape is None or state2 is None or tape2 is None:
        return None, 'Invalid memory value on line #%d' % (line_number + 1)

      # Store the instruction.
      if (state, tape) in imap:
        return None, 'Duplicate instruction on line #%d' % (line_number + 1)
      imap[(state, tape)] = (action, state2, tape2)
      line_number += 1

  # Excess instructions.
  if line_number < len(tokenized_output):
    return None, 'Excess output starting on line #%d' % (line_number + 1)
  return imap_list, None


def Execute(imap, expected_position, max_moves):
  """Simulates a robot based on a set of instructions.

  Args:
    imap: A set of robot instructions, as returned by ParseAttempt.
    expected_position: The number of spots right of the start that the robot is
        supposed to stop at.
    max_moves: The maximum number of moves the robot is allowed to make,
        including the stop.

  Returns:
    None if the supplied imap is correct and a 'str' error otherwise.
  """
  # Starting state.
  tape_map = {}
  moves, position, state = 0, 0, 0

  # Keep doing moves until 'S' or we run out of time. Note that we need to do
  # this check as we go rather than at the end, so contestants can't time out
  # the verifier.
  while moves < max_moves:
    moves += 1

    # Get the robot's instructions for this state.
    tape = tape_map.get(position, 0)
    if (state, tape) not in imap:
      return 'No instruction found for (%d, %d)' % (state, tape)
    (action, state, tape) = imap[(state, tape)]

    # Execute the instructions.
    tape_map[position] = tape
    if action == 'r':
      if position == expected_position:
        return None
      else:
        return 'Stopped at incorrect position %d' % position
    elif action == 'w':
      position -= 1
    else:
      position += 1

  # We ran out of moves.
  return 'Too many moves without stopping'


def FindError(unused_self, input_file, output_file, attempt):
  """Returns None if the output is correct and a 'str' error otherwise.

  Args:
    see judge.Judge.FindError().
  """
  # Parse all input.
  expected_positions = ParseInput(input_file)
  try:
    max_instructions, max_moves, min_memory_value, max_memory_value = (
        ParseExpectedOutput(output_file))
  except ValueError:
    logging.error('Expected output is badly formatted')
    return 'Expected output is badly formatted.'
  imaps, error_message = ParseAttempt(attempt, len(expected_positions),
                                      max_instructions,
                                      min_memory_value, max_memory_value)
  if imaps is None:
    return error_message

  # Simulate each test case.
  for test_case in xrange(len(expected_positions)):
    error_message = Execute(imaps[test_case], expected_positions[test_case],
                            max_moves)
    if error_message is not None:
      return 'Case #%d: %s' % (test_case + 1, error_message)

  # Huge success!
  return None

import sys
if __name__ == "__main__":
  if sys.argv[1] == '-2':
    sys.exit(0)
  result = FindError(None,
                     file(sys.argv[1]).read(),
                     file(sys.argv[3]).read(),
                     file(sys.argv[2]).read())
  if result:
    print >> sys.stderr, result
    sys.exit(1)
