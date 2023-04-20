"""judge.py for Board Meeting."""

# Usage: `judge.py test_number`, where the argument test_number is either 0
# (small), 1 (large) or -2 (test mode).

import sys
import collections
import itertools
import random
import math

NUM_CASES = 15
N_MAXS = (1, 10)
MAX_COORD = int(1e6)
MAX_REQUEST_COORD = 10 * MAX_COORD
MAX_REQUESTS = 1000

END_OF_PHASE_1 = "READY"
END_OF_PHASE_2 = "DONE"
INVALID_OUTPUT = "ERROR"

TestCase = collections.namedtuple("TestCase", ["kings", "requests"])


def GenerateRandomRequests(generator, num_requests):
  requests = []
  for _ in xrange(num_requests):
    if generator.randint(0, 1) == 0:
      # Put half of the requests within the bounding box, as those might
      # be more tricky than outside ones.
      max_coord = MAX_COORD
    else:
      max_coord = MAX_REQUEST_COORD
    requests.append(
        (generator.randint(-max_coord, max_coord),
         generator.randint(-max_coord, max_coord)))
  return requests


def GenerateTrickyRandomRequests(generator, kings, num_requests):
  # If the locations of the kings have been determined incorrectly,
  # the outputs will be incorrect on some x+y=const and x-y=const lines.
  # Therefore we try to check such lines around the king locations.
  requests = []
  for _ in xrange(num_requests):
    x0, y0 = kings[generator.randint(0, len(kings) - 1)]
    slope = [-1, 1][generator.randint(0, 1)]
    x_plus_y = slope * x0 + y0 + generator.randint(-3, 3)
    while True:
      x = generator.randint(-MAX_REQUEST_COORD, MAX_REQUEST_COORD)
      y = x_plus_y - slope * x
      if y >= -MAX_REQUEST_COORD and y <= MAX_REQUEST_COORD:
        break
    requests.append((x, y))
  return requests


def GenerateTrickierRandomRequests(generator, kings, max_requests):
  requests = list(kings)
  requests += GenerateRandomRequests(generator, max_requests / 2)
  requests += GenerateTrickyRandomRequests(
      generator, kings, max_requests - len(requests))
  generator.shuffle(requests)
  return requests


def GenerateSmallBoundaryCases(generator):
  cases = []
  # Four corner points to make sure binary searches have big enough
  # boundaries.
  for sx in [-1, 1]:
    for sy in [-1, 1]:
      kings = [(sx * MAX_COORD, sy * MAX_COORD)]
      # Add king locations themselves to requests as those might be corner
      # cases.
      requests = GenerateTrickierRandomRequests(generator, kings, MAX_REQUESTS)
      cases.append(TestCase(kings=tuple(kings), requests=tuple(requests)))
  return cases


def Generate3x3Grid(generator):
  # A case with kings in a huge 3x3 grid.
  kings = []
  for sx in [-1, 0, 1]:
    for sy in [-1, 0, 1]:
      kings.append((sx * MAX_COORD, sy * MAX_COORD))
  requests = GenerateTrickierRandomRequests(generator, kings, MAX_REQUESTS)
  return [TestCase(kings=tuple(kings), requests=tuple(requests))]


def GenerateDiagonals(generator, n_max, slopes):
  # Generates a case with all kings on one of y=slope*x+offset diagonals.
  # For each given slope, an offset is picked randomly.
  # Each slope must be 1 or -1.
  while True:
    offsets = [generator.randint(-MAX_COORD / 10, MAX_COORD / 10)
               for _ in slopes]
    if len(set(offsets)) == len(slopes):
      break
  kings = []
  for _ in xrange(n_max):
    while True:
      diagonal_id = generator.randint(0, len(slopes) - 1)
      slope = slopes[diagonal_id]
      offset = offsets[diagonal_id]
      x = generator.randint(-MAX_COORD, MAX_COORD)
      y = slope * x + offset
      if -MAX_COORD <= y <= MAX_COORD:
        king = (x, y)
        if king not in kings:
          break
    kings.append(king)
  requests = GenerateTrickierRandomRequests(generator, kings, MAX_REQUESTS)
  return [TestCase(kings=tuple(kings), requests=tuple(requests))]


def MinManhattanDistance(points):
  res = 1e9
  for i in range(len(points)):
    for j in range(i):
      a = points[i]
      b = points[j]
      res = min(res, abs(a[0] - b[0]) + abs(a[1] - b[1]))
  return res


def GenerateClusters(
    generator, n_max, num_clusters, cluster_x_size, cluster_y_size):
  # A case where the kings are located in clusters, each of given size.
  while True:
    clusters = [
        (generator.randint(-MAX_COORD, MAX_COORD - cluster_x_size + 1),
         generator.randint(-MAX_COORD, MAX_COORD - cluster_y_size + 1))
        for _ in range(num_clusters)]
    if MinManhattanDistance(clusters) >= 2 * (cluster_x_size + cluster_y_size):
      break
  kings = []
  for _ in xrange(n_max):
    while True:
      cluster_id = generator.randint(0, num_clusters - 1)
      x = generator.randint(0, cluster_x_size - 1) + clusters[cluster_id][0]
      y = generator.randint(0, cluster_y_size - 1) + clusters[cluster_id][1]
      king = (x, y)
      if king not in kings:
        break
    kings.append(king)
  requests = GenerateTrickierRandomRequests(generator, kings, MAX_REQUESTS)
  return [TestCase(kings=tuple(kings), requests=tuple(requests))]


def GenerateRandom(generator, n_max):
  n_min = int(round(0.7 * n_max))
  n = generator.randint(n_min, n_max)
  kings = []
  for _ in xrange(n):
    while True:
      x = generator.randint(-MAX_COORD, MAX_COORD)
      y = generator.randint(-MAX_COORD, MAX_COORD)
      king = (x, y)
      if king not in kings:
        break
    kings.append(king)
  requests = GenerateTrickierRandomRequests(generator, kings, MAX_REQUESTS)
  return [TestCase(kings=tuple(kings), requests=tuple(requests))]


def DescribeOnAxes(kings):
  """Returns enough data to answer all (x,0) and (0,y) requests."""
  xs = sorted(itertools.chain(*[[x - abs(y), x + abs(y)] for x, y in kings]))
  ys = sorted(itertools.chain(*[[y - abs(x), y + abs(x)] for x, y in kings]))
  return xs, ys


def RecursiveFindEquivalentSets(xs, ys, points, res, visited):
  key = (tuple(xs), tuple(sorted(ys.elements())), tuple(sorted(points)))
  if key in visited:
    return
  visited.add(key)
  if not xs:
    res_key = (tuple(sorted(x + y for x, y in points)),
               tuple(sorted(x - y for x, y in points)))
    res[res_key] = points
    return
  x1 = xs[0]
  for i in range(1, len(xs)):
    x2 = xs[i]
    if (x1 + x2) % 2 != 0:
      continue
    x = (x1 + x2) // 2
    if x < -MAX_COORD or x > MAX_COORD:
      continue
    absy = x - x1
    for y in [-absy, absy]:
      if y < -MAX_COORD or y > MAX_COORD:
        continue
      if (x, y) in points:
        continue
      y1 = y - abs(x)
      y2 = y + abs(x)
      if ys[y1] > 0:
        ys[y1] -= 1
        if ys[y2] > 0:
          ys[y2] -= 1
          RecursiveFindEquivalentSets(
              xs[1:i] + xs[i + 1:], ys, points + [(x, y)], res, visited)
          ys[y2] += 1
        ys[y1] += 1


def FindEquivalentCases(kings):
  """Finds cases equivalent to the given one for yutak@'s solution.

  They will give the same answers as the given case for all (x,0) and (0,y)
  requests, but different answers for some other requests.
  """
  xs, ys = DescribeOnAxes(kings)
  res = {}
  visited = set()
  RecursiveFindEquivalentSets(xs, collections.Counter(ys), [], res, visited)
  cases = sorted(res.values())
  assert all(DescribeOnAxes(case) == (xs, ys) for case in cases)
  return cases


def GetTrickyCoordinateAxesRectangle(max_coord):
  return [(-max_coord, -max_coord),
          (max_coord, max_coord),
          (-max_coord + 1, max_coord - 1),
          (max_coord - 1, -max_coord + 1)]


def GenerateHardcodedCaseByYutak(generator):
  kings = [(111, 111), (112, 111), (111, 112), (112, 112), (-111, -111),
           (-112, 111), (-111, -112), (112, -111), (-112, -111), (-111, 112)]
  requests = GenerateTrickierRandomRequests(generator, kings, MAX_REQUESTS)
  return [TestCase(kings=tuple(kings), requests=tuple(requests))]


def GenerateTrickyCoordinateAxesCases(generator):
  """A family of tricky cases breaking bad solution reported by yutak@.

  It breaks the solutions which only ever send requests of form (x,0) or (0,y),
  as it has many possible sets of points (up to reshuffles not changing
  the answers) giving the same results to those, as well as to all requests
  that have small enough coordinates.
  """
  kings = (GetTrickyCoordinateAxesRectangle(MAX_COORD) +
           GetTrickyCoordinateAxesRectangle(MAX_COORD - 2) +
           GetTrickyCoordinateAxesRectangle(MAX_COORD - 4)[:2])
  equivalent_cases = FindEquivalentCases(kings)
  assert 32 == len(equivalent_cases)
  # Sample 3 out of 32 possibilities randomly.
  return [
      TestCase(kings=tuple(kings),
               requests=tuple(GenerateTrickierRandomRequests(
                   generator, kings, MAX_REQUESTS)))
      for kings in generator.sample(equivalent_cases, 3)]


def GenerateExtremeTrickyCoordinateAxes(generator):
  """An extreme version of GenerateTrickyCoordinateAxesCases.

  Generates a case where sending all requests of form (x,0) or (0,y), as well
  as all requests with abs(x) and abs(y) being less than MAX_COORD would not
  be enough to distinguish several possibilities.
  """
  kings = GetTrickyCoordinateAxesRectangle(MAX_COORD)
  requests = GenerateTrickierRandomRequests(generator, kings, MAX_REQUESTS)
  return [TestCase(kings=tuple(kings), requests=tuple(requests))]


def GenerateCases(test_index):
  generator = random.Random(926153 + test_index)
  n_max = N_MAXS[test_index]

  cases = []
  if test_index == 0:
    cases.extend(GenerateSmallBoundaryCases(generator))

  if test_index == 1:
    cases.extend(Generate3x3Grid(generator))
    cases.extend(GenerateDiagonals(generator, n_max, [1]))
    cases.extend(GenerateDiagonals(generator, n_max, [-1]))
    cases.extend(GenerateDiagonals(generator, n_max, [1, 1, 1]))
    cases.extend(GenerateDiagonals(generator, n_max, [-1, 1]))

    cases.extend(GenerateClusters(generator, n_max, 1, 3, 4))
    cases.extend(GenerateClusters(generator, n_max, 3, 2, 2))
    cases.extend(GenerateHardcodedCaseByYutak(generator))
    cases.extend(GenerateTrickyCoordinateAxesCases(generator))
    cases.extend(GenerateExtremeTrickyCoordinateAxes(generator))
  # Fill the rest with big random cases, make sure we have at least 3.
  assert len(cases) <= NUM_CASES - 3
  while len(cases) < NUM_CASES:
    cases.extend(GenerateRandom(generator, n_max))

  generator.shuffle(cases)
  return cases


CASES = (GenerateCases(0), GenerateCases(1))


class Error(Exception):
  pass


WRONG_NUM_TOKENS_ERROR = (
    "Wrong number of tokens: expected {}, found {}.".format)
EXCEEDED_REQUESTS_ERROR = "Exceeded number of requests: {}.".format
OUT_OF_BOUNDS_ERROR = "Request out of bounds: ({}, {}).".format
NOT_INTEGER_ERROR = "Not an integer: {}".format
INVALID_LINE_ERROR = "Couldn't read a valid line."
CASE_FAILED_ERROR = "Case #{} failed: {}".format
WRONG_ANSWER = "Wrong answer for request {}: expected {}, found {}.".format
EXCEPTION_AFTER_END_ERROR = (
    "Exception raised while reading input after all cases finish.")
ADDITIONAL_INPUT_ERROR = "Additional input after all cases finish: {}".format


def ReadValues(line, num_tokens):
  t = line.split()
  if len(t) != num_tokens:
    raise Error(WRONG_NUM_TOKENS_ERROR(num_tokens, len(t)))
  r = []
  for s in t:
    try:
      v = int(s)
    except:
      raise Error(NOT_INTEGER_ERROR(s[:100]))
    r.append(v)
  return r


def AssertEqual(expected, actual):
  assert expected == actual, (
      "Expected [{}], got [{}]".format(expected, actual))


def AssertReturns(expected, fn, *args):
  result = fn(*args)
  AssertEqual(expected, result)


def AssertRaisesError(expected_message, fn, *args):
  try:
    fn(*args)
    assert False, (
        "Expected error [{}], but there was none".format(expected_message))
  except Error as error:
    message = str(error)
    assert expected_message == message, (
        "Expected error [{}], got [{}]".format(expected_message, message))


def TestReadValues():
  AssertReturns([1], ReadValues, "1", 1)
  AssertReturns([2, 3], ReadValues, "  2   3 ", 2)
  AssertRaisesError(WRONG_NUM_TOKENS_ERROR(1, 2), ReadValues, "1 2", 1)
  AssertRaisesError(WRONG_NUM_TOKENS_ERROR(2, 1), ReadValues, "1", 2)
  AssertRaisesError(NOT_INTEGER_ERROR("foo"), ReadValues, "foo", 1)
  AssertRaisesError(NOT_INTEGER_ERROR("bar"), ReadValues, "1 bar", 2)


def EvaluateRequest(kings, rx, ry):
  res = 0
  for x, y in kings:
    res += max(abs(rx - x), abs(ry - y))
  return res


def TestEvaluateRequest():
  AssertReturns(0, EvaluateRequest, [], 1, 1)
  AssertReturns(1 + 7 + 4, EvaluateRequest, [(0, 0), (5, -6), (-3, -1)], 1, 1)


def RunCase(case, test_input=None, test_output_storage=None):

  def Input():
    if test_input is None:
      return raw_input()
    else:
      return test_input.pop(0)

  def Output(line):
    if test_input is None:
      print line
      sys.stdout.flush()
    else:
      test_output_storage.append(line)

  received_requests = 0
  while True:
    try:
      line = Input()
    except:
      Output(INVALID_OUTPUT)
      raise Error(INVALID_LINE_ERROR)

    if line.strip().lower() == END_OF_PHASE_1.lower():
      break

    try:
      (x, y) = ReadValues(line, 2)
    except:
      Output(INVALID_OUTPUT)
      raise

    received_requests += 1
    if received_requests > MAX_REQUESTS:
      Output(INVALID_OUTPUT)
      raise Error(EXCEEDED_REQUESTS_ERROR(received_requests))

    if not(-MAX_REQUEST_COORD <= x <= MAX_REQUEST_COORD and
           -MAX_REQUEST_COORD <= y <= MAX_REQUEST_COORD):
      Output(INVALID_OUTPUT)
      raise Error(OUT_OF_BOUNDS_ERROR(x, y))

    Output(str(EvaluateRequest(case.kings, x, y)))

  for i, (x, y) in enumerate(case.requests):
    Output("{} {}".format(x, y))

    try:
      line = Input()
    except:
      Output(INVALID_OUTPUT)
      raise Error(INVALID_LINE_ERROR)

    try:
      (v,) = ReadValues(line, 1)
    except:
      Output(INVALID_OUTPUT)
      raise

    expected = EvaluateRequest(case.kings, x, y)
    # Remove the next comparison for IO time measurements.
    if v != expected:
      Output(INVALID_OUTPUT)
      raise Error(WRONG_ANSWER(i, expected, v))

  Output(END_OF_PHASE_2)


def TestRunCase():
  outputs = []
  AssertReturns(
      None,
      RunCase,
      TestCase(
          kings=[(0, 0), (5, -6), (-3, -1)],
          requests=[(1, 1), (-2, -4)]),
      ["0 0", "2 -2", END_OF_PHASE_1, str(1+7+4), str(4+7+3)],
      outputs)
  AssertEqual([str(0+6+3), str(2+4+5), "1 1", "-2 -4", END_OF_PHASE_2], outputs)

  outputs = []
  AssertReturns(
      None,
      RunCase,
      TestCase(
          kings=[(0, 0), (5, -6), (-3, -1)],
          requests=[(1, 1), (-2, -4)]),
      [END_OF_PHASE_1, str(1+7+4), str(4+7+3)],
      outputs)
  AssertEqual(["1 1", "-2 -4", END_OF_PHASE_2], outputs)

  outputs = []
  AssertReturns(
      None,
      RunCase,
      TestCase(
          kings=[(0, 0), (5, -6), (-3, -1)],
          requests=[(1, 1), (-2, -4)]),
      [END_OF_PHASE_1.lower(), str(1+7+4), str(4+7+3)],
      outputs)
  AssertEqual(["1 1", "-2 -4", END_OF_PHASE_2], outputs)

  outputs = []
  AssertReturns(
      None,
      RunCase,
      TestCase(
          kings=[(0, 0), (5, -6), (-3, -1)],
          requests=[(1, 1), (-2, -4)]),
      [END_OF_PHASE_1[:2] + END_OF_PHASE_1[2:].lower(), str(1+7+4), str(4+7+3)],
      outputs)
  AssertEqual(["1 1", "-2 -4", END_OF_PHASE_2], outputs)

  outputs = []
  AssertRaisesError(
      WRONG_ANSWER(1, str(4+7+3), "5"),
      RunCase,
      TestCase(
          kings=[(0, 0), (5, -6), (-3, -1)],
          requests=[(1, 1), (-2, -4)]),
      [END_OF_PHASE_1, str(1+7+4), "5"],
      outputs)
  AssertEqual(["1 1", "-2 -4", INVALID_OUTPUT], outputs)

  outputs = []
  AssertRaisesError(
      WRONG_NUM_TOKENS_ERROR(1, 2),
      RunCase,
      TestCase(
          kings=[(0, 0), (5, -6), (-3, -1)],
          requests=[(1, 1), (-2, -4)]),
      [END_OF_PHASE_1, str(1+7+4), str(4+7+3) + " 0"],
      outputs)
  AssertEqual(["1 1", "-2 -4", INVALID_OUTPUT], outputs)

  outputs = []
  AssertRaisesError(
      INVALID_LINE_ERROR,
      RunCase,
      TestCase(
          kings=[(0, 0), (5, -6), (-3, -1)],
          requests=[(1, 1), (-2, -4)]),
      [END_OF_PHASE_1, str(1+7+4)],
      outputs)
  AssertEqual(["1 1", "-2 -4", INVALID_OUTPUT], outputs)

  outputs = []
  AssertRaisesError(
      INVALID_LINE_ERROR,
      RunCase,
      TestCase(
          kings=[(0, 0), (5, -6), (-3, -1)],
          requests=[(1, 1), (-2, -4)]),
      [],
      outputs)
  AssertEqual([INVALID_OUTPUT], outputs)

  outputs = []
  AssertRaisesError(
      NOT_INTEGER_ERROR("NOT"),
      RunCase,
      TestCase(
          kings=[(0, 0), (5, -6), (-3, -1)],
          requests=[(1, 1), (-2, -4)]),
      ["NOT READY"],
      outputs)
  AssertEqual([INVALID_OUTPUT], outputs)

  outputs = []
  AssertReturns(
      None,
      RunCase,
      TestCase(
          kings=[(0, 0), (5, -6), (-3, -1)],
          requests=[(1, 1), (-2, -4)]),
      ["0 0"] * MAX_REQUESTS + [END_OF_PHASE_1, str(1+7+4), str(4+7+3)],
      outputs)
  AssertEqual([str(0+6+3)] * MAX_REQUESTS + ["1 1", "-2 -4", END_OF_PHASE_2],
              outputs)

  outputs = []
  AssertRaisesError(
      EXCEEDED_REQUESTS_ERROR(MAX_REQUESTS + 1),
      RunCase,
      TestCase(
          kings=[(0, 0), (5, -6), (-3, -1)],
          requests=[(1, 1), (-2, -4)]),
      ["0 0"] * (MAX_REQUESTS + 1) + [END_OF_PHASE_1, str(1+7+4), str(4+7+3)],
      outputs)
  AssertEqual([str(0+6+3)] * MAX_REQUESTS + [INVALID_OUTPUT], outputs)

  outputs = []
  AssertReturns(
      None,
      RunCase,
      TestCase(
          kings=[(0, 0)],
          requests=[]),
      ["{} {}".format(MAX_REQUEST_COORD, -MAX_REQUEST_COORD),
       END_OF_PHASE_1],
      outputs)
  AssertEqual([str(MAX_REQUEST_COORD), END_OF_PHASE_2], outputs)

  outputs = []
  AssertRaisesError(
      OUT_OF_BOUNDS_ERROR(MAX_REQUEST_COORD+1, -MAX_REQUEST_COORD),
      RunCase,
      TestCase(
          kings=[(0, 0)],
          requests=[]),
      ["{} {}".format(MAX_REQUEST_COORD+1, -MAX_REQUEST_COORD),
       END_OF_PHASE_1],
      outputs)
  AssertEqual([INVALID_OUTPUT], outputs)

  outputs = []
  AssertRaisesError(
      OUT_OF_BOUNDS_ERROR(MAX_REQUEST_COORD, -MAX_REQUEST_COORD-1),
      RunCase,
      TestCase(
          kings=[(0, 0)],
          requests=[]),
      ["{} {}".format(MAX_REQUEST_COORD, -MAX_REQUEST_COORD-1),
       END_OF_PHASE_1],
      outputs)
  AssertEqual([INVALID_OUTPUT], outputs)


def ValidateCases():
  assert len(N_MAXS) == len(CASES) == 2  # 2 test sets
  for n_max, cases in zip(N_MAXS, CASES):
    assert len(set(cases)) == len(cases) == NUM_CASES
    for case in cases:
      assert 1 <= len(case.kings) <= n_max
      assert 1 <= len(case.requests) <= MAX_REQUESTS
      assert len(case.kings) == len(set(case.kings))
      for x, y in case.kings:
        assert -MAX_COORD <= x <= MAX_COORD
        assert -MAX_COORD <= y <= MAX_COORD
      for x, y in case.requests:
        assert -MAX_REQUEST_COORD <= x <= MAX_REQUEST_COORD
        assert -MAX_REQUEST_COORD <= y <= MAX_REQUEST_COORD


def RunCases(cases, test_input=None, test_output_storage=None):
  for i, case in enumerate(cases, 1):
    try:
      RunCase(case, test_input=test_input,
              test_output_storage=test_output_storage)
    except Error as error:
      raise Error(CASE_FAILED_ERROR(i, error))

  def Input():
    if test_input is None:
      return raw_input()
    else:
      if test_input:
        return test_input.pop(0)
      else:
        raise EOFError()

  try:
    extra_input = Input()
  except EOFError:
    return
  except Exception:  # pylint: disable=broad-except
    raise Error(EXCEPTION_AFTER_END_ERROR)
  raise Error(ADDITIONAL_INPUT_ERROR(extra_input[:100]))


def TestRunCases():
  outputs = []
  AssertReturns(
      None,
      RunCases,
      [TestCase(
          kings=[(0, 0), (5, -6), (-3, -1)],
          requests=[(1, 1), (-2, -4)]),
       TestCase(
           kings=[(0, 0)],
           requests=[])],
      ["0 0", "2 -2", END_OF_PHASE_1, str(1+7+4), str(4+7+3), "5 5",
       END_OF_PHASE_1],
      outputs)
  AssertEqual([str(0+6+3), str(2+4+5), "1 1", "-2 -4", END_OF_PHASE_2, "5",
               END_OF_PHASE_2], outputs)

  outputs = []
  AssertRaisesError(
      CASE_FAILED_ERROR(1, WRONG_ANSWER(1, str(4+7+3), "8")),
      RunCases,
      [TestCase(
          kings=[(0, 0), (5, -6), (-3, -1)],
          requests=[(1, 1), (-2, -4)]),
       TestCase(
           kings=[(0, 0)],
           requests=[])],
      ["0 0", "2 -2", END_OF_PHASE_1, str(1+7+4), "8"],
      outputs)
  AssertEqual([str(0+6+3), str(2+4+5), "1 1", "-2 -4", INVALID_OUTPUT], outputs)

  outputs = []
  AssertReturns(
      None,
      RunCases,
      [],
      [],
      outputs)
  AssertEqual([], outputs)

  outputs = []
  AssertRaisesError(
      ADDITIONAL_INPUT_ERROR("foo"),
      RunCases,
      [],
      ["foo"],
      outputs)
  AssertEqual([], outputs)


def Test():
  TestReadValues()
  TestEvaluateRequest()
  TestRunCase()
  TestRunCases()
  ValidateCases()


def main():
  assert len(sys.argv) == 2
  index = int(sys.argv[1])
  if index == -2:
    Test()
  else:
    try:
      cases = CASES[index]
      n_max = N_MAXS[index]
      print len(cases), n_max, MAX_COORD, MAX_REQUESTS
      sys.stdout.flush()
      try:
        RunCases(cases)
      except Error as error:
        print >> sys.stderr, error
        sys.stdout.flush()
        sys.exit(1)
    except Exception as exception:
      # Hopefully this will never happen, but try to finish gracefully
      # and report a judge error in case of unexpected exception.
      print INVALID_OUTPUT
      sys.stdout.flush()
      print >> sys.stderr, 'JUDGE_ERROR! Internal judge exception:',
      print >> sys.stderr, str(exception)[:1000]
      sys.exit(1)


if __name__ == "__main__":
  main()
