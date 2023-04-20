"""judge.py for the Go, Gopher! interactive judge.
"""

# Usage: `judge.py test_number`, where the argument test_number is either 0
# (small), 1 (large) or -2 (test mode).

import itertools
import random
import sys

FIELD_SIZE = 1000  # the field is 1000 * 1000
MAX_NUM_TRIES = 1000  # maximum number of tries for each test case
_ERROR_MSG_EXTRA_NEW_LINES = "Input has extra newlines."
_ERROR_MSG_INCORRECT_ARG_NUM = "Input does not have exactly 2 tokens."
_ERROR_MSG_INVALID_TOKEN = "Input has invalid token."
_ERROR_MSG_OUT_OF_RANGE = "Input should be in the range of [2, {}]".format(
    FIELD_SIZE - 1)
_ERROR_MSG_READ_FAILURE = "Read for input fails."


class JudgeSingleCase:

  def __init__(self, min_prepared_cells):
    self.__min_prepared_cells = min_prepared_cells  # min num of prepared cells
    self.__prepared_cells_count = 0  # number of cells that have been prepared
    self.__field = set()
    self.__northmost = self.__southmost = self.__eastmost = self.__westmost = 0

  def _parse_contestant_input(self, response):
    """Parses contestant's input.

    Parse contestant's input which should be two integers in [2, FIELD_SIZE - 1]
    separated by a space. Only extra spaces and tabs are allowed (not newlines).

    Args:
      response: (str) one-line input given by the contestant.

    Returns:
      (int, int, string): row, column of the cell location sent by the
      contestant, and the error string in case of error.
      If the parsing succeeds, the return value should be (int, int, None).
      If the parsing fails, the return value shoud be (0, 0, str). (0, 0) is
      chosen because it is not a valid cell in the problem.
    """
    if (response.find("\n") >= 0) or (response.find("\r") >= 0):
      return (0, 0, _ERROR_MSG_EXTRA_NEW_LINES)
    tokens = response.split()
    if len(tokens) != 2:
      return (0, 0, _ERROR_MSG_INCORRECT_ARG_NUM)
    target_cell_coordinate = []
    for token in tokens:
      if (len(token) < 1) or (len(token) > 3):
        return (0, 0, _ERROR_MSG_INVALID_TOKEN)
      try:
        token = int(token)
      except Exception:
        return (0, 0, _ERROR_MSG_INVALID_TOKEN)
      if (token < 2) or (token > FIELD_SIZE - 1):
        return (0, 0, _ERROR_MSG_OUT_OF_RANGE)
      target_cell_coordinate.append(token)
    return (target_cell_coordinate[0], target_cell_coordinate[1], None)

  def _get_deviation(self, num):
    """Given a number, return an int in [num - 1, num + 1] uniformly at random.

    Args:
      num: (int) a number between 2 and FIELD_SIZE - 1 (inclusive).

    Returns:
      An integer in [num - 1, num + 1].
    """
    return random.randint(num - 1, num + 1)

  def _add_new_prepared_cell(self, prepared_cell):
    """Add a newly-prepared cell to the field.

    Args:
      prepared_cell: (tuple(int, int)) indicating location of the new cell.

    Returns:
      A boolean indicating whether the contestant solves the test case with the
      new cell.
    """
    if prepared_cell in self.__field:
      return False
    if self.__northmost == 0:
      self.__northmost = prepared_cell[0]
      self.__southmost = prepared_cell[0]
      self.__westmost = prepared_cell[1]
      self.__eastmost = prepared_cell[1]
    else:
      self.__northmost = min(prepared_cell[0], self.__northmost)
      self.__southmost = max(prepared_cell[0], self.__southmost)
      self.__westmost = min(prepared_cell[1], self.__westmost)
      self.__eastmost = max(prepared_cell[1], self.__eastmost)
    self.__field.add(prepared_cell)
    self.__prepared_cells_count += 1
    if (self.__prepared_cells_count >= self.__min_prepared_cells) and (
        self.__prepared_cells_count == (
            self.__southmost - self.__northmost + 1) *
        (self.__eastmost - self.__westmost + 1)):
      return True
    return False

  def Judge(self):
    """Judge one single case; should only be called once.

    Returns:
      An error string, or None if the attempt was correct.
    """
    for _ in xrange(MAX_NUM_TRIES):
      try:
        contestant_input = raw_input()
      except Exception:
        return _ERROR_MSG_READ_FAILURE
      r, c, err = self._parse_contestant_input(contestant_input)
      if err is not None:
        return err
      prepared_cell = (self._get_deviation(r), self._get_deviation(c))
      if self._add_new_prepared_cell(prepared_cell):
        print 0, 0
        sys.stdout.flush()
        return None
      else:
        print prepared_cell[0], prepared_cell[1]
        sys.stdout.flush()
    return "Not able to prepare at least {} cells.".format(
        self.__min_prepared_cells)


class JudgeSingleCaseTest:

  @staticmethod
  def TestParseContestantInput():
    """Test _parse_contestant_input using assert.
    """
    case = JudgeSingleCase(20)
    for contestant_input in ["\r2 2", "2\r2", "\n2 2", "3 \n\n"]:
      assert case._parse_contestant_input(contestant_input)[
          2] == _ERROR_MSG_EXTRA_NEW_LINES
    for contestant_input in [
        "", " 10   ", "  200 30 \t 3 \t", "5 6 7 8", "2,3", "2.3", "9 9 9"
    ]:
      assert case._parse_contestant_input(contestant_input)[
          2] == _ERROR_MSG_INCORRECT_ARG_NUM
    for contestant_input in [
        "1000 2", "abcd 2", "999 !?!?", "999 !?!?!!", "a 23", "2, 3", "abc 23",
        "23 1.2", "!!! 1.2", "999 1000", "2a 23", "2.0, 2.0"
    ]:
      assert case._parse_contestant_input(contestant_input)[
          2] == _ERROR_MSG_INVALID_TOKEN
    for contestant_input in ["1 2", "2 -1", "-12 2"]:
      assert case._parse_contestant_input(contestant_input)[
          2] == _ERROR_MSG_OUT_OF_RANGE
    for (contestant_input, expected_result) in zip([
        "999 999", "  999 999 ", "\t999\t999\t", "  \t999     999",
        "999 \t \t999  ", "2 2", "2 100", "28 987"
    ], [(999, 999, None), (999, 999, None), (999, 999, None), (999, 999, None),
        (999, 999, None), (2, 2, None), (2, 100, None), (28, 987, None)]):
      assert case._parse_contestant_input(contestant_input) == expected_result

  @staticmethod
  def __test__add__cell__h(min_prepared_cells,
                           prepared_cells,
                           expect_success=True):
    """Helper for TestAddNewPreparedCell given a list of cells to add.

    Args:
      min_prepared_cells: (int) arg to construct JudgeSingleCase object.
      prepared_cells: (list[(int, int)]) list of prepared cells to add in order.
      expect_success: (bool) whether we expect the last prepared cell to solve
          the test case. (We expect that all previous additions will not solve
          it.)
    """
    case = JudgeSingleCase(min_prepared_cells)
    num_cells = len(prepared_cells)
    for i in xrange(1, num_cells + 1):
      result = case._add_new_prepared_cell(prepared_cells[i - 1])
      assert (((not result) and (i < num_cells)) or
              ((expect_success == result) and (i == num_cells)))

  @staticmethod
  def TestAddNewPreparedCell():
    """Test _add_new_prepared_cell

    Returns:
      An error string, empty if no errors
    """
    JudgeSingleCaseTest.__test__add__cell__h(4, [(1, 1), (1, 1), (1, 1), (1, 1),
                                                 (1, 1)], False)

    JudgeSingleCaseTest.__test__add__cell__h(4, [(1, 4), (1, 1), (1, 3), (1, 3),
                                                 (1, 2)])

    JudgeSingleCaseTest.__test__add__cell__h(
        4, [(2, 2), (2, 3), (2, 4), (3, 2), (2, 5), (3, 3), (3, 4), (3, 5)])

    JudgeSingleCaseTest.__test__add__cell__h(4, [(1, 1), (999, 999), (1, 2),
                                                 (2, 1), (2, 2)], False)

    JudgeSingleCaseTest.__test__add__cell__h(
        6, [(10, 10), (11, 11), (10, 10), (10, 11), (11, 10), (10, 12),
            (10, 13), (10, 11), (11, 12), (10, 12), (10, 13), (11, 13)])

    JudgeSingleCaseTest.__test__add__cell__h(8, [(1, 1), (2, 2), (1, 2), (2, 1),
                                                 (3, 1), (3, 2), (1, 3), (3, 3),
                                                 (2, 3)])

    JudgeSingleCaseTest.__test__add__cell__h(1, [(287, 288)])

    JudgeSingleCaseTest.__test__add__cell__h(5, [(2, 3), (1, 1), (1, 2), (1, 3),
                                                 (2, 2), (2, 1)])

    JudgeSingleCaseTest.__test__add__cell__h(4, [(1, 1), (1, 4), (1, 2), (3, 1),
                                                 (3, 2), (4, 1), (4, 2),
                                                 (1, 3)], False)

    prepared_cells = []
    for i in xrange(MAX_NUM_TRIES / 2):
      prepared_cells.append((1, i))
    for i in xrange(MAX_NUM_TRIES / 2 + 1, MAX_NUM_TRIES + 1):
      prepared_cells.append((1, i))
    prepared_cells.append((1, MAX_NUM_TRIES / 2))
    JudgeSingleCaseTest.__test__add__cell__h(MAX_NUM_TRIES, prepared_cells)
    """ Test 9 cases of not-quite-complete-rectangles.
        .XX
        XXX
        XXX
        or
        XXX
        X.X
        XXX
        etc."""
    rectangle = [(1, 1), (1, 2), (1, 3), (2, 1), (2, 2), (2, 3), (3, 1), (3, 2),
                 (3, 3)]
    for prepared_cells in itertools.combinations(rectangle, 8):
      JudgeSingleCaseTest.__test__add__cell__h(7, prepared_cells, False)

  @staticmethod
  def Test():
    """Runs all unit tests.
    """
    """Need end-to-end testing for:

      Case 1 succeeds but Case 2 fails;
      Flushing behavior;
      Case that fails for all 1000 tries.
    """
    JudgeSingleCaseTest.TestParseContestantInput()
    JudgeSingleCaseTest.TestAddNewPreparedCell()


def JudgeAllCases():
  """Sends input to contestant and judges contestant output.

  Returns:
    An error string, or None if the attempt was correct.
  """
  test_number = int(sys.argv[1])
  total_num_cases = 20
  min_prepared_cells = 20 if test_number == 0 else 200
  print total_num_cases
  sys.stdout.flush()
  for case_number in xrange(1, total_num_cases + 1):
    print min_prepared_cells
    sys.stdout.flush()
    random.seed(case_number + test_number + 101)
    single_case = JudgeSingleCase(min_prepared_cells)
    err = single_case.Judge()
    if err is not None:
      return "Case #{} fails:\n{}".format(case_number, err)
  # Make sure nothing other than EOF is printed after all cases finish.
  try:
    response = raw_input()
  except EOFError:
    return None
  except Exception:  # pylint: disable=broad-except
    return "Exception raised while reading input after all cases finish."
  return "Additional input after all cases finish: {}".format(response[:1000])


def main():
  if int(sys.argv[1]) == -2:
    result = JudgeSingleCaseTest.Test()
  else:
    result = JudgeAllCases()
    if result is not None:
      print >> sys.stderr, result
      print -1, -1
      sys.stdout.flush()
      sys.exit(1)


if __name__ == "__main__":
  main()
