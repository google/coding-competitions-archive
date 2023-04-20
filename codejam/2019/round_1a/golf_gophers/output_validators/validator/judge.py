"""judge.py for the Golf Gophers interactive judge.
"""

# Usage: `judge.py test_number`, where the argument test_number is either 0
# (small), 1 (large) or -2 (test mode).

import random
import sys

MAX_G = 10 ** 6
CASES = ([1, 2, 3, 4, 5, 7, 10, 11, 15, 50, 51, 55, 64, 81, 83,
          88, 91, 98, 99, 100],
         [1, 2, 3, 5, 7, 10, 11, 81, 99, 100, 120, 121, 125, 128, 200,
          MAX_G / 2, MAX_G / 2 + 1, MAX_G / 2 + 2, MAX_G - 1, MAX_G])
QS = (365, 7)
MAX_GOPHERS = (100, 10 ** 6)

WRONG_ANSWER, CORRECT_ANSWER = -1, 1

EXCEEDED_QUERIES_ERROR = "Exceeded number of queries: {}.".format
INVALID_LINE_ERROR = "Couldn't read a valid line."
NOT_INTEGER_ERROR = "Not an integer: {}".format
NUM_BLADES_OUT_OF_RANGE_ERROR = "Num blades {} is out of range [2-18].".format
NUM_GOPHERS_OUT_OF_RANGE_ERROR = "Num gophers {} is out of range [1-{}].".format
WRONG_NUM_TOKENS_ERROR = "Wrong number of tokens: {}. Expected 1 or 18.".format
WRONG_GUESS_ERROR = "Wrong guess: {}. Expected: {}.".format


def ReadValues(line, mg=None):
  t = line.split()
  if len(t) != 1 and len(t) != 18:
    return WRONG_NUM_TOKENS_ERROR(len(t))
  r = []
  for s in t:
    try:
      v = int(s)
    except:
      return NOT_INTEGER_ERROR(s if len(s) < 100 else s[:100])
    r.append(v)
  if len(r) == 1:
    if not (1 <= r[0] <= mg):
      return NUM_GOPHERS_OUT_OF_RANGE_ERROR(r[0], mg)
  else:
    for ri in r:
      if not (2 <= ri <= 18):
        return NUM_BLADES_OUT_OF_RANGE_ERROR(ri)
  return r


def TestReadValues():
  assert ReadValues("1", 500) == [1]
  assert ReadValues("500", 500) == [500]
  assert ReadValues(" 2  ", 500) == [2]
  assert ReadValues(" 0  ", 1) == NUM_GOPHERS_OUT_OF_RANGE_ERROR(0, 1)
  assert ReadValues("501", 500) == NUM_GOPHERS_OUT_OF_RANGE_ERROR(501, 500)
  assert ReadValues("-5", 5) == NUM_GOPHERS_OUT_OF_RANGE_ERROR(-5, 5)
  assert ReadValues("2 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18"
                    ) == [2] + range(2, 19)
  assert ReadValues(("18 " * 18)) == [18] * 18
  assert ReadValues("18 " * 17 + "1") == NUM_BLADES_OUT_OF_RANGE_ERROR(1)
  assert ReadValues("18 " * 17 + "0") == NUM_BLADES_OUT_OF_RANGE_ERROR(0)
  assert ReadValues("18 " * 17 + "-1") == NUM_BLADES_OUT_OF_RANGE_ERROR(-1)
  assert ReadValues("18 " * 17 + "19") == NUM_BLADES_OUT_OF_RANGE_ERROR(19)
  assert ReadValues("2 20 2 " + "18 " * 14 + "19") == NUM_BLADES_OUT_OF_RANGE_ERROR(20)
  for v, expected in (("1 1", WRONG_NUM_TOKENS_ERROR(2)),
                      ("   ", WRONG_NUM_TOKENS_ERROR(0)),
                      ("", WRONG_NUM_TOKENS_ERROR(0)),
                      ("18 " * 17, WRONG_NUM_TOKENS_ERROR(17)),
                      ("18 " * 19, WRONG_NUM_TOKENS_ERROR(19)),
                      ("a11", NOT_INTEGER_ERROR("a11")),
                      ("11a", NOT_INTEGER_ERROR("11a")),
                      ("abcdefghij" * 11,
                       NOT_INTEGER_ERROR("abcdefghij" * 10))):
    result = ReadValues(v)
    assert result == expected, (
      "TestReadValue({}): expected {}, got {}".format(
        v, expected, result))


def ValidateBinomial(r, g):
  assert len(r) == 18 and min(r) >= 0 and sum(r) == g, (
      "{} is not a valid binomial for {} gophers".format(r, g))


def ValidateHardcodedBinomials():
  # HARDCODED_BINOMIALS defined at the bottom.
  for g in HARDCODED_BINOMIALS:
    assert 1 <= g <= max(MAX_GOPHERS)
    for r in HARDCODED_BINOMIALS[g]:
      ValidateBinomial(r, g)
  # Make sure we never have to run the simulation online for tests with large
  # numbers of gophers.
  for g in CASES[1]:
    if g > 300:
      assert g in HARDCODED_BINOMIALS and len(HARDCODED_BINOMIALS[g]) == 7


def GopherChoices(g):
  # HARDCODED_BINOMIALS defined at the bottom.
  if g in HARDCODED_BINOMIALS and HARDCODED_BINOMIALS[g]:
    return HARDCODED_BINOMIALS[g].pop()
  r = [0] * 18
  for _ in xrange(g):
    r[random.randrange(18)] += 1
  return r


def TestGopherChoices():
  global HARDCODED_BINOMIALS
  HARDCODED_BINOMIALS = {1: [[1] + [0] * 17, [0] * 17 + [1]], 18: [[1] * 18]}
  assert GopherChoices(18) == [1] * 18
  for g in (1, 2, 3, 100, 2, 2, 18):
    ValidateBinomial(GopherChoices(g), g)
  assert GopherChoices(1) == [1] + [0] * 17
  for g in (1, 18):
    ValidateBinomial(GopherChoices(g), g)
  # This is flaky, but the probability of false negative is super low.
  assert len(set(tuple(GopherChoices(18)) for _ in xrange(10))) > 8
  HARDCODED_BINOMIALS = {19: [[i, 19 - i] + 16 * [0]] for i in xrange(10)}
  assert len(set(tuple(GopherChoices(19)) for _ in xrange(10))) == 10

def RunCase(qs, mg, case, test_input=None):
  outputs = []

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
      outputs.append(line)

  for ex in xrange(qs + 1):
    try:
      line = Input()
    except:
      Output(WRONG_ANSWER)
      return INVALID_LINE_ERROR, outputs
    v = ReadValues(line, mg)
    if isinstance(v, str):
      Output(WRONG_ANSWER)
      return v, outputs
    if len(v) == 18:
      if ex == qs:
        Output(WRONG_ANSWER)
        return EXCEEDED_QUERIES_ERROR(qs), outputs
      else:
        r = GopherChoices(case)
        for i in xrange(18):
          r[i] %= v[i]
        Output(" ".join(map(str, r)))
    else:
      if v[0] != case:
        Output(WRONG_ANSWER)
        return WRONG_GUESS_ERROR(v[0], case), outputs
      else:
        Output(CORRECT_ANSWER)
        return None, outputs


def TestRunCase():
  global HARDCODED_BINOMIALS
  HARDCODED_BINOMIALS = {10: [[10] + [0] * 17, [0] * 17 + [10],
                              [7] + [0] * 16 + [3]],
                         360: [[20] * 18]}
  for qs, mg, case, inputs, exp_outputs, exp_result in (
      (4, 100, 10, ["5 " + "2 " * 16 + "3", "8 " * 18, "10"],
       ["2" + " 0" * 17, "0 " * 17 + "2", 1], None),
      (4, 400, 360, ["2 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18", "360"],
       ["0 0 2 0 0 2 6 4 2 0 9 8 7 6 5 4 3 2", 1], None),
      (4, 100, 10, ["6 " * 18, "10"], ["4" + " 0" * 17, 1], None),
      (4, 100, 6, [], [-1], INVALID_LINE_ERROR),
      (4, 100, 6, ["HELLO"], [-1], NOT_INTEGER_ERROR("HELLO")),
      (4, 100, 6, ["1 2"], [-1], WRONG_NUM_TOKENS_ERROR(2)),
      (4, 100, 6, ["0 1 2 3 4 5 6"], [-1], WRONG_NUM_TOKENS_ERROR(7)),
      (4, 100, 6, ["6"], [1], None),
      (4, 100, 6, ["7"], [-1],
       WRONG_GUESS_ERROR(7, 6)),
      (4, 100, 6, ["2 " * 17 + "19"], [-1],
       NUM_BLADES_OUT_OF_RANGE_ERROR(19)),
      (4, 100, 6, ["2 " * 17 + "1"], [-1],
       NUM_BLADES_OUT_OF_RANGE_ERROR(1)),
      (4, 100, 6, ["101"], [-1],
       NUM_GOPHERS_OUT_OF_RANGE_ERROR(101, 100)),
      (4, 100, 6, ["0"], [-1],
       NUM_GOPHERS_OUT_OF_RANGE_ERROR(0, 100)),
      (4, 100, 6, ["18 " * 18] * 4 + ["6"], 1, None),
      (4, 100, 6, ["18 " * 18] * 5 + ["6"], -1,
       EXCEEDED_QUERIES_ERROR(4))):
    result, outputs = RunCase(qs, mg, case, test_input=inputs[:])
    if isinstance(exp_outputs, int):
      outputs = outputs[-1]
    assert (result, outputs) == (exp_result, exp_outputs), (
      "TestRunCase(qs={}, mg={}, case={}, test_input={}): "
      "expected {}, got {}".format(
        qs, mg, case, inputs, (exp_result, exp_outputs), (result, outputs)))

  RunCase(1, 50, 10, test_input=["", "10"])


def ValidateCases():
  assert len(MAX_GOPHERS) == len(QS) == len(CASES) == 2  # 2 test sets
  for i, cases in enumerate(CASES):
    assert len(set(cases)) == 20
    for case in cases:
      assert 1 <= case <= MAX_GOPHERS[i]


def RunCases(qs, mg, cases):
  for i, case in enumerate(cases, 1):
    result, _ = RunCase(qs, mg, case)
    if result:
      return "Case #{} ({}) failed: {}".format(i, case, result)
  try:
    extra_input = raw_input()
  except EOFError:
    return None
  except Exception:  # pylint: disable=broad-except
    return "Exception raised while reading input after all cases finish."
  return "Additional input after all cases finish: {}".format(extra_input[:100])


def Test():
  # ValidateHardcodedBinomials goes first because other tests modify the global.
  ValidateHardcodedBinomials()
  TestReadValues()
  TestGopherChoices()
  TestRunCase()
  ValidateCases()


def main():
  random.seed(313122)
  assert len(sys.argv) == 2
  index = int(sys.argv[1])
  if index == -2:
    Test()
  else:
    cases = CASES[index]
    qs = QS[index]
    mg = MAX_GOPHERS[index]
    random.shuffle(cases)
    print len(cases), qs, mg
    sys.stdout.flush()
    result = RunCases(qs, mg, cases)
    if result:
      print >> sys.stderr, result
      sys.stdout.flush()
      sys.exit(1)


# Generated by running generate_hardcoded_binonmials.py.
HARDCODED_BINOMIALS = {500000: [[27884, 27779, 27603, 27688, 27808, 27567, 28034, 27817, 28028, 27843, 27704, 27853, 27604, 27900, 27758, 27710, 27745, 27675], [27773, 27758, 27730, 27632, 27796, 27734, 27777, 28002, 27621, 27711, 28028, 27804, 27705, 27718, 27808, 27973, 27722, 27708], [27798, 27687, 27574, 27973, 27832, 27741, 27954, 27964, 27554, 27639, 27723, 27765, 27746, 27844, 27862, 27861, 27777, 27706], [27735, 27850, 27742, 27620, 27827, 27959, 27913, 27853, 27859, 27949, 27717, 27734, 27635, 27764, 27825, 27516, 27597, 27905], [27837, 28037, 27702, 27668, 27874, 27985, 27727, 27780, 27823, 27845, 27823, 27701, 27721, 27804, 27607, 27505, 27740, 27821], [27662, 27833, 27832, 27598, 27541, 28021, 27826, 27847, 27573, 27661, 27726, 27682, 27852, 27565, 28081, 27719, 28091, 27890], [28016, 27642, 27541, 27866, 27740, 27909, 27743, 27800, 27662, 27838, 27720, 27856, 27839, 28228, 27722, 27632, 27636, 27610]], 500001: [[27895, 27882, 27928, 27818, 28000, 27792, 27608, 27599, 27948, 27878, 27639, 27895, 27733, 27597, 27699, 27813, 27659, 27618], [27813, 28022, 28074, 28101, 27705, 27516, 27779, 27704, 27550, 27599, 27913, 27675, 27780, 27557, 27766, 27894, 27790, 27763], [27387, 27666, 27789, 28175, 27902, 27953, 27834, 27757, 27735, 27925, 27780, 27864, 27919, 27566, 27806, 27594, 27924, 27425], [27971, 27686, 27821, 27696, 28208, 27957, 27542, 27809, 27849, 27493, 27883, 27836, 27667, 27840, 27712, 27535, 27673, 27823], [28063, 27510, 27704, 27783, 27390, 27795, 27567, 27788, 28026, 27854, 27796, 27652, 27803, 28038, 27548, 27800, 28184, 27700], [27935, 27832, 27789, 27783, 27888, 28243, 27839, 27835, 27704, 27475, 27761, 27755, 27714, 27464, 27893, 27394, 27947, 27750], [27772, 27808, 27591, 27819, 27987, 27983, 27832, 27789, 27856, 27561, 27669, 27709, 27817, 28056, 27703, 27512, 27696, 27841]], 500002: [[27723, 27796, 27740, 27725, 27843, 27728, 27737, 27540, 28173, 27786, 27609, 27972, 27676, 28074, 27656, 27872, 27724, 27628], [27569, 27471, 27855, 27917, 28025, 27654, 27665, 27888, 27728, 28092, 27966, 27737, 27855, 27842, 27540, 27686, 27677, 27835], [27881, 27690, 27750, 27711, 27888, 27817, 27780, 27860, 27833, 27882, 27850, 27669, 27893, 27347, 27421, 27905, 27970, 27855], [27471, 27710, 27701, 27825, 27750, 27985, 27725, 28093, 27861, 27859, 27599, 27832, 27666, 27882, 27915, 27651, 27829, 27648], [27955, 27701, 27857, 28065, 27802, 27672, 27976, 27845, 27723, 27588, 27579, 27735, 27846, 27653, 27776, 27798, 27872, 27559], [27654, 27800, 27820, 27817, 27689, 27394, 27941, 27720, 27719, 27658, 27954, 27989, 27735, 27954, 27793, 27970, 27535, 27860], [27595, 27951, 27788, 27567, 27411, 27775, 27643, 27847, 28044, 28057, 27721, 27911, 27760, 27737, 27880, 28030, 27641, 27644]], 1000000: [[55467, 55478, 55443, 55509, 56050, 55606, 55246, 55284, 55644, 55548, 55895, 55433, 55961, 55452, 55367, 55555, 55588, 55474], [55557, 55489, 55346, 55308, 55320, 55309, 55468, 55926, 55682, 55873, 55444, 55715, 55368, 55266, 55737, 55808, 55858, 55526], [55557, 55467, 55280, 55724, 55629, 55944, 55773, 55619, 55524, 55176, 55304, 55394, 55523, 55350, 55664, 55207, 55944, 55921], [55711, 55999, 55946, 55109, 55888, 55588, 55613, 55473, 55785, 55485, 55577, 55420, 55328, 55583, 55021, 55678, 55606, 55190], [55586, 55705, 55692, 55600, 55899, 55346, 55579, 55124, 55694, 55748, 55555, 55641, 55247, 55086, 55467, 55919, 55826, 55286], [55272, 55412, 55539, 55615, 55371, 55657, 55534, 55710, 55387, 55611, 55448, 55837, 55370, 55610, 56037, 55661, 55461, 55468], [55687, 55605, 55479, 55573, 56097, 55500, 55280, 55777, 55548, 55935, 55274, 55264, 55266, 55519, 55775, 55372, 55337, 55712]], 999999: [[55656, 55449, 55279, 55737, 55882, 56192, 55816, 55667, 55241, 55309, 55244, 55186, 55044, 55779, 55475, 55913, 55500, 55630], [55396, 55855, 55497, 55814, 55625, 55685, 55253, 55552, 55270, 55895, 55258, 55299, 55916, 55834, 55595, 55523, 55328, 55404], [55732, 55527, 55636, 55727, 55646, 55620, 55607, 55942, 55408, 55269, 55631, 55717, 55691, 55470, 55322, 55340, 55221, 55493], [55600, 55502, 55648, 55753, 55941, 55525, 55586, 55501, 55220, 55165, 55684, 56197, 56011, 55375, 55744, 54919, 55542, 55086], [55678, 55768, 55750, 55629, 55529, 55796, 55005, 55570, 55736, 55336, 55400, 55537, 55559, 55547, 55375, 56226, 55059, 55499], [55747, 55622, 54957, 55354, 55971, 55687, 55353, 55618, 55851, 55070, 55659, 55732, 55816, 55593, 55663, 55514, 55525, 55267], [55738, 55692, 56066, 55141, 55780, 55679, 55309, 55871, 55344, 55299, 55616, 55488, 55481, 55343, 55745, 55306, 55389, 55712]]}


if __name__ == "__main__":
  main()

